"""Integrity validation; run after notebook and figures finish."""
from pathlib import Path
import json,hashlib,subprocess,sys,base64
import numpy as np,pandas as pd,nbformat
O=Path(__file__).resolve().parent;root=O.parent.parent

def run():
 checks={};errors=[]
 old=json.loads((O/'previous_results_sha256.json').read_text());changed=[]
 for path,digest in old.items():
  p=root/path
  if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:changed.append(path)
 checks['previous_files_checked']=len(old);checks['previous_files_changed']=changed;assert not changed
 inputhash={}
 for p in [O.parent/'screen_test_20261026'/f'input_cache/O{i}_structured_broadbands.npz' for i in range(1,6)]+[O.parent/'screen_test_20261026'/'instrument.py',O.parent/'screen_test_20261026'/'forward_physics.py',root/'ULTIMATE_TNG50_SKIRT_294866_dust_pilot.ipynb']:
  inputhash[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
 assert inputhash[str(root/'ULTIMATE_TNG50_SKIRT_294866_dust_pilot.ipynb')]=='ba9ed6be682f65d5a8687ebf46c86170abe22279a3a615357fa8d6b05a46dcbd'
 (O/'input_provenance.json').write_text(json.dumps(inputhash,indent=2))
 notebook=nbformat.read(O/'Calibrated_DR1_screen_experiment.ipynb',as_version=4);nbformat.validate(notebook);cells=[c for c in notebook.cells if c.cell_type=='code'];assert all(c.execution_count is not None for c in cells)
 assert not [v for c in cells for v in c.outputs if v.output_type=='error']
 checks['executed_notebook_code_cells']=len(cells);checks['embedded_notebook_images']=sum('image/png' in o.get('data',{}) for c in cells for o in c.outputs)
 checks['html_preview_exists']=(O/'Calibrated_DR1_screen_experiment.html').exists();assert checks['html_preview_exists']
 test=subprocess.run([sys.executable,str(O/'test_validation.py')],cwd=O,capture_output=True,text=True);(O/'numerical_test_results.log').write_text(test.stdout+test.stderr);checks['numerical_tests_exit_code']=test.returncode;assert test.returncode==0
 final=pd.read_csv(O/'FINAL_calibrated_rates.csv');assert len(final)==192;assert set(final.n_evaluation)=={500};assert final.condition.nunique()==8
 checks['final_summary_rows']=len(final);checks['final_evaluation_per_scene']=500
 raw=pd.read_csv(O/'FINAL_evaluation_statistics.csv.gz');assert len(raw)==len(final)*500;checks['final_evidence_evaluations']=len(raw)
 for keys,g in raw.groupby(['condition','bandset','truth']):
  rec=final[(final.condition==keys[0])&(final.bandset==keys[1])&(final.truth==keys[2])].iloc[0]
  assert g.detected.sum()==rec.detections;assert np.isclose(g.score.median(),rec.median_statistic)
 cal=pd.read_csv(O/'FINAL_calibration_statistics.csv.gz');checks['final_calibration_scores']=len(cal);assert len(cal)==8*3*5*500
 anchors=pd.read_csv(O/'FINAL_population_anchor_stress.csv');assert set(anchors.n)=={500};assert len(anchors)==8*3*5
 checks['anchor_summary_rows']=len(anchors)
 transfer=pd.read_csv(O/'transfer_validation.csv');checks['max_gaussian_padded_flux_loss']=float(transfer[transfer.kind=='gaussian'].max_crop_flux_loss.max());checks['max_moffat_padded_flux_loss']=float(transfer[transfer.kind=='moffat'].max_crop_flux_loss.max());assert checks['max_gaussian_padded_flux_loss']<1e-5
 norm=pd.read_csv(O/'normalized_noise_validation.csv');assert norm.max_normalized_bias_in_sigma.max()<.1;assert norm.max_variance_relative_error.max()<.08;checks['normalization_noise_validation_pass']=True
 exact=pd.read_csv(O/'exact_poisson_validation.csv');assert abs(exact.mean_standardized).max()<.12;assert abs(exact.variance_standardized-1).max()<.12;checks['exact_poisson_projection_validation_pass']=True
 figures=list((O/'figures').glob('*.png'));pdfs=list((O/'figures').glob('*.pdf'));assert len(figures)==9 and len(pdfs)==9;checks['PNG_figures']=len(figures);checks['PDF_figures']=len(pdfs)
 gain=pd.read_csv(O/'GLAO_power_comparison.csv');assert gain.calibration_bootstrap_ci_low.notna().all();checks['calibration_plus_evaluation_bootstrap']=True
 embedded={hashlib.sha256(base64.b64decode(o['data']['image/png'])).hexdigest() for c in cells for o in c.outputs if 'image/png' in o.get('data',{})}
 disk={hashlib.sha256(p.read_bytes()).hexdigest() for p in figures}
 assert embedded==disk
 checks['notebook_embedded_figures_match_saved_PNGs']=True
 checks['visual_inspection']='All nine PNG figures inspected; representative GLAO PDF rendered and inspected; HTML structurally checked, not separately browser-rendered.'
 checks['scientific_validation']='Numerical and preservation checks pass; population-anchor failures and predictive inadequacy are retained scientific negative results, not passed physical-model tests.'
 checks['not_established']=['general false-positive control across stellar populations','physical SPS/SFH recovery','unique 3D dust geometry','exact observer-filter ULTIMATE performance','galaxy-to-galaxy generalization']
 (O/'validation.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2));return checks
if __name__=='__main__':run()
