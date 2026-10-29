"""Measure source-null and aperture-policy scales beside operational ML errors."""
import pandas as pd
import numpy as np
from ml_data import OUT, PREV


def run():
    labels=pd.read_csv(OUT/'operational_labels.csv')
    zero=labels[labels.zero_projected_dust]
    rows=[]
    for target in ['A_g','A_Ks','A_g_p50_1kpc','dR50_g','dR50_Ks','dC_g','dC_Ks']:
        rows.append(dict(target=target,n_control_galaxies=zero.subhalo_id.nunique(),
                         median_control_value=zero[target].median(),
                         median_control_absolute_value=abs(zero[target]).median(),
                         maximum_control_absolute_value=abs(zero[target]).max(),
                         interpretation='Unresolved empirical source-product residual scale, not a transferable error distribution'))
    pd.DataFrame(rows).to_csv(OUT/'source_null_label_audit.csv',index=False)
    robustness=pd.read_csv(PREV/'aperture_center_robustness.csv')
    eligible=labels.loc[~labels.zero_projected_dust,'subhalo_id'].unique()
    robustness=robustness[robustness.subhalo_id.isin(eligible)]
    results=[]
    for (band,setting),group in robustness.groupby(['band','setting_alternative']):
        for metric in ['R50','C']:
            gal=group.groupby('subhalo_id')['change_delta_'+metric].apply(lambda x:abs(x).mean())
            results.append(dict(target='d'+metric+'_'+('g' if band=='LSST_g' else 'Ks'),
                alternative_setting=setting,n_galaxies=len(gal),
                median_galaxy_mean_absolute_label_change=gal.median(),
                mean_galaxy_mean_absolute_label_change=gal.mean(),
                maximum_galaxy_mean_absolute_label_change=gal.max(),
                interpretation='Different aperture/center definitions are systematic task changes, not independent Gaussian label noise'))
    pd.DataFrame(results).to_csv(OUT/'label_policy_uncertainty_summary.csv',index=False)
    # Held-out prediction errors compared with alternative definitions, without retuning.
    # This is explicitly a label-definition stress, NOT accuracy for a newly trained aperture task.
    predictions=pd.read_csv(OUT/'heldout_predictions.csv.gz')
    predictions=predictions[(predictions.condition=='original_noise')&(predictions['mode']=='glao')&
                            (predictions.bandset=='g_J_Ks')&(predictions.model=='ridge')&predictions.target.str.startswith('d')]
    stress=[]
    for row in predictions.groupby(['subhalo_id','view','target']).prediction.mean().reset_index().itertuples():
        metric,band=row.target[1:].split('_')
        selected=robustness[(robustness.subhalo_id==row.subhalo_id)&(robustness.view==row.view)&
                            (robustness.band==('LSST_g' if band=='g' else '2MASS_Ks'))]
        for alternative in selected.itertuples():
            truth=getattr(alternative,'delta_'+metric+'_alternative')
            stress.append(dict(subhalo_id=row.subhalo_id,view=row.view,target=row.target,
                               setting=alternative.setting_alternative,prediction=row.prediction,
                               alternative_truth=truth,abs_error=abs(row.prediction-truth)))
    pd.DataFrame(stress).to_csv(OUT/'fixed_prediction_label_definition_stress.csv',index=False)
    print(pd.DataFrame(rows).to_string(index=False))
    print(pd.DataFrame(results).to_string(index=False))


if __name__=='__main__':run()
