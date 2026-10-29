"""Inspect completed sensitivity, including identity to independently saved baseline."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd

O=Path(__file__).resolve().parent
d=pd.read_csv(O/'stress_features.csv.gz')
meta=['subhalo_id','view','draw','partition','aperture','condition','mode','case']
cols=[c for c in d if c not in meta]
selected=pd.read_csv(O/'selected_galaxies.csv')
assert len(d)==640 and len(selected)==20
assert d.partition.value_counts().to_dict()=={'validation':448,'development':192}
assert set(d.subhalo_id)==set(selected.subhalo_id)
assert d.groupby(['subhalo_id','case','mode']).size().eq(4).all()
assert not d.duplicated(['subhalo_id','view','draw','mode','case']).any()
assert len(cols)==180
keys=['subhalo_id','view','draw','mode']
baseline_errors=[]
for sid in selected.subhalo_id:
    p=O.parent/'derived'/str(sid)/'features.csv.gz'
    if not p.exists():continue
    original=pd.read_csv(p)
    original=original[(original.view=='O1')&(original.aperture=='adaptive')&(original.condition=='nominal')]
    current=d[(d.subhalo_id==sid)&(d.case=='A')]
    a=current.sort_values(keys)[cols].to_numpy();b=original.sort_values(keys)[cols].to_numpy()
    assert np.allclose(a,b,rtol=1e-10,atol=1e-10,equal_nan=True)
    baseline_errors.append(dict(subhalo_id=int(sid),max_absolute_difference=float(np.nanmax(np.abs(a-b)))))
bc=d[d.case.isin(['B','C'])].pivot(index=keys,columns='case',values=cols)
unchanged=[c for c in cols if c.startswith(('g_','J_','cell_g_'))]
assert np.allclose(bc.loc[:,[(c,'B') for c in unchanged]].to_numpy(),bc.loc[:,[(c,'C') for c in unchanged]].to_numpy(),equal_nan=True)
render=pd.read_csv(O/'render_validation.csv')
manifest=pd.read_csv(O/'hawki_sharing_manifest.csv')
for r in manifest.itertuples():
    p=Path(r.original_path)
    assert p.stat().st_size==r.bytes
    assert hashlib.sha256(p.read_bytes()).hexdigest()==r.sha256
result=dict(passed=True,n_rows=len(d),n_galaxies=d.subhalo_id.nunique(),feature_count=len(cols),
    feature_nonfinite_cells=int((~np.isfinite(d[cols].to_numpy())).sum()),
    final_test_rows=int((d.partition=='final_test').sum()),
    baseline_identity_checks=baseline_errors,
    max_padded_flux_loss=float(render.padded_flux_loss.max()),
    max_bin_flux_sum_relative_error=float(render.flux_sum_relative_error.max()),
    max_bin_variance_sum_relative_error=float(render.variance_sum_relative_error.max()),
    manifest_files_verified=len(manifest))
(O/'verification.json').write_text(json.dumps(result,indent=2))
metrics=['g_R50','J_R50','Ks_R50','Ks_C','Ks_A','Ks_logJy','color_J_Ks','gradient_J_Ks','Ks_texture_0.5']
base=d[d.case=='A'].set_index(keys)
rows=[]
for (case,mode),group in d[d.case!='A'].groupby(['case','mode']):
    group=group.set_index(keys)
    delta=group[metrics]-base.loc[group.index,metrics]
    for metric in metrics:
        a=delta[metric].to_numpy()
        rows.append(dict(case=case,mode=mode,feature=metric,median_delta=float(np.nanmedian(a)),median_abs_delta=float(np.nanmedian(abs(a))),p90_abs_delta=float(np.nanquantile(abs(a),.9)),n_finite=int(np.isfinite(a).sum())))
pd.DataFrame(rows).to_csv(O/'observable_feature_shifts.csv',index=False)
print(json.dumps(result,indent=2))
