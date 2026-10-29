from pathlib import Path
import json,sys
import numpy as np,pandas as pd,joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from model_study import O,S,TARGETS,metrics,SEED
plt.rcParams.update({'font.size':10,'figure.dpi':120,'axes.spines.top':False,'axes.spines.right':False})

def paired(a,b):
 d=a-b;rng=np.random.default_rng(SEED);v=d.to_numpy();z=v[rng.integers(len(v),size=(5000,len(v)))].mean(axis=1)
 return float(d.mean()),float(np.quantile(z,.025)),float(np.quantile(z,.975))

def run():
 p=pd.read_csv(O/'heldout_predictions.csv.gz');m=pd.read_csv(O/'model_comparison.csv');y=pd.read_csv(O/'target_table.csv');f=pd.read_csv(O/'feature_table.csv.gz')
 v=p[(p.stage=='validation')&(p.aperture=='fixed12')];r=v.assign(ae=abs(v.truth-v.prediction)).groupby(['target','bands','mode','model','subhalo_id']).ae.mean()
 comparisons=[]
 for target in TARGETS:
  for model in v.model.unique():
   a=r.loc[target,'nir','seeing',model];b=r.loc[target,'nir','glao',model];gain,lo,hi=paired(a,b)
   comparisons.append(dict(target=target,model=model,comparison='seeing_minus_GLAO_MAE',gain=gain,lo=lo,hi=hi,n_galaxies=len(a)))
   a=r.loc[target,'optical','seeing',model];b=r.loc[target,'nir','seeing',model];gain,lo,hi=paired(a,b)
   comparisons.append(dict(target=target,model=model,comparison='optical_minus_NIRseeing_MAE',gain=gain,lo=lo,hi=hi,n_galaxies=len(a)))
   for mode in ['seeing','glao']:
    a=r.loc[target,'nir',mode,'constant_photo_median'];b=r.loc[target,'nir',mode,model];gain,lo,hi=paired(a,b)
    comparisons.append(dict(target=target,model=model,mode=mode,comparison='constant_minus_model_MAE',gain=gain,lo=lo,hi=hi,n_galaxies=len(a)))
 pd.DataFrame(comparisons).to_csv(O/'paired_galaxy_comparisons.csv',index=False)
 # Aperture definition sensitivity at galaxy level, including zero controls.
 a=y[y.aperture=='fixed12'];b=y[y.aperture=='adaptive'];z=a.merge(b,on=['subhalo_id','view','partition'],suffixes=['_fixed','_adaptive'],validate='one_to_one');ar=[]
 for target in TARGETS:
  delta=z[target+'_adaptive']-z[target+'_fixed'];gg=z.assign(delta=delta,absolute=abs(delta)).groupby('subhalo_id').agg(delta=('delta','mean'),absolute=('absolute','mean'))
  ar.append(dict(target=target,median_galaxy_absolute_change=gg.absolute.median(),mean_galaxy_absolute_change=gg.absolute.mean(),max_galaxy_absolute_change=gg.absolute.max()))
 pd.DataFrame(ar).to_csv(O/'aperture_target_sensitivity.csv',index=False)
 envelopes=json.loads((O/'label_policy_freeze.json').read_text())['envelopes']
 flags=y[['subhalo_id','view','partition','aperture','zero_projected_dust','reference_aperture_limited','adaptive_radius_capped']].copy()
 for t in TARGETS:
  flags['finite_'+t]=np.isfinite(y[t]);en={v['aperture']:v['max_abs'] for v in envelopes if v['target']==t};flags['within_control_envelope_'+t]=[abs(x)<=en[ap] for x,ap in zip(y[t],y.aperture)]
 flags.to_csv(O/'label_quality_flags.csv',index=False)
 # Correction accuracy explicitly includes the PSF/noisy observation discrepancy.
 c=v[v.target.isin(['dR50_Ks','dC_Ks'])].copy();cr=[]
 for keys,g in c.groupby(['target','bands','mode','model']):
  row=dict(zip(['target','bands','mode','model'],keys))
  for label,col in [('uncorrected_observed','observed'),('corrected_observed','corrected'),('uncorrected_native','dusty_native'),('corrected_native','native_corrected')]:
   errors=abs(g[col]-g.clear_native);row[label+'_MAE']=g.assign(error=errors).groupby('subhalo_id').error.mean().mean()
  cr.append(row)
 pd.DataFrame(cr).to_csv(O/'morphology_correction_accuracy.csv',index=False)
 # Diagnose variation using metadata for evaluation only, never inputs.
 d=v.assign(ae=abs(v.truth-v.prediction),residual=v.prediction-v.truth)
 for col in ['log_stellar_mass','SFR_Msun_yr','dust_mass_field_Msun','Ks_q','Ks_logJy']:
  values=d[['subhalo_id','view','draw',col]].drop_duplicates();edges=np.unique(np.quantile(values[col],[0,1/3,2/3,1]));d['bin_'+col]=pd.cut(d[col],edges,include_lowest=True,duplicates='drop').astype(str)
 seg=[]
 for dim in ['view']+['bin_'+x for x in ['log_stellar_mass','SFR_Msun_yr','dust_mass_field_Msun','Ks_q','Ks_logJy']]:
  t=d.groupby(['target','bands','mode','model',dim,'subhalo_id']).agg(MAE=('ae','mean'),bias=('residual','mean')).reset_index();t=t.groupby(['target','bands','mode','model',dim]).agg(MAE=('MAE','mean'),bias=('bias','mean'),galaxies=('subhalo_id','nunique')).reset_index().rename(columns={dim:'bin'});t['dimension']=dim;seg.append(t)
 pd.concat(seg).to_csv(O/'validation_subgroups.csv',index=False)
 # Freeze-fitted model stress scores on O1 only.
 settings=json.loads((O/'model_settings.json').read_text());stress=[]
 files=list((O/'sensitivity_features').glob('*.csv.gz'));all_sf=pd.concat([pd.read_csv(x) for x in files],ignore_index=True)
 for tag,conf in settings.items():
  ap,bands,mode=tag.split('_')[:3];target=next(t for t in sorted(TARGETS,key=len,reverse=True) if tag.startswith('_'.join([ap,bands,mode,t])+'_'))
  sf=all_sf[(all_sf.aperture==ap)&(all_sf['mode']==mode)].copy()
  sf=sf.merge(y[y.aperture==ap][['subhalo_id','view',target,'partition','zero_projected_dust']],on=['subhalo_id','view'],validate='many_to_one');sf=sf[(sf.partition=='validation')|sf.zero_projected_dust]
  pred=np.full(len(sf),conf['constant']) if conf['model']=='constant' else joblib.load(O/'models'/f'{tag}.joblib').predict(sf[conf['features']])
  sf['prediction']=pred;sf['truth']=sf[target];sf['target']=target;sf['tag']=tag;sf['model']=next(g for g in p[p.tag==tag].model.unique());sf['bands']=bands;sf['stage']=np.where(sf.zero_projected_dust,'source_controls','validation');stress.append(sf[['subhalo_id','view','draw','scenario','mode','aperture','prediction','truth','target','tag','model','bands','stage']])
 sp=pd.concat(stress,ignore_index=True);sp.to_csv(O/'sensitivity_predictions.csv.gz',index=False);metrics(sp,['stage','scenario','aperture','bands','mode','target','model','tag']).to_csv(O/'sensitivity_summary.csv',index=False)
 # Frozen models scored with equal per-pixel variance and noiseless inputs.
 extra=[]
 for tag,conf in settings.items():
  ap,bands,mode=tag.split('_')[:3];target=next(t for t in sorted(TARGETS,key=len,reverse=True) if tag.startswith('_'.join([ap,bands,mode,t])+'_'))
  ff=f[(f.partition=='validation')&(f.aperture==ap)&(f['mode']==mode)&f.condition.isin(['equal_noise','noiseless'])].merge(y[y.aperture==ap][['subhalo_id','view',target]],on=['subhalo_id','view'],validate='many_to_one')
  ff['prediction']=conf['constant'] if conf['model']=='constant' else joblib.load(O/'models'/f'{tag}.joblib').predict(ff[conf['features']]);ff['truth']=ff[target];ff['tag']=tag;ff['target']=target
  extra.append(ff[['subhalo_id','view','draw','condition','prediction','truth','tag','target']])
 ep=pd.concat(extra,ignore_index=True);ep.to_csv(O/'noise_condition_predictions.csv.gz',index=False);metrics(ep,['condition','target','tag']).to_csv(O/'noise_condition_summary.csv',index=False)
 # Publication figure panels.
 selected=['constant_photo_median','ridge_photo','ridge_summary','forest_summary','boost_summary','ridge_spatial']
 fig,axes=plt.subplots(1,3,figsize=(14,4))
 for ax,target,unit in zip(axes,TARGETS[:3],['mag','kpc','dimensionless']):
  mm=m[(m.stage=='validation')&(m.aperture=='fixed12')&(m.bands=='nir')&(m['mode']=='seeing')&(m.target==target)].set_index('model').loc[selected]
  x=np.arange(len(mm));ax.barh(x,mm.MAE,color='#4477AA');ax.errorbar(mm.MAE,x,xerr=[mm.MAE-mm.MAE_lo,mm.MAE_hi-mm.MAE],fmt='none',color='black',capsize=2);ax.set_yticks(x,selected);ax.set_xlabel('Galaxy-weighted MAE ('+unit+')');ax.set_title(target+'; validation14')
 fig.tight_layout();fig.savefig(O/'figures/model_comparison.png',dpi=240);fig.savefig(O/'figures/model_comparison.pdf');plt.close(fig)
 fig,axes=plt.subplots(2,3,figsize=(12,7))
 for j,target in enumerate(TARGETS[:3]):
  for model,color in [('ridge_photo','#4477AA'),('ridge_spatial','#CC6677')]:
   pp=v[(v.target==target)&(v.bands=='nir')&(v['mode']=='seeing')&(v.model==model)];gg=pp.groupby(['subhalo_id','view'])[['truth','prediction']].mean();axes[0,j].scatter(gg.truth,gg.prediction,s=12,alpha=.6,label=model,color=color);axes[1,j].scatter(gg.truth,gg.prediction-gg.truth,s=12,alpha=.6,color=color)
  low=min(axes[0,j].get_xlim()[0],axes[0,j].get_ylim()[0]);hi=max(axes[0,j].get_xlim()[1],axes[0,j].get_ylim()[1]);axes[0,j].plot([low,hi],[low,hi],':',color='black');axes[1,j].axhline(0,color='black',ls=':');axes[0,j].set_title(target);axes[0,j].set_ylabel('Predicted');axes[1,j].set_ylabel('Predicted − pair reference');axes[1,j].set_xlabel('Native DR1 pair reference')
 axes[0,0].legend(fontsize=8);fig.tight_layout();fig.savefig(O/'figures/predictions_residuals.png',dpi=240);fig.savefig(O/'figures/predictions_residuals.pdf');plt.close(fig)
 comp=pd.DataFrame(comparisons);fig,axes=plt.subplots(1,3,figsize=(13,4))
 for ax,target in zip(axes,TARGETS[:3]):
  t=comp[(comp.target==target)&(comp.comparison=='seeing_minus_GLAO_MAE')].set_index('model').loc[selected];xx=np.arange(len(t));ax.errorbar(t.gain,xx,xerr=[t.gain-t.lo,t.hi-t.gain],fmt='o',color='#228833',capsize=3);ax.axvline(0,color='black',ls=':');ax.set_yticks(xx,selected);ax.set_title(target);ax.set_xlabel('Seeing MAE − GLAO MAE ('+{'A_g':'mag','dR50_Ks':'kpc','dC_Ks':'dimensionless'}[target]+')')
 fig.tight_layout();fig.savefig(O/'figures/GLAO_increment.png',dpi=240);fig.savefig(O/'figures/GLAO_increment.pdf');plt.close(fig)
 lc=pd.read_csv(O/'learning_curves.csv');fig,axes=plt.subplots(1,3,figsize=(12,3.5))
 for ax,target in zip(axes,TARGETS[:3]):
  for kind in ['photo','spatial']:
   ll=lc[(lc.tag=='fixed12_nir_seeing_'+target+'_ridge_'+kind+'_')].copy();ll['subset']=np.where(ll.n_train_galaxies>48,999,ll.n_train_galaxies);ll=ll.groupby('subset').agg(n_train_galaxies=('n_train_galaxies','mean'),mean=('MAE','mean'),std=('MAE','std')).reset_index();ax.errorbar(ll.n_train_galaxies,ll['mean'],yerr=ll['std'],marker='o',label=kind,capsize=2)
  ax.set_title(target);ax.set_xlabel('Independent training galaxies');ax.set_ylabel('Development group-CV MAE')
 axes[0].legend();fig.tight_layout();fig.savefig(O/'figures/learning_curves.png',dpi=240);fig.savefig(O/'figures/learning_curves.pdf');plt.close(fig)
 # Interval assessment and morphology correction, both with explicit reference.
 cal=pd.read_csv(O/'uncertainty_calibration.csv');corr=pd.DataFrame(cr)
 fig,axes=plt.subplots(1,3,figsize=(12,3.5))
 for ax,target,kind in zip(axes,TARGETS[:3],['photo','spatial','spatial']):
  row=cal[cal.tag=='fixed12_nir_seeing_'+target+'_ridge_'+kind+'_'].iloc[0]
  pp=v[(v.target==target)&(v.bands=='nir')&(v['mode']=='seeing')&(v.model=='ridge_'+kind)]
  split=json.loads((O/'validation_interval_split.json').read_text());pp=pp[pp.subhalo_id.isin(split['assessment'])]
  maximum=pp.assign(error=abs(pp.truth-pp.prediction)).groupby('subhalo_id').error.max().sort_values()
  ax.bar(np.arange(len(maximum)),maximum,color='#4477AA');ax.axhline(row.half_width,color='#CC6677',ls='--',label='calibrated half-width');ax.set_title(target);ax.set_xlabel('Assessment galaxies (7)');ax.set_ylabel('Maximum |residual| over views/draws');ax.legend(fontsize=8)
 fig.tight_layout();fig.savefig(O/'figures/interval_assessment.png',dpi=240);fig.savefig(O/'figures/interval_assessment.pdf');plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(10,4))
 for ax,target in zip(axes,['dR50_Ks','dC_Ks']):
  cc=corr[(corr.target==target)&(corr.bands=='nir')&(corr['mode']=='seeing')].set_index('model').loc[selected]
  ax.barh(np.arange(len(cc)),cc.corrected_observed_MAE,color='#4477AA',label='Observed minus predicted pair bias');ax.axvline(cc.uncorrected_observed_MAE.iloc[0],color='#CC6677',ls='--',label='Observed uncorrected');ax.set_yticks(np.arange(len(cc)),selected);ax.set_title(target);ax.set_xlabel('MAE relative to native clear morphology');ax.legend(fontsize=8)
 fig.tight_layout();fig.savefig(O/'figures/morphology_correction.png',dpi=240);fig.savefig(O/'figures/morphology_correction.pdf');plt.close(fig)
 fig,axes=plt.subplots(1,3,figsize=(12,3.5))
 sm=pd.read_csv(O/'sensitivity_summary.csv')
 for ax,target,kind in zip(axes,TARGETS[:3],['photo','spatial','spatial']):
  ss=sm[(sm.stage=='validation')&(sm.tag=='fixed12_nir_seeing_'+target+'_ridge_'+kind+'_')].sort_values('scenario')
  ax.barh(np.arange(len(ss)),ss.MAE,color='#228833');ax.set_yticks(np.arange(len(ss)),ss.scenario);ax.set_title(target+'; O1 only');ax.set_xlabel('Galaxy-weighted MAE')
 fig.tight_layout();fig.savefig(O/'figures/empirical_stress.png',dpi=240);fig.savefig(O/'figures/empirical_stress.pdf');plt.close(fig)
 print('Summary and figures complete',flush=True)
if __name__=='__main__':run()
