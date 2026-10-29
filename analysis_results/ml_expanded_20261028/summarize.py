"""Frozen scoring definitions; saved predictions only, never refits models."""
import json
import numpy as np
import pandas as pd
from expanded_features import O,TARGETS

KEYS=['evaluation','aperture','scenario','family','target']

def metrics(pred):
    x=pred.copy()
    x['corrected_abs']=abs(x.corrected_error);x['uncorrected_abs']=abs(x.uncorrected_error)
    gal=x.groupby(KEYS+['subhalo_id'],dropna=False).agg(MAE=('abs_error','mean'),MSE=('square_error','mean'),bias=('error','mean'),point_coverage=('covered','mean'),galaxy_coverage=('covered','all'),corrected_MAE=('corrected_abs','mean'),uncorrected_MAE=('uncorrected_abs','mean')).reset_index()
    out=[]
    for key,part in gal.groupby(KEYS,dropna=False):
        rng=np.random.default_rng(20261028);v=part.MAE.to_numpy();idx=rng.integers(0,len(v),(5000,len(v)));boot=v[idx].mean(1)
        out.append(dict(zip(KEYS,key),n_galaxies=len(part),MAE=v.mean(),MAE_low=np.quantile(boot,.025),MAE_high=np.quantile(boot,.975),RMSE=np.sqrt(part.MSE.mean()),bias=part.bias.mean(),point_coverage=part.point_coverage.mean(),galaxy_coverage=part.galaxy_coverage.mean(),corrected_MAE=part.corrected_MAE.mean(),uncorrected_MAE=part.uncorrected_MAE.mean()))
    return gal,pd.DataFrame(out)

def paired_gains(gal):
    out=[]
    common=['evaluation','aperture','target','subhalo_id']
    for family,part in gal.groupby('family'):
        a=part[part.scenario=='seeing_NIR'][common+['MAE']]
        b=part[part.scenario=='GLAO_NIR'][common+['MAE']]
        merged=a.merge(b,on=common,suffixes=('_a','_b'))
        merged['gain']=merged.MAE_a-merged.MAE_b
        for key,p in merged.groupby(common[:-1]):
            v=p.gain.to_numpy();rng=np.random.default_rng(20261028);boot=v[rng.integers(0,len(v),(5000,len(v)))].mean(1)
            out.append(dict(zip(common[:-1],key),comparison='seeing_minus_GLAO_MAE',family=family,n_galaxies=len(v),gain=v.mean(),low=np.quantile(boot,.025),high=np.quantile(boot,.975),fraction_galaxies_improved=np.mean(v>0)))
    # Additional bands: optical - seeingNIR. Extra time explicitly not resolution.
    for family,part in gal.groupby('family'):
        a=part[part.scenario=='optical'][common+['MAE']];b=part[part.scenario=='seeing_NIR'][common+['MAE']]
        merged=a.merge(b,on=common,suffixes=('_a','_b'));merged['gain']=merged.MAE_a-merged.MAE_b
        for key,p in merged.groupby(common[:-1]):
            v=p.gain.to_numpy();rng=np.random.default_rng(20261028);boot=v[rng.integers(0,len(v),(5000,len(v)))].mean(1)
            out.append(dict(zip(common[:-1],key),comparison='optical_minus_seeingNIR_MAE',family=family,n_galaxies=len(v),gain=v.mean(),low=np.quantile(boot,.025),high=np.quantile(boot,.975),fraction_galaxies_improved=np.mean(v>0)))
    for baseline in ['median','phot_ridge']:
        common=['evaluation','aperture','scenario','target','subhalo_id']
        a=gal[gal.family==baseline][common+['MAE']]
        for family,part in gal.groupby('family'):
            b=part[common+['MAE']];merged=a.merge(b,on=common,suffixes=('_a','_b'));merged['gain']=merged.MAE_a-merged.MAE_b
            for key,p in merged.groupby(common[:-1]):
                v=p.gain.to_numpy();rng=np.random.default_rng(20261028);boot=v[rng.integers(0,len(v),(5000,len(v)))].mean(1)
                out.append(dict(zip(common[:-1],key),comparison=baseline+'_minus_model_MAE',family=family,n_galaxies=len(v),gain=v.mean(),low=np.quantile(boot,.025),high=np.quantile(boot,.975),fraction_galaxies_improved=np.mean(v>0)))
    return pd.DataFrame(out)

def recommended(data):
    choice=pd.read_csv(O/'recommended_settings.csv')[['target','family']]
    return data.merge(choice,on=['target','family'],validate='many_to_one')

