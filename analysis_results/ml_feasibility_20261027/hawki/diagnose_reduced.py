"""Diagnostics on downloaded ESO SODA cutouts; original archive headers retained."""
from pathlib import Path
import os,json
os.environ.setdefault('MPLCONFIGDIR','/tmp/hawki_mpl')
import numpy as np,pandas as pd,sep
from astropy.io import fits
from astropy.wcs import WCS
from astropy.wcs.utils import proj_plane_pixel_scales
from scipy.ndimage import binary_dilation
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=Path(__file__).resolve().parent;rng=np.random.default_rng(9475)
a=fits.getdata(O/'reduced_jan6_image.fits').astype('f4');h=fits.getheader(O/'reduced_jan6_image.fits');var=fits.getdata(O/'reduced_jan6_varmap.fits');weight=fits.getdata(O/'reduced_jan6_weightmap.fits');wcs=WCS(h);scale=float(np.mean(proj_plane_pixel_scales(wcs))*3600);ny,nx=a.shape
base=(~np.isfinite(a))|(~np.isfinite(var))|(var<=0)|(weight<80)
bg=sep.Background(a,mask=base,bw=64,bh=64);sub=a-bg.back();objs,seg=sep.extract(sub,5,err=bg.rms(),mask=base,minarea=8,segmentation_map=True)
yy,xx=np.indices(a.shape);gx,gy=wcs.all_world2pix([[156.96365,-43.90355]],0)[0];galaxy=(xx-gx)**2+(yy-gy)**2<650**2
mask=base|galaxy|binary_dilation(seg>0,iterations=15)|(np.abs(sub)>6*bg.rms());mask[:32]=True;mask[-32:]=True;mask[:,:32]=True;mask[:,-32:]=True
vals=sub[~mask];med=np.median(vals);sig=float(1.4826*np.median(abs(vals-med)));norm=(sub[~mask]-med)/np.sqrt(var[~mask]);corr=[]
for dy,dx in [(0,1),(1,0),(0,2),(2,0),(0,4),(4,0),(0,8),(8,0),(0,16),(16,0)]:
 s1=(slice(0,ny-dy),slice(0,nx-dx));s2=(slice(dy,None),slice(dx,None));ok=~mask[s1]&~mask[s2];c=float(np.mean((sub[s1][ok]-med)*(sub[s2][ok]-med)));corr.append(dict(dx=dx,dy=dy,covariance_ADU2=c,correlation=c/np.var(vals),n_pairs=int(ok.sum())))
ap=[]
for rad in [2,4,8,16,32]:
 Y,X=np.mgrid[-rad:rad+1,-rad:rad+1];disk=X*X+Y*Y<=rad*rad;sums=[];pred=[]
 for iy,ix in rng.integers(40,min(ny,nx)-40,size=(30000,2)):
  sl=(slice(iy-rad,iy+rad+1),slice(ix-rad,ix+rad+1))
  if not mask[sl][disk].any():sums.append(sub[sl][disk].sum());pred.append(np.sqrt(var[sl][disk].sum()))
  if len(sums)>=500:break
 su=np.array(sums);ss=1.4826*np.median(abs(su-np.median(su)));ap.append(dict(radius_pix=rad,radius_arcsec=rad*scale,n_pixels=int(disk.sum()),n_apertures=len(su),sum_robust_sigma_ADU=ss,sum_std_ADU=np.std(su),independent_pixel_prediction=sig*np.sqrt(disk.sum()),median_propagated_sigma_ADU=np.median(pred),noise_ratio_to_pixel=ss/(sig*np.sqrt(disk.sum())),noise_ratio_to_variance=ss/np.median(pred)))
