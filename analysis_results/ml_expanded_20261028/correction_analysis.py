"""Predeclared native morphology accuracy, dust correction and paired galaxy gains."""
import numpy as np
import pandas as pd
from expanded_features import O
from expanded_models import frame
from summarize import recommended

def interval(values):
    v=np.asarray(values);rng=np.random.default_rng(20261028)
    boot=v[rng.integers(0,len(v),(5000,len(v)))].mean(1)
    return dict(gain=float(v.mean()),low=float(np.quantile(boot,.025)),high=float(np.quantile(boot,.975)),n_galaxies=len(v))

def run():
    rows=[]
    for scenario in ['seeing_NIR','GLAO_NIR']:
        data=frame(scenario,partitions=['final_test']);data=data[~data.zero_projected_dust]
        for metric in ['R50','C']:
            error=data['Ks_'+metric]-data['dusty_'+metric+'_Ks']
            rows.append(pd.DataFrame(dict(subhalo_id=data.subhalo_id,view=data.view,draw=data.draw,scenario=scenario,metric=metric,PSF_noise_error=error,absolute_error=abs(error),squared_error=error**2)))
    p=pd.concat(rows,ignore_index=True);p.to_csv(O/'final_native_dusty_morphology_transfer.csv.gz',index=False)
    gal=p.groupby(['subhalo_id','scenario','metric']).agg(MAE=('absolute_error','mean'),MSE=('squared_error','mean'),bias=('PSF_noise_error','mean')).reset_index()
    summaries=gal.groupby(['scenario','metric']).agg(MAE=('MAE','mean'),MSE=('MSE','mean'),bias=('bias','mean'),n_galaxies=('subhalo_id','nunique')).reset_index();summaries['RMSE']=np.sqrt(summaries.pop('MSE'))
    summaries.to_csv(O/'final_native_dusty_morphology_transfer_summary.csv',index=False)
    gains=[]
    pivot=gal.pivot(index=['subhalo_id','metric'],columns='scenario',values='MAE').reset_index()
    for metric,s in pivot.groupby('metric'):gains.append(dict(metric=metric,comparison='seeing_minus_GLAO_native_dusty_error',**interval(s.seeing_NIR-s.GLAO_NIR)))
    pred=pd.read_csv(O/'final_predictions.csv.gz');pred=pred[(pred.aperture=='adaptive')&~pred.zero_projected_dust]
    selected=recommended(pred);selected=selected[selected.target.isin(['dR50_Ks','dC_Ks'])]
    selected['a']=abs(selected.corrected_error);selected['b']=abs(selected.uncorrected_error)
    g=selected.groupby(['subhalo_id','target','scenario']).agg(corrected=('a','mean'),uncorrected=('b','mean')).reset_index()
    for (target,scenario),s in g.groupby(['target','scenario']):gains.append(dict(metric=target,scenario=scenario,comparison='uncorrected_minus_corrected_native_clear_error',**interval(s.uncorrected-s.corrected)))
    pivot=g.pivot(index=['subhalo_id','target'],columns='scenario',values='corrected').reset_index()
    for target,s in pivot.groupby('target'):gains.append(dict(metric=target,comparison='seeing_minus_GLAO_corrected_native_clear_error',**interval(s.seeing_NIR-s.GLAO_NIR)))
    pd.DataFrame(gains).to_csv(O/'final_morphology_correction_gains.csv',index=False)
    print(summaries.to_string(index=False));print(pd.DataFrame(gains).to_string(index=False))

if __name__=='__main__':run()
