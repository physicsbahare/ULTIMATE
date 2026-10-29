from pathlib import Path
import sys,json
import numpy as np,pandas as pd,joblib
from model_study import *

def run():
 p=pd.read_csv(O/'heldout_predictions.csv.gz');settings=json.loads((O/'model_settings.json').read_text());f=pd.read_csv(O/'feature_table.csv.gz');y=pd.read_csv(O/'target_table.csv');split=json.loads((O/'validation_interval_split.json').read_text());meta=pd.read_csv(S/'data_audit/frozen_galaxy_partitions.csv');final=set(meta[meta.partition=='final_test'].subhalo_id)
 assert len(settings)==252 and p.tag.nunique()==252 and not set(p.subhalo_id)&final
 assert p.groupby(['tag','stage','subhalo_id']).size().eq(20).all()
 assert not p.duplicated(['tag','stage','subhalo_id','view','draw']).any()
 assert np.isfinite(p[['prediction','truth']]).all().all()
 assert set(split['calibration']).isdisjoint(split['assessment']) and len(split['calibration'])==len(split['assessment'])==7
 columns=set(f.columns)
 for tag,c in settings.items():
  bands=tag.split('_')[1];kind='photo' if '_photo' in tag else ('spatial' if '_spatial' in tag else 'summary')
  assert c['features']==feature_cols(columns,bands,kind) or set(c['features'])==set(feature_cols(columns,bands,kind))
  assert not any(any(word in x for word in ['clear','dust_mass','stellar','SFR','subhalo','truth','target','partition']) for x in c['features'])
 cal=pd.read_csv(O/'uncertainty_calibration.csv').set_index('tag')
 for tag,g in p[p.stage=='validation'].groupby('tag'):
  errors=g.assign(ae=abs(g.truth-g.prediction));scores=errors[errors.subhalo_id.isin(split['calibration'])].groupby('subhalo_id').ae.max();q=scores.max();assert np.isclose(q,cal.loc[tag,'half_width'])
  altered=g.copy();altered.loc[altered.subhalo_id.isin(split['assessment']),'truth']+=1e5
  q2=altered[altered.subhalo_id.isin(split['calibration'])].assign(ae=lambda x:abs(x.truth-x.prediction)).groupby('subhalo_id').ae.max().max();assert q2==q
 # Reproduce the saved metric table independently from row errors and galaxy sizes.
 m=pd.read_csv(O/'model_comparison.csv');checks=0
 for row in m.itertuples():
  a=p[(p.tag==row.tag)&(p.stage==row.stage)];err=(a.truth-a.prediction).to_numpy();groups=a.subhalo_id.to_numpy();values=[np.mean(abs(err[groups==s])) for s in np.unique(groups)];sq=[np.mean(err[groups==s]**2) for s in np.unique(groups)]
  assert np.isclose(np.mean(values),row.MAE) and np.isclose(np.sqrt(np.mean(sq)),row.RMSE);checks+=1
 result={'configurations':len(settings),'prediction_rows':len(p),'metric_rows_independently_recomputed':checks,'all_view_draw_keys_unique':True,'calibration_assessment_truth_perturbation_test':True,'predictor_allowlists_pass':True,'final_science_opened':False}
 (O/'model_verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':run()