# Candidate identities remain unconfirmed; exclude central galaxy and strong/possibly saturated sources.
pos=np.c_[objs['x'],objs['y']];near=cKDTree(pos).query(pos,k=2)[0][:,1];stars=[];examples=[]
for j,s in enumerate(objs):
 ix,iy=np.rint([s['x'],s['y']]).astype(int)
 if not(24<ix<nx-24 and 24<iy<ny-24) or s['flag'] or near[j]<40 or not(.6<s['a']<7) or s['b']/s['a']<.5 or galaxy[iy,ix] or base[iy,ix]:continue
 cut=sub[iy-15:iy+16,ix-15:ix+16].astype(float);raw=a[iy-15:iy+16,ix-15:ix+16];err=np.sqrt(var[iy-15:iy+16,ix-15:ix+16]);amp=cut.max()
 if raw.max()>15000 or amp<40*bg.globalrms:continue
 Y,X=np.indices(cut.shape)
 def model(t):
  A,cx,cy,ax,ay,beta,theta,b,gx,gy=t;z=0
  for oy in [-1/3,0,1/3]:
   for ox in [-1/3,0,1/3]:
    u=(X+ox-cx)*np.cos(theta)+(Y+oy-cy)*np.sin(theta);v=-(X+ox-cx)*np.sin(theta)+(Y+oy-cy)*np.cos(theta);z=z+A*(1+(u/ax)**2+(v/ay)**2)**(-beta)/9
  return z+b+gx*(X-15)+gy*(Y-15)
 sol=least_squares(lambda t:((model(t)-cut)/err).ravel(),[amp,15,15,3,3,2.5,0,0,0,0],bounds=([amp*.3,13,13,.5,.5,1.15,-np.pi,-5*bg.globalrms,-bg.globalrms,-bg.globalrms],[amp*3,17,17,20,20,12,np.pi,5*bg.globalrms,bg.globalrms,bg.globalrms]),max_nfev=160)
 A,cx,cy,ax,ay,beta,theta,b,gxx,gyy=sol.x;major=max(ax,ay);minor=min(ax,ay);fac=2*np.sqrt(2**(1/beta)-1);fw=fac*np.sqrt(ax*ay);res=mod=model(sol.x);rel=np.sqrt(np.mean((mod-cut)**2))/A;ok=bool(sol.success and 1.5<fw<12 and minor/major>.4 and 1.17<beta<11.8 and rel<.04)
 row=dict(x=ix+cx-15,y=iy+cy-15,accepted=ok,fwhm_circularized_arcsec=fw*scale,fwhm_major_arcsec=major*fac*scale,fwhm_minor_arcsec=minor*fac*scale,q=minor/major,ellipticity=1-minor/major,beta=beta,ee50_circularized_arcsec=np.sqrt(ax*ay)*np.sqrt(.5**(1/(1-beta))-1)*scale,ee80_circularized_arcsec=np.sqrt(ax*ay)*np.sqrt(.2**(1/(1-beta))-1)*scale,relative_rms=rel,peak_snr=A/bg.globalrms)
 stars.append(row)
 if ok and len(examples)<6:examples.append((cut.copy(),mod.copy(),row))
s=pd.DataFrame(stars);s.to_csv(O/'reduced_psf_candidates.csv',index=False);pd.DataFrame(corr).to_csv(O/'reduced_covariance.csv',index=False);pd.DataFrame(ap).to_csv(O/'reduced_aperture_noise.csv',index=False)
keys=['BUNIT','EXPTIME','TEXPTIME','CASUEXPT','PHOTSYS','PHOTZP','PHOTZPER','FLUXCAL','PSF_FWHM','PROCSOFT','QCFLAG','OB_GRADE','ESO DRS STDCRMS','ESO DRS NUMBRMS','ESO DRS MAGNZPTIM','ESO DRS DARKCOR','ESO DRS FLATCOR','ESO PRO DATANCOM','ESO PRO REC1 PARAM5 NAME','ESO PRO REC1 PARAM5 VALUE'];summary={k:h.get(k) for k in keys};summary.update(shape=list(a.shape),pixel_scale_arcsec=scale,mask_fraction=float(mask.mean()),blank_pixel_robust_sigma_ADU=sig,blank_pixel_std_ADU=float(np.std(vals)),median_background_ADU=float(np.median(bg.back()[~base])),normalized_residual_robust_sigma=float(1.4826*np.median(abs(norm-np.median(norm)))),median_sqrt_variance_ADU=float(np.median(np.sqrt(var[~mask]))),weight_min_median_max=[float(np.min(weight)),float(np.median(weight)),float(np.max(weight))],psf_fitted=len(s),psf_accepted=int(s.accepted.sum()))
for c in ['fwhm_circularized_arcsec','q','beta','ee50_circularized_arcsec','ee80_circularized_arcsec']:summary['median_'+c]=float(s[s.accepted][c].median())
for typ in ['image','varmap','weightmap']:
 with fits.open(O/f'reduced_jan6_{typ}.fits',checksum=True) as f:
  summary[typ+'_checksum_valid']=bool(f[0].verify_checksum()==1 and f[0].verify_datasum()==1)
  (O/(typ+'_header.txt')).write_text(repr(f[0].header))
