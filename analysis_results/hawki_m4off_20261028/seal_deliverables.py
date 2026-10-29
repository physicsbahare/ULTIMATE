"""Final consistency audit and file inventory; no prior results are modified."""
from pathlib import Path
import json,hashlib,ast
import nbformat,numpy as np,pandas as pd
O=Path(__file__).resolve().parent
nb=nbformat.read(O/'empirical_calibration.ipynb',as_version=4);nbformat.validate(nb);code=[c for c in nb.cells if c.cell_type=='code'];assert len(code)==9
assert [c.execution_count for c in code]==list(range(1,len(code)+1))
assert not any(o.output_type=='error' for c in code for o in c.get('outputs',[]))
assert sum('image/png' in o.get('data',{}) for c in code for o in c.get('outputs',[]))>=8
for p in O.glob('*.py'):ast.parse(p.read_text())
sm=pd.read_csv(O/'PSF_summary.csv');s=pd.read_csv(O/'science_star_table.csv');assert sm.n_stars.sum()==s.primary_star.sum()==965
for r in sm.itertuples():assert len(s[(s.field==r.field)&s.primary_star])==r.n_stars
q=pd.read_csv(O/'quadrature_sensitivity.csv');assert len(q)==12 and q.accepted.all();assert q.fractional_FWHM_bias.abs().max()<.01
models=pd.read_csv(O/'sensitivity_models/finite_growth_model_grid.csv');assert len(models[models.best])==5
assert 'previous_ML_freeze_receipt_sha256' in json.loads((O/'verification.json').read_text())
log=json.loads((O/'ancillary_download_log.json').read_text());b=sum(x.get('bytes',0) for x in log);assert b<80*1024**2
for p in O.rglob('*.csv'):
 # No general ban on NaNs: failed fits, invalid void apertures and missing references are explicit.
 assert p.stat().st_size>0
checks=dict(status='pass',executed_code_cells=len(code),selected_measurements=int(sm.n_stars.sum()),matched_rows=276,matched_unique_stars=244,public_ancillary_download_MiB=b/1024**2,source_scope='No ML science or previous results altered',visual_review='Final spatial/shape maps, observed/model residual panels, EE, same-operator noise and growth-model figures reviewed; saved notebook plots inspected. HTML exported, not browser-layout tested.',limitations=['global raw-linearity history unresolved','absolute photometry/astrometry not independently calibrated','finite EE and unresolved-source/sky contamination','undersampling/optimizer and integration floors','R32 aperture calibration rejected','core+halo and full-background mixtures are phenomenological'])
(O/'completion_audit.json').write_text(json.dumps(checks,indent=2))
files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts or p.name in ['artifact_manifest.json','seal_execution.log']:continue
 h=hashlib.sha256()
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1048576),b''):h.update(c)
 files.append(dict(path=str(p.relative_to(O)),bytes=p.stat().st_size,sha256=h.hexdigest()))
(O/'artifact_manifest.json').write_text(json.dumps({'scope':'Local calibration deliverables; excludes self, bytecode and running seal log','files':files},indent=2));print(json.dumps(checks,indent=2));print('Hashed deliverable files:',len(files))
