"""Bounded spatial detection and pixel-integrated PSF fits on uploaded images only."""
from pathlib import Path
import os,json,warnings
os.environ.setdefault('MPLCONFIGDIR','/tmp/hawki_m4_mpl')
import numpy as np,pandas as pd,sep
from astropy.io import fits
from astropy.wcs import WCS,FITSFixedWarning
from astropy.wcs.utils import proj_plane_pixel_scales
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from scipy.optimize import least_squares
warnings.filterwarnings('ignore',category=FITSFixedWarning)
O=Path(__file__).resolve().parent;ROOT=O.parents[1];STEP=1024;HALO=64;PEAK_MAX=10000;RAW_MAX=40000

def fit_star(cut,sigma,scale):
 r=cut.shape[0]//2;Y,X=np.indices(cut.shape);amp=float(cut.max());offsets=[-1/3,0,1/3]
 def model(t):
  A,cx,cy,ax,ay,beta,theta,b,gx,gy=t;z=0;ct=np.cos(theta);st=np.sin(theta)
  for oy in offsets:
   for ox in offsets:
    u=(X+ox-cx)*ct+(Y+oy-cy)*st;v=-(X+ox-cx)*st+(Y+oy-cy)*ct;z=z+A*(1+(u/ax)**2+(v/ay)**2)**(-beta)/9
  return z+b+gx*(X-r)+gy*(Y-r)
 init=[amp,r,r,3,3,3,0,0,0,0];lo=[amp*.3,r-2,r-2,.5,.5,1.15,-np.pi,-10*sigma,-sigma,-sigma];hi=[amp*3,r+2,r+2,20,20,15,np.pi,10*sigma,sigma,sigma]
 sol=least_squares(lambda t:((model(t)-cut)/sigma).ravel(),init,bounds=(lo,hi),max_nfev=130)
 A,cx,cy,ax,ay,beta,theta,b,gx,gy=sol.x;fac=2*np.sqrt(2**(1/beta)-1);fw=fac*np.sqrt(ax*ay)*scale;q=min(ax,ay)/max(ax,ay);rel=float(np.sqrt(np.mean((model(sol.x)-cut)**2))/A)
 return dict(dx=cx-r,dy=cy-r,amplitude=A,alpha_x_pixels=ax,alpha_y_pixels=ay,beta=beta,theta_rad=theta,q=q,ellipticity=1-q,fwhm_arcsec=fw,major_arcsec=fac*max(ax,ay)*scale,minor_arcsec=fac*min(ax,ay)*scale,background=b,background_dx=gx,background_dy=gy,relative_rms=rel,solver_success=bool(sol.success),accepted=bool(sol.success and .15<fw<.75 and q>.4 and 1.2<beta<14.8 and rel<.04),model_R50_infinite_elliptical_circularized_arcsec=np.sqrt(ax*ay)*np.sqrt(2**(1/(beta-1))-1)*scale),model(sol.x)

