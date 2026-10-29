"""Frozen-partition, read-only DR1 archive audit and central native crop cache."""
from pathlib import Path
import json,hashlib,tarfile,gzip,io,re,shutil,traceback,time
from concurrent.futures import ThreadPoolExecutor,as_completed
import numpy as np,pandas as pd
from astropy.io import fits
ROOT=Path('/home/bahareh/ULTIMATE'); OUT=Path(__file__).resolve().parent
META=ROOT/'analysis_results/ml_feasibility_20261027/expansion/galaxy_partitions.csv'
KEEP=['LSST_g','2MASS_J','2MASS_Ks']; PHYSICAL=['dustmass','stellarmass','stellarage','stellarmetallicity']
GRID={'NAXIS':2,'NAXIS1':1600,'NAXIS2':1600,'CDELT1':100,'CDELT2':100,'CUNIT1':'pc','CUNIT2':'pc','CRPIX1':800.5,'CRPIX2':800.5,'CRVAL1':0.,'CRVAL2':0.}

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()

def sources():
 states={}
 for folder in ['TNG50_SKIRT_DR1_extra','TNG50_SKIRT_DR1_ml_expansion']:
  p=ROOT/'data'/folder
  state=json.loads((p/'download_state.json').read_text())
  for sid,rec in state['galaxies'].items():states[int(sid)]={**rec,'path':p/f'TNG50_DR1_{sid}.tar.gz'}
 old=pd.read_csv(ROOT/'analysis_results/multigalaxy_morphology_20261027/archive_inventory.csv').set_index('subhalo_id').loc[294866]
 states[294866]={'path':ROOT/old.path,'bytes':int(old.bytes),'sha256':old.sha256,'gzip_CRC':'passed','status':'verified','tar_read':'passed','mtime_ns':int(old.mtime_ns)}
 return states

def integrity(sid,rec,partition):
 p=rec['path']; st=p.stat(); d=sha(p)
 row=dict(subhalo_id=sid,partition=partition,path=str(p.relative_to(ROOT)),bytes=st.st_size,mtime_ns=st.st_mtime_ns,sha256=d,recorded_sha256=rec['sha256'],sha_matches=d==rec['sha256'],size_matches=st.st_size==rec['bytes'],mtime_matches=st.st_mtime_ns==rec.get('mtime_ns'),recorded_status=rec.get('status'),recorded_gzip_CRC=rec.get('gzip_CRC'),recorded_tar_read=rec.get('tar_read'),sealed_final=partition=='final_test',science_opened=False,CRC_evidence='Inherited downloader CRC/tar verification; current compressed SHA256 and byte length identical')
 assert row['sha_matches'] and row['size_matches'] and rec['gzip_CRC']=='passed'
 (OUT/'integrity'/f'{sid}.json').write_text(json.dumps(row,indent=2))
 return row

