"""Read-only archive audit and streamed intrinsic analysis, with compact resumable cache."""
from pathlib import Path
import io,json,tarfile,hashlib,re,time,gzip
import numpy as np,pandas as pd
from astropy.io import fits
from morphology import Geometry,measure
O=Path(__file__).resolve().parent;ROOT=O.parents[1];DATA=ROOT/'data/TNG50_SKIRT_DR1_extra'
DEV=[294866,167418,626287,535051,638950]
GEOM={str(r):Geometry(800,.1,r) for r in [12,20,30]}
GEOM.update({f'offset{v}':Geometry(800,.1,12,v) for v in [-.2,.2]})
KEEP=['LSST_g','2MASS_J','2MASS_Ks']

def gzip_crc(path):
 n=0
 with gzip.open(path,'rb') as f:
  for chunk in iter(lambda:f.read(8*1024**2),b''):n+=len(chunk)
 return n

def valid_pixels(a,band):
 tolerance=1e-10*max(float(np.max(a)),1.) if band in ['dustmass','stellarmass','stellarage','stellarmetallicity'] else 0.
 return bool(np.isfinite(a).all() and np.min(a)>=-tolerance)

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()

def preserve():
 manifest={}
 for d in ['screen_test_20261026','dr1_calibrated_screen_20261026','multiplicative_diagnosis_20261026','spatial_structure_pilot_20261026']:
  for p in (O.parent/d).rglob('*'):
   if p.is_file() and p.suffix in ['.md','.py','.json','.csv','.ipynb','.pdf','.png']:
    manifest[str(p.relative_to(ROOT))]=sha(p)
 dest=O/'previous_results_sha256.json'
 if dest.exists():assert json.loads(dest.read_text())==manifest,'Previous results changed'
 else:dest.write_text(json.dumps(manifest,indent=2))

