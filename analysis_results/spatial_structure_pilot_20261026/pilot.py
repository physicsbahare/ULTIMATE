"""Full-image structure and morphology pilot. Truth is absent from measure()."""
import os,sys,json,hashlib
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/ultimate-mpl')
sys.dont_write_bytecode=True
import numpy as np,pandas as pd
from scipy import ndimage as ndi,signal,stats
from astropy.io import fits
O=Path(__file__).resolve().parent
OLD=O.parent/'screen_test_20261026'
sys.path.insert(0,str(OLD))
from forward_physics import cosmology,overlap_flux,ARCSEC_PER_RAD
from instrument import setup_instrument
BANDS=['g','J','Ks'];SOURCE=['LSST_g','2MASS_J','2MASS_Ks'];WAVE=np.array([.482,1.235,2.159]);SCALES=[.5,1.,2.];N=40;CAL_SEED=761902;EVAL_SEED=982310;AMAG=2.5/np.log(10)
METHODS=['g_Ks_matched','J_Ks_NIR','Ks_native']
INST=[next(b for b in setup_instrument() if b['band']==lab) for lab in BANDS]

def load(view):
 a=np.load(OLD/f'input_cache/{view}_structured_broadbands.npz');ix=[list(a['band']).index(x) for x in SOURCE]
 return a['clear'][ix,200:600,200:600].astype(float),a['dusty'][ix,200:600,200:600].astype(float),a['dust'][200:600,200:600].astype(float)

def scenes(clear,dusty):
 yy,xx=np.mgrid[:400,:400];xx=(xx+.5)*.1-20;yy=(yy+.5)*.1-20
 rng=np.random.default_rng(73921);patch=ndi.gaussian_filter(rng.normal(size=(400,400)),8);patch/=patch.std()
 field=.65*np.tanh((xx+2*yy-1)/4)+.35*np.tanh(patch)
 # Positive, non-screen spectral shifts; the generator is not a fitted population model.
 shifted=clear*np.exp(np.array([-.24,.055,0])[:,None,None]*field)
 k=(WAVE/.55)**-1/((.44/.55)**-1-1)
 return {'clear':clear,'uniform':clear*10**(-.4*.15*k[:,None,None]),'population_shift':shifted,'SKIRT':dusty}

def gaussian_kernel(sigma):
 if sigma<1e-7:return np.ones((1,1))
 q=np.arange(-int(np.ceil(5*sigma)),int(np.ceil(5*sigma))+1);v=np.exp(-.5*(q/sigma)**2);v/=v.sum();return np.outer(v,v)

def psf_kernel(width,pixel,kind):
 if width==0:return np.ones((1,1))
 if kind=='gaussian':return gaussian_kernel(width/2.354820045/pixel)
 # width is D50, not FWHM; beta=2.5. alpha from enclosed half light.
 beta=2.5;alpha=width/(2*np.sqrt(2**(1/(beta-1))-1))/pixel
 q=np.arange(-int(np.ceil(12*alpha)),int(np.ceil(12*alpha))+1);y,x=np.meshgrid(q,q,indexing='ij');k=(1+(x*x+y*y)/alpha**2)**-beta;return k/k.sum()

def make_geometry(z,mode,kind='gaussian'):
 scale=cosmology.kpc_proper_per_arcmin(z).value/60;native=.1/scale;pixel=.1
 edges=(np.arange(561)-280)*native;nout=2*int(np.ceil(28/scale/pixel));outedges=(np.arange(nout+1)-nout/2)*pixel
 size=2*int(np.ceil(16/scale/pixel));start=(nout-size)//2;sl=slice(start,start+size)
 xy=(np.arange(size)+.5-size/2)*pixel*scale;yy,xx=np.meshgrid(xy,xy,indexing='ij');radius=np.hypot(xx,yy)
 widths=np.array([b['seeing_fwhm_arcsec'] if mode=='seeing' else b['glao_fwhm_arcsec'] for b in INST])
 return dict(z=z,mode=mode,kind=kind,scale=scale,native=native,pixel=pixel,edges=edges,outedges=outedges,nout=nout,sl=sl,shape=(size,size),x=xx,y=yy,r=radius,roi=radius<12,widths=widths)

