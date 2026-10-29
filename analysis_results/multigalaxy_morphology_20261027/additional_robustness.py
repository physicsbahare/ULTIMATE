"""Post-protocol sensitivity, never replaces the five-view primary evaluation."""
from pathlib import Path
import numpy as np,pandas as pd
from statistics_analysis import interval
O=Path(__file__).resolve().parent

def run():
 base=pd.read_csv(O/'primary_dust_bias.csv');score=pd.read_csv(O/'measurement_accuracy_draws.csv');rows=[];gainrows=[]
 for scope,bb in [('five_views_primary',base),('four_views_no_O5',base[base.view!='O5'])]:
  for band in ['LSST_g','2MASS_Ks']:
   for metric in ['R50','C','A','q']:
    g=bb[bb.band==band].groupby('subhalo_id')['delta_'+metric].mean();lo,hi=interval(g,'median')
    rows.append(dict(scope=scope,band=band,metric=metric,n_galaxies=len(g),galaxy_median=g.median(),CI_low=lo,CI_high=hi,mean=g.mean()))
  ss=score if scope=='five_views_primary' else score[score.view!='O5']
  for band in ['LSST_g','2MASS_Ks']:
   for pairing in ['common','independent_clear']:
    for metric in ['R50','C','A','q']:
     s=ss[(ss.band==band)&(ss.pairing==pairing)&(ss.metric==metric)]
     for target in ['preservation_abs_error','dust_delta_abs_error']:
      byview=s.groupby(['subhalo_id','mode','view'])[target].agg(['mean','count']).reset_index()
      valid=byview.groupby(['subhalo_id','mode'])['count'].min()>=6
      a=byview.groupby(['subhalo_id','mode'])['mean'].mean().where(valid).unstack('mode');v=(a.seeing-a.glao).dropna();lo,hi=interval(v)
      gainrows.append(dict(scope=scope,band=band,pairing=pairing,metric=metric,target=target,n_galaxies=len(v),mean_gain=v.mean(),CI_low=lo,CI_high=hi))
 pd.DataFrame(rows).to_csv(O/'four_view_morphology_robustness.csv',index=False);pd.DataFrame(gainrows).to_csv(O/'four_view_GLAO_robustness.csv',index=False)
 # Truth-reference resampling contribution is separate from the optical PSF contribution.
 native=base[base.band.isin(['LSST_g','2MASS_J','2MASS_Ks'])]
 observed=pd.read_csv(O/'observed_morphology.csv');ref=observed[(observed.phase=='reference')&(observed['mode']=='seeing')]
 for metric in ['R50','C','A','q']:
  c=ref[ref.scene=='clear'].set_index(['subhalo_id','view','band'])[metric];d=ref[ref.scene=='dusty'].set_index(['subhalo_id','view','band'])[metric];delta=(d-c).rename('sampled_delta_'+metric).reset_index();native=native.merge(delta,on=['subhalo_id','view','band'],validate='one_to_one')
  native['sampling_change_delta_'+metric]=native['sampled_delta_'+metric]-native['delta_'+metric]
 native.to_csv(O/'detector_sampling_robustness.csv',index=False)
 # Explicit high-frequency/noise sensitivity of asymmetry (not a new physical estimator).
 scores=pd.read_csv(O/'GLAO_bootstrap_summary.csv');scores[(scores.metric.isin(['A','A_raw']))&(scores.band=='2MASS_Ks')].to_csv(O/'asymmetry_estimator_sensitivity.csv',index=False)
if __name__=='__main__':run()
