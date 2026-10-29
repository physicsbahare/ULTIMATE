from pathlib import Path
import json,shutil
import pandas as pd
O=Path(__file__).resolve().parent;A=O/'integrated_Ks'
assert (O/'execution_complete.json').exists() and (A/'execution_complete.json').exists()
assert not (O/'integrated_Ks_merged.json').exists()
assert json.loads((O/'input_hashes.json').read_text())==json.loads((A/'input_hashes.json').read_text())
assert json.loads((O/'validation_interval_split.json').read_text())==json.loads((A/'validation_interval_split.json').read_text())
s=json.loads((O/'model_settings.json').read_text());a=json.loads((A/'model_settings.json').read_text());assert not set(s)&set(a) and len(s)==210 and len(a)==42
for file in ['heldout_predictions.csv.gz','model_comparison.csv','galaxy_residuals.csv','development_tuning.csv','uncertainty_calibration.csv']:
 x=pd.read_csv(O/file);y=pd.read_csv(A/file);pd.concat([x,y],ignore_index=True).to_csv(O/file,index=False)
s.update(a);(O/'model_settings.json').write_text(json.dumps(s,indent=2))
for p in (A/'models').glob('*.joblib'):assert not (O/'models'/p.name).exists();shutil.copyfile(p,O/'models'/p.name)
(O/'integrated_Ks_merged.json').write_text(json.dumps({'configurations':len(s),'main':210,'integrated_Ks':42,'input_hashes_identical':True,'validation_splits_identical':True},indent=2));print('Merged 252 model configurations; no validation selection')
