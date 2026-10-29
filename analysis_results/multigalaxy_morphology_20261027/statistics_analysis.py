"""Galaxy is the sampling unit; orientations and noise draws are repeated measurements."""
from pathlib import Path
import json
import numpy as np,pandas as pd
from scipy import stats
O=Path(__file__).resolve().parent;DATA=O.parents[1]/'data/TNG50_SKIRT_DR1_extra';METRICS=['R50','C','A','q']

def interval(a,statistic='mean'):
 a=np.asarray(a,dtype=float);a=a[np.isfinite(a)]
 if not len(a):return [np.nan,np.nan]
 rng=np.random.default_rng(20261027);sample=a[rng.integers(0,len(a),(5000,len(a)))]
 vals=np.mean(sample,axis=1) if statistic=='mean' else np.median(sample,axis=1)
 return np.quantile(vals,[.025,.975]).tolist()

def pairs(df,keys,metrics):
 c=df[df.scene=='clear'].set_index(keys);d=df[df.scene=='dusty'].set_index(keys)
 assert c.index.is_unique and d.index.is_unique and c.index.equals(d.index) or (c.index.is_unique and d.index.is_unique and set(c.index)==set(d.index))
 out=pd.DataFrame(index=d.index)
 for metric in metrics:
  out[metric+'_clear']=c[metric];out[metric+'_dusty']=d[metric];out['delta_'+metric]=d[metric]-c[metric]
 out['attenuation_mag']=-2.5*np.log10(d.flux/c.flux)
 return out.reset_index()

