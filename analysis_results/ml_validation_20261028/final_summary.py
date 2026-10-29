"""Predeclared final diagnostics; no refits, selection or parameter changes."""
from model_study import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def run():
 p=pd.read_csv(O/'final_predictions.csv.gz');lookup=pd.read_csv(O/'model_comparison.csv')[['tag','aperture','bands','mode','target','model']].drop_duplicates('tag');p=p.merge(lookup,on=['tag','target'],validate='many_to_one');y=pd.read_csv(O/'final_products/final_targets.csv');f=pd.read_csv(O/'final_products/final_features.csv.gz')
 p=p.merge(y[['subhalo_id','view','aperture','zero_projected_dust','stellar_mass_Msun','SFR_Msun_yr','dust_mass_field_Msun','clear_R50_Ks','dusty_R50_Ks','clear_C_Ks','dusty_C_Ks']],on=['subhalo_id','view','aperture'],validate='many_to_one')
 p=p.merge(f[(f.condition=='nominal')][['subhalo_id','view','aperture','mode','draw','Ks_R50','Ks_C','Ks_q','Ks_logJy']],on=['subhalo_id','view','aperture','mode','draw'],validate='many_to_one');p['residual']=p.prediction-p.truth
 metrics(p,['tag','target','zero_projected_dust']).to_csv(O/'final_source_control_strata.csv',index=False)
 cal=pd.read_csv(O/'uncertainty_calibration.csv').set_index('tag');interval=[];correct=[]
 for tag,g in p.groupby('tag'):
  width=cal.loc[tag,'half_width'];covered=g.assign(covered=abs(g.residual)<=width).groupby('subhalo_id').covered.all();interval.append(dict(tag=tag,half_width=width,entire_galaxy_coverage=covered.mean(),covered_galaxies=int(covered.sum()),n_galaxies=len(covered)))
  if g.target.iloc[0] in ['dR50_Ks','dC_Ks']:
   metric='R50' if g.target.iloc[0]=='dR50_Ks' else 'C';row=dict(tag=tag,target=g.target.iloc[0])
   for kind,values in [('observed_uncorrected',g['Ks_'+metric]),('observed_corrected',g['Ks_'+metric]-g.prediction),('native_uncorrected',g['dusty_'+metric+'_Ks']),('native_corrected',g['dusty_'+metric+'_Ks']-g.prediction)]:row[kind+'_MAE']=g.assign(error=abs(values-g['clear_'+metric+'_Ks'])).groupby('subhalo_id').error.mean().mean()
   correct.append(row)
 pd.DataFrame(interval).to_csv(O/'final_uncertainty_calibration.csv',index=False);pd.DataFrame(correct).to_csv(O/'final_morphology_correction.csv',index=False)
 # Paired band and model improvements, resampling final galaxies only.
 comparisons=[];err=p.assign(ae=abs(p.residual)).groupby(['target','aperture','bands','mode','model','subhalo_id']).ae.mean()
 for target in TARGETS:
  for model in p.model.unique():
   for comparison,aa,bb in [('seeing_minus_GLAO',('nir','seeing',model),('nir','glao',model)),('optical_minus_NIR',('optical','seeing',model),('nir','seeing',model)),('constant_minus_model',('nir','seeing','constant_photo_median'),('nir','seeing',model)),('photo_minus_model',('nir','seeing','ridge_photo'),('nir','seeing',model))]:
    a=err.loc[(target,'fixed12',*aa)];b=err.loc[(target,'fixed12',*bb)];v=(a-b).to_numpy();rng=np.random.default_rng(SEED);boot=v[rng.integers(len(v),size=(5000,len(v)))].mean(axis=1);comparisons.append(dict(target=target,model=model,comparison=comparison,gain=v.mean(),lo=np.quantile(boot,.025),hi=np.quantile(boot,.975),n_galaxies=len(v)))
 pd.DataFrame(comparisons).to_csv(O/'final_paired_comparisons.csv',index=False)
 # Keep every final view and draw with diagnostics, separate from raw scoring output.
 p.to_csv(O/'final_diagnostic_predictions.csv.gz',index=False)
 sub=[]
 for dim in ['view','zero_projected_dust']:
  a=p.assign(ae=abs(p.residual)).groupby(['tag',dim,'subhalo_id']).agg(MAE=('ae','mean'),bias=('residual','mean')).reset_index();a=a.groupby(['tag',dim]).agg(MAE=('MAE','mean'),bias=('bias','mean'),galaxies=('subhalo_id','nunique')).reset_index().rename(columns={dim:'bin'});a['dimension']=dim;sub.append(a)
 pd.concat(sub).to_csv(O/'final_orientation_diagnostics.csv',index=False)
 fig,axes=plt.subplots(2,3,figsize=(12,7))
 for j,target in enumerate(TARGETS[:3]):
  for model,color in [('ridge_photo','#4477AA'),('ridge_spatial','#CC6677')]:
   pp=p[(p.target==target)&(p.aperture=='fixed12')&(p.bands=='nir')&(p['mode']=='seeing')&(p.model==model)].groupby(['subhalo_id','view'])[['truth','prediction']].mean();axes[0,j].scatter(pp.truth,pp.prediction,s=12,alpha=.6,label=model,color=color);axes[1,j].scatter(pp.truth,pp.prediction-pp.truth,s=12,alpha=.6,color=color)
  low=min(axes[0,j].get_xlim()[0],axes[0,j].get_ylim()[0]);hi=max(axes[0,j].get_xlim()[1],axes[0,j].get_ylim()[1]);axes[0,j].plot([low,hi],[low,hi],':',color='black');axes[1,j].axhline(0,color='black',ls=':');axes[0,j].set_title(target+'; final20');axes[0,j].set_ylabel('Predicted');axes[1,j].set_xlabel('Native signed pair reference');axes[1,j].set_ylabel('Prediction − reference')
 axes[0,0].legend(fontsize=8);fig.tight_layout();fig.savefig(O/'figures/final_predictions_residuals.png',dpi=240);fig.savefig(O/'figures/final_predictions_residuals.pdf');plt.close(fig)
 print('Final diagnostics complete without refitting')
if __name__=='__main__':run()