def run(ids=None):
 selected=pd.read_csv(DATA/'selected_galaxies.csv');state=json.loads((DATA/'download_state.json').read_text())['galaxies']
 cat=np.loadtxt(DATA/'baes24_tng50_skirt_atlas.txt');cols=['subhalo_id','stellar_mass_Msun','gas_mass_Msun','dark_matter_mass_Msun','SFR_Msun_yr','stellar_half_mass_radius_kpc']
 original=pd.DataFrame([cat[cat[:,0]==294866][0]],columns=cols)
 original['log10_stellar_mass']=np.log10(original.stellar_mass_Msun);original['sSFR_yr_inverse']=original.SFR_Msun_yr/original.stellar_mass_Msun
 meta=pd.concat([original,selected],ignore_index=True);meta['subhalo_id']=meta.subhalo_id.astype(int)
 meta['role']=np.where(meta.subhalo_id.isin(DEV),'development','held_out')
 meta.to_csv(O/'galaxy_metadata.csv',index=False)
 preserve()
 for sid in meta.subhalo_id:
  if ids is not None and sid not in ids:continue
  if sid not in DEV:assert json.loads((O/'development_gate.json').read_text())['passed']
  out=O/'cache'/str(sid);out.mkdir(exist_ok=True)
  if (out/'complete.json').exists():print('resume',sid,flush=True);continue
  path=ROOT/'TNG50_SKIRT/downloads/TNG50_DR1_294866.tar.gz' if sid==294866 else DATA/f'TNG50_DR1_{sid}.tar.gz'
  st=path.stat();rec=state.get(str(sid),{});digest=sha(path)
  integrity=dict(subhalo_id=sid,path=str(path.relative_to(ROOT)),bytes=st.st_size,mtime_ns=st.st_mtime_ns,sha256=digest,recorded_status=rec.get('status','original'),recorded_CRC=rec.get('gzip_CRC','not in extra download state'),recorded_tar_read=rec.get('tar_read','not in extra download state'),size_matches=st.st_size==rec.get('bytes',st.st_size),mtime_matches=st.st_mtime_ns==rec.get('mtime_ns',st.st_mtime_ns),sha_matches=digest==rec.get('sha256',digest))
  assert integrity['size_matches'] and integrity['sha_matches']
  inv=[];morph=[];physical=[];atten=[];cache={f'O{i}':{} for i in range(1,6)};prev=None
  print('stream',sid,flush=True)
  with gzip.open(path,'rb') as gzip_stream, tarfile.open(fileobj=gzip_stream,mode='r|') as tf:
   for member in tf:
    if not member.isfile():continue
    name=Path(member.name).name
    mt=re.fullmatch(r'TNG(\d+)_(O[1-5])_(.+)\.fits',name);assert mt and int(mt[1])==sid,name
    view,key=mt[2],mt[3];scene='clear' if key.endswith('_nodust') else 'dusty';band=key.removesuffix('_nodust')
    raw=tf.extractfile(member).read()
    with fits.open(io.BytesIO(raw),memmap=False) as hd:
     hd.verify('exception');h=hd[0].header;a=hd[0].data
     good=a.shape==(1600,1600) and valid_pixels(a,band)
     coord=all(h[k]==v for k,v in {'CDELT1':100,'CDELT2':100,'CUNIT1':'pc','CUNIT2':'pc','CRPIX1':800.5,'CRPIX2':800.5,'CRVAL1':0.,'CRVAL2':0.}.items())
     isband=band not in ['dustmass','stellarmass','stellarage','stellarmetallicity']
     unit=h.get('BUNIT');assert good and coord and (not isband or unit=='MJy/sr'),name
     im=a[400:1200,400:1200].astype(float)
     inv.append(dict(subhalo_id=sid,view=view,product=key,band=band,scene=scene if isband else 'physical',unit=unit,nx=1600,ny=1600,pixel_pc=100,member=member.name,member_sha256=hashlib.sha256(raw).hexdigest(),valid=True,field_sum=float(a.sum(dtype=float)),zero_fraction=float(np.mean(a==0)),negative_fraction=float(np.mean(a<0)),minimum=float(np.min(a))))
     if isband:
      settings=['12','20','30','offset-0.2','offset0.2'] if band in ['LSST_g','2MASS_Ks'] else ['12']
      for setting in settings:
       vals=measure(im,GEOM[setting]);morph.append(dict(subhalo_id=sid,view=view,band=band,scene=scene,setting=setting,**vals,field_flux=float(a.sum(dtype=float))))
      if scene=='dusty':prev=(view,band,im)
      elif prev is not None and prev[:2]==(view,band):
       di=prev[2];mask=GEOM['12'].mask&(im>1e-4*im.max())&(di>0)&(im>0)
       eff=-2.5*np.log10(di[mask]/im[mask]);atten.append(dict(subhalo_id=sid,view=view,band=band,n_valid=int(mask.sum()),negative_Aeff_fraction=float(np.mean(eff<0)) if mask.any() else np.nan,Aeff_median_mag=float(np.median(eff)) if mask.any() else np.nan));prev=None
      if band in KEEP:cache[view][f'{scene}_{band}']=im[200:600,200:600].astype('f4')
     else:
      if band in ['dustmass','stellarmass']:
       assert unit=='Msun/pc2'
       physical.append(dict(subhalo_id=sid,view=view,product=band,field_mass_Msun=float(a.sum(dtype=float)*10000),R12_mass_Msun=float(im[GEOM['12'].mask].sum()*10000),R30_mass_Msun=float(im[GEOM['30'].mask].sum()*10000)))
      if band=='dustmass':cache[view]['dust']=im[200:600,200:600].astype('f4')
   # Tar streaming consumes regular payloads; explicit gzip drain verifies trailer CRC.
   while tf.fileobj.read(8*1024**2):pass
  pd.DataFrame(inv).to_csv(out/'fits.csv',index=False);pd.DataFrame(morph).to_csv(out/'intrinsic.csv',index=False);pd.DataFrame(physical).to_csv(out/'physical.csv',index=False);pd.DataFrame(atten).to_csv(out/'attenuation.csv',index=False)
  bands=set(x['band'] for x in inv if x['scene']=='dusty');assert len(bands)==22 and len(inv)==240
  expected={(v,b,s) for v in cache for b in bands for s in ['dusty','clear']};actual={(x['view'],x['band'],x['scene']) for x in inv if x['scene'] in ['dusty','clear']};assert actual==expected
  for v,c in cache.items():
   assert len(c)==7
   np.savez_compressed(out/f'{v}.npz',**c)
  integrity.update(current_gzip_CRC='passed',CRC_evidence='Independently read through gzip.GzipFile EOF and trailer',current_tar_members=len(inv),bands=sorted(bands),complete_pairing=True)
  (out/'complete.json').write_text(json.dumps(integrity,indent=2));print('complete',sid,len(morph),'morphology rows',flush=True)
 for file,target in [('fits.csv','fits_inventory.csv'),('intrinsic.csv','intrinsic_morphology.csv'),('physical.csv','physical_maps.csv'),('attenuation.csv','effective_attenuation.csv')]:
  parts=[pd.read_csv(O/'cache'/str(s)/file) for s in meta.subhalo_id if (O/'cache'/str(s)/'complete.json').exists()]
  if parts:pd.concat(parts,ignore_index=True).to_csv(O/target,index=False)
 records=[json.loads((O/'cache'/str(s)/'complete.json').read_text()) for s in meta.subhalo_id if (O/'cache'/str(s)/'complete.json').exists()]
 pd.DataFrame(records).to_csv(O/'archive_inventory.csv',index=False)
if __name__=='__main__':
 import sys
 run([int(s) for s in sys.argv[1:]] or None)
