"""Stage-aware numerical/provenance verification, no scientific model selection."""
import hashlib,json
from datetime import datetime,timezone
import numpy as np
import pandas as pd
from expanded_features import O,PART,TARGETS
from expanded_models import columns,SCENARIOS,FAMILIES

def run():
    checks={};parts=pd.read_csv(PART);frozen=pd.read_csv(O/'data_audit/frozen_galaxy_partitions.csv')
    pd.testing.assert_frame_equal(parts,frozen);checks['original_frozen_partitions_unchanged']=True
    labels=pd.read_csv(O/'target_table.csv');features=pd.read_csv(O/'feature_table.csv.gz')
    assert len(labels)==1000 and len(features)==24000
    assert labels.groupby('partition').subhalo_id.nunique().to_dict()==dict(development=86,validation=14)
    assert labels.groupby('subhalo_id').size().eq(10).all()
    assert features.groupby('subhalo_id').size().eq(240).all()
    assert np.isfinite(labels[TARGETS]).all().all();checks['nonfinal_100_complete_finite_labels']=True
    folds=pd.read_csv(O/'development_group_folds.csv')
    for fold,s in folds.groupby('fold'):
        fit=set(s.loc[s.role=='fit','subhalo_id']);test=set(s.loc[s.role=='test','subhalo_id'])
        assert not fit&test and len(fit|test)==74
    assert folds[folds.role=='test'].subhalo_id.nunique()==74
    assert folds[folds.role=='test'].groupby('subhalo_id').size().eq(1).all()
    checks['five_whole_galaxy_folds_disjoint']=True
    forbidden={'subhalo_id','view','draw','partition','zero_projected_dust','dust_mass_field_Msun','stellar_mass_Msun','log_stellar_mass','SFR_Msun_yr',*TARGETS}
    for scenario in SCENARIOS:
        for family in FAMILIES:
            a,b=columns(scenario,family);assert not (set(a+b)&forbidden);assert set(a+b)<=set(features.columns)
    checks['all_model_predictors_explicit_observable_allowlist']=True
    k=['subhalo_id','view','draw','partition','aperture','condition']
    a=features[features['mode']=='seeing'].set_index(k);b=features[features['mode']=='glao'].set_index(k)
    cols,_=columns('optical','spatial_ridge');cells=columns('optical','spatial_ridge')[1]
    assert np.allclose(a[cols+cells],b[cols+cells],atol=0,rtol=0,equal_nan=True)
    checks['g_observables_exact_same_between_modes']=True
    transfer=pd.read_csv(O/'render_validation.csv');assert transfer.padded_flux_loss.max()<1e-5
    checks['maximum_padded_flux_loss']=float(transfer.padded_flux_loss.max())
    chosen=pd.read_csv(O/'chosen_family_settings.csv');assert len(chosen)==8*8
    cal=pd.read_csv(O/'calibration_thresholds.csv');assert cal.n_calibration_galaxies.eq(13).all() and cal['rank'].eq(12).all()
    assert len(cal)==2*3*8*8 and np.isfinite(cal.halfwidth).all()
    checks['calibration_13_galaxies_rank12_per_target']=True
    prediction=pd.read_csv(O/'validation_and_control_predictions.csv.gz')
    assert prediction.loc[prediction.evaluation=='validation','subhalo_id'].nunique()==13
    assert prediction.loc[prediction.evaluation=='source_controls','subhalo_id'].nunique()==13
    assert np.isfinite(prediction[['truth','prediction','error']]).all().all()
    checks['nonfinal_predictions_finite_and_controls_separate']=True
    assert (O/'instrument_sensitivity/verification.json').exists()
    if (O/'FINAL_EVALUATION_COMPLETED.json').exists():
        from freeze_guard import verify
        checks['frozen_artifact_hash']=verify()
        p=pd.read_csv(O/'final_predictions.csv.gz');t=pd.read_csv(O/'final_target_table.csv')
        assert set(p.subhalo_id)==set(parts.loc[parts.partition=='final_test','subhalo_id'])
        assert len(t)==200 and np.isfinite(p[['truth','prediction','error']]).all().all()
        assert not set(p.subhalo_id)&set(prediction.subhalo_id)
        checks['final20_disjoint_and_finite']=True
        checks['final_primary_galaxies']=int(p.loc[~p.zero_projected_dust,'subhalo_id'].nunique())
        checks['final_source_control_galaxies']=int(p.loc[p.zero_projected_dust,'subhalo_id'].nunique())
        filename='POSTFINAL_VALIDATION.json'
    else:
        assert not any((O/'data_audit/cache'/str(sid)).exists() for sid in parts.loc[parts.partition=='final_test','subhalo_id'])
        checks['final_science_still_sealed']=True;filename='PREFINAL_VALIDATION.json'
    (O/filename).write_text(json.dumps(dict(passed=True,utc=datetime.now(timezone.utc).isoformat(),checks=checks),indent=2))
    print(json.dumps(checks,indent=2))

if __name__=='__main__':run()
