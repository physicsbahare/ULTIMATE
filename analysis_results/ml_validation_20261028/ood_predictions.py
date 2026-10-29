from model_study import *

def run():
 f=pd.read_csv(O/'feature_table.csv.gz');y=pd.read_csv(O/'target_table.csv');summary=pd.read_csv(O/'OOD_summary.csv');settings=json.loads((O/'model_settings.json').read_text());records=[]
 for row in summary.itertuples():
  cfg=settings[row.tag];ap,bands,mode=row.tag.split('_')[:3];target=next(t for t in sorted(TARGETS,key=len,reverse=True) if row.tag.startswith('_'.join([ap,bands,mode,t])+'_'))
  d=f[(f.partition=='development')&(f.aperture==ap)&(f.condition=='nominal')&(f['mode']==mode)].merge(y[y.aperture==ap],on=['subhalo_id','view','aperture','partition'],validate='many_to_one');d=d[~d.zero_projected_dust]
  mass=d.groupby('subhalo_id').log_stellar_mass.mean();hi=mass[mass>=mass.quantile(.75)].index;train=d[~d.subhalo_id.isin(hi)];test=d[d.subhalo_id.isin(hi)]
  fit=estimator('ridge',row.setting).fit(train[cfg['features']],train[target]);pred=fit.predict(test[cfg['features']]);assert np.isclose(group_mae(test[target].to_numpy(),pred,test.subhalo_id.to_numpy()),row.MAE)
  a=test[['subhalo_id','view','draw','log_stellar_mass','Ks_q']].copy();a['truth']=test[target];a['prediction']=pred;a['tag']=row.tag;a['target']=target;records.append(a)
 pd.concat(records,ignore_index=True).to_csv(O/'OOD_per_orientation_predictions.csv.gz',index=False);print('OOD refits reproduce stored summary and preserve views/draws')
if __name__=='__main__':run()
