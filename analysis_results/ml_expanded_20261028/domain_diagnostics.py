"""Descriptive OOD/control diagnostics after fixed evaluation; no selection/tuning."""
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from expanded_features import O,TARGETS
from expanded_models import frame,columns
from summarize import recommended

def run():
    predictions=pd.concat([pd.read_csv(O/'validation_and_control_predictions.csv.gz'),pd.read_csv(O/'final_predictions.csv.gz')],ignore_index=True)
    predictions=recommended(predictions[predictions.aperture=='adaptive'])
    rows=[];cutoffs=[]
    for scenario in ['seeing_NIR','GLAO_NIR']:
        data=frame(scenario,partitions=['development']);data=data[~data.zero_projected_dust]
        feature,_=columns(scenario,'summary_ridge')
        a=data.groupby('subhalo_id')[feature].mean();imputer=SimpleImputer(strategy='median');scaler=StandardScaler()
        z=scaler.fit_transform(imputer.fit_transform(a));nn=NearestNeighbors(n_neighbors=2).fit(z)
        distances=nn.kneighbors(z)[0][:,1];threshold=float(np.quantile(distances,.95))
        cutoffs.append(dict(scenario=scenario,quantile=.95,threshold=threshold,basis='development-only leave-one-galaxy nearest distance; exploratory diagnostic, not a model gate'))
        dist=pd.read_csv(O/'observable_distance.csv');dist=dist[dist.scenario==scenario]
        p=predictions[(predictions.scenario==scenario)&~predictions.zero_projected_dust]
        gal=p.groupby(['subhalo_id','target','evaluation']).agg(MAE=('abs_error','mean'),RMSE=('square_error',lambda v:np.sqrt(v.mean())),bias=('error','mean'),galaxy_coverage=('covered','all')).reset_index()
        gal=gal.merge(dist[['subhalo_id','standardized_nearest_development_distance']],on='subhalo_id',validate='many_to_one')
        gal['outside_development_distance95']=gal.standardized_nearest_development_distance>threshold
        gal['scenario']=scenario;rows.append(gal)
    result=pd.concat(rows,ignore_index=True);result.to_csv(O/'observable_OOD_galaxy_errors.csv',index=False)
    pd.DataFrame(cutoffs).to_csv(O/'observable_OOD_development_thresholds.csv',index=False)
    result.groupby(['evaluation','scenario','target','outside_development_distance95']).agg(MAE=('MAE','mean'),bias=('bias','mean'),galaxy_coverage=('galaxy_coverage','mean'),n_galaxies=('subhalo_id','nunique')).reset_index().to_csv(O/'observable_OOD_summary.csv',index=False)
    control=predictions[predictions.zero_projected_dust]
    pergal=control.groupby(['partition','scenario','target','subhalo_id']).agg(operational_MAE=('abs_error','mean'),signed_mean_prediction=('prediction','mean'),mean_atlas_contrast=('truth','mean')).reset_index()
    pergal.to_csv(O/'source_control_recommended_predictions.csv',index=False)
    pergal.groupby(['partition','scenario','target']).agg(n_galaxies=('subhalo_id','nunique'),operational_MAE=('operational_MAE','mean'),signed_mean_prediction=('signed_mean_prediction','mean'),mean_atlas_contrast=('mean_atlas_contrast','mean')).reset_index().to_csv(O/'source_control_recommended_summary.csv',index=False)
    # Explicit outlier list retains every view/draw in original prediction files.
    p=predictions[(predictions.evaluation=='final_test')&~predictions.zero_projected_dust]
    p.groupby(['scenario','target','subhalo_id']).agg(MAE=('abs_error','mean'),bias=('error','mean'),max_error=('abs_error','max')).reset_index().sort_values('MAE',ascending=False).to_csv(O/'final_galaxy_outlier_ranking.csv',index=False)
    training=pd.read_csv(O/'target_table.csv').query("partition=='development' and aperture=='adaptive' and not zero_projected_dust")
    final=pd.read_csv(O/'final_target_table.csv').query("aperture=='adaptive' and not zero_projected_dust")
    ranges=[]
    for target in TARGETS:
        lo,hi=training[target].min(),training[target].max();outside=(final[target]<lo)|(final[target]>hi)
        ranges.append(dict(target=target,development_min=lo,development_max=hi,final_min=final[target].min(),final_max=final[target].max(),final_views_outside_training_range=int(outside.sum()),final_galaxies_with_outside_view=final.loc[outside,'subhalo_id'].nunique(),use='Post-evaluation truth-range diagnostic; not an observable OOD flag or exclusion'))
    pd.DataFrame(ranges).to_csv(O/'target_range_diagnostics.csv',index=False)
    print('OOD, source-control and outlier diagnostics written; no models changed.')

if __name__=='__main__':run()
