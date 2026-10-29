"""Guarded final20 extraction. Merely importing this module never reads final science."""
from pathlib import Path
import argparse,hashlib,json,sys,traceback
from datetime import datetime,timezone
import pandas as pd
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
RECEIPT=HERE.parent/'FINAL_PROTOCOL_FROZEN.json'
REQUIRED_STAGES={'development_cv_settings','models','calibration','integrity_tests','sensitivity_choices'}
REQUIRED_ARTIFACTS={str(p.relative_to(ROOT)) for p in [HERE/'unseal_final.py',HERE/'prepare_data.py',HERE/'frozen_galaxy_partitions.csv',HERE/'validation.json',HERE/'archive_inventory.csv',HERE/'cache_file_integrity.csv',HERE.parent/'expanded_features.py',HERE.parent/'expanded_models.py']}

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()

def verify_receipt(path=RECEIPT):
 """Read receipt/artifact bytes and frozen metadata only; no final archive payloads."""
 path=Path(path).resolve()
 if path!=RECEIPT.resolve():raise PermissionError(f'Receipt must be {RECEIPT}')
 if not path.is_file():raise PermissionError('FINAL_PROTOCOL_FROZEN.json does not exist')
 receipt_bytes=path.read_bytes();receipt=json.loads(receipt_bytes)
 if receipt.get('protocol_frozen') is not True or receipt.get('allow_final_unseal') is not True:
  raise PermissionError('Receipt must explicitly freeze protocol and allow final unsealing')
 if not REQUIRED_STAGES<=set(receipt.get('stages_frozen',[])):
  raise PermissionError('Receipt is missing a required completed freeze stage')
 entries=receipt.get('artifacts');seen=set();roles=set();verified=[]
 if not isinstance(entries,list) or not entries:raise PermissionError('Receipt artifacts must be a nonempty list')
 for entry in entries:
  relative=entry.get('path');expected=entry.get('sha256')
  if not isinstance(relative,str) or not isinstance(expected,str) or len(expected)!=64:
   raise PermissionError('Every artifact needs a root-relative path and SHA256')
  p=(ROOT/relative).resolve()
  if Path(relative).is_absolute() or not p.is_relative_to(ROOT) or not p.is_file() or p==path:
   raise PermissionError(f'Invalid frozen artifact path: {relative}')
  canonical=str(p.relative_to(ROOT))
  if canonical in seen:raise PermissionError(f'Duplicate frozen artifact: {canonical}')
  seen.add(canonical)
  role=entry.get('role',entry.get('roles',[]));roles.update([role] if isinstance(role,str) else role)
  digest=sha(p)
  if digest!=expected:raise PermissionError(f'Frozen artifact SHA256 mismatch: {canonical}')
  verified.append(dict(path=canonical,sha256=digest,bytes=p.stat().st_size))
 if not REQUIRED_ARTIFACTS<=seen:raise PermissionError(f'Missing required frozen artifacts: {sorted(REQUIRED_ARTIFACTS-seen)}')
 if not {'code','model','calibration','protocol'}<=roles:
  raise PermissionError('Frozen artifacts must include code, model, calibration and protocol roles')
 meta=pd.read_csv(HERE/'frozen_galaxy_partitions.csv')
 if meta.partition.value_counts().to_dict()!={'development':86,'final_test':20,'validation':14}:
  raise PermissionError('Frozen partition counts differ')
 final=sorted(int(x) for x in meta.loc[meta.partition=='final_test','subhalo_id'])
 if sorted(receipt.get('final_test_ids',[]))!=final:raise PermissionError('Receipt final20 IDs differ from frozen manifest')
 validation=json.loads((HERE/'validation.json').read_text())
 if validation.get('passed') is not True or validation.get('final_science_opened') is not False:
  raise PermissionError('Pre-unseal nonfinal audit validation did not pass with sealed final20')
 old=pd.read_csv(HERE/'archive_inventory.csv');sealed=old[old.partition=='final_test']
 if len(sealed)!=20 or not sealed.sealed_final.all() or sealed.science_opened.any():
  raise PermissionError('Pre-unseal archive snapshot must retain sealed-final integrity-only status')
 return dict(receipt_sha256=hashlib.sha256(receipt_bytes).hexdigest(),final_ids=final,verified_artifacts=verified)