def stream(sid,rec,partition):
 out=OUT/'cache'/str(sid);out.mkdir(parents=True,exist_ok=True)
 if (out/'complete.json').exists():return json.loads((out/'complete.json').read_text())
 assert partition!='final_test' or (OUT.parent/'FINAL_PROTOCOL_FROZEN.json').exists(), 'final science sealed'
 print('START',sid,partition,flush=True)
 row=integrity(sid,rec,partition)
 inv=[];phys=[];cache={f'O{i}':{} for i in range(1,6)};grids={};bands=set(); identities=set()
 with gzip.open(rec['path'],'rb') as gf:
  with tarfile.open(fileobj=gf,mode='r|') as tf:
   for member in tf:
    assert member.isfile(),f'nonregular {member.name}'
    name=Path(member.name).name;mt=re.fullmatch(r'TNG(\d+)_(O[1-5])_(.+)\.fits',name)
    assert mt and int(mt[1])==sid,name
    view,product=mt[2],mt[3]; band=product.removesuffix('_nodust');isband=band not in PHYSICAL
    scene=('clear' if product.endswith('_nodust') else 'dusty') if isband else 'physical'
    ident=(view,band,scene);assert ident not in identities;identities.add(ident)
    raw=tf.extractfile(member).read();h=fits.Header.fromfile(io.BytesIO(raw));unit=h.get('BUNIT')
    assert all(h.get(k)==v for k,v in GRID.items()),(name,'grid')
    assert h['BITPIX']==-32 and h['SIMPLE'] and h.get('EXTEND') is True
    assert unit==('MJy/sr' if isband else {'dustmass':'Msun/pc2','stellarmass':'Msun/pc2','stellarage':'Gyr','stellarmetallicity':'(dimensionless)'}[band]),(name,unit)
    grid=tuple(h.get(k) for k in GRID)
    if isband:
     bands.add(band);grids[ident]=grid
    item=dict(subhalo_id=sid,partition=partition,view=view,product=product,band=band,scene=scene,unit=unit,nx=h['NAXIS1'],ny=h['NAXIS2'],pixel_pc=h['CDELT1'],member=member.name,member_bytes=member.size,member_sha256=hashlib.sha256(raw).hexdigest(),header_valid=True,grid_valid=True,pixel_validated=band in KEEP+['dustmass'],band_identity_evidence='archive basename/product; analytic FITS has no filter keyword')
    if band in KEEP+['dustmass']:
     with fits.open(io.BytesIO(raw),memmap=False) as hd:
      hd.verify('exception');a=hd[0].data
      minimum=float(a.min());maximum=float(a.max());finite=bool(np.isfinite(a).all());tol=1e-10*max(maximum,1.) if band=='dustmass' else 0.
      assert finite and minimum>=-tol,(name,minimum,maximum)
      crop=a[400:1200,400:1200].astype('f4')
      item.update(finite=finite,minimum=minimum,maximum=maximum,negative_fraction=float(np.mean(a<0)),roundoff_tolerance=tol,field_sum=float(a.sum(dtype=float)))
      if band=='dustmass':
       cache[view]['dust']=crop
       phys.append(dict(subhalo_id=sid,partition=partition,view=view,product=band,field_mass_Msun=float(a.sum(dtype=float)*10000),crop_mass_Msun=float(crop.sum(dtype=float)*10000),zero_projected_dust=bool(np.all(a==0)),minimum=minimum,negative_fraction=float(np.mean(a<0))))
      else:cache[view][f'{scene}_{band}']=crop
    inv.append(item)
  while gf.read(8*1024**2):pass
 assert len(inv)==240 and len(bands)==22
 expected={(v,b,s) for v in cache for b in bands for s in ['dusty','clear']}
 assert expected=={i for i in identities if i[2]!='physical'}
 assert all(grids[(v,b,'dusty')]==grids[(v,b,'clear')] for v,b,s in expected)
 assert {(v,b,'physical') for v in cache for b in PHYSICAL}=={i for i in identities if i[2]=='physical'}
 expected_keys={f'{s}_{b}' for s in ['dusty','clear'] for b in KEEP}|{'dust'}
 for v,images in cache.items():
  assert set(images)==expected_keys and all(a.shape==(800,800) for a in images.values())
  temp=out/f'{v}.tmp.npz';np.savez_compressed(temp,**images);temp.replace(out/f'{v}.npz')
 pd.DataFrame(inv).to_csv(out/'fits.csv',index=False);pd.DataFrame(phys).to_csv(out/'physical.csv',index=False)
 row.update(science_opened=True,header_members=240,bands=sorted(bands),complete_pairing=True,current_gzip_CRC='passed',pixel_arrays_validated=35,cache_shape=[800,800],pixel_pc=100,crop=[400,1200,400,1200],CRC_evidence='Current stream consumed to gzip EOF/trailer; inherited unchanged compressed hash also matched')
 (out/'complete.json').write_text(json.dumps(row,indent=2));print('COMPLETE',sid,flush=True)
 return row

def aggregate(meta):
 records=[];avail=[];invs=[];phys=[]
 for r in meta.to_dict('records'):
  sid=int(r['subhalo_id']);p=OUT/'integrity'/f'{sid}.json';c=OUT/'cache'/str(sid)/'complete.json'
  rec=json.loads(c.read_text()) if c.exists() else json.loads(p.read_text()) if p.exists() else None
  if rec:records.append(rec)
  r.update(archive_integrity_verified=rec is not None,cache_complete=c.exists(),sealed_final=r['partition']=='final_test');avail.append(r)
  if c.exists():
   invs.append(pd.read_csv(c.parent/'fits.csv'));phys.append(pd.read_csv(c.parent/'physical.csv'))
 pd.DataFrame(records).to_csv(OUT/'archive_inventory.csv',index=False)
 pd.DataFrame(avail).to_csv(OUT/'available_galaxies.csv',index=False)
 if invs:pd.concat(invs,ignore_index=True).to_csv(OUT/'fits_inventory.csv',index=False)
 if phys:pd.concat(phys,ignore_index=True).to_csv(OUT/'physical_maps.csv',index=False)

