from pathlib import Path
import os,json
os.environ.setdefault('MPLCONFIGDIR','/tmp/hawki_m4_mpl')
import numpy as np,pandas as pd
from scipy import signal,ndimage as ndi
from scipy.optimize import nnls
from astropy.io import fits
from astropy.wcs import WCS
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=Path(__file__).resolve().parent;rng=np.random.default_rng(10361)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})

def interval_cluster(a,col,nboot=2000):
 groups=[g[col].dropna().to_numpy() for _,g in a.groupby(['bx','by']) if g[col].notna().any()]
 if not groups:return [np.nan,np.nan]
 v=[np.median(np.concatenate([groups[i] for i in rng.integers(len(groups),size=len(groups))])) for _ in range(nboot)]
 return list(np.quantile(v,[.025,.975]))

def save(fig,name):
 fig.savefig(O/'figures'/(name+'.png'),dpi=170,bbox_inches='tight');fig.savefig(O/'figures'/(name+'.pdf'),bbox_inches='tight');plt.close(fig)

def run():
 s=pd.read_csv(O/'validated_stars.csv');quality=pd.read_csv(O/'saturation_profile_checks.csv');s=s.merge(quality,on=['field','source_local_id'],how='left',validate='one_to_one');s['primary_star']=s.primary_star&~s.flat_core_flag.fillna(True).astype(bool)
 # Position angle mapped to the sky; do not compare arbitrary pixel angles across planes.
 planes={}
 for p in (O.parents[1]/'data/HAWKI_M4off_2019').glob('*.fits'):
  with fits.open(p) as h:
   for i,hd in enumerate(h):
    if hd.data is not None:planes[('tile' if len(h)==1 else 'pawprint')+str(i)]=WCS(hd.header)
 for field,g in s.groupby('field'):
  theta=g.theta_rad+np.where(g.alpha_x_pixels>=g.alpha_y_pixels,0,np.pi/2);xy=g[['x','y']].to_numpy();end=xy+np.c_[np.cos(theta),np.sin(theta)];sky1=planes[field].all_pix2world(xy,0);sky2=planes[field].all_pix2world(end,0);pa=np.arctan2((sky2[:,0]-sky1[:,0])*np.cos(np.deg2rad(sky1[:,1])),sky2[:,1]-sky1[:,1]);s.loc[g.index,'sky_PA_deg']=np.degrees(pa)%180;s.loc[g.index,'e1']=(1-g.q)/(1+g.q)*np.cos(2*pa);s.loc[g.index,'e2']=(1-g.q)/(1+g.q)*np.sin(2*pa)
 s['wing_reliable']=s.primary_star&s.wing_isolated&(s.annular_contamination_ratio<1.5)&np.isfinite(s.empirical_R50_R2_arcsec)
 s.to_csv(O/'science_star_table.csv',index=False);summary=[];bins=[]
 for field,g in s[s.primary_star].groupby('field'):
  row=dict(field=field,n_stars=len(g),n_wing_reliable=int(g.wing_reliable.sum()),spatial_cells=g.groupby(['bx','by']).ngroups)
  for c in ['fwhm_arcsec','q','beta','empirical_R50_R2_arcsec','empirical_R80_R2_arcsec','model_R50_infinite_elliptical_circularized_arcsec']:
   lo,hi=interval_cluster(g,c);row[c+'_median']=g[c].median();row[c+'_p16']=g[c].quantile(.16);row[c+'_p84']=g[c].quantile(.84);row[c+'_median_CI95_lo']=lo;row[c+'_median_CI95_hi']=hi
  summary.append(row)
  for (bx,by),gg in g.groupby(['bx','by']):
   bins.append(dict(field=field,bx=bx,by=by,n=len(gg),x=gg.x.median(),y=gg.y.median(),ra=gg.ra.median(),dec=gg.dec.median(),fwhm_arcsec=gg.fwhm_arcsec.median(),q=gg.q.median(),beta=gg.beta.median()))
 sm=pd.DataFrame(summary);sm.to_csv(O/'PSF_summary.csv',index=False);b=pd.DataFrame(bins);b.to_csv(O/'PSF_spatial_cells.csv',index=False)
 # Paired table selection includes identical validation flags; collapse repeated Gaia IDs for CIs.
 pairs=pd.read_csv(O/'matched_stars.csv');good=set(zip(s[s.primary_star].field,s[s.primary_star].source_local_id));pairs=pairs[[((r.field_pawprint,int(r.source_local_id_pawprint)) in good and ('tile0',int(r.source_local_id_tile)) in good) for r in pairs.itertuples()]];
 for suffix in ['pawprint','tile']:
  cols=s[['field','source_local_id','e1','e2','sky_PA_deg']].rename(columns={'field':'field_'+suffix,'source_local_id':'source_local_id_'+suffix,'e1':'e1_'+suffix,'e2':'e2_'+suffix,'sky_PA_deg':'PA_'+suffix})
  pairs=pairs.merge(cols,on=['field_'+suffix,'source_local_id_'+suffix],validate='many_to_one')
 pairs['delta_e1']=pairs.e1_tile-pairs.e1_pawprint;pairs['delta_e2']=pairs.e2_tile-pairs.e2_pawprint
 pairs.to_csv(O/'matched_stars_primary.csv',index=False);pstats=[]
 for field,g in [('all_pawprints',pairs)]+list(pairs.groupby('field_pawprint')):
  for c in ['delta_fwhm_arcsec','delta_q','delta_beta','delta_empirical_R50_R2_arcsec','delta_empirical_R80_R2_arcsec','aperture_magnitude_delta_with_ZP','delta_e1','delta_e2']:
   unique=g.groupby('gaia_id')[c].mean().dropna().to_numpy();boot=np.median(unique[rng.integers(len(unique),size=(3000,len(unique)))],axis=1);u=g.groupby('gaia_id').agg(value=(c,'mean'),bx=('bx_tile','first'),by=('by_tile','first')).dropna();blocks=[t.value.to_numpy() for _,t in u.groupby(['bx','by'])];cluster=np.array([np.median(np.concatenate([blocks[i] for i in rng.integers(len(blocks),size=len(blocks))])) for _ in range(1500)])
   pstats.append(dict(field=field,quantity=c,n_rows=len(g),n_unique_stars=len(unique),median=np.median(unique),lo=np.quantile(boot,.025),hi=np.quantile(boot,.975),cluster_lo=np.quantile(cluster,.025),cluster_hi=np.quantile(cluster,.975),spatial_clusters=len(blocks),CI_scope='Unique-star and tile-spatial-cell cluster bootstrap; fixed common-exposure products, not temporal repeatability'))
 pd.DataFrame(pstats).to_csv(O/'paired_changes.csv',index=False)
 # PSF family: preserve joint parameter samples. Positive normalized analytic kernels are extrapolations.
 modeldir=O/'sensitivity_models';modeldir.mkdir(exist_ok=True);samples=s[s.primary_star][['field','source_local_id','gaia_id','bx','by','fwhm_arcsec','q','beta','sky_PA_deg','alpha_x_pixels','alpha_y_pixels','theta_rad','scale_arcsec','wing_reliable']];samples.to_csv(modeldir/'joint_PSF_parameter_samples.csv',index=False)
 kernels={};specs=[]
 for field,g in s[s.primary_star].groupby('field'):
  eligible=g[g.wing_reliable];eligible=eligible if len(eligible)>=5 else g
  for quant in [.1,.5,.9]:
   target=eligible.fwhm_arcsec.quantile(quant);r=eligible.iloc[np.argmin(abs(eligible.fwhm_arcsec-target))];scale=float(r.scale_arcsec);axis=(np.arange(129)-64)*scale;Y,X=np.meshgrid(axis,axis,indexing='ij');theta=r.theta_rad;u=X*np.cos(theta)+Y*np.sin(theta);v=-X*np.sin(theta)+Y*np.cos(theta);k=(1+(u/(r.alpha_x_pixels*scale))**2+(v/(r.alpha_y_pixels*scale))**2)**(-r.beta);k/=k.sum();name=field+'_q'+str(int(quant*100));kernels[name]=k.astype('f4');specs.append(dict(name=name,field=field,source_local_id=int(r.source_local_id),pixel_arcsec=scale,fwhm_arcsec=float(r.fwhm_arcsec),q=float(r.q),beta=float(r.beta),normalization='finite129pixel grid; Moffat wings beyond measured R2 are model extrapolations'))
 np.savez_compressed(modeldir/'positive_Moffat_PSF_kernels.npz',**kernels);(modeldir/'PSF_kernel_manifest.json').write_text(json.dumps(specs,indent=2))
 # Noise family is positive-semidefinite by construction: sum independent filtered white components.
 ap=pd.read_csv(O/'aperture_noise.csv');co=pd.read_csv(O/'background_covariance.csv');noise=[];response=[]
 sigmas=[(0,0),(.35,.7),(.7,.35),(.7,.7),(1.5,1.5),(3.,3.),(6.,6.),(12.,12.)];axis=np.arange(-48,49);Y,X=np.meshgrid(axis,axis,indexing='ij');K=[]
 for sx,sy in sigmas:
  if sx==0:k=np.zeros(X.shape);k[48,48]=1
  else:k=np.exp(-.5*((X/sx)**2+(Y/sy)**2));k/=np.sqrt((k*k).sum())
  K.append(k)
 A=[]
 for dy,dx in [(0,1),(1,0),(0,2),(2,0),(0,4),(4,0)]:A.append([np.sum(k[:97-dy,:97-dx]*k[dy:,dx:]) for k in K])
 for rad in [2,4,8,16]:
  y,x=np.mgrid[-rad:rad+1,-rad:rad+1];disk=(x*x+y*y<=rad*rad);A.append([np.sum(signal.fftconvolve(disk,k)**2)/disk.sum() for k in K])
 A=np.array(A)
 for field in s.field.unique():
  c=co[(co.field==field)&(co.kind=='grid')&(co.mesh==128)&(co.dilation_pixels==12)];a=ap[(ap.field==field)&(ap.kind=='grid')&(ap.mesh==128)&(ap.dilation_pixels==12)&(ap.status=='ok')];target=[]
  for dy,dx in [(0,1),(1,0),(0,2),(2,0),(0,4),(4,0)]:target.append(c[(c.dx==dx)&(c.dy==dy)].correlation.median())
  for rad in [2,4,8,16]:target.append(a[a.radius_pixels==rad].ratio_pixel_MAD.median()**2)
  target=np.array(target);weights=np.r_[np.full(6,3.),1/np.maximum(target[6:],1.)];matrix=np.vstack([A*weights[:,None],np.ones((1,len(K)))*15]);rhs=np.r_[target*weights,15.];coeff,_=nnls(matrix,rhs);coeff/=coeff.sum();prediction=A@coeff
  noise.append(dict(field=field,component_sigma_xy_pixels=sigmas,variance_fractions=coeff.tolist(),observed_pixel_scale_arcsec=.10656,scope='phenomenological total reduced-background stress, includes unresolved stars/sky; not unique instrumental covariance; no ADU amplitude transfer',fit_largest_radius_pixels=16,normalization='sum independent unit-L2 Gaussian-filtered white fields with sqrt(variance_fraction) amplitudes',max_fractional_response_error=float(np.max(abs(prediction-target)/np.maximum(abs(target),.1)))))
  for j,(obs,pred) in enumerate(zip(target,prediction)):response.append(dict(field=field,statistic=['rho_x1','rho_y1','rho_x2','rho_y2','rho_x4','rho_y4','ap_R2_ratio2','ap_R4_ratio2','ap_R8_ratio2','ap_R16_ratio2'][j],measured=obs,model=pred))
 (modeldir/'noise_family.json').write_text(json.dumps(noise,indent=2));pd.DataFrame(response).to_csv(modeldir/'noise_response_validation.csv',index=False)
 # Figures.
 fig,axes=plt.subplots(1,5,figsize=(18,4),layout='constrained');lo=s[s.primary_star].fwhm_arcsec.quantile(.05);hi=s[s.primary_star].fwhm_arcsec.quantile(.95)
 for ax,(field,g) in zip(axes,s[s.primary_star].groupby('field')):
  im=ax.scatter(g.x,g.y,c=g.fwhm_arcsec,s=12,vmin=lo,vmax=hi,cmap='viridis');ax.set(title=field,xlabel='Stacked-image x (pixel)',ylabel='Stacked-image y (pixel)');fig.colorbar(im,ax=ax,label='Fitted FWHM (arcsec)',shrink=.7)
 save(fig,'spatial_PSF_maps')
 fig,axes=plt.subplots(1,3,figsize=(12,4),layout='constrained')
 for ax,c,label in zip(axes,['fwhm_arcsec','q','beta'],['Pixel-integrated Moffat FWHM (arcsec)','Axis ratio q','Fitted Moffat beta']):
  groups=[g[c].to_numpy() for _,g in s[s.primary_star].groupby('field')];ax.boxplot(groups,tick_labels=sorted(s.field.unique()),showfliers=False);ax.set_ylabel(label);ax.tick_params(axis='x',rotation=35)
 save(fig,'PSF_distributions')
 ee=pd.read_csv(O/'empirical_profiles.csv').merge(s[['field','source_local_id','primary_star','wing_reliable']],on=['field','source_local_id']);ngc=pd.read_csv(O/'ngc3256_empirical_profiles.csv');fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
 for field,g in ee[ee.wing_reliable].groupby('field'):
  t=g.groupby('radius_arcsec').EE_R2.agg(['median',lambda x:x.quantile(.16),lambda x:x.quantile(.84)]);axes[0].plot(t.index,t['median'],marker='.',label=field)
 for label,g in [('M4 tile Gaia stars',ee[(ee.field=='tile0')&ee.wing_reliable]),('NGC3256 2MASS stars',ngc[ngc.stellar_2mass])]:
  t=g.groupby('radius_arcsec').EE_R2.median();axes[1].plot(t.index,t,marker='o',label=label)
 for ax in axes:ax.set(xlabel='Circular aperture radius (arcsec)',ylabel='Measured fraction relative to R=2 arcsec',xlim=(0,1.5),ylim=(0,1.05));ax.legend(fontsize=8)
 save(fig,'empirical_encircled_energy')
 fig,axes=plt.subplots(1,3,figsize=(12,4),layout='constrained')
 for ax,c,label in zip(axes,['fwhm_arcsec','q','beta'],['FWHM (arcsec)','Axis ratio','Moffat beta']):
  for field,g in pairs.groupby('field_pawprint'):ax.scatter(g[c+'_pawprint'],g[c+'_tile'],s=12,alpha=.5,label=field)
  bounds=[min(ax.get_xlim()[0],ax.get_ylim()[0]),max(ax.get_xlim()[1],ax.get_ylim()[1])];ax.plot(bounds,bounds,':',color='black');ax.set(xlabel='Pawprint '+label,ylabel='Tile '+label)
 axes[0].legend(fontsize=8);save(fig,'matched_star_processing_changes')
 fig,axes=plt.subplots(1,2,figsize=(12,4),layout='constrained')
 for field,c in co[(co.kind=='grid')&(co.mesh==128)&(co.dilation_pixels==12)].groupby('field'):
  t=c[(c.dy==0)].groupby('dx').correlation.median();axes[0].plot(t.index,t,'o-',label=field)
 for field,a in ap[(ap.kind=='grid')&(ap.mesh==128)&(ap.dilation_pixels==12)&(ap.status=='ok')&(ap.radius_pixels<=16)].groupby('field'):
  t=a.groupby('radius_pixels').ratio_pixel_MAD.median();axes[1].plot(t.index,t,'o-',label=field)
 old=pd.read_csv(O.parent/'ml_feasibility_20261027/hawki/reduced_aperture_noise.csv');axes[1].plot(old.radius_pix,old.noise_ratio_to_pixel,'k--',label='NGC3256 prior mask');axes[0].set(xlabel='Pixel lag in x',ylabel='Masked-background correlation');axes[1].set(xlabel='Aperture radius (pixels)',ylabel='Aperture MAD / pixel MAD sqrt(N)');axes[0].legend(fontsize=8);axes[1].legend(fontsize=8);save(fig,'background_noise_comparison')
 fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
 for dilation,g in ap[(ap.field=='tile0')&(ap.kind=='grid')&(ap.mesh==128)&(ap.status=='ok')&(ap.radius_pixels<=16)].groupby('dilation_pixels'):
  t=g.groupby('radius_pixels').ratio_pixel_MAD.median();axes[0].plot(t.index,t,'o-',label=f'mask growth {dilation} pixels')
 cf=pd.read_csv(O/'confusion_apertures.csv');t=cf[(cf.dilation_pixels==12)&(cf.status=='ok')&(cf.radius_pixels<=16)].groupby('radius_pixels').ratio_pixel_MAD.median();axes[0].plot(t.index,t,'k--',label='additional faint-catalogue masks (ancillary regions)')
 for field,g in ap[(ap.kind=='grid')&(ap.dilation_pixels==12)&(ap.mesh==128)].groupby('field'):
  t=g.groupby('radius_pixels').n_nonoverlapping_lower_bound.sum();axes[1].plot(t.index,t,'o-',label=field)
 axes[0].set(xlabel='Aperture radius (pixels)',ylabel='Noise excess; regions/masks differ');axes[0].legend(fontsize=8);axes[1].set(xlabel='Aperture radius (pixels)',ylabel='Geometrically nonoverlapping aperture count');axes[1].set_yscale('log');axes[1].legend(fontsize=8);save(fig,'crowding_and_aperture_reliability')
 # Representative fit inspection, including failures stored in complete tables.
 fig,axes=plt.subplots(5,3,figsize=(9,12),layout='constrained')
 for axrow,(field,g) in zip(axes,s[s.primary_star].groupby('field')):
  t=g.iloc[np.argmin(abs(g.fwhm_arcsec-g.fwhm_arcsec.median()))];z=np.load(O/(field+'_stamps.npz'));j=int(np.flatnonzero(z['ids']==t.source_local_id)[0]);data=z['cuts'][j][6:47,6:47];model=z['models'][j]
  for ax,img,label in zip(axrow,[data,model,data-model],['Observed locally detrended','Pixel-integrated Moffat','Residual']):ax.imshow(img,origin='lower',cmap='gray');ax.set_title(label,fontsize=9)
  axrow[0].set_ylabel(field+f'\n{t.fwhm_arcsec:.3f} arcsec')
 save(fig,'fit_inspection')
 print('Models, summary tables and figures complete')
if __name__=='__main__':run()
