from pathlib import Path
import hashlib,json,sys
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
O=Path(__file__).resolve().parent;R=O.parents[1];S=O.parent/'ml_expanded_20261028'
sys.path.insert(0,str(S/'data_audit'));from prepare_data import sources
m=pd.read_csv(R/'analysis_results/ml_feasibility_20261027/expansion/galaxy_partitions.csv');states=sources()
assert len(m)==120 and m.subhalo_id.nunique()==120 and set(states)==set(m.subhalo_id)
assert m.partition.value_counts().to_dict()=={'development':86,'final_test':20,'validation':14}
assert m[m.provenance=='existing'].partition.eq('development').all()
def check(r):
 s=states[r.subhalo_id];p=s['path'];h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 assert h.hexdigest()==s['sha256'] and p.stat().st_size==s['bytes'] and s['gzip_CRC']=='passed' and s['tar_read']=='passed'
 return dict(subhalo_id=r.subhalo_id,partition=r.partition,path=str(p.relative_to(R)),bytes=p.stat().st_size,sha256=h.hexdigest(),inherited_crc_tar_pass=True,current_hash_and_size_match=True,science_opened_by_this_audit=False)
with ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(check,m.itertuples()))
pd.DataFrame(rows).to_csv(O/'verified_archive_inventory.csv',index=False)
assert not any((S/'data_audit/cache'/str(s)).exists() for s in m[m.partition=='final_test'].subhalo_id)
(O/'acquisition_verified.json').write_text(json.dumps(dict(archives=120,new_archives=94,final_sealed=20,current_SHA256_match=120,gzip_tar_evidence='inherited downloader; identical current compressed hashes and byte lengths',duplicate_downloads_started=0),indent=2))
print('PASS: 120 current archive hashes/lengths match verified downloader; final20 byte-integrity only')