def run():
 meta=pd.read_csv(O/'galaxy_metadata.csv');intr=pd.read_csv(O/'intrinsic_morphology.csv');phys=pd.read_csv(O/'physical_maps.csv')
 pair=pairs(intr,['subhalo_id','view','band','setting'],METRICS);pair.to_csv(O/'intrinsic_pairs.csv',index=False)
 base=pair[pair.setting=='12'].copy();base.to_csv(O/'primary_dust_bias.csv',index=False)
 galaxy=base.groupby(['subhalo_id','band']).agg(**{f'{k}_{s}':(k,s) for k in ['delta_'+m for m in METRICS]+['attenuation_mag','q_clear','C_clear','R50_clear'] for s in ['mean','median','std','min','max']}).reset_index()
 galaxy=galaxy.merge(meta,on='subhalo_id',validate='many_to_one')
 dust=phys[phys['product']=='dustmass'].groupby('subhalo_id').agg(dust_mass_field_Msun=('field_mass_Msun','mean'),dust_mass_R12_Msun=('R12_mass_Msun','mean'),dust_mass_view_SD_Msun=('field_mass_Msun','std')).reset_index()
 galaxy=galaxy.merge(dust,on='subhalo_id',validate='many_to_one');galaxy.to_csv(O/'galaxy_level_morphology.csv',index=False)
 summary=[]
 for scope,sub in [('all_26',galaxy),('held_out_21',galaxy[galaxy.role=='held_out']),('development_5',galaxy[galaxy.role=='development'])]:
  for band,g in sub.groupby('band'):
   for metric in ['delta_'+m for m in METRICS]+['attenuation_mag']:
    a=g[metric+'_mean'];lo,hi=interval(a,'median');ml,mh=interval(a)
    summary.append(dict(scope=scope,band=band,metric=metric,n_galaxies=len(a),galaxy_mean=a.mean(),mean_CI_low=ml,mean_CI_high=mh,galaxy_median=a.median(),median_CI_low=lo,median_CI_high=hi,between_galaxy_SD=a.std(),median_within_galaxy_view_SD=g[metric+'_std'].median(),n_positive=int((a>1e-8).sum()),n_negative=int((a< -1e-8).sum()),n_near_zero=int((abs(a)<=1e-8).sum()),minimum=a.min(),maximum=a.max()))
 pd.DataFrame(summary).to_csv(O/'galaxy_bootstrap_summary.csv',index=False)
 # Radius and centre sensitivity relative to R12; no post-hoc exclusion.
 robust=pair[pair.setting!='12'].merge(base,on=['subhalo_id','view','band'],suffixes=('_alternative','_primary'),validate='many_to_one')
 for m in METRICS:
  robust[f'change_delta_{m}']=robust[f'delta_{m}_alternative']-robust[f'delta_{m}_primary']
  robust[f'sign_flip_{m}']=(robust[f'delta_{m}_alternative']*robust[f'delta_{m}_primary']<0)&(abs(robust[f'delta_{m}_alternative'])>1e-6)&(abs(robust[f'delta_{m}_primary'])>1e-6)
 robust.to_csv(O/'aperture_center_robustness.csv',index=False)
 flux=intr[(intr.band.isin(['LSST_g','2MASS_Ks']))&(intr.setting.isin(['12','30']))].pivot(index=['subhalo_id','view','band','scene'],columns='setting',values='flux').reset_index()
 flux['F12_over_F30']=flux['12']/flux['30'];flux['aperture_limited']=flux.F12_over_F30<.8;flux.to_csv(O/'aperture_quality.csv',index=False)
 inv=meta.merge(dust,on='subhalo_id');inv=inv.merge(flux.groupby('subhalo_id').agg(min_F12_over_F30=('F12_over_F30','min'),n_aperture_limited=('aperture_limited','sum')).reset_index(),on='subhalo_id')
 inv=inv.merge(galaxy[galaxy.band=='2MASS_Ks'][['subhalo_id','q_clear_mean','C_clear_mean','R50_clear_mean']].rename(columns={'q_clear_mean':'Ks_intrinsic_apparent_q_mean','C_clear_mean':'Ks_intrinsic_concentration_mean','R50_clear_mean':'Ks_intrinsic_R50_R12_kpc_mean'}),on='subhalo_id',validate='one_to_one')
 inv['mean_R12_dust_surface_density_Msun_pc2']=inv.dust_mass_R12_Msun/(np.pi*12**2*1e6)
 inv['dust_field_projection_CV']=inv.dust_mass_view_SD_Msun/inv.dust_mass_field_Msun.where(inv.dust_mass_field_Msun>0)
 inv['dust_projection_CV_above_5pct']=inv.dust_field_projection_CV>.05
 inv['zero_projected_dust']=inv.dust_mass_field_Msun==0;inv['all_22_bands_all_5_views']=True;inv['true_inclination_available']=False;inv['morphological_classification_available']=False
 inv.to_csv(O/'galaxy_inventory.csv',index=False)
 # Association is exploratory, unadjusted; sample balanced, no scaling-law regression.
 assoc=[]
 for band in ['LSST_g','2MASS_Ks']:
  gg=galaxy[galaxy.band==band].copy();gg['log_dust_mass']=np.log10(gg.dust_mass_field_Msun.where(gg.dust_mass_field_Msun>0));gg['log_sSFR']=np.log10(gg.sSFR_yr_inverse.where(gg.sSFR_yr_inverse>0))
  for x in ['log10_stellar_mass','log_sSFR','log_dust_mass','q_clear_mean','C_clear_mean']:
   for y in ['delta_'+m+'_mean' for m in METRICS]:
    sel=gg[[x,y]].dropna();r=stats.spearmanr(sel[x],sel[y]);assoc.append(dict(band=band,property=x,response=y,n_galaxies=len(sel),Spearman_rho=r.statistic,unadjusted_p=r.pvalue,interpretation='exploratory, no multiple-test-controlled claim'))
 pd.DataFrame(assoc).to_csv(O/'property_associations.csv',index=False)
 parent=pd.read_csv(DATA/'eligible_catalogue.csv');sel=pd.read_csv(DATA/'selected_galaxies.csv')
 cells=parent.groupby(['mass_stratum','activity_stratum']).size().rename('eligible_cell_N').reset_index();cells['selected_N']=1;cells['selection_probability']=1/cells.eligible_cell_N;cells.to_csv(O/'selection_cells.csv',index=False)
 cat=np.loadtxt(DATA/'baes24_tng50_skirt_atlas.txt');selection=dict(parent_N=len(cat),eligible_N=len(parent),selected_random_N=len(sel),convenience_original_N=1,parent_zero_SFR_fraction=float(np.mean(cat[:,4]==0)),eligible_zero_SFR_fraction=float(np.mean(parent.SFR_Msun_yr==0)),selected_zero_SFR_fraction=float(np.mean(sel.SFR_Msun_yr==0)),parent_logmass_range=np.log10([cat[:,1].min(),cat[:,1].max()]).tolist(),selected_logmass_range=[float(sel.log10_stellar_mass.min()),float(sel.log10_stellar_mass.max())],parent_median_logmass=float(np.median(np.log10(cat[:,1]))),selected_median_logmass=float(sel.log10_stellar_mass.median()),min_selection_probability=float(cells.selection_probability.min()),max_selection_probability=float(cells.selection_probability.max()),population_weighting='Not applied: primary target balanced feasibility sample; original is convenience benchmark; parent-volume claims not supported',orientations='Five fixed correlated views, not an isotropic random orientation sample')
 (O/'selection_audit.json').write_text(json.dumps(selection,indent=2))
 observed=pd.read_csv(O/'observed_morphology.csv');score,psfpairs=score_observations(observed);score.to_csv(O/'measurement_accuracy_draws.csv',index=False);psfpairs.to_csv(O/'observed_dust_pairs.csv',index=False)
 # Average each draw distribution and then each view, then equal galaxy weights.
 keys=['subhalo_id','band','pairing','mode','metric'];scores=[]
 for vals,g in score.groupby(keys):
  viewmeans=g.groupby('view')[['preservation_abs_error','dust_delta_abs_error']].mean();row=dict(zip(keys,vals))
  for name in ['preservation_abs_error','dust_delta_abs_error']:
   counts_valid=g.groupby('view')[name].count()
   eligible=bool(len(counts_valid)==5 and (counts_valid>=6).all())
   row[name]=viewmeans[name].mean() if eligible else np.nan;row[name+'_view_SD']=viewmeans[name].std()
   row[name+'_eligible']=eligible;row[name+'_min_valid_draws']=int(counts_valid.min());row[name+'_nvalid']=int(g[name].notna().sum())
   sds=g.groupby('view')[name].std();counts=g.groupby('view')[name].count();row[name+'_MC_SE']=np.sqrt((sds*sds/counts).sum())/len(viewmeans)
  scores.append(row)
 gs=pd.DataFrame(scores);gs.to_csv(O/'galaxy_observing_accuracy.csv',index=False)
 gains=gs.pivot(index=['subhalo_id','band','pairing','metric'],columns='mode',values=['preservation_abs_error','dust_delta_abs_error']);grows=[]
 for ix,row in gains.iterrows():
  for target in ['preservation_abs_error','dust_delta_abs_error']:
   grows.append(dict(zip(['subhalo_id','band','pairing','metric'],ix),target=target,seeing=row[(target,'seeing')],glao=row[(target,'glao')],gain=row[(target,'seeing')]-row[(target,'glao')]))
 gains=pd.DataFrame(grows).merge(meta[['subhalo_id','role']],on='subhalo_id');gains.to_csv(O/'galaxy_GLAO_gains.csv',index=False)
 sums=[]
 for scope,ss in [('all_26',gains),('held_out_21',gains[gains.role=='held_out'])]:
  for vals,g in ss.groupby(['band','pairing','metric','target']):
   g=g.dropna(subset=['gain']);lo,hi=interval(g.gain);sums.append(dict(zip(['band','pairing','metric','target'],vals),scope=scope,n_galaxies=len(g),seeing_mean_error=g.seeing.mean(),glao_mean_error=g.glao.mean(),mean_gain=g.gain.mean(),CI_low=lo,CI_high=hi,n_improved=int((g.gain>1e-10).sum()),n_worsened=int((g.gain< -1e-10).sum()),n_equal=int((abs(g.gain)<=1e-10).sum()),median_gain=g.gain.median(),between_galaxy_gain_SD=g.gain.std()))
 pd.DataFrame(sums).to_csv(O/'GLAO_bootstrap_summary.csv',index=False)
 # Focused conditional sensitivity, processed identically; O1 only.
 senspaths=list((O/'cache').glob('*/sensitivity.csv'))
 if senspaths:
  ss=pd.concat([pd.read_csv(p) for p in senspaths]);ss.to_csv(O/'sensitivity_morphology.csv',index=False);sco,_=score_observations(ss);sco.to_csv(O/'sensitivity_accuracy.csv',index=False)
 # Spatial mean errors preserve galaxy units. Near-zero reference excluded from normalized metric only.
 spatial=pd.read_csv(O/'spatial_information.csv');sg=spatial.groupby(['subhalo_id','mode','scale_kpc','target','SB_stratum'])[['RMSE','NRMSE','correlation','truth_RMS']].mean().reset_index();sg.to_csv(O/'galaxy_spatial_information.csv',index=False)
 return selection

