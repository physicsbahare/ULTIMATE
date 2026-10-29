"""Read-only verification of new saved results, no scientific imports/refits."""
from pathlib import Path
import hashlib,json,ast
import numpy as np
import pandas as pd
O=Path(__file__).resolve().parent;ROOT=O.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def verify():
    errors=[];checks={}
    provenance=json.loads((O/'provenance.json').read_text())
    for rec in provenance['inputs']:
        if sha(ROOT/rec['path'])!=rec['sha256']:errors.append('Input/source changed: '+rec['path'])
    checks['input_source_hashes']=len(provenance['inputs'])
    labels=pd.read_csv(O/'subset_saved_labels.csv');folds=pd.read_csv(O/'galaxy_folds.csv')
    ids=set(labels.subhalo_id);fitids=ids-{13}
    assert len(ids)==14 and len(folds)==13 and set(folds.subhalo_id)==fitids
    assert set(labels.partition)=={'development'} and labels.groupby('subhalo_id').size().eq(5).all()
    checks['development_only_galaxies']=len(ids);checks['independent_fit_galaxies']=len(fitids)
    f=pd.read_csv(O/'observable_features.csv.gz');m=pd.read_csv(O/'morphology_resolution_results.csv')
    assert len(f)==280 and len(m)==560
    assert not f.duplicated(['subhalo_id','view','family','condition']).any()
    assert set(f.subhalo_id)==ids
    assert np.isfinite(f.select_dtypes(include='number')).all().all()
    checks['feature_rows']=len(f);checks['morphology_rows']=len(m)
    np.testing.assert_allclose(m.morphology_abs_error,abs(m.observed_dusty-m.native_dusty),atol=1e-12)
    np.testing.assert_allclose(m.pair_transfer_abs_error,abs(m.observed_pair_difference-m.native_pair_difference),atol=1e-12)
    r=pd.read_csv(O/'render_checks.csv');assert len(r)==280 and r.padded_flux_loss.max()<1e-4
    checks['max_render_flux_loss']=float(r.padded_flux_loss.max())
    op=pd.read_csv(O/'psf_definition_and_operator_checks.csv')
    point=op[op.check=='point_analytic'];quad=op[op.check=='quadrature_control13_O1']
    assert point.relative_L1_analytic.max()<.02 and abs(point.detector_flux-1).max()<1e-4
    assert quad.R50_change_kpc.abs().max()<.03 and quad.C_change.abs().max()<.03
    checks['max_point_L1_error']=float(point.relative_L1_analytic.max())
    checks['grid_refinement_morphology_max_R50_change']=float(quad.R50_change_kpc.abs().max())
    p=pd.read_csv(O/'ml_predictions.csv.gz');p=p[~p.source_control]
    assert set(p.subhalo_id)==fitids and len(p)==6240
    joined=p.merge(folds,on='subhalo_id',suffixes=('','_expected'),validate='many_to_one')
    assert (joined.fold==joined.fold_expected).all()
    keys=['family','model','train_condition','test_condition','target']
    assert p.groupby(keys+['subhalo_id']).size().eq(5).all()
    np.testing.assert_allclose(p.signed_error,p.prediction-p.truth,atol=1e-12)
    np.testing.assert_allclose(p.abs_error,abs(p.signed_error),atol=1e-12)
    truth=p[['subhalo_id','view','target','truth']].drop_duplicates()
    assert not truth.duplicated(['subhalo_id','view','target']).any()
    scores=pd.read_csv(O/'ml_information_gain_results.csv')
    recompute=p.groupby(keys+['subhalo_id']).abs_error.mean().groupby(keys).mean().rename('recomputed').reset_index()
    joined=scores.merge(recompute,on=keys,validate='one_to_one')
    np.testing.assert_allclose(joined.MAE,joined.recomputed,atol=1e-12)
    u=pd.read_csv(O/'galaxy_level_uncertainties.csv')
    np.testing.assert_allclose(u.paired_width_gain,u.MAE_w039-u.MAE_w020,atol=1e-12)
    np.testing.assert_allclose(u.change_in_incremental_gain,u.incremental_spatial_gain_w020-u.incremental_spatial_gain_w039,atol=1e-12)
    checks['primary_cv_prediction_rows']=len(p);checks['score_rows']=len(scores);checks['galaxy_paired_rows']=len(u)
    checks['held_out_fold_assignments']='all primary predictions match unique galaxy test fold'
    checks['score_recomputation']='all96 MAEs equal galaxy-aggregated saved predictions'
    checks['canonical_freeze_sha256']=sha(ROOT/'analysis_results/ml_expanded_20261028/FINAL_PROTOCOL_FROZEN.json')
    assert checks['canonical_freeze_sha256']=='587aab56d39e6b29ad47f381c4b1440c8dd28eb52811ebc4ae3842b6fc220ce4'
    receipt=json.loads((ROOT/'analysis_results/ml_expanded_20261028/FINAL_EVALUATION_COMPLETED.json').read_text())
    assert receipt['final_evaluation_count']==1
    checks['canonical_final_count']=1;checks['new_final_inference_count']=0
    for py in O.glob('*.py'):ast.parse(py.read_text())
    for stem in ['morphology_width_gain','ml_width_gain']:
        for suffix in ['png','pdf']:assert (O/'figures'/f'{stem}.{suffix}').stat().st_size>1000
    return dict(status='pass' if not errors else 'fail',date='2026-10-29 Asia/Taipei',checks=checks,errors=errors,
        uncertainty='Exploratory conditional galaxy bootstrap; shared fitted fold models, no retraining/selection/source/instrument variance',
        omitted_outputs='No .300 intermediate, fixed-exposure noise run, new calibration or confirmation data; none required for this noiseless pilot.')

if __name__=='__main__':
    report=verify();print(json.dumps(report,indent=2));raise SystemExit(0 if report['status']=='pass' else 1)