def render(scene,g,psf=True):
 imgs=[];loss=[]
 for s,b,w in zip(scene,INST,g['widths']):
  f=np.pad(s/(1+g['z'])**3*1e6*(g['native']/ARCSEC_PER_RAD)**2,80)
  if psf:f=signal.fftconvolve(f,psf_kernel(w,g['native'],g['kind']),mode='same')
  full=overlap_flux(f,g['edges'],g['outedges']);loss.append(1-full.sum()/np.sum(np.pad(s,80)/(1+g['z'])**3*1e6*(g['native']/ARCSEC_PER_RAD)**2))
  imgs.append(np.maximum(full[g['sl'],g['sl']],0)*b['flat_e_s_per_jy'])
 return np.array(imgs),max(abs(np.array(loss)))

def variance(rate,hours):
 t=hours*3600;nexp=int(round(t/60));assert nexp*60==t
 return np.array([(r+b['background_e_s_pixel']+b['dark_e_s'])*t+nexp*b['read_noise_e']**2 for r,b in zip(rate,INST)])/t**2

def normalized_intensity(rate):
 return rate/np.array([b['flat_e_s_per_jy'] for b in INST])[:,None,None]

class FilterPlan:
 """Combined matching + fine/broad kernels, including their covariance."""
 def __init__(self,g,method,size):
  self.method=method;self.size=size
  self.indices=[0,2] if method=='g_Ks_matched' else [1,2] if method=='J_Ks_NIR' else [2]
  if method=='g_Ks_matched':target=.8
  elif method=='J_Ks_NIR':target=max(g['widths'][1:])
  else:target=g['widths'][2]
  self.target=target;self.kernels=[]
  for i in self.indices:
   # Moffat runs use native brightness only; no Gaussian matching assumption.
   match=np.sqrt(max(0,target**2-g['widths'][i]**2)) if method!='Ks_native' else 0.
   sf=np.hypot(size/(g['pixel']*g['scale']),match/g['pixel'])/2.354820045
   sb=np.hypot(3*size/(g['pixel']*g['scale']),match/g['pixel'])/2.354820045
   kf=gaussian_kernel(sf);kb=gaussian_kernel(sb)
   diff=(kb.shape[0]-kf.shape[0])//2;small=np.pad(kf,diff)
   self.kernels.append((kf,kb,small*kb))
 def prepare(self,var):
  self.v=[]
  for i,(kf,kb,cross) in zip(self.indices,self.kernels):
   self.v.append((signal.fftconvolve(var[i],kf*kf,mode='same'),signal.fftconvolve(var[i],kb*kb,mode='same'),signal.fftconvolve(var[i],cross,mode='same')))
 def measure(self,images,roi):
  """Observed images/variance only: no dust-free image or truth map."""
  value=np.zeros(images.shape[-2:]);v=np.zeros_like(value);mask=roi.copy()
  for j,(i,(kf,kb,cross),(vf,vb,vc)) in enumerate(zip(self.indices,self.kernels,self.v)):
   f=signal.fftconvolve(images[i],kf,mode='same');b=signal.fftconvolve(images[i],kb,mode='same')
   good=(f>0)&(b>0)&(f>10*np.sqrt(np.maximum(vf,0)))&(b>10*np.sqrt(np.maximum(vb,0)))
   mask&=good;f=np.maximum(f,1e-30);b=np.maximum(b,1e-30)
   if self.method=='Ks_native':
    value=1-f/b;v=vf/b**2+f*f*vb/b**4-2*f*vc/b**3
   else:
    sign=1 if j==0 else -1;value+=-sign*AMAG*np.log(f/b)
    v+=AMAG**2*(vf/f**2+vb/b**2-2*vc/(f*b))
  sigma=np.sqrt(np.maximum(v,0));amp=.03 if self.method=='Ks_native' else .05
  detected=mask&(value>amp)&(value>3*sigma)
  return value,sigma,mask,detected

def truth_maps(images,g,method,size):
 p=FilterPlan(g,method,size);p.prepare(np.zeros_like(images));return p.measure(images,g['roi'])[0]

