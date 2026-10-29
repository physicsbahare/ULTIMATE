"""Read-only verification of an already completed final evaluation. No inference."""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
O=Path(__file__).resolve().parent;S=O.parent/'ml_expanded_20261028'
p=pd.read_csv(S/'final_predictions.csv.gz');m=pd.read_csv(S/'performance_summary.csv');m=m[m.evaluation=='final_test'];meta=pd.read_csv(S/'data_audit/frozen_galaxy_partitions.csv')
assert len(p)==153600 and set(p.subhalo_id)==set(meta[meta.partition=='final_test'].subhalo_id)
assert not set(p.subhalo_id)&set(meta[meta.partition!='final_test'].subhalo_id)
assert p.loc[~p.zero_projected_dust,'subhalo_id'].nunique()==16 and p.loc[p.zero_projected_dust,'subhalo_id'].nunique()==4
keys=['aperture','scenario','family','target'];assert not p.duplicated(keys+['subhalo_id','view','draw']).any();assert p.groupby(keys+['subhalo_id']).size().eq(20).all()
assert np.isfinite(p[['truth','prediction','error']]).all().all();np.testing.assert_allclose(p.error,p.prediction-p.truth,atol=1e-12)
primary=p[~p.zero_projected_dust];rows=[]
for key,g in primary.groupby(keys):
 err=g.prediction-g.truth;d=g.assign(ae=abs(err),se=err*err,b=err);gg=d.groupby('subhalo_id').agg(MAE=('ae','mean'),MSE=('se','mean'),bias=('b','mean'));ref=m
 for name,value in zip(keys,key):ref=ref[ref[name]==value]
 assert len(ref)==1;r=ref.iloc[0];assert np.isclose(gg.MAE.mean(),r.MAE) and np.isclose(np.sqrt(gg.MSE.mean()),r.RMSE) and np.isclose(gg.bias.mean(),r.bias)
 assert np.isclose(g.groupby('subhalo_id').covered.all().mean(),r.galaxy_coverage)
 rows.append(dict(zip(keys,key),MAE=gg.MAE.mean(),RMSE=np.sqrt(gg.MSE.mean()),bias=gg.bias.mean(),galaxies=16))
pd.DataFrame(rows).to_csv(O/'canonical_final_metric_recomputation.csv',index=False)
result={'passed':True,'scope':'Verification of existing stored predictions, no model.predict and no new final evaluation','final_rows':len(p),'primary_galaxies':16,'control_galaxies':4,'metric_rows_recomputed':len(rows),'per_orientation_draw_keys_unique':True,'finite_predictions':True,'final_evaluation_count':1}
(O/'canonical_final_score_audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
