"""Prepared scoring gate. Never reads archives. No tuning or final access by default.

A future approved frozen protocol supplies audited final feature/target tables.
The method bundle must be immutable before those tables are generated.
"""
from pathlib import Path
import json,hashlib,argparse
import numpy as np,pandas as pd,joblib
from model_study import O,S,TARGETS,metrics

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def evaluate(bundle,features,targets):
 assert not (S/'FINAL_EVALUATION_COMPLETED.json').exists(), 'Project final20 already evaluated once; supplementary models are validation-only'
 b=json.loads(Path(bundle).read_text());assert b['status']=='frozen_for_final_evaluation'
 assert b['source_label_policy_resolved_or_explicitly_operational'] and b['all_tuning_complete']
 for file,h in b['method_hashes'].items():assert digest(O/file)==h
 assert not (O/'final_evaluation_started.json').exists(),'One final evaluation already started; do not repeat'
 meta=pd.read_csv(S/'data_audit/frozen_galaxy_partitions.csv');ids=set(meta[meta.partition=='final_test'].subhalo_id)
 f=pd.read_csv(features);y=pd.read_csv(targets)
 assert set(f.subhalo_id)==ids==set(y.subhalo_id) and len(ids)==20
 assert f.partition.eq('final_test').all() and y.partition.eq('final_test').all()
 assert f.groupby('subhalo_id').view.nunique().eq(5).all()
 settings=json.loads((O/'model_settings.json').read_text());results=[]
 # Exclusive marker written before any final prediction. An interrupted run requires documented recovery.
 with (O/'final_evaluation_started.json').open('x') as file:json.dump({'bundle_sha256':digest(bundle),'features_sha256':digest(features),'targets_sha256':digest(targets),'methods_frozen':True},file,indent=2)
 for tag in b['selected_tags']:
  conf=settings[tag];ap,bands,mode=tag.split('_')[:3];target=next(t for t in sorted(TARGETS,key=len,reverse=True) if tag.startswith('_'.join([ap,bands,mode,t])+'_'))
  data=f[(f.aperture==ap)&(f['mode']==mode)&(f.condition=='nominal')].merge(y[y.aperture==ap][['subhalo_id','view',target]],on=['subhalo_id','view'],validate='many_to_one')
  assert data.groupby('subhalo_id').size().eq(20).all()
  data['prediction']=conf['constant'] if conf['model']=='constant' else joblib.load(O/'models'/f'{tag}.joblib').predict(data[conf['features']]);data['truth']=data[target];data['tag']=tag;data['target']=target
  results.append(data[['subhalo_id','view','draw','tag','target','prediction','truth']])
 p=pd.concat(results,ignore_index=True);p.to_csv(O/'final_predictions.csv.gz',index=False);metrics(p,['tag','target']).to_csv(O/'final_metrics.csv',index=False)
 print('One frozen final scoring complete; no model refits or tuning')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--frozen-bundle');a.add_argument('--features');a.add_argument('--targets');args=a.parse_args()
 if not args.frozen_bundle:print('SEALED: no final table read. Requires immutable method hashes, explicit operational-label policy, selected tags and audited final-only tables.')
 else:
  assert args.features and args.targets;evaluate(args.frozen_bundle,args.features,args.targets)
