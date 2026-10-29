"""Old-control reliability, learning curves and declared shifted evaluations."""
import json
import numpy as np
import pandas as pd
import joblib
from expanded_features import O,TARGETS
from expanded_models import SCENARIOS,frame,model,name,prediction_rows


def control_envelopes():
    records=[]
    for sid in [13,167418,184937,613192]:
        records.append(pd.read_csv(O/'derived'/str(sid)/'labels.csv'))
    old=pd.concat(records,ignore_index=True)
    assert old.zero_projected_dust.all()
    rows=[]
    for aperture,part in old.groupby('aperture'):
        for target in TARGETS:
            rows.append(dict(aperture=aperture,target=target,n_control_galaxies=4,
                median=part[target].median(),maximum_absolute=float(abs(part[target]).max()),
                use='Descriptive warning only; not sigma/detection/exclusion threshold; no offset subtraction'))
    pd.DataFrame(rows).to_csv(O/'old_control_operator_envelopes.csv',index=False)
    (O/'CONTROL_OPERATOR_FROZEN.json').write_text(json.dumps(dict(
        control_IDs=[13,167418,184937,613192],new_validation_or_final_values_used=False,
        aperture_selection='Dusty commonseeingKs only, R80 within35kpc',
        envelope_use='Descriptive only; no correction or calibrated physical threshold',
        target_definitions='expanded_features.labels_for',rows=rows),indent=2))


def learning_curves():
    selected=pd.read_csv(O/'recommended_settings.csv')
    rows=[]
    for scenario in ['seeing_NIR','GLAO_NIR']:
        data=frame(scenario,partitions=['development','validation'])
        train=data[(data.partition=='development')&~data.zero_projected_dust]
        validation=data[(data.partition=='validation')&~data.zero_projected_dust]
        ids=np.sort(train.subhalo_id.unique());counts=sorted(set([n for n in [12,24,48,len(ids)] if n<=len(ids)]))
        for size in counts:
            for seed in [31,71,113]:
                chosen=np.random.default_rng(seed).permutation(ids)[:size]
                subset=train[train.subhalo_id.isin(chosen)]
                for (family,value),requests in selected.groupby(['family','value']):
                    config=dict(family=family,value=int(value));estimator=model(config,scenario)
                    estimator.fit(subset,subset[TARGETS]);prediction=estimator.predict(validation)
                    for target in requests.target:
                        j=TARGETS.index(target)
                        error=pd.DataFrame(dict(subhalo_id=validation.subhalo_id.to_numpy(),abs_error=abs(prediction[:,j]-validation[target].to_numpy())))
                        gal=error.groupby('subhalo_id').abs_error.mean()
                        rows.append(dict(scenario=scenario,target=target,family=family,value=int(value),n_training_galaxies=size,seed=seed,n_validation_galaxies=len(gal),MAE=gal.mean()))
                print('Learning curve',scenario,size,seed,flush=True)
    pd.DataFrame(rows).to_csv(O/'learning_curves.csv',index=False)


def shifted_and_noise_tests():
    selected=pd.read_csv(O/'recommended_settings.csv');rows=[]
    # Diagnostic after frozen model selection; fixed prior ridge10 avoids tuning on OOD target labels.
    for scenario in ['seeing_NIR','GLAO_NIR']:
        data=frame(scenario,partitions=['development']);data=data[~data.zero_projected_dust]
        mass=data.groupby('subhalo_id').log_stellar_mass.first();edge=mass.quantile(.75)
        high=mass.index[mass>=edge];train=data[~data.subhalo_id.isin(high)];test=data[data.subhalo_id.isin(high)]
        for family in ['phot_ridge','spatial_ridge']:
            config=dict(family=family,value=10);estimator=model(config,scenario);estimator.fit(train,train[TARGETS])
            rows.append(prediction_rows(test,estimator.predict(test),scenario=scenario,family=family,condition='high_mass_OOD',aperture='adaptive',evaluation='development_shift'))
        for condition in ['equal_noise','noiseless']:
            shifted=frame(scenario,condition=condition,partitions=['development','validation'])
            fit=shifted[(shifted.partition=='development')&~shifted.zero_projected_dust]
            validation=shifted[(shifted.partition=='validation')&~shifted.zero_projected_dust]
            for (family,value),requests in selected.groupby(['family','value']):
                config=dict(family=family,value=int(value));estimator=model(config,scenario);estimator.fit(fit,fit[TARGETS])
                artifact=O/'models'/f'sensitivity_{condition}_{scenario}_{name(config)}.joblib';joblib.dump(estimator,artifact,compress=3)
                result=prediction_rows(validation,estimator.predict(validation),scenario=scenario,family=family,condition=condition,aperture='adaptive',evaluation='validation_sensitivity')
                rows.append(result[result.target.isin(requests.target)])
    pd.concat(rows,ignore_index=True).to_csv(O/'shift_and_noise_predictions.csv.gz',index=False)


def score_instrument():
    selected=pd.read_csv(O/'recommended_settings.csv')
    features=pd.read_csv(O/'instrument_sensitivity/stress_features.csv.gz')
    labels=pd.read_csv(O/'target_table.csv')
    features=features[features.partition=='validation']
    joined=features.merge(labels,on=['subhalo_id','view','partition','aperture'],validate='many_to_one')
    rows=[]
    for (case,mode),subset in joined.groupby(['case','mode']):
        scenario='GLAO_NIR' if mode=='glao' else 'seeing_NIR'
        for (family,value),requests in selected.groupby(['family','value']):
            config=dict(family=family,value=int(value))
            estimator=joblib.load(O/'models'/f'adaptive_{scenario}_{name(config)}.joblib')
            prediction=prediction_rows(subset,estimator.predict(subset),scenario=scenario,family=family,
                condition=case,aperture='adaptive',evaluation='instrument_shift')
            rows.append(prediction[prediction.target.isin(requests.target)])
    pd.concat(rows,ignore_index=True).to_csv(O/'instrument_stress_predictions.csv.gz',index=False)


if __name__=='__main__':
    import sys
    if '--controls' in sys.argv:control_envelopes()
    else:learning_curves();shifted_and_noise_tests();score_instrument()
