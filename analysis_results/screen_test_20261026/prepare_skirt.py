"""Read selected archive members, crop identically and cache structured images. No raw extraction."""
from pathlib import Path
import io,tarfile,json,hashlib
import numpy as np
from astropy.io import fits
O=Path(__file__).resolve().parent; R=O.parents[1]; C=O/'input_cache'; C.mkdir(exist_ok=True)
bands={'GALEX_FUV':.153,'GALEX_NUV':.231,'LSST_u':.367,'LSST_g':.482,'LSST_r':.622,'LSST_i':.754,'LSST_z':.869,'LSST_y':.971,'Euclid_Y':1.08,'2MASS_J':1.235,'2MASS_H':1.662,'2MASS_Ks':2.159,'WISE_W1':3.4}
need={f'TNG294866_O{i}_{b}{s}.fits' for i in range(1,6) for b in bands for s in ['', '_nodust']}
need|={f'TNG294866_O{i}_dustmass.fits' for i in range(1,6)}
manifest=[]; data={f'O{i}':{} for i in range(1,6)}
with tarfile.open(R/'TNG50_SKIRT/downloads/TNG50_DR1_294866.tar.gz','r|gz') as archive:
 for entry in archive:
  name=Path(entry.name).name
  if name not in need: continue
  raw=archive.extractfile(entry).read(); ori=name.split('_')[1]; key=name.split(ori+'_',1)[1][:-5]
  with fits.open(io.BytesIO(raw)) as h:
   h.verify('exception'); a=h[0].data; header=h[0].header
   assert a.shape==(1600,1600) and np.isfinite(a).all() and (a>=0).all()
   assert header['CDELT1']==header['CDELT2']==100 and header['CUNIT1']==header['CUNIT2']=='pc'
   assert header['BUNIT']==('Msun/pc2' if key=='dustmass' else 'MJy/sr')
   data[ori][key]=np.asarray(a[400:1200,400:1200],dtype=np.float32)
  manifest.append({'archive_member':entry.name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'crop_native_pixels':'[400:1200,400:1200]','cropped_field_kpc':80})
assert len(manifest)==len(need)==135
for ori,d in data.items():
 dusty=np.stack([d[b] for b in bands]); clear=np.stack([d[b+'_nodust'] for b in bands]); dust=d['dustmass']
 np.savez_compressed(C/f'{ori}_structured_broadbands.npz',dusty=dusty,clear=clear,dust=dust,wave_um=np.array(list(bands.values())),band=np.array(list(bands)))
 print(ori,dusty.shape,flush=True)
(O/'sources/skirt_stream_manifest.json').write_text(json.dumps(manifest,indent=2))
