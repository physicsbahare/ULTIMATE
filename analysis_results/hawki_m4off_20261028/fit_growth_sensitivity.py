"""Finite-growth-constrained positive core+Gaussian-halo sensitivity, not optical truth."""
from pathlib import Path
import json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/hawki_m4_mpl')
import numpy as np,pandas as pd,sep
from scipy.optimize import minimize_scalar
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=Path(__file__).resolve().parent;M=O/'sensitivity_models';samples=pd.read_csv(M/'joint_PSF_parameter_samples.csv');ee=pd.read_csv(O/'EE_uncertainty.csv');manifest=json.loads((M/'PSF_kernel_manifest.json').read_text());rows=[];kernels={};y,x=np.indices((129,129));X=x-64;Y=y-64;fig,axs=plt.subplots(1,5,figsize=(18,4),layout='constrained')
for ax,field in zip(axs,sorted(samples.field.unique())):
 spec=next(z for z in manifest if z['name']==field+'_q50');r=samples[(samples.field==field)&(samples.source_local_id==spec['source_local_id'])].iloc[0];scale=r.scale_arcsec;core=np.zeros(X.shape)
 for oy in (np.arange(9)+.5)/9-.5:
  for ox in (np.arange(9)+.5)/9-.5:
   u=(X+ox)*np.cos(r.theta_rad)+(Y+oy)*np.sin(r.theta_rad);v=-(X+ox)*np.sin(r.theta_rad)+(Y+oy)*np.cos(r.theta_rad);core+=(1+(u/r.alpha_x_pixels)**2+(v/r.alpha_y_pixels)**2)**(-r.beta)/81
 core/=core.sum();g=ee[ee.field==field];radii=g.radius_arcsec.to_numpy();target=g['median'].to_numpy();fit=(radii>=.2)&(radii<=1.5)
 def growth(k):return sep.sum_circle(np.ascontiguousarray(k,dtype='f8'),np.full(len(radii),64.),np.full(len(radii),64.),radii/scale,subpix=5)[0]
 c=growth(core);options=[]
 for width in np.linspace(.5,3,51):
  sigma=width/(2*np.sqrt(2*np.log(2)))/scale;halo=np.exp(-.5*(X*X+Y*Y)/sigma**2);halo/=halo.sum();h=growth(halo)
  def curve(f):return ((1-f)*c+f*h)/((1-f)*c[-1]+f*h[-1])
  opt=minimize_scalar(lambda f:np.mean((curve(f)[fit]-target[fit])**2),bounds=(0,.5),method='bounded');f=opt.x;err=np.sqrt(opt.fun);options.append((err,width,f,halo,curve(f)))
 best=min(options,key=lambda z:z[0]);err,width,f,halo,pred=best;kernel=(1-f)*core+f*halo;kernel/=kernel.sum();kernels[field]=kernel.astype('f4');n=int(g.n_stars.iloc[0])
 for e,w,frac,_,curve in options:rows.append(dict(field=field,halo_FWHM_arcsec=w,halo_fraction_extrapolated_total=frac,finite_EE_RMS=e,best=bool(w==width),within_0p01_RMS_of_best=e<=err+.01,n_clean_wing_stars=n,scope='positive phenomenological core+Gaussian halo; finite R2 constrained, full halo flux and outer tail are degenerate extrapolations',wing_support='sparse: sensitivity only' if n<5 else 'conditional finite-growth support'))
 ax.plot(radii,target,'o',label='Finite measured EE');ax.fill_between(radii,g.median_CI95_lo,g.median_CI95_hi,alpha=.2);ax.plot(radii,c/c[-1],':',label='Single core model');ax.plot(radii,pred,label='Core+halo stress');ax.set(title=f'{field}: RMS={err:.3f}',xlabel='Radius (arcsec)',ylabel='EE relative to R2',xlim=(0,1.5),ylim=(0,1.05))
axs[0].legend(fontsize=7)
for ext in ['png','pdf']:fig.savefig(O/'figures'/('growth_curve_model_sensitivity.'+ext),dpi=170)
plt.close(fig);np.savez_compressed(M/'finite_growth_core_halo_kernels.npz',**kernels);pd.DataFrame(rows).to_csv(M/'finite_growth_model_grid.csv',index=False)
print(pd.DataFrame(rows).query('best')[['field','halo_FWHM_arcsec','halo_fraction_extrapolated_total','finite_EE_RMS','n_clean_wing_stars']].to_string(index=False))