def atomic_json(path,value):
 tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(value,indent=2));tmp.replace(path)

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--run',action='store_true',help='Execute final extraction after explicit RUN authorization and valid freeze receipt')
 parser.add_argument('--check',action='store_true',help='Validate receipt only; never open final archive science')
 args=parser.parse_args()
 if args.run==args.check:parser.error('Select exactly one of --check or --run')
 authorization=verify_receipt()
 if args.check:
  print(json.dumps(dict(receipt_valid=True,final_science_opened=False,**authorization),indent=2));return
 import prepare_data as prep
 destination=HERE/'final_unseal';destination.mkdir(exist_ok=True)
 import fcntl
 lock=(destination/'.extraction.lock').open('a')
 try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:raise PermissionError('Another final extraction is already running')
 (destination/'integrity').mkdir(exist_ok=True)
 marker=destination/'FINAL_UNSEAL_STARTED.json'
 if marker.exists():
  previous=json.loads(marker.read_text())
  if previous['frozen_receipt_sha256']!=authorization['receipt_sha256']:
   raise PermissionError('Final20 were already unsealed under another receipt')
 else:
  value=dict(started_utc=datetime.now(timezone.utc).isoformat(),frozen_receipt_sha256=authorization['receipt_sha256'],final_ids=authorization['final_ids'],purpose='One final protocol; extraction resume only, no model retuning')
  with marker.open('x') as f:json.dump(value,f,indent=2)
 states=prep.sources();meta=pd.read_csv(HERE/'frozen_galaxy_partitions.csv')
 baseline_hashes={str(p.relative_to(HERE)):sha(p) for p in [HERE/'archive_inventory.csv',HERE/'fits_inventory.csv',HERE/'available_galaxies.csv',HERE/'physical_maps.csv',HERE/'validation.json']}
 prep.OUT=destination
 records=[];failures=[]
 for sid in authorization['final_ids']:
  try:
   row=prep.stream(sid,states[sid],'final_test',final_receipt=RECEIPT,cache_root=HERE/'cache')
   records.append(row)
  except Exception as e:
   failures.append(dict(subhalo_id=sid,error=str(e),traceback=traceback.format_exc()))
   atomic_json(destination/'failures.json',failures)
   raise
  pd.DataFrame(records).to_csv(destination/'archive_inventory.csv',index=False)
  pd.concat([pd.read_csv(HERE/'cache'/str(r['subhalo_id'])/'fits.csv') for r in records],ignore_index=True).to_csv(destination/'fits_inventory.csv',index=False)
  pd.concat([pd.read_csv(HERE/'cache'/str(r['subhalo_id'])/'physical.csv') for r in records],ignore_index=True).to_csv(destination/'physical_maps.csv',index=False)
  meta[meta.subhalo_id.isin([r['subhalo_id'] for r in records])].assign(cache_complete=True,sealed_final=False,sealed_final_at_preunseal_audit=True).to_csv(destination/'available_galaxies.csv',index=False)
 verify_receipt()
 for relative,digest in baseline_hashes.items():
  if sha(HERE/relative)!=digest:raise RuntimeError(f'Pre-unseal audit snapshot changed: {relative}')
 inventory=pd.read_csv(destination/'fits_inventory.csv');physical=pd.read_csv(destination/'physical_maps.csv')
 if len(records)!=20 or len(inventory)!=4800 or len(physical)!=100:raise RuntimeError('Incomplete final20 extraction')
 cache_integrity=[]
 expected={f'{scene}_{band}' for scene in ['clear','dusty'] for band in prep.KEEP}|{'dust'}
 import numpy as np
 for sid in authorization['final_ids']:
  for view in [f'O{i}' for i in range(1,6)]:
   path=HERE/'cache'/str(sid)/f'{view}.npz'
   with np.load(path) as z:
    if set(z.files)!=expected or any(z[k].shape!=(800,800) or not np.isfinite(z[k]).all() for k in expected):raise RuntimeError(f'Invalid final cache: {path}')
   cache_integrity.append(dict(subhalo_id=sid,view=view,sha256=sha(path),bytes=path.stat().st_size))
 pd.DataFrame(cache_integrity).to_csv(destination/'cache_file_integrity.csv',index=False)
 atomic_json(destination/'failures.json',[])
 atomic_json(destination/'receipt.json',dict(passed=True,audit_stage='final_unseal',completed_utc=datetime.now(timezone.utc).isoformat(),frozen_receipt_sha256=authorization['receipt_sha256'],final_ids=authorization['final_ids'],final_science_opened=True,sealed_final=False,sealed_final_at_preunseal_audit=True,galaxies=20,views=100,FITS_headers=4800,cache_arrays=700,preunseal_snapshots_unchanged=baseline_hashes,verified_frozen_artifacts=authorization['verified_artifacts']))
 print('Final20 extraction complete; final_unseal/receipt.json written. Pre-unseal100nonfinal audit snapshots unchanged.')

if __name__=='__main__':main()