def morph(image,var,g):
 """Fixed-centre circular morphology, R<12kpc, signed sky-subtracted flux."""
 mask=g['roi'];f=image[mask];r=g['r'][mask];order=np.argsort(r);r=r[order];f=f[order];total=f.sum()
 if total<=0:return dict(R20=np.nan,R50=np.nan,R80=np.nan,C=np.nan,A=np.nan,axis_ratio=np.nan)
 cum=np.cumsum(f);radii=[]
 for q in [.2,.5,.8]:
  hits=np.flatnonzero(cum>=q*total);radii.append(float(r[hits[0]]) if len(hits) else np.nan)
 rotated=image[::-1,::-1];vv=var+var[::-1,::-1];expect=np.sqrt(2/np.pi)*np.sqrt(vv)
 asym=np.sum((abs(image-rotated)-expect)[mask])/total
 # Measured second moments; invalid eigenvalues are retained as NaN, no clipping flux.
 m=np.array([[np.sum(image[mask]*g['x'][mask]**2),np.sum(image[mask]*g['x'][mask]*g['y'][mask])],[np.sum(image[mask]*g['x'][mask]*g['y'][mask]),np.sum(image[mask]*g['y'][mask]**2)]])/total
 val=np.linalg.eigvalsh(m);q=np.sqrt(val[0]/val[1]) if np.all(val>0) else np.nan
 return dict(R20=radii[0],R50=radii[1],R80=radii[2],C=5*np.log10(radii[2]/radii[0]),A=asym,axis_ratio=q)

def score(value,observed_mask,detected,reference,limited,valid,g,size):
 cut=.03 if reference['method']=='Ks_native' else .05
 ref=valid&(reference['value']>cut);lim=valid&(limited>cut);pred=valid&detected
 nref=ref.sum();npred=pred.sum();inter=(pred&ref).sum();union=(pred|ref).sum()
 def divide(a,b):return float(a/b) if b else np.nan
 sel=valid&observed_mask
 if sel.sum()>5 and np.std(value[sel])>0 and np.std(reference['value'][sel])>0:
  corr=np.corrcoef(value[sel],reference['value'][sel])[0,1]
 else:corr=np.nan
 # Connected features are descriptive; area cuts fixed in protocol.
 minpix=max(4,int(np.pi*(size/2)**2/(g['pixel']*g['scale'])**2));labels,n=ndi.label(ref);predlab,npr=ndi.label(pred)
 tr=[labels==i for i in range(1,n+1) if (labels==i).sum()>=minpix];pr=[predlab==i for i in range(1,npr+1) if (predlab==i).sum()>=minpix]
 recovered=sum((x&pred).sum()>=.3*x.sum() for x in tr);false=sum((x&ref).sum()<.3*x.sum() for x in pr)
 out=dict(completeness=divide(inter,nref),contamination=divide(npred-inter,npred),IoU=divide(inter,union),correlation=corr,PSF_limited_completeness=divide((pred&lim).sum(),lim.sum()),reference_area_kpc2=nref*(g['pixel']*g['scale'])**2,candidate_area_fraction=divide(npred,valid.sum()),usable_area_fraction=divide(sel.sum(),valid.sum()),n_reference_features=len(tr),n_candidate_features=len(pr),feature_completeness=divide(recovered,len(tr)),feature_contamination=divide(false,len(pr)),has_candidate=bool(npred),any_component=bool(len(pr)))
 # No independent-pixel intervals: surface-brightness strata scored per draw.
 sb=reference['sb'];a=sb[valid];qs=np.quantile(a,[1/3,2/3]);strata=np.digitize(sb,qs)
 for s in range(3):
  domain=valid&(strata==s);rr=ref&domain;pp=pred&domain;it=(rr&pp).sum();out[f'completeness_SB{s}']=divide(it,rr.sum());out[f'contamination_SB{s}']=divide(pp.sum()-it,pp.sum())
 return out

def reference(view,clear,dusty,dust):
 yy,xx=np.mgrid[:400,:400];rr=np.hypot((xx+.5)*.1-20,(yy+.5)*.1-20);eff=np.full_like(clear,np.nan);rows=[]
 for j,b in enumerate(BANDS):
  m=(rr<12)&(clear[j]>1e-4*clear[j].max())&(dusty[j]>0)&(clear[j]>0)
  eff[j,m]=-2.5*np.log10(dusty[j,m]/clear[j,m]);rows.append(dict(view=view,band=b,n_pixels=m.sum(),negative_attenuation_fraction=float(np.mean(eff[j,m]<0)),integrated_A_R12_mag=-2.5*np.log10(dusty[j,rr<12].sum()/clear[j,rr<12].sum()),rho_projected_dust=float(stats.spearmanr(eff[j,m],dust[m]).statistic)))
 np.savez_compressed(O/f'references/{view}_effective_attenuation.npz',clear=clear.astype('f4'),dusty=dusty.astype('f4'),A_eff=eff.astype('f4'),dust_surface_density=dust.astype('f4'),band=BANDS,source_pixel_kpc=.1)
 return rows

