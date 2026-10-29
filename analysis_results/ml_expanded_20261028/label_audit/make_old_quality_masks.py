"""Descriptive flags for OLD fixed-R12 operational labels; not training exclusion rules.
Run with python3. No expansion image or label is opened.
"""
from pathlib import Path
import json
import pandas as pd
O=Path(__file__).resolve().parent
R=O.parents[2]
S=R/'analysis_results/ml_feasibility_20261027'
labels=pd.read_csv(S/'operational_labels.csv')
env=pd.read_csv(S/'source_null_label_audit.csv')
rows=[]
for t in env.itertuples():
    for x in labels.itertuples():
        v=getattr(x,t.target)
        rows.append(dict(subhalo_id=x.subhalo_id,view=x.view,target=t.target,label=v,old_fixed12_null_abs_max=t.maximum_control_absolute_value,within_old_control_envelope=abs(v)<=t.maximum_control_absolute_value,source_null_control=bool(x.zero_projected_dust),aperture_limited=bool(x.aperture_limited),label_finite=bool(pd.notna(v)),interpretation='operational_source_product_pair; physical_calibration_unresolved'))
pd.DataFrame(rows).to_csv(O/'old_fixed12_quality_flags.csv',index=False)
(O/'quality_policy.json').write_text(json.dumps(dict(version='2026-10-28',scope='Old fixed R12 native source-pair labels only. New apertures/PSFs require matched-control remeasurement.',targets={x.target:dict(control_absolute_envelope=x.maximum_control_absolute_value,n_control_galaxies=int(x.n_control_galaxies)) for x in env.itertuples()},rules=['Keep signed labels; never clip negative attenuation or morphology differences.','Do not subtract a universal null offset.','Flags within_old_control_envelope are descriptive resolution warnings, not calibrated confidence intervals or row rejection criteria.','Require matching pair band, WCS, shape, units, finite nonnegative intensity and positive aperture sums.','Same observed dusty-Ks-selected aperture for clear and dusty. Record aperture truncation/clipping; retain fixed12 sensitivity.','Separate source quality, source-null status, observational quality, aperture limitation, and label uncertainty flags.','Exclude invalid pairs; retain valid null controls for evaluation.','Do not transplant fixed12/native envelopes to adaptive apertures or seeing without matched-control remeasurement.','No new final or validation labels may be opened for thresholds or feature/model selection.']),indent=2))
print('wrote',len(rows),'descriptive old target flags')
