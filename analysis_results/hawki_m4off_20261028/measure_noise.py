"""Crowding-aware reduced-background measurements; no pure detector-noise claim."""
from pathlib import Path
import os,warnings,json
os.environ.setdefault('MPLCONFIGDIR','/tmp/hawki_m4_mpl')
import numpy as np,pandas as pd,sep
from scipy import ndimage as ndi,signal
from astropy.io import fits
from astropy.wcs import WCS,FITSFixedWarning
from astropy.wcs.utils import proj_plane_pixel_scales
warnings.filterwarnings('ignore',category=FITSFixedWarning)
O=Path(__file__).resolve().parent;ROOT=O.parents[1];rng=np.random.default_rng(10361);rows=[];cov=[];ap=[];samples=[];wcschecks=[]

def characterize(a,field,region,scale,base=None,var=None,kind='grid',mesh=128):
 a=np.array(a,dtype='f4',order='C');ny,nx=a.shape
 if base is None:base=np.zeros(a.shape,bool)
 base=base|~np.isfinite(a)|((ndi.maximum_filter(a,size=3)-ndi.minimum_filter(a,size=3))<1e-5)
 if (~base).mean()<.3:return
 bg=sep.Background(a,mask=base,bw=mesh,bh=mesh);sub=a-bg.back();rms=float(bg.globalrms)
 if rms<=0:return
 obs,seg=sep.extract(sub,3,err=np.maximum(bg.rms(),rms*.3),mask=base,minarea=4,segmentation_map=True,deblend_cont=.005)
 for dilation in [8,12,20]:
  mask=base|ndi.binary_dilation(seg>0,iterations=dilation)|(abs(sub)>6*rms);mask[:35]=True;mask[-35:]=True;mask[:,:35]=True;mask[:,-35:]=True
  v=sub[~mask].astype(float)
  if len(v)<1000:continue
  med=float(np.median(v));sig=float(1.4826*np.median(abs(v-med)));std=float(np.std(v));variance=float(np.var(v));q16,q84=np.quantile(v,[.16,.84]);skew=float(np.mean(((v-v.mean())/std)**3))
  row=dict(field=field,region=region,kind=kind,mesh=mesh,dilation_pixels=dilation,scale_arcsec=scale,mask_fraction=mask.mean(),n_blank=len(v),pixel_MAD_ADU=sig,pixel_std_ADU=std,background_median_ADU=float(np.median(bg.back()[~base])),pixel_skew=skew,tail_asymmetry=(q84-med)/(med-q16),median_sqrt_variance_ADU=float(np.median(np.sqrt(var[~mask]))) if var is not None else np.nan)
  rows.append(row)
  for dy,dx in [(0,1),(1,0),(1,1),(0,2),(2,0),(0,4),(4,0),(0,8),(8,0),(0,16),(16,0),(0,32),(32,0)]:
   aa=(slice(0,ny-dy),slice(0,nx-dx));bb=(slice(dy,None),slice(dx,None));ok=~mask[aa]&~mask[bb];u=sub[aa][ok].astype(float);v2=sub[bb][ok].astype(float)
   cv=float(np.mean((u-med)*(v2-med)));cov.append(dict(field=field,region=region,kind=kind,mesh=mesh,dilation_pixels=dilation,dx=dx,dy=dy,covariance_ADU2=cv,correlation=cv/variance,n_pairs=int(ok.sum())))
  for rad in [2,4,8,16,32]:
   Y,X=np.mgrid[-rad:rad+1,-rad:rad+1];disk=(X*X+Y*Y<=rad*rad).astype(float);count=signal.fftconvolve(mask.astype(float),disk,mode='same');eligible=count<.1;eligible[:rad+1]=False;eligible[-rad-1:]=False;eligible[:,:rad+1]=False;eligible[:,-rad-1:]=False;iy,ix=np.where(eligible)
   if len(ix)<30:ap.append(dict(field=field,region=region,kind=kind,mesh=mesh,dilation_pixels=dilation,radius_pixels=rad,n_centres=len(ix),status='insufficient_unmasked_apertures'));continue
   choice=rng.choice(len(ix),min(500,len(ix)),replace=False);iy=iy[choice];ix=ix[choice];sums=signal.fftconvolve(sub-med,disk,mode='same')[iy,ix];smad=float(1.4826*np.median(abs(sums-np.median(sums))));pred=np.sqrt(signal.fftconvolve(var,disk,mode='same')[iy,ix]) if var is not None else None
   entry=dict(field=field,region=region,kind=kind,mesh=mesh,dilation_pixels=dilation,radius_pixels=rad,radius_arcsec=rad*scale,n_pixels=int(disk.sum()),n_centres=len(ix),sigma_sum_MAD_ADU=smad,sigma_sum_std_ADU=float(sums.std()),ratio_pixel_MAD=smad/(sig*np.sqrt(disk.sum())),ratio_pixel_std=float(sums.std()/(std*np.sqrt(disk.sum()))),ratio_diagonal_variance=smad/float(np.median(pred)) if pred is not None else np.nan,median_sum_ADU=float(np.median(sums)),status='ok');ap.append(entry)
   if dilation==12 and mesh==128:
    samples.extend(dict(field=field,region=region,kind=kind,radius_pixels=rad,x=int(x),y=int(y),normalized_sum=float(z/(sig*np.sqrt(disk.sum())))) for x,y,z in zip(ix,iy,sums))

