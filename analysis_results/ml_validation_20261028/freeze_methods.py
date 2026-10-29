from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import pandas as pd
O=Path(__file__).resolve().parent
assert not (O.parent/'ml_expanded_20261028/FINAL_EVALUATION_COMPLETED.json').exists(), 'Project final evaluation already completed; no second final freeze'
assert not (O/'FINAL_PROTOCOL_FROZEN.json').exists()
verification=json.loads((O/'model_verification.json').read_text());assert verification['configurations']==252 and verification['predictor_allowlists_pass']
settings=json.loads((O/'model_settings.json').read_text());assert len(settings)==252
sample=pd.read_csv(O/'sensitivity_sample.csv');files=list((O/'sensitivity_features').glob('*.csv.gz'));assert len(files)==len(sample)==30
assert pd.read_csv(O/'sensitivity_summary.csv').scenario.nunique()==7
assert (O/'model_feature_interpretation.csv').exists() and (O/'OOD_per_orientation_predictions.csv.gz').exists()
assert (O/'scientific_report.md').exists() and (O/'expanded_training_evaluation.ipynb').exists()
methods=['model_study.py','empirical_sensitivity.py','final_source_reader.py','frozen_features.py','final_evaluation.py','final_stage.py','final_summary.py','summarize.py','ood_predictions.py','label_policy_freeze.json','protocol.md','model_settings.json','validation_interval_split.json','uncertainty_calibration.csv','input_hashes.json','verified_archive_inventory.csv']
methods += [str(p.relative_to(O)) for p in (O/'models').glob('*.joblib')]
hashes={f:hashlib.sha256((O/f).read_bytes()).hexdigest() for f in methods}
# Every source feature function is the exact version used by the nonfinal producer.
assert (O/'frozen_features.py').read_bytes()==(O.parent/'ml_expanded_20261028/expanded_features.py').read_bytes()
bundle={'status':'frozen_for_final_evaluation','frozen_UTC':datetime.now(timezone.utc).isoformat(),'source_label_policy_resolved_or_explicitly_operational':True,'label_claim':'Signed DR1 paired-product prediction only; physical source calibration remains unresolved. No unique3D or validated ULTIMATE forecast.','all_tuning_complete':True,'selected_tags':list(settings),'method_selection':'All252 specified configurations retained; no validation-winner filtering','primary_targets':['A_g','dR50_Ks','dC_Ks'],'additional_target':'A_Ks, successful in prior pilot; identical method family','exploratory_targets':['A_g_p50_1kpc','A_g_IQR_1kpc'],'primary_aperture':'fixed12','adaptive_role':'task-definition sensitivity; idealized deep-Ks selection','point_metric':'galaxy mean of view/draw absolute errors, then equal galaxy mean; analogous RMSE','uncertainty':'Frozen7 validation calibrators and7 assessment IDs;80% max-residual-per-galaxy widths; final20 coverage separately','final_policy':'All20 final galaxies, all5 orientations, all4 nominal draws; no refitting, exclusion based on final residuals or retuning; one evaluation marker','method_hashes':hashes}
with (O/'FINAL_PROTOCOL_FROZEN.json').open('x') as f:json.dump(bundle,f,indent=2)
print('FROZEN:252 configurations,180 fitted artifacts, exact methods and calibration widths; final20 may now be prepared once')