def evaluate_condition(view,z,mode,hours,kind='gaussian',n=N):
 clear,dusty,dust=load(view);g=make_geometry(z,mode,kind);allsc=scenes(clear,dusty);rates={};variances={};trans=[]
 for name,s in allsc.items():
  r,loss=render(s,g);rates[name]=r;variances[name]=variance(r,hours);trans.append(dict(view=view,z=z,mode=mode,hours=hours,kind=kind,scene=name,padded_render_flux_loss=loss))
 # Exact same reference detector-grid image with no observational PSF, for both modes.
 base,_=render(clear,g,False);dustbase,_=render(dusty,g,False)
 valid=g['roi']&(base>1e-4*np.max(base,axis=(1,2))[:,None,None]).all(axis=0)
 methods=METHODS if kind=='gaussian' else ['Ks_native'];reference_data={};plans={};limited={}
 for method in methods:
  for size in SCALES:
   ref=truth_maps(dustbase,g,method,size)-truth_maps(base,g,method,size)
   # With no PSF, use matching=0 rather than add optical matching blur to reference.
   zero=dict(g);zero['widths']=np.array([.8,.8,.8]) if method=='g_Ks_matched' else np.array([.7,.7,.7])
   ref=truth_maps(dustbase,zero,method,size)-truth_maps(base,zero,method,size)
   limited[(method,size)]=truth_maps(rates['SKIRT'],g,method,size)-truth_maps(rates['clear'],g,method,size)
   reference_data[(method,size)]={'method':method,'value':ref,'sb':base[-1]}
 for name in allsc:
  for method in methods:
   for size in SCALES:
    p=FilterPlan(g,method,size);p.prepare(variances[name]);plans[(name,method,size)]=p
 rows=[];morphrows=[];saved={};condition_seed=EVAL_SEED+int(view[1:])*10000+int(z*100)*100+int(hours*4)
 rng=np.random.default_rng(condition_seed)
 for draw in range(n):
  innovation=rng.standard_normal((3,)+g['shape'])
  for name in allsc:
   obs=rates[name]+np.sqrt(variances[name])*innovation
   group=dict(view=view,z=z,mode=mode,hours=hours,kind=kind,scene=name,draw=draw)
   for method in methods:
    for size in SCALES:
     p=plans[(name,method,size)];value,sig,mask,det=p.measure(obs,g['roi'])
     # Dust truth only applies to SKIRT; controls have no varying attenuation.
     ref=reference_data[(method,size)] if name=='SKIRT' else dict(reference_data[(method,size)],value=np.zeros(g['shape']))
     lim=limited[(method,size)] if name=='SKIRT' else np.zeros(g['shape'])
     rows.append(dict(**group,method=method,scale_kpc=size,effective_psf_fwhm_kpc=np.hypot(p.target*g['scale'],size),**score(value,mask,det,ref,lim,valid,g,size)))
     if draw==0 and size==1.:
      saved[f'{name}_{method}_value']=value.astype('f4');saved[f'{name}_{method}_sigma']=sig.astype('f4');saved[f'{name}_{method}_detected']=det;saved[f'{method}_reference']=reference_data[(method,size)]['value'].astype('f4');saved[f'{method}_limited']=limited[(method,size)].astype('f4')
   for j in [0,2]:
    values=morph(obs[j],variances[name][j],g);truth=morph(rates[name][j],np.zeros(g['shape']),g)
    morphrows.append(dict(**group,band=BANDS[j],**values,**{f'noiseless_{k}':v for k,v in truth.items()}))
   if draw==0:saved[f'{name}_observed_rate']=obs.astype('f4');saved[f'{name}_expected_rate']=rates[name].astype('f4');saved[f'{name}_rate_variance']=variances[name].astype('f4')
  if (draw+1)%20==0:print(f'{view} z={z} {mode} {hours}h {kind}: {draw+1}/{n}',flush=True)
 # Noiseless intrinsic morphology, with no data-taking PSF; mass map not used to measure.
 for name,s in allsc.items():
  unblurred,_=render(s,g,False)
  for j in [0,2]:morphrows.append(dict(view=view,z=z,mode=mode,hours=hours,kind=kind,scene=name,draw=-1,band=BANDS[j],**morph(unblurred[j],np.zeros(g['shape']),g)))
 saved['pixel_kpc']=g['pixel']*g['scale'];saved['valid_truth']=valid;saved['radius_kpc']=g['r'];saved['widths_arcsec']=g['widths'];saved['band']=BANDS
 np.savez_compressed(O/f'observations/{view}_z{z}_{mode}_{hours}h_{kind}.npz',**saved)
 return rows,morphrows,trans

