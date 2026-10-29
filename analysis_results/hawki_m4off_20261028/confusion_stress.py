"""Faint-catalogue-mask sensitivity on the ancillary tile patches."""
from pathlib import Path
import numpy as np,pandas as pd
from scipy import ndimage as ndi
from astropy.io import fits
from astropy.wcs import WCS
import measure_noise as n
O=n.O
with fits.open(O/'tile_catalogue.fits') as h:
 c=h[1].data;xy=np.c_[c['X_coordinate']-1,c['Y_coordinate']-1];use=c['Classification']!=0;xy=xy[use]
path=next((O.parents[1]/'data/HAWKI_M4off_2019').glob('*26.018.fits'))
with fits.open(path) as h:
 w=WCS(h[0].header);science=h[0].data
 for j in range(4):
  with fits.open(O/f'tile_variance_region{j}.fits') as vh,fits.open(O/f'tile_confidence_region{j}.fits') as ch:
   var=vh[0].data.astype(float);conf=ch[0].data;vW=WCS(vh[0].header);ny,nx=var.shape;YY,XX=np.indices(var.shape);coords=w.all_world2pix(vW.all_pix2world(np.c_[XX.ravel(),YY.ravel()],0),0);sx,sy=np.rint(coords).astype(int).T;a=science[sy,sx].reshape(var.shape)
   local=xy-np.array([sx[0],sy[0]]);ix,iy=np.rint(local).astype(int).T;ok=(ix>=0)&(ix<nx)&(iy>=0)&(iy<ny);points=np.zeros(var.shape,bool);points[iy[ok],ix[ok]]=True
   positive=conf[conf>0];base=(var<=0)|(conf<.6*np.median(positive))|ndi.binary_dilation(points,iterations=8)
   n.characterize(a,'tile0',f'catalogue{j}',.106556,base=base,var=var,kind='catalogue_augmented')
for name,rows in [('confusion_background',n.rows),('confusion_covariance',n.cov),('confusion_apertures',n.ap)]:pd.DataFrame(rows).to_csv(O/(name+'.csv'),index=False)
print('Faint catalogue mask stress complete')
