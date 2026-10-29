"""Frozen one-pass final source preparation and scoring; default is sealed dry run."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import importlib.util,json,sys,hashlib,argparse
from datetime import datetime,timezone
import pandas as pd
from model_study import O,S
from final_evaluation import digest,evaluate

def run():
 assert not (S/'FINAL_EVALUATION_COMPLETED.json').exists(), 'Project final20 already evaluated once; supplementary models are validation-only'
 bundle=O/'FINAL_PROTOCOL_FROZEN.json'
 assert bundle.exists(),'Final remains sealed until complete method freeze'
 b=json.loads(bundle.read_text())
 for file,h in b['method_hashes'].items():assert digest(O/file)==h
 assert not (O/'final_evaluation_started.json').exists()
 access=O/'final_scientific_access_started.json'
 if not access.exists():
  with access.open('x') as file:json.dump({'opened_UTC':datetime.now(timezone.utc).isoformat(),'freeze_bundle_SHA256':digest(bundle),'method_hashes_checked':True,'scope':'final-only source preparation then one frozen scoring; no tuning'},file,indent=2)
 else:assert json.loads(access.read_text())['freeze_bundle_SHA256']==digest(bundle)

 spec=importlib.util.spec_from_file_location('frozen_source_reader',O/'final_source_reader.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
 reader.OUT=O/'final_data_audit';reader.OUT.mkdir(exist_ok=True);(reader.OUT/'integrity').mkdir(exist_ok=True);(reader.OUT/'cache').mkdir(exist_ok=True)
 meta=pd.read_csv(S/'data_audit/frozen_galaxy_partitions.csv');final=meta[meta.partition=='final_test'];states=reader.sources()
 def work(sid):return reader.stream(int(sid),states[int(sid)],'final_test')
 with ThreadPoolExecutor(max_workers=2) as pool:records=list(pool.map(work,final.subhalo_id))
 pd.DataFrame(records).to_csv(reader.OUT/'archive_inventory.csv',index=False)
 # Use the exact frozen feature/label code on a separate final-only cache.
 spec=importlib.util.spec_from_file_location('frozen_features',O/'frozen_features.py');e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
 e.O=O/'final_products';e.O.mkdir(exist_ok=True);(e.O/'FINAL_PROTOCOL_FROZEN.json').write_text(bundle.read_text());(e.O/'data_audit').mkdir(exist_ok=True)
 cache=e.O/'data_audit/cache'
 if not cache.exists():cache.symlink_to(reader.OUT/'cache',target_is_directory=True)
 for sid in final.subhalo_id:e.process(int(sid),'final_test',final=True)
 paths=[e.O/'derived'/str(sid) for sid in final.subhalo_id]
 for filename,dest in [('features.csv.gz','final_features.csv.gz'),('labels.csv','final_targets.csv')]:pd.concat([pd.read_csv(p/filename) for p in paths],ignore_index=True).to_csv(e.O/dest,index=False)
 evaluate(bundle,e.O/'final_features.csv.gz',e.O/'final_targets.csv')
 print('Final stage finished, no method selection/refitting',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--execute-frozen',action='store_true');a=p.parse_args()
 if a.execute_frozen:run()
 else:print('SEALED dry run: final source preparation/scoring requires verified immutable freeze bundle')