summary['wcs_equal_science_variance']=all(np.isclose(h.get(k),fits.getheader(O/'reduced_jan6_varmap.fits').get(k),rtol=0,atol=1e-10) for k in ['CRVAL1','CRVAL2','CRPIX1','CRPIX2','CD1_1','CD1_2','CD2_1','CD2_2'])
(O/'reduced_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2),flush=True)
fig,axs=plt.subplots(1,3,figsize=(14,5),layout='constrained')
for ax,img,title in zip(axs,[a,weight,np.sqrt(var)],['ESO reduced Ks tile cutout (ADU)','Archive confidence/weight (relative)','Propagated sigma (sqrt variance)']):
 if title.startswith('ESO'):im=ax.imshow(np.arcsinh((img-1984)/10),origin='lower',cmap='gray',vmin=-.5,vmax=5)
 else:im=ax.imshow(img,origin='lower',cmap='viridis',vmin=np.percentile(img,1),vmax=np.percentile(img,99))
 ax.set(title=title,xlabel='Tile x (pixels)',ylabel='Tile y (pixels)');fig.colorbar(im,ax=ax,shrink=.6)
axs[0].scatter(s[s.accepted].x,s[s.accepted].y,s=30,facecolors='none',edgecolors='cyan');fig.suptitle('Official Jan6 HAWK-I reduced product | 0.035 degree-radius cutout');fig.savefig(O/'reduced_overview.png',dpi=170);plt.close(fig)
fig,axs=plt.subplots(max(1,len(examples)),3,figsize=(8,2.2*max(1,len(examples))),layout='constrained',squeeze=False)
for axes,(cut,mod,row) in zip(axs,examples):
 for ax,img,title in zip(axes,[cut,mod,cut-mod],['Reduced source','Integrated Moffat','Residual']):ax.imshow(img,origin='lower',cmap='gray');ax.set_title(title,fontsize=9)
 axes[0].set_ylabel(f"{row['fwhm_circularized_arcsec']:.3f}\" q={row['q']:.2f}")
fig.savefig(O/'reduced_fit_inspection.png',dpi=150);plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(10,4),layout='constrained');t=pd.DataFrame(ap);axs[0].plot(t.radius_pix,t.noise_ratio_to_pixel,'o-',label='Pixel sigma sqrt(N)');axs[0].plot(t.radius_pix,t.noise_ratio_to_variance,'s-',label='Propagated diagonal variance');axs[0].legend();axs[0].set(xlabel='Aperture radius (tile pixels)',ylabel='Measured / predicted aperture noise')
t=pd.DataFrame(corr)
for name,u in t.assign(axis=np.where(t.dx>0,'x','y'),lag=t.dx+t.dy).groupby('axis'):axs[1].plot(u.lag,u.correlation,'o-',label=name)
axs[1].legend();axs[1].set(xlabel='Tile pixel lag',ylabel='Masked reduced-background correlation');fig.savefig(O/'reduced_noise.png',dpi=170);plt.close(fig)