def summarize(df,keys,metrics):
 rows=[]
 for vals,g in df.groupby(keys):
  row=dict(zip(keys,vals if isinstance(vals,tuple) else [vals]));row['n_draws']=len(g)
  for metric in metrics:
   v=g[metric].dropna().to_numpy(dtype=float);m=float(np.mean(v)) if len(v) else np.nan
   se=float(stats.sem(v)) if len(v)>1 else np.nan;ci=stats.t.ppf(.975,len(v)-1)*se if len(v)>1 else np.nan
   row[metric]=m;row[metric+'_lo']=m-ci;row[metric+'_hi']=m+ci;row[metric+'_nvalid']=len(v)
  rows.append(row)
 return pd.DataFrame(rows)

def run():
 for sub in ['references','observations','figures']:(O/sub).mkdir(exist_ok=True)
 pd.DataFrame([{k:v for k,v in b.items() if k not in ['wave','throughput']} for b in INST]).to_csv(O/'instrument_parameters.csv',index=False)
 refs=[]
 for v in ['O1','O2','O3','O4','O5']:refs.extend(reference(v,*load(v)))
 pd.DataFrame(refs).to_csv(O/'reference_summary.csv',index=False)
 conditions=[('O1',z,m,h,'gaussian') for z in [.05,.1] for h in [.25,1.,4.] for m in ['seeing','glao']]
 conditions += [(v,.1,m,1.,'gaussian') for v in ['O2','O3','O4','O5'] for m in ['seeing','glao']]
 conditions += [('O1',.1,m,1.,'moffat') for m in ['seeing','glao']]
 rows=[];mr=[];tr=[]
 for c in conditions:
  a,b,t=evaluate_condition(*c);rows.extend(a);mr.extend(b);tr.extend(t)
  pd.DataFrame(rows).to_csv(O/'feature_draws.csv',index=False);pd.DataFrame(mr).to_csv(O/'morphology_draws.csv',index=False);pd.DataFrame(tr).to_csv(O/'transfer_validation.csv',index=False)
 df=pd.DataFrame(rows);metrics=['completeness','contamination','IoU','correlation','PSF_limited_completeness','candidate_area_fraction','usable_area_fraction','feature_completeness','feature_contamination','completeness_SB0','completeness_SB1','completeness_SB2','contamination_SB0','contamination_SB1','contamination_SB2']
 keys=['view','z','mode','hours','kind','scene','method','scale_kpc'];summarize(df,keys,metrics).to_csv(O/'feature_summary.csv',index=False)
 morphdf=pd.DataFrame(mr);summarize(morphdf[morphdf.draw>=0],['view','z','mode','hours','kind','scene','band'],['C','A','R50','axis_ratio']).to_csv(O/'morphology_summary.csv',index=False)
 # Pairwise uncertainty is across independent noise innovations, not galaxies.
 keys=['view','z','hours','kind','scene','draw','method','scale_kpc'];paired=df.pivot(index=keys,columns='mode',values=['completeness','contamination','IoU','candidate_area_fraction'])
 changes=pd.DataFrame({x:paired[x]['glao']-paired[x]['seeing'] for x in ['completeness','contamination','IoU','candidate_area_fraction']}).reset_index();changes.to_csv(O/'paired_GLAO_draws.csv',index=False)
 summarize(changes,[x for x in keys if x!='draw'],['completeness','contamination','IoU','candidate_area_fraction']).to_csv(O/'paired_GLAO_summary.csv',index=False)
 return df,morphdf
if __name__=='__main__':run()
