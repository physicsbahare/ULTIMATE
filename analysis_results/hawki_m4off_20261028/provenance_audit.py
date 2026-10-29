from pathlib import Path
import json,hashlib,warnings
import numpy as np,pandas as pd
from astropy.io import fits
from astropy.wcs import WCS,FITSFixedWarning
from astropy.wcs.utils import proj_plane_pixel_scales
warnings.filterwarnings('ignore',category=FITSFixedWarning)
O=Path(__file__).resolve().parent;R=O.parents[1];rows=[];provenance=[];calrefs=[];sets=[];anc=[]
for p in sorted((R/'data/HAWKI_M4off_2019').glob('*.fits')):
 with fits.open(p,checksum=True) as hd:
  hd.verify('exception');primary=hd[0].header;ids=[v for k,v in primary.items() if k.startswith('PROV')];sets.append(set(ids));assert len(ids)==28 and len(set(ids))==28
  provenance.extend(dict(product=p.name,raw_id=i) for i in ids)
  for k,v in primary.items():
   if 'CAL' in k and k.endswith('NAME'):calrefs.append(dict(product=p.name,keyword=k,reference=v,category=primary.get(k.replace('NAME','CATG'))))
  for ext,h in enumerate(hd):
   assert h.verify_checksum()==1 and h.verify_datasum()==1
   if h.data is None:continue
   w=WCS(h.header);ny,nx=h.shape;xy=np.array([(x,y) for x in np.linspace(50,nx-50,5) for y in np.linspace(50,ny-50,5)]);back=w.all_world2pix(w.all_pix2world(xy,0),0);err=float(np.max(abs(back-xy)));assert err<1e-6
   rows.append(dict(product=p.name,extension=ext,extname=h.name,shape=str(h.shape),BUNIT=h.header.get('BUNIT'),scale_arcsec=float(np.mean(proj_plane_pixel_scales(w))*3600),wcs_roundtrip_max_pixel=err,PROCSOFT=primary.get('PROCSOFT'),mode=primary.get('ESO INS MODE'),GRAAL=primary.get('ESO INS AO OPTI1 NAME'),PRODCATG=primary.get('PRODCATG'),PROG_ID=primary.get('PROG_ID'),DATE_OBS=primary.get('DATE-OBS'),total_header_seconds=primary.get('EXPTIME'),DIT=primary.get('DIT'),NDIT=primary.get('ESO DET NDIT'),PHOTSYS=h.header.get('PHOTSYS'),PHOTZP=h.header.get('PHOTZP'),PHOTZPER=h.header.get('PHOTZPER'),PSF_FWHM_metadata=h.header.get('PSF_FWHM'),QCFLAG_digits=str(primary.get('QCFLAG')).zfill(7),QC_interpretation='flag3: global nonlinear-pixel count warning; not a per-selected-star saturation flag',DET_SATLEVEL=primary.get('ESO DET SATLEVEL')))
assert sets[0]==sets[1]
pd.DataFrame(rows).to_csv(O/'fits_provenance.csv',index=False);pd.DataFrame(provenance).to_csv(O/'raw_provenance_ids.csv',index=False);pd.DataFrame(calrefs).to_csv(O/'calibration_reference_manifest.csv',index=False)
for p in list(O.glob('tile_*_region*.fits'))+list(O.glob('pawprint_*_region*.fits'))+[O/'tile_catalogue.fits']:
 with fits.open(p,checksum=True) as hd:
  hd.verify('exception');anc.append(dict(path=p.name,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),checksums_present=all('CHECKSUM' in h.header for h in hd),checksums_pass=all(h.verify_checksum()==1 and h.verify_datasum()==1 for h in hd),hdus=len(hd)))
assert all(a['checksums_pass'] for a in anc);pd.DataFrame(anc).to_csv(O/'ancillary_integrity.csv',index=False)
print('Input/ancillary integrity, identical28 raw IDs, actual EXTNAME order and WCS grid checks pass')
