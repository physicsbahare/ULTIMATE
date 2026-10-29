"""Read-only raw diagnostics. Run with phd Python; outputs only beside script."""
from pathlib import Path
import os,json,warnings,sys,shutil
os.environ.setdefault('MPLCONFIGDIR','/tmp/hawki_mpl')
import numpy as np,pandas as pd,sep
from astropy.io import fits
from astropy.wcs import WCS
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
from scipy.ndimage import binary_dilation
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
warnings.filterwarnings('ignore',message='Card is too long')
R=Path('/home/bahareh/ULTIMATE');O=Path(__file__).resolve().parent
rng=np.random.default_rng(9475); stars=[];noise=[];aps=[];covs=[];examples=[];aud=[]
scale=.10643
files=sorted((R/'HAWKI_GRAAL/NGC3256').glob('*.fits'))
# Representative first/last exposure per night; previous inspection covers all22 circularly.
files=[files[0],files[13],files[14],files[-1]]
for p in files:
 with fits.open(p,mode='readonly',memmap=False) as hd:
  for ext in hd[1:5]:
   print(p.name,ext.name,'background',flush=True);a=np.array(ext.data,dtype='f4',order='C');bg=sep.Background(a,bw=64,bh=64); sub=a-bg.back();rms=float(bg.globalrms)
   objs,seg=sep.extract(sub,5,err=bg.rms(),minarea=8,segmentation_map=True)
   pos=np.c_[objs['x'],objs['y']];near=cKDTree(pos).query(pos,k=2)[0][:,1] if len(pos)>1 else np.zeros(len(pos))
   mask=binary_dilation(seg>0,iterations=12)|(~np.isfinite(sub))|(a>20000)|(np.abs(sub)>6*rms)
   yy,xx=np.indices(a.shape)
   try:
    gx,gy=WCS(ext.header).all_world2pix([[156.96365,-43.90355]],0)[0];mask|=(xx-gx)**2+(yy-gy)**2<750**2
   except Exception:pass
   mask[:32]=True;mask[-32:]=True;mask[:,:32]=True;mask[:,-32:]=True
   vals=sub[~mask].astype(float);med=np.median(vals);sig=1.4826*np.median(abs(vals-med));v=np.var(vals)
   blocks=[]
   for iy in range(32,2016,64):
    for ix in range(32,2016,64):
     m=~mask[iy:iy+64,ix:ix+64]
     if m.mean()>.7:blocks.append(np.median(sub[iy:iy+64,ix:ix+64][m]))
   noise.append(dict(filename=p.name,extension=ext.name,background_raw=np.median(bg.back()),sep_rms=rms,masked_fraction=mask.mean(),blank_pixel_robust_sigma=sig,blank_pixel_std=np.std(vals),residual_64px_tile_median_rms=np.std(blocks),n_blank=len(vals)))
   for dy,dx in [(0,1),(1,0),(0,2),(2,0),(0,4),(4,0),(0,8),(8,0),(0,16),(16,0)]:
    s1=(slice(0,2048-dy),slice(0,2048-dx));s2=(slice(dy,None),slice(dx,None));good=~mask[s1]&~mask[s2];c=np.mean((sub[s1][good]-med)*(sub[s2][good]-med));covs.append(dict(filename=p.name,extension=ext.name,dx=dx,dy=dy,covariance_raw_unit2=c,correlation=c/v,n_pairs=good.sum()))
   for rad in [2,4,8,16]:
    Y,X=np.mgrid[-rad:rad+1,-rad:rad+1];disk=X*X+Y*Y<=rad*rad; sums=[]
    for iy,ix in rng.integers(40,2008,size=(6000,2)):
     sl=(slice(iy-rad,iy+rad+1),slice(ix-rad,ix+rad+1))
     if not mask[sl][disk].any():sums.append(sub[sl][disk].sum())
     if len(sums)>=300:break
    su=np.array(sums);ss=1.4826*np.median(abs(su-np.median(su))) if len(su) else np.nan
    aps.append(dict(filename=p.name,extension=ext.name,radius_pix=rad,n_pixels=disk.sum(),n_apertures=len(sums),sum_robust_sigma=ss,sum_std=np.std(su),independent_pixel_prediction=sig*np.sqrt(disk.sum()),noise_ratio=ss/(sig*np.sqrt(disk.sum()))))
   print(p.name,ext.name,'noise complete',flush=True)
   candidates=[]
   for j,s in enumerate(objs):
    ix,iy=np.rint([s['x'],s['y']]).astype(int)
    if not(24<ix<2024 and 24<iy<2024) or s['flag'] or near[j]<40 or not(1<s['a']<7) or s['b']/s['a']<.5:continue
    if np.isfinite(gx) and (ix-gx)**2+(iy-gy)**2<750**2:continue
    cut=a[iy-15:iy+16,ix-15:ix+16]
    if cut.max()>20000 or sub[iy-15:iy+16,ix-15:ix+16].max()<40*rms:continue
    core=sub[iy-1:iy+2,ix-1:ix+2]
    if core.max()/max(core.sum(),1e-20)>.5:continue
    candidates.append((j,ix,iy))
   # Preserve spatial coverage: maximum one highest-S/N candidate per detector quadrant.
   chosen=[]
   for bx in range(2):
    for by in range(2):
     pool=[c for c in candidates if c[1]//1024==bx and c[2]//1024==by]
     chosen+=sorted(pool,key=lambda c:objs[c[0]]['peak'],reverse=True)[:1]
   print(p.name,ext.name,'fitting',len(chosen),flush=True)
   for j,ix,iy in chosen:
    cut=sub[iy-15:iy+16,ix-15:ix+16].astype(float);Y,X=np.indices(cut.shape);amp=cut.max(); offsets=[-.333333,0,.333333]
    def model(t):
     A,cx,cy,ax,ay,beta,theta,b,gx,gy=t;z=0
     for oy in offsets:
      for ox in offsets:
       u=(X+ox-cx)*np.cos(theta)+(Y+oy-cy)*np.sin(theta);v=-(X+ox-cx)*np.sin(theta)+(Y+oy-cy)*np.cos(theta)
       z=z+A*(1+(u/ax)**2+(v/ay)**2)**(-beta)/9
     return z+b+gx*(X-15)+gy*(Y-15)
    sol=least_squares(lambda t:((model(t)-cut)/rms).ravel(),[amp,15,15,3,3,2.5,0,0,0,0],bounds=([amp*.3,13,13,.5,.5,1.15,-np.pi,-5*rms,-rms,-rms],[amp*3,17,17,20,20,12,np.pi,5*rms,rms,rms]),max_nfev=160)
    A,cx,cy,ax,ay,beta,theta,b,gx,gy=sol.x;major=max(ax,ay);minor=min(ax,ay);q=minor/major;fac=2*np.sqrt(2**(1/beta)-1);fw=fac*np.sqrt(ax*ay);res=(model(sol.x)-cut);rel=np.sqrt(np.mean(res**2))/A
    accepted=bool(sol.success and 1.5<fw<12 and q>.4 and 1.17<beta<11.8 and rel<.04)
    # EE is analytic in elliptical radius rho; semiaxes = alpha_major/minor * rho.
    rho50=np.sqrt(.5**(1/(1-beta))-1);rho80=np.sqrt(.2**(1/(1-beta))-1)
    row=dict(filename=p.name,extension=ext.name,x=ix+cx-15,y=iy+cy-15,accepted=accepted,fwhm_major_arcsec=major*fac*scale,fwhm_minor_arcsec=minor*fac*scale,fwhm_circularized_arcsec=fw*scale,q=q,ellipticity=1-q,beta=beta,ee50_circularized_arcsec=np.sqrt(ax*ay)*rho50*scale,ee80_circularized_arcsec=np.sqrt(ax*ay)*rho80*scale,relative_rms=rel,peak_snr=A/rms,reduced_chi2_nominal=np.mean((res/rms)**2),sep_b_over_a=objs[j]['b']/objs[j]['a'],solver_success=sol.success)
    stars.append(row)
    if accepted and (len(examples)<3 or ('2018-01-06' in p.name and len(examples)<6)):examples.append((cut.copy(),model(sol.x),row))
   print(p.name,ext.name,'fit complete',flush=True)
   aud.append(dict(filename=p.name,extension=ext.name,n_detections=len(objs),preselection=len(candidates),n_fitted=len(chosen)))
  for name,rows in [('elliptical_moffat_candidates',stars),('native_background',noise),('blank_aperture_noise',aps),('native_covariance',covs),('selection_audit',aud)]:pd.DataFrame(rows).to_csv(O/(name+'.csv'),index=False)
  print(p.name,'total fits',len(stars),flush=True)
for name,rows in [('elliptical_moffat_candidates',stars),('native_background',noise),('blank_aperture_noise',aps),('native_covariance',covs),('selection_audit',aud)]:pd.DataFrame(rows).to_csv(O/(name+'.csv'),index=False)
s=pd.DataFrame(stars);s=s[s.accepted];s.groupby('filename').median(numeric_only=True).to_csv(O/'psf_per_exposure.csv');s.groupby('extension').agg({'fwhm_circularized_arcsec':['count','median','min','max'],'q':'median','beta':'median'}).to_csv(O/'psf_per_chip.csv');s.assign(xbin=(s.x//512).astype(int),ybin=(s.y//512).astype(int)).groupby(['extension','xbin','ybin']).median(numeric_only=True).to_csv(O/'psf_spatial_bins.csv')
fig,axs=plt.subplots(6,3,figsize=(9,15),layout='constrained')
for axes,(cut,mod,row) in zip(axs,examples):
 for ax,im,label in zip(axes,[cut,mod,cut-mod],['Raw locally detrended cutout','Pixel-integrated Moffat','Residual']):
  ax.imshow(im,origin='lower',cmap='gray');ax.set_title(label,fontsize=9)
 axes[0].set_ylabel(f"{row['extension']} {row['filename'][6:16]}\nFWHM={row['fwhm_circularized_arcsec']:.3f}\" q={row['q']:.2f}")
fig.suptitle('Provisional raw compact sources; no catalog confirmation')
fig.savefig(O/'fit_inspection.png',dpi=160);plt.close(fig)
fig,axs=plt.subplots(2,2,figsize=(10,8),layout='constrained')
for ax,(ext,t) in zip(axs.flat,s.groupby('extension')):
 im=ax.scatter(t.x,t.y,c=t.fwhm_circularized_arcsec,s=15,vmin=.22,vmax=.45,cmap='viridis');ax.set(title=ext,xlabel='Native detector x',ylabel='Native detector y',xlim=(0,2048),ylim=(0,2048));fig.colorbar(im,ax=ax,label='Circularized FWHM (arcsec)')
fig.suptitle('Raw candidate width field; combines changing seeing across exposures');fig.savefig(O/'psf_field.png',dpi=180);plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(10,4),layout='constrained');ap=pd.DataFrame(aps);co=pd.DataFrame(covs)
for ext,t in ap.groupby('extension'):axs[0].plot(t.groupby('radius_pix').noise_ratio.median(),marker='o',label=ext)
axs[0].set(xlabel='Blank aperture radius (native pixels)',ylabel='Robust aperture noise / sigma_pixel sqrt(N)');axs[0].legend(fontsize=7)
for axis,t in co.assign(axis=np.where(co.dx>0,'x','y'),lag=co.dx+co.dy).groupby('axis'):axs[1].plot(t.groupby('lag').correlation.median(),marker='o',label=axis)
axs[1].set(xlabel='Native pixel lag',ylabel='Median raw background correlation');axs[1].legend();fig.savefig(O/'native_noise.png',dpi=180);plt.close(fig)
summary={'python':sys.executable,'accepted':len(s),'fitted':len(stars),'median_fwhm_arcsec':s.fwhm_circularized_arcsec.median(),'fwhm_IQR_arcsec':s.fwhm_circularized_arcsec.quantile([.25,.75]).tolist(),'median_q':s.q.median(),'median_beta':s.beta.median(),'median_ee50_arcsec':s.ee50_circularized_arcsec.median(),'median_ee80_arcsec':s.ee80_circularized_arcsec.median(),'esorex':shutil.which('esorex')}
(O/'diagnostic_summary.json').write_text(json.dumps(summary,indent=2));print(summary)
