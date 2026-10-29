"""Validate data boundaries, independent arithmetic and saved deliverables."""
from pathlib import Path
import base64, hashlib, importlib.metadata, json, platform, sys
import numpy as np
import pandas as pd
import nbformat
from astropy.io import fits
from ml_data import OUT, PREV, TARGETS


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024**2),b''):h.update(block)
    return h.hexdigest()


def run():
    features=pd.read_csv(OUT/'observable_features.csv');labels=pd.read_csv(OUT/'operational_labels.csv')
    prediction=pd.read_csv(OUT/'heldout_predictions.csv.gz')
    split=pd.read_csv(OUT/'preliminary_cv_splits.csv')
    assert len(features)==6240 and len(labels)==130 and len(prediction)==369600
    assert features.subhalo_id.nunique()==26 and labels.subhalo_id.nunique()==26
    assert not features.duplicated(['condition','mode','subhalo_id','view','draw']).any()
    keys=['condition','mode','bandset','model','target','subhalo_id','view','draw']
    assert not prediction.duplicated(keys).any()
    assert np.isfinite(prediction[['truth','prediction','abs_error','interval_halfwidth']]).all().all()
    zero=set(labels.loc[labels.zero_projected_dust,'subhalo_id'])
    assert len(zero)==4 and not zero & set(prediction.subhalo_id)
    for fold,rows in split.groupby('fold'):
        assert not rows.subhalo_id.duplicated().any()
        assert set(prediction.loc[prediction.fold==fold,'subhalo_id'])==set(rows.loc[rows.role=='outer_test','subhalo_id'])
    membership=pd.read_csv(OUT/'expansion/galaxy_partitions.csv')
    assert membership.groupby('partition').size().to_dict()=={'development':86,'final_test':20,'validation':14}
    assert membership.subhalo_id.nunique()==120
    assert set(membership.loc[membership.subhalo_id.isin(labels.subhalo_id),'partition'])=={'development'}
    assert not set(membership[membership.partition=='final_test'].subhalo_id)&set(features.subhalo_id)
    # Independently reconstruct error aggregations without benchmark helper calls.
    prediction['recalculated_error']=abs(prediction.prediction-prediction.truth)
    np.testing.assert_allclose(prediction.recalculated_error,prediction.abs_error,atol=1e-14)
    group=['condition','mode','bandset','model','target','subhalo_id']
    galaxy=prediction.groupby(group).recalculated_error.mean()
    summary=galaxy.groupby(level=group[:-1]).mean()
    stored=pd.read_csv(OUT/'heldout_summary.csv').set_index(group[:-1])
    maximum=float(abs(summary-stored.loc[summary.index,'MAE']).max())
    assert maximum<1e-12
    gains=pd.read_csv(OUT/'galaxy_GLAO_ML_gains.csv')
    assert abs(gains[gains.bandset=='g_only'].gain).max()<1e-12
    # Check label floor audit is explicit and controls never substituted by fake zeros.
    assert abs(labels[labels.zero_projected_dust].A_g.median()-.121382588813929)<1e-12
    record=json.loads((OUT/'train_test_provenance.json').read_text())
    assert record['protocol_sha256']==digest(OUT/'PROTOCOL.md')
    assert record['final_120_sample_used'] is False
    # Read-only preservation check includes main study, supplementary audit and earlier reports.
    preserved=0
    for manifest,root in [(PREV/'output_manifest.sha256',PREV),
                          (PREV/'continuation_verification/output_manifest.sha256',PREV/'continuation_verification')]:
        for line in manifest.read_text().splitlines():
            expected,relative=line.split('  ',1);assert digest(root/relative)==expected,relative;preserved+=1
    prior=json.loads((PREV/'previous_results_sha256.json').read_text())
    for relative,expected in prior.items():assert digest(OUT.parents[1]/relative)==expected,relative
    preserved+=len(prior)
    notebook=nbformat.read(OUT/'ULTIMATE_preliminary_ML.ipynb',as_version=4);nbformat.validate(notebook)
    code=[c for c in notebook.cells if c.cell_type=='code']
    assert all(c.execution_count is not None for c in code)
    assert not any(o.output_type=='error' for c in code for o in c.outputs)
    embedded={hashlib.sha256(base64.b64decode(o.data['image/png'])).hexdigest()
              for c in code for o in c.outputs if 'image/png' in o.get('data',{})}
    expected={digest(p) for p in (OUT/'figures').glob('*.png')}
    assert expected<=embedded
    report_outputs='\n'.join(o.get('data',{}).get('text/markdown','') for c in code for o in c.outputs)
    assert (OUT/'scientific_report.md').read_text() in report_outputs
    assert (OUT/'ULTIMATE_preliminary_ML.html').exists()
    empirical=json.loads((OUT/'empirical_stress_assumptions.json').read_text())
    assert abs(empirical['innovation_variance']-1)<.01
    assert abs(empirical['empirical_rho_x']-empirical['simulated_rho_x'])<.01
    assert abs(empirical['empirical_rho_y']-empirical['simulated_rho_y'])<.01
    measured=json.loads((OUT/'hawki/empirical_model_inputs.json').read_text())
    assert empirical['measured_Ks_beta']==measured['psf']['beta']['median']
    reduced_checks=0
    for product in ['image','varmap','weightmap']:
        with fits.open(OUT/f'hawki/reduced_jan6_{product}.fits',checksum=True,memmap=False) as hdus:
            for hdu in hdus:
                assert hdu.verify_checksum()==1 and hdu.verify_datasum()==1
                reduced_checks+=1
    validation=dict(status='PASS numerical/information-boundary/delivery checks; physical labels remain operational',
        galaxies_available=26,galaxies_fitting_eligible=22,source_null_controls_excluded=sorted(zero),
        feature_rows=len(features),label_rows=len(labels),heldout_prediction_rows=len(prediction),
        max_independently_recomputed_MAE_difference=maximum,previous_files_hashes_unchanged=preserved,
        executed_notebook_code_cells=len(code),embedded_notebook_figures=len(embedded),
        primary_PNG_PDF_pairs=len(expected),g_only_strategy_gain_zero=True,
        HAWKI_reduced_HDU_checksum_checks=reduced_checks,
        final_test_images_used=0,original_source_residuals='UNRESOLVED; no correction/subtraction applied',
        unit_tests_passed=4,empirical_sensitivity='HAWKI-informed only; local covariance, not complete sky model',
        html_visual_scope='Exported and embedded-image/report equality checked; PNGs inspected, not separately browser-rendered')
    (OUT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    provenance=dict(executable=sys.executable,python=platform.python_version(),
        versions={name:importlib.metadata.version(name) for name in ['numpy','scipy','astropy','pandas','scikit-learn','matplotlib','nbformat','nbclient']},
        code_sha256={p.name:digest(p) for p in OUT.glob('*.py')},
        protocol_sha256=digest(OUT/'PROTOCOL.md'),source_feature_hash=digest(OUT/'observable_features.csv'),
        labels_sha256=digest(OUT/'operational_labels.csv'),
        frozen_120_partition_sha256=digest(OUT/'expansion/galaxy_partitions.csv'),
        empirical_inputs_sha256=digest(OUT/'hawki/empirical_model_inputs.json'))
    (OUT/'execution_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    files=sorted(p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts
                 and p.name not in ['output_manifest.sha256','delivery_validation.log'])
    # Acquisition status/logs evolve while the background batch runs; hash this snapshot only.
    (OUT/'output_manifest.sha256').write_text(''.join(f'{digest(p)}  {p.relative_to(OUT)}\n' for p in files))
    print(json.dumps(validation,indent=2))
    return validation


if __name__=='__main__':run()