def benchmark():
 import sys
 sys.dont_write_bytecode=True
 sys.path.insert(0,str(ROOT/'analysis_results/multigalaxy_morphology_20261027'))
 from morphology import Geometry,measure
 old=pd.read_csv(ROOT/'analysis_results/multigalaxy_morphology_20261027/primary_dust_bias.csv');old=old[(old.subhalo_id==294866)&old.band.isin(KEEP)&(old.setting==12)]
 geom=Geometry(800,.1,12);rows=[]
 for view in [f'O{i}' for i in range(1,6)]:
  with np.load(OUT/'cache/294866'/f'{view}.npz') as z:
   for b in KEEP:
    ref=old[(old.view==view)&(old.band==b)].iloc[0]
    for scene in ['clear','dusty']:
     vals=measure(z[f'{scene}_{b}'],geom)
     for metric in ['R50','C','A','q']:
      previous=float(ref[f'{metric}_{scene}']);cur=vals[metric]
      rows.append(dict(subhalo_id=294866,view=view,band=b,scene=scene,metric=metric,previous=previous,current=cur,difference=cur-previous,within_float32_tolerance=bool(np.isclose(cur,previous,rtol=2e-6,atol=2e-6))))
 pd.DataFrame(rows).to_csv(OUT/'original_R12_benchmark.csv',index=False)
 assert all(x['within_float32_tolerance'] for x in rows)

if __name__=='__main__':
 OUT.mkdir(exist_ok=True);(OUT/'integrity').mkdir(exist_ok=True);(OUT/'cache').mkdir(exist_ok=True)
 meta=pd.read_csv(META);assert meta.partition.value_counts().to_dict()=={'development':86,'final_test':20,'validation':14}
 shutil.copyfile(META,OUT/'frozen_galaxy_partitions.csv')
 for folder in ['TNG50_SKIRT_DR1_extra','TNG50_SKIRT_DR1_ml_expansion']:
  for name in ['download_state.json','selection_manifest.json']:
   shutil.copyfile(ROOT/'data'/folder/name,OUT/f'{folder}_{name}')
 shutil.copyfile(ROOT/'data/TNG50_SKIRT_DR1_ml_expansion/download.log',OUT/'downloader_completed_snapshot.log')
 states=sources();assert set(states)==set(meta.subhalo_id)
 parts=dict(zip(meta.subhalo_id,meta.partition))
 newdev=[int(r.subhalo_id) for r in meta.itertuples() if r.partition=='development' and r.provenance!='existing'][:3]
 gate=[294866]+newdev
 failures=[]
 for sid in gate:stream(sid,states[sid],parts[sid]);aggregate(meta)
 benchmark();(OUT/'development_gate.json').write_text(json.dumps(dict(passed=True,galaxies=gate,benchmark='original_R12_benchmark.csv',final_science_opened=False),indent=2));print('GATE PASSED',gate,flush=True)
 def work(sid):
  return integrity(sid,states[sid],parts[sid]) if parts[sid]=='final_test' else stream(sid,states[sid],parts[sid])
 with ThreadPoolExecutor(max_workers=2) as pool:
  futures={pool.submit(work,int(s)):int(s) for s in meta.subhalo_id if s not in gate}
  for f in as_completed(futures):
   sid=futures[f]
   try:f.result()
   except Exception as e:
    failures.append(dict(subhalo_id=sid,error=str(e),traceback=traceback.format_exc()));print('FAILED',sid,traceback.format_exc(),flush=True)
   aggregate(meta)
 (OUT/'failures.json').write_text(json.dumps(failures,indent=2));aggregate(meta)
 print('ALL FINISHED failures=',len(failures),flush=True)