def run():
 for p in sorted((ROOT/'data/HAWKI_M4off_2019').glob('*.fits')):
  with fits.open(p,memmap=True) as h:
   for ext,plane in enumerate(h):
    if plane.data is None:continue
    product='tile' if len(h)==1 else 'pawprint';field=product+str(ext);w=WCS(plane.header);scale=float(np.mean(proj_plane_pixel_scales(w))*3600);ny,nx=plane.shape
    for gy,fy in enumerate([.2,.5,.8]):
     for gx,fx in enumerate([.2,.5,.8]):
      x=int(nx*fx);y=int(ny*fy);a=plane.data[y-384:y+384,x-384:x+384];characterize(a,field,f'grid{gx}{gy}',scale)
      if gx==1 and gy==1:characterize(a,field,'grid11',scale,mesh=256)
    # Ancillary comparisons on exact science grid, with confidence and positive variance.
    for j in range(4):
     vp=O/f'{product}_variance_region{j}.fits';cp=O/f'{product}_confidence_region{j}.fits'
     with fits.open(vp) as vh,fits.open(cp) as ch:
      vext=0 if product=='tile' else ext;v=vh[vext].data.astype(float);conf=ch[vext].data.astype(float);vw=WCS(vh[vext].header);yy,xx=np.indices(v.shape);world=vw.all_pix2world(np.c_[xx.ravel(),yy.ravel()],0);coord=w.all_world2pix(world,0);delta=float(np.max(abs(coord-np.rint(coord))));wcschecks.append(dict(field=field,region=j,max_fractional_pixel=delta,shape=str(v.shape),variance_BUNIT=vh[vext].header.get('BUNIT')))
      assert delta<1e-5
      sx,sy=np.rint(coord).astype(int).T
      assert sx.min()>=0 and sy.min()>=0 and sx.max()<nx and sy.max()<ny
      science=plane.data[sy,sx].reshape(v.shape);base=~np.isfinite(v)|(v<=0)|~np.isfinite(conf)|(conf<=0)|(conf<.6*np.median(conf[conf>0]))
      characterize(science,field,f'ancillary{j}',scale,base=base,var=v,kind='ancillary')
    print('Noise complete',field,flush=True)
    for name,data in [('background_regions',rows),('background_covariance',cov),('aperture_noise',ap),('aperture_samples',samples),('ancillary_grid_checks',wcschecks)]:pd.DataFrame(data).to_csv(O/(name+'.csv'),index=False)
 print('Noise characterization complete',flush=True)
if __name__=='__main__':run()
