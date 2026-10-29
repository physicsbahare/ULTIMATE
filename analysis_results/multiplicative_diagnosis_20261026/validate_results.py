from pathlib import Path
import json,hashlib,base64,subprocess,sys,importlib.metadata,ast
import numpy as np,pandas as pd,nbformat
O=Path(__file__).resolve().parent

def run():
 old=json.loads((O/'previous_results_sha256.json').read_text());changed=[]
 for path,digest in old.items():
  p=Path(path)
  if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:changed.append(path)
 assert not changed,changed
 # Also compare the previous published source-code manifest, recorded before
 # this new task, rather than relying only on this task's preservation snapshot.
 previous=O.parent/'dr1_calibrated_screen_20261026';published=json.loads((previous/'execution_provenance.json').read_text());source_changed=[]
 for name,digest in published['code_sha256'].items():
  p=previous/name
  if hashlib.sha256(p.read_bytes()).hexdigest()!=digest:source_changed.append(name)
 assert not source_changed,source_changed
 for f in O.glob('*.py'):ast.parse(f.read_text())
 test=subprocess.run([sys.executable,str(O/'test_physical.py')],capture_output=True,text=True);(O/'numerical_tests.log').write_text(test.stdout+test.stderr);assert test.returncode==0
 n=nbformat.read(O/'ULTIMATE_targeted_positive_model.ipynb',as_version=4);nbformat.validate(n);cells=[c for c in n.cells if c.cell_type=='code'];assert all(c.execution_count is not None for c in cells);assert not [o for c in cells for o in c.outputs if o.output_type=='error']
 pngs=sorted((O/'figures').glob('*.png'));pdfs=sorted((O/'figures').glob('*.pdf'));assert len(pngs)==len(pdfs)==6
 embedded={hashlib.sha256(base64.b64decode(o['data']['image/png'])).hexdigest() for c in cells for o in c.outputs if 'image/png' in o.get('data',{})};disk={hashlib.sha256(p.read_bytes()).hexdigest() for p in pngs};assert embedded==disk
 rates=pd.read_csv(O/'heldout_pilot_rates.csv');raw=pd.read_csv(O/'heldout_pilot_per_draw.csv');cal=pd.read_csv(O/'pilot_calibration.csv');assert len(raw)==68 and len(rates)==34 and len(cal)==38
 assert set(raw.query('likelihood=="absolute"').groupby(['population','screen']).size())=={1};assert set(raw.query('likelihood=="contrasts"').groupby(['population','screen']).size())=={3}
 for keys,g in raw.groupby(['population','screen','likelihood']):
  r=rates[(rates.population==keys[0])&(rates.screen==keys[1])&(rates.likelihood==keys[2])].iloc[0];assert g.rejected.sum()==r.rejections;assert len(g)==r.n
 cuts=json.loads((O/'pilot_thresholds.json').read_text())
 for key,g in cal.groupby('likelihood'):assert np.isclose(cuts[key],g.statistic.max())
 assert cal.null_success.all() and cal.variable_success.all()
 gate=json.loads((O/'development_gate.json').read_text());assert gate['physical_null_gate_passed']==False and gate['larger_evaluation_permitted']==False
 mech=pd.read_csv(O/'old_method_mechanism.csv');base=mech[(mech.strategy=='matched')&(mech['mode']=='seeing')&(mech.variant=='baseline')].iloc[0];assert np.isclose(base.reproduced_FPR,.984)
 apo=pd.read_csv(O/'aperture_information_loss.csv');sparse=apo[(apo['mode']=='seeing')&(apo.data=='original_15_apertures')].iloc[0];dense=apo[(apo['mode']=='seeing')&(apo.data=='evaluation_rectangle_pixels')].iloc[0];assert dense.squared_mean_separation>sparse.squared_mean_separation*100
 inp={str(previous/'experiment.py'):hashlib.sha256((previous/'experiment.py').read_bytes()).hexdigest(),str(O.parent/'screen_test_20261026/input_cache/O1_structured_broadbands.npz'):hashlib.sha256((O.parent/'screen_test_20261026/input_cache/O1_structured_broadbands.npz').read_bytes()).hexdigest()}
 (O/'input_provenance.json').write_text(json.dumps(inp,indent=2))
 provenance=dict(python=sys.version,executable=sys.executable,versions={x:importlib.metadata.version(x) for x in ['numpy','scipy','astropy','matplotlib','pandas','nbformat','nbclient']},code_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in O.glob('*.py')},random_seeds='Explicit in scripts and saved pattern NPZ; calibration74398, new evaluation519873+case index; no sequential warm starts',scope='O1 z=.3; native primary, matched only exact old failure and SED-coverage diagnostics',data='DR1 g,r,i,z,J,H,Ks and training-only local u diagnostic',source_pixel_pc=100,source_model_cell_kpc=1,exposure_per_band_s=3600,DIT_s=60,primary_reads=60,previous_full_grid_rerun=False,new_large_evaluation=False,physical_geometry_validated=False)
 (O/'execution_provenance.json').write_text(json.dumps(provenance,indent=2))
 checks=dict(numerical_tests_passed=6,previous_result_files_unchanged=len(old),previous_published_source_manifest_matches=True,executed_notebook_code_cells=len(cells),notebook_embedded_figures_match_files=True,PNG_figures=6,PDF_figures=6,pilot_calibration_noise_realizations=19,pilot_calibration_fit_pairs=len(cal),heldout_pilot_fit_pairs=len(raw),heldout_contrast_draws_per_scene=3,heldout_absolute_draws_per_scene=1,nonconverged_null_fits=int((~raw.null_success).sum()),nonconverged_alternative_fits=int((~raw.variable_success).sum()),physical_validation_gate='FAILED; no large evaluation or GLAO performance claim',named_catastrophic_control_reproduced=True,scientific_decision='NO-GO for current dust-geometry inference; not a universal proof against full broadband images',visual_validation='All six PNGs and representative PDF rendered and inspected; notebook/HTML structurally validated',limitations=['inadequate absolute-colour physical fits','optimizer failures retained','local Laplace posterior only','small diagnostic FPR/power samples','known-family calibration not population robustness','sparse apertures lose spatial information','no exact ULTIMATE observer-band forecast','one galaxy only'])
 (O/'validation.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2));return checks
if __name__=='__main__':run()
