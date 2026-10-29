"""Same PSF estimator and finite-aperture EE on existing NGC3256 products, read only."""
from pathlib import Path
import numpy as np,pandas as pd,sep
from astropy.io import fits
from astropy.wcs import WCS
from astropy.wcs.utils import proj_plane_pixel_scales
from measure_psf import fit_star
from analysis_refinements import crossing
O=Path(__file__).resolve().parent;P=O.parent/'ml_feasibility_20261027/hawki';old=pd.read_csv(P/'catalogue_crossmatches.csv');old=old[old.accepted].copy();rows=[];profiles=[]
with fits.open(P/'reduced_jan6_image.fits') as h:
 image=h[0].data;scale=float(np.mean(proj_plane_pixel_scales(WCS(h[0].header)))*3600)
 for i,t in old.iterrows():
  x=int(round(t.x));y=int(round(t.y))
  if not(27<x<image.shape[1]-27 and 27<y<image.shape[0]-27):continue
  large=image[y-26:y+27,x-26:x+27].astype(float);Y,X=np.indices(large.shape);rr=np.hypot(X-26,Y-26)*scale;ann=(rr>1.8)&(rr<2.5);sky=np.median(large[ann]);sigma=1.4826*np.median(abs(large[ann]-sky));cut=large[6:47,6:47]-sky
  fit,_=fit_star(cut,sigma,scale);fit.update(source_id=i,stellar_2mass=bool(t.positional_match and t.catalogue_quality_pass),x=x+fit['dx'],y=y+fit['dy']);cx=26+fit['dx'];cy=26+fit['dy'];rr=np.hypot(X-cx,Y-cy)*scale;ann=(rr>1.8)&(rr<2.5);sky=np.median(large[ann]);r=np.array([.1,.15,.2,.25,.3,.4,.5,.7,1,1.5,2]);flux,_,_=sep.sum_circle(np.ascontiguousarray(large-sky),np.repeat(cx,len(r)),np.repeat(cy,len(r)),r/scale,subpix=5)
  for frac in [.5,.8]:fit[f'empirical_R{int(frac*100)}_R2_arcsec']=crossing(r,flux,frac*flux[-1])
  rows.append(fit)
  profiles.extend(dict(source_id=i,stellar_2mass=fit['stellar_2mass'],radius_arcsec=ra,EE_R2=f/flux[-1]) for ra,f in zip(r,flux))
pd.DataFrame(rows).to_csv(O/'ngc3256_same_estimator.csv',index=False);pd.DataFrame(profiles).to_csv(O/'ngc3256_empirical_profiles.csv',index=False);print('NGC same-estimator fits',len(rows),'2MASS stars',sum(x['stellar_2mass'] for x in rows))