def residual_diagnostics(pred):
    x=recommended(pred[(pred.aperture=='adaptive')&~pred.zero_projected_dust])
    noise=x.groupby(KEYS+['subhalo_id','view']).error.agg(['mean','std']).reset_index()
    noise.to_csv(O/'within_view_noise_and_orientation_residuals.csv',index=False)
    rows=[]
    properties=['log_stellar_mass','SFR_Msun_yr','dust_mass_field_Msun','observed_Ks_q','observable_Ks_logSB']
    for key,p in x.groupby(KEYS):
        for prop in properties:
            # Strata are descriptive, not additional independent observations or tuning.
            summary=p.groupby('subhalo_id').agg(value=(prop,'median'),MAE=('abs_error','mean'))
            if summary.value.nunique()<2:continue
            bins=pd.qcut(summary.value,3,duplicates='drop')
            for level,s in summary.groupby(bins,observed=True):
                rows.append(dict(zip(KEYS,key),property=prop,stratum=str(level),n_galaxies=len(s),MAE=s.MAE.mean()))
    pd.DataFrame(rows).to_csv(O/'property_stratified_errors.csv',index=False)
    # Fixed leave-one-view-out reporting; no altered fits.
    no5=x[x.view!='O5'];_,m=metrics(no5);m.to_csv(O/'exclude_O5_scoring_sensitivity.csv',index=False)

def observable_distance():
    from expanded_models import frame,columns
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler
    from sklearn.neighbors import NearestNeighbors
    rows=[]
    for scenario in ['seeing_NIR','GLAO_NIR']:
        data=frame(scenario,partitions=['development','validation']);fit=data[(data.partition=='development')&~data.zero_projected_dust]
        columns_,_=columns(scenario,'summary_ridge');imputer=SimpleImputer(strategy='median');scaler=StandardScaler()
        # Galaxy means avoid counting near-identical orientations as independent training galaxies.
        a=fit.groupby('subhalo_id')[columns_].mean();z=scaler.fit_transform(imputer.fit_transform(a));nn=NearestNeighbors(n_neighbors=1).fit(z)
        sets=[('validation',data[data.partition=='validation'])]
        if (O/'FINAL_EVALUATION_COMPLETED.json').exists():sets.append(('final_test',frame(scenario,partitions=['final_test'])))
        for part,subset in sets:
            b=subset.groupby('subhalo_id')[columns_].mean();dist=nn.kneighbors(scaler.transform(imputer.transform(b)))[0][:,0]
            rows.extend(dict(scenario=scenario,partition=part,subhalo_id=int(sid),standardized_nearest_development_distance=float(d)) for sid,d in zip(b.index,dist))
    pd.DataFrame(rows).to_csv(O/'observable_distance.csv',index=False)

def run():
    pred=pd.read_csv(O/'validation_and_control_predictions.csv.gz')
    if (O/'FINAL_EVALUATION_COMPLETED.json').exists():pred=pd.concat([pred,pd.read_csv(O/'final_predictions.csv.gz')],ignore_index=True)
    pred['evaluation']=np.where(pred.zero_projected_dust,pred.evaluation+'_source_control',pred.evaluation)
    positive=pred[~pred.zero_projected_dust];gal,summary=metrics(positive)
    gal.to_csv(O/'galaxy_metrics.csv',index=False);summary.to_csv(O/'performance_summary.csv',index=False)
    gains=paired_gains(gal);gains.to_csv(O/'paired_galaxy_gains.csv',index=False)
    recommended(summary).to_csv(O/'recommended_performance.csv',index=False)
    recommended(gains).to_csv(O/'recommended_gains.csv',index=False)
    cg,cm=metrics(pred[pred.zero_projected_dust]);cm.to_csv(O/'source_control_performance.csv',index=False)
    residual_diagnostics(pred);observable_distance()
    for source in ['shift_and_noise_predictions','instrument_stress_predictions']:
        p=pd.read_csv(O/(source+'.csv.gz'));p=p[~p.zero_projected_dust].copy();p['covered']=False
        p['evaluation']=p['evaluation']+'_'+p.condition
        g,m=metrics(p);m[['point_coverage','galaxy_coverage']]=np.nan;m.to_csv(O/(source+'_summary.csv'),index=False)
        paired_gains(g).to_csv(O/(source+'_gains.csv'),index=False)
    print(recommended(summary).query("aperture=='adaptive'")[[*KEYS,'n_galaxies','MAE','RMSE','bias','galaxy_coverage']].to_string(index=False))

if __name__=='__main__':run()