def score_observations(m):
 keys=['subhalo_id','view','band','z','hours','kind','mode'];metrics=METRICS+['A_raw'];rr=[];pp=[]
 for vals,g in m.groupby(keys):
  row=dict(zip(keys,vals));ref=g[g.phase=='reference'].set_index('scene');psf=g[g.phase=='psf'].set_index('scene')
  for metric in metrics:
   truth_delta=ref.loc['dusty',metric]-ref.loc['clear',metric];psf_delta=psf.loc['dusty',metric]-psf.loc['clear',metric]
   pp.append(dict(**row,metric=metric,phase='psf',draw=-1,pairing='common',delta=psf_delta,reference_delta=truth_delta,signed_delta_bias=psf_delta-truth_delta,dusty_signed_preservation_bias=psf.loc['dusty',metric]-ref.loc['dusty',metric]))
  for draw,drawg in g[g.phase=='noise'].groupby('draw'):
   dusty=drawg[(drawg.scene=='dusty')&(drawg.pairing=='common')].iloc[0]
   for pairing in ['common','independent_clear']:
    clear=drawg[(drawg.scene=='clear')&(drawg.pairing==pairing)].iloc[0]
    for metric in metrics:
     delta=dusty[metric]-clear[metric];reference_delta=ref.loc['dusty',metric]-ref.loc['clear',metric]
     rr.append(dict(**row,draw=draw,pairing=pairing,metric=metric,preservation_abs_error=abs(dusty[metric]-ref.loc['dusty',metric]),dust_delta_abs_error=abs(delta-reference_delta),dust_delta_signed_error=delta-reference_delta,preservation_signed_error=dusty[metric]-ref.loc['dusty',metric]))
     pp.append(dict(**row,metric=metric,phase='noise',draw=draw,pairing=pairing,delta=delta,reference_delta=reference_delta,signed_delta_bias=delta-reference_delta,dusty_signed_preservation_bias=dusty[metric]-ref.loc['dusty',metric]))
 scores=pd.DataFrame(rr)
 if len(scores):
  joint_keys=['subhalo_id','view','band','z','hours','kind','draw','pairing','metric']
  for target in ['preservation_abs_error','dust_delta_abs_error']:
   valid=scores.groupby(joint_keys)[target].transform(lambda x: bool(len(x)==2 and np.isfinite(x).all()))
   scores.loc[~valid,target]=np.nan
 return scores,pd.DataFrame(pp)
if __name__=='__main__':print(run())
