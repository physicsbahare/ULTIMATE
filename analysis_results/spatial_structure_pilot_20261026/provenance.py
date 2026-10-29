from pathlib import Path
import hashlib,json,sys,importlib.metadata
O=Path(__file__).resolve().parent

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot():
 paths=[]
 for name in ['screen_test_20261026','dr1_calibrated_screen_20261026','multiplicative_diagnosis_20261026']:
  root=O.parent/name
  paths.extend(p for p in root.rglob('*') if p.is_file() and p.suffix in ['.py','.md','.json','.csv','.ipynb'] and 'sources' not in p.parts and '__pycache__' not in p.parts)
 manifest={str(p):digest(p) for p in paths};(O/'previous_results_sha256.json').write_text(json.dumps(manifest,indent=2));print(len(manifest),'previous analysis artifacts recorded')
 cache=O.parent/'screen_test_20261026/input_cache';files=[cache/f'O{i}_structured_broadbands.npz' for i in range(1,6)]
 (O/'input_provenance.json').write_text(json.dumps({str(p):digest(p) for p in files},indent=2))
def validate():
 old=json.loads((O/'previous_results_sha256.json').read_text());assert all(digest(Path(p))==v for p,v in old.items())
 info=dict(python=sys.version,executable=sys.executable,versions={x:importlib.metadata.version(x) for x in ['numpy','scipy','astropy','pandas','matplotlib','nbformat','nbclient']},code_sha256={p.name:digest(p) for p in O.glob('*.py')},previous_artifacts_unchanged=len(old),science_scope='observable structure/morphology; no dust-geometry inference',random_seed_calibration=761902,random_seed_evaluation_base=982310,stellar_control_seed=73921,independent_evaluation_noise_draws_per_scene_condition=40,no_threshold_training=True,observational_methods_receive_truth=False)
 (O/'execution_provenance.json').write_text(json.dumps(info,indent=2));return info
if __name__=='__main__':snapshot()