def run():
 allrows=[];profiles=[];aud=[];snapshots={};manifest=[]
 for path in sorted((ROOT/'data/HAWKI_M4off_2019').glob('*.fits')):
  with fits.open(path,memmap=True) as hd:
   for ext,hdu in enumerate(hd):
    if hdu.data is None:continue
    product='tile' if len(hd)==1 else 'pawprint';field=product+str(ext);dest=O/(field+'_stars.csv');raw=hdu.data;ny,nx=raw.shape;w=WCS(hdu.header);scale=float(np.mean(proj_plane_pixel_scales(w))*3600)
    manifest.append(dict(field=field,product=product,extension=ext,extname=hdu.name,path=str(path.relative_to(ROOT)),ny=ny,nx=nx,pixel_scale_arcsec=scale))
    if dest.exists():continue
    rows=[];ee=[];dets=[];stamps=[]
    for by,y0 in enumerate(range(0,ny,STEP)):
     for bx,x0 in enumerate(range(0,nx,STEP)):
      x1=min(nx,x0+STEP);y1=min(ny,y0+STEP);sx=max(0,x0-HALO);sy=max(0,y0-HALO);ex=min(nx,x1+HALO);ey=min(ny,y1+HALO)
      a=np.array(raw[sy:ey,sx:ex],dtype='f4',order='C');finite=np.isfinite(a);fill=(ndi.maximum_filter(a,size=3)-ndi.minimum_filter(a,size=3))<1e-5;mask=~finite|ndi.binary_dilation(fill,iterations=2)
      if (~mask).mean()<.03:continue
      bg=sep.Background(a,mask=mask,bw=128,bh=128,fw=3,fh=3);sub=a-bg.back();rmsmap=bg.rms();rms=float(bg.globalrms)
      if not np.isfinite(rms) or rms<=0:continue
      obs=sep.extract(sub,5,err=np.maximum(rmsmap,rms*.3),mask=mask,minarea=6,deblend_cont=.005);pos=np.c_[obs['x'],obs['y']]
      if len(obs)<2:continue
      near=cKDTree(pos).query(pos,k=2)[0][:,1];pool=[]
      for j,t in enumerate(obs):
       x=float(t['x'])+sx;y=float(t['y'])+sy;ix=int(round(t['x']));iy=int(round(t['y']));peak=float(t['peak']);q=t['b']/t['a']
       if not(x0<=x<x1 and y0<=y<y1):continue
       dets.append(dict(field=field,x=x,y=y,peak=peak,sep_flag=int(t['flag']),nearest_arcsec=near[j]*scale))
       if not(28<ix<a.shape[1]-28 and 28<iy<a.shape[0]-28) or t['flag'] or near[j]*scale<2.5 or not(.7<t['a']<6) or q<.4 or mask[iy,ix]:continue
       if peak<60*rms or peak>PEAK_MAX or a[iy-3:iy+4,ix-3:ix+4].max()>RAW_MAX:continue
       pool.append((j,x,y,ix,iy,peak))
      # Spatially balanced bounded sample; no narrow roundness or FWHM-locus cut.
      pool=sorted(pool,key=lambda t:t[-1],reverse=True)[:6]
      aud.append(dict(field=field,bx=bx,by=by,n_detected=len(obs),n_candidates=len(pool),background=float(np.median(bg.back())),sigma=rms,usable_fraction=float((~mask).mean())))
      for j,x,y,ix,iy,peak in pool:
       cut=sub[iy-20:iy+21,ix-20:ix+21].astype(float)
       try:row,model=fit_star(cut,rms,scale)
       except Exception as er:rows.append(dict(field=field,x=x,y=y,bx=bx,by=by,accepted=False,error=repr(er)));continue
       xx=ix+sx+row['dx'];yy=iy+sy+row['dy'];ra,dec=w.all_pix2world([[xx,yy]],0)[0];row.update(field=field,product=product,extension=ext,source_local_id=len(rows),x=xx,y=yy,bx=bx,by=by,ra=ra,dec=dec,scale_arcsec=scale,peak_snr=row['amplitude']/rms,raw_peak=float(a[iy,ix]),nearest_arcsec=near[j]*scale,local_sigma_ADU=rms,wing_isolated=bool(near[j]*scale>=4.5))
       # Direct circular EE, finite reference radius, with independently estimated annular sky.
       large=sub[iy-26:iy+27,ix-26:ix+27].astype('f8');Y,X=np.indices(large.shape);cx=26+row['dx'];cy=26+row['dy'];rr=np.hypot(X-cx,Y-cy)*scale;ann=(rr>=1.8)&(rr<2.5);sky=float(np.median(large[ann]));sigsky=float(1.4826*np.median(abs(large[ann]-sky)));image=np.ascontiguousarray(large-sky)
       radii=np.array([.1,.15,.2,.25,.3,.4,.5,.7,1.,1.5,2.]);flux,_,_=sep.sum_circle(image,np.repeat(cx,len(radii)),np.repeat(cy,len(radii)),radii/scale,subpix=5);ref=float(flux[-1]);ref15=float(flux[-2]);row.update(annular_sky_ADU=sky,annular_sigma_ADU=sigsky,flux_R2_ADU=ref,flux_R15_ADU=ref15,annular_contamination_ratio=sigsky/rms)
       for frac in [.5,.8]:
        row[f'empirical_R{int(frac*100)}_R2_arcsec']=float(np.interp(frac*ref,flux,radii)) if ref>0 and np.all(np.diff(flux)>=0) else np.nan
        row[f'empirical_R{int(frac*100)}_R15_arcsec']=float(np.interp(frac*ref15,flux[:-1],radii[:-1])) if ref15>0 and np.all(np.diff(flux[:-1])>=0) else np.nan
       for r,f in zip(radii,flux):ee.append(dict(field=field,source_local_id=row['source_local_id'],radius_arcsec=r,flux_ADU=f,EE_R2=f/ref if ref>0 else np.nan,EE_R15=f/ref15 if ref15>0 else np.nan))
       rows.append(row)
       if row['accepted']:stamps.append(dict(source_local_id=row['source_local_id'],cut=large.astype('f4'),model=model.astype('f4')))
    pd.DataFrame(rows).to_csv(dest,index=False);pd.DataFrame(ee).to_csv(O/(field+'_profiles.csv'),index=False);pd.DataFrame(dets).to_csv(O/(field+'_detections.csv.gz'),index=False)
    np.savez_compressed(O/(field+'_stamps.npz'),ids=np.array([s['source_local_id'] for s in stamps]),cuts=np.array([s['cut'] for s in stamps]),models=np.array([s['model'] for s in stamps]))
    print(field,'fitted',len(rows),'accepted',sum(r['accepted'] for r in rows),flush=True)
    pd.DataFrame(aud).to_csv(O/'detection_spatial_audit.csv',index=False)
 pd.DataFrame(manifest).to_csv(O/'image_planes.csv',index=False)
 pd.concat([pd.read_csv(O/(r['field']+'_stars.csv')) for r in manifest],ignore_index=True).to_csv(O/'psf_fits.csv',index=False)
 pd.concat([pd.read_csv(O/(r['field']+'_profiles.csv')) for r in manifest],ignore_index=True).to_csv(O/'empirical_profiles.csv',index=False)
 print('PSF extraction complete',flush=True)
if __name__=='__main__':run()
