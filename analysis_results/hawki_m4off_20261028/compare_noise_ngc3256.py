from pathlib import Path
import numpy as np,pandas as pd
from astropy.io import fits
from astropy.wcs import WCS
from astropy.wcs.utils import proj_plane_pixel_scales
import measure_noise as n
O=n.O;P=O.parent/'ml_feasibility_20261027/hawki'
with fits.open(P/'reduced_jan6_image.fits') as h,fits.open(P/'reduced_jan6_varmap.fits') as v,fits.open(P/'reduced_jan6_weightmap.fits') as c:
 image=h[0].data;var=v[0].data;conf=c[0].data;w=WCS(h[0].header);scale=float(np.mean(proj_plane_pixel_scales(w))*3600);gx,gy=w.all_world2pix([[156.96365,-43.90355]],0)[0];ny,nx=image.shape
 for j,(fx,fy) in enumerate([(.25,.25),(.75,.25),(.25,.75),(.75,.75)]):
  x=int(nx*fx);y=int(ny*fy);sl=(slice(y-384,y+384),slice(x-384,x+384));a=image[sl];vv=var[sl];cc=conf[sl];Y,X=np.indices(a.shape);galaxy=(X+x-384-gx)**2+(Y+y-384-gy)**2<650**2;base=galaxy|(vv<=0)|(cc<=0)|(cc<.6*np.median(cc[cc>0]));n.characterize(a,'NGC3256_tile',f'comparison{j}',scale,base=base,var=vv,kind='same_operator')
for name,rows in [('ngc_noise_background',n.rows),('ngc_noise_covariance',n.cov),('ngc_noise_apertures',n.ap)]:pd.DataFrame(rows).to_csv(O/(name+'.csv'),index=False)
print('NGC noise measured with same mesh128 /3sigma/mask-growth operator, galaxy explicitly masked')
