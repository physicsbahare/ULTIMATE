"""Available-development-only checkpoint; no validation or final labels."""
from model_study import *
from sklearn.model_selection import GroupKFold
meta=pd.read_csv(S/'data_audit/frozen_galaxy_partitions.csv');paths=[S/'derived'/str(s) for s in meta[meta.partition=='development'].subhalo_id if (S/'derived'/str(s)/'complete.json').exists()]
f=pd.concat([pd.read_csv(p/'features.csv.gz') for p in paths]);y=pd.concat([pd.read_csv(p/'labels.csv') for p in paths]);d=f[(f.aperture=='fixed12')&(f.condition=='nominal')&(f['mode']=='seeing')].merge(y[y.aperture=='fixed12'],on=['subhalo_id','view','aperture','partition'],validate='many_to_one');d=d[~d.zero_projected_dust].reset_index(drop=True);rows=[]
for target in TARGETS[:3]:
 for model in ['constant','photo_ridge','spatial_ridge']:
  cols=feature_cols(f.columns,'nir','photo' if model=='photo_ridge' else 'spatial');X=d[cols];yy=d[target].to_numpy();g=d.subhalo_id.to_numpy();pred=np.zeros(len(d))
  for tr,te in GroupKFold(5).split(X,yy,g):
   if model=='constant':pred[te]=np.median(yy[tr])
   else:
    st,_,_=choose(X.iloc[tr].reset_index(drop=True),yy[tr],g[tr],'ridge');pred[te]=estimator('ridge',st).fit(X.iloc[tr],yy[tr]).predict(X.iloc[te])
  rows.append(dict(target=target,model=model,galaxies=len(set(g)),nested_group_CV_MAE=group_mae(yy,pred,g)))
pd.DataFrame(rows).to_csv(O/'available_development_checkpoint.csv',index=False);print(pd.DataFrame(rows).to_string(index=False))
