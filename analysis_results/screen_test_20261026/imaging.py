from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.signal import fftconvolve,convolve2d
from scipy.optimize import brentq, minimize_scalar
from forward_physics import cosmology,overlap_flux,ARCSEC_PER_RAD
O=Path(__file__).resolve().parent

def band_weights(source_wave,z,inst,coordinate='log'):
    weights=[]
    x=np.log(source_wave) if coordinate=='log' else source_wave
    for b in inst:
        rest=b['wave']/(1+z)
        if rest.min()<source_wave.min() or rest.max()>source_wave.max(): raise ValueError('Unbracketed band')
        xt=np.log(rest) if coordinate=='log' else rest
        inds=np.clip(np.searchsorted(x,xt)-1,0,len(x)-2)
        f=(xt-x[inds])/(x[inds+1]-x[inds])
        response=b['throughput']/b['wave']
        hats=np.zeros((len(rest),len(source_wave)))
        hats[np.arange(len(rest)),inds]=1-f; hats[np.arange(len(rest)),inds+1]=f
        weights.append(np.trapezoid(hats*response[:,None],b['wave'],axis=0)/np.trapezoid(response,b['wave']))
    return np.array(weights)

def make_truths(cache):
    wave=cache['wave_um']; clear=cache['clear'].astype(float); mixed=cache['dusty'].astype(float)
    y,x=np.indices(clear.shape[1:]); r=np.hypot(x+.5-clear.shape[2]/2,y+.5-clear.shape[1]/2)*.1; mask=r<20
    gi=list(cache['band']).index('LSST_g')
    target=-2.5*np.log10(mixed[gi][mask].sum()/clear[gi][mask].sum())
    curve=(wave/.55)**-1.
    au=target/curve[gi]
    column=cache['dust'].astype(float); positive=column[mask&(column>0)]
    pattern=np.minimum(column/np.median(positive),10.)
    def attenuation(a): return -2.5*np.log10(np.sum(clear[gi][mask]*10**(-.4*a*pattern[mask]*curve[gi]))/clear[gi][mask].sum())
    avscale=brentq(lambda a:attenuation(a)-target,0,20)
    uniform=clear*10**(-.4*au*curve[:,None,None])
    variable=clear*10**(-.4*avscale*pattern[None,:,:]*curve[:,None,None])
    return {'mixed_SKIRT':mixed,'uniform_control':uniform,'variable_control':variable}, {'screen_slope':1.,'uniform_Av':au,'variable_scale':avscale,'g_R20_attenuation_matched_mag':target,'variable_Av_min':float((avscale*pattern).min()),'variable_Av_max':float((avscale*pattern).max())}

def project_scene(broadband,source_wave,z,inst,mode='seeing',coordinate='log',psf_scale=1.,psf_kind='gaussian'):
    weights=band_weights(source_wave,z,inst,coordinate)
    scenes=np.einsum('bk,kyx->byx',weights,broadband,optimize=True)/(1+z)**3
    kpc_arcsec=cosmology.kpc_proper_per_arcmin(z).value/60
    native_arcsec=.1/kpc_arcsec
    # Same padding/grid for all bands/modes; the input crop is 80 kpc, analysis aperture R<20.
    pad=int(np.ceil(8*.8/2.354820045/native_arcsec))
    ninput=scenes.shape[-1]+2*pad
    oldedges=(np.arange(ninput+1)-ninput/2)*native_arcsec
    nout=2*int(np.ceil(oldedges[-1]/.1)); outedges=(np.arange(nout+1)-nout/2)*.1
    pixel_sr=(native_arcsec/ARCSEC_PER_RAD)**2
    rendered=[]; flux_checks=[]; widths=[]
    for b,scene in zip(inst,scenes):
        width=b['seeing_fwhm_arcsec'] if mode=='seeing' else b['glao_fwhm_arcsec']
        if mode=='optimistic' and b['band'] in ['Y','J','H','Ks']: width=.2
        width*=psf_scale
        widths.append(width)
        flux=np.pad(scene*1e6*pixel_sr,((pad,pad),(pad,pad)))
        before=flux.sum()
        if psf_kind=='gaussian': conv=gaussian_filter(flux,width/2.354820045/native_arcsec,mode='constant',truncate=6.)
        else:
            # Sensitivity only: beta=2.5, equal D50 (not equal FWHM) to Gaussian primary.
            from scipy.signal import fftconvolve
            beta=2.5
            alpha=width/(2*np.sqrt(2**(1/(beta-1))-1))/native_arcsec
            half=min(pad,int(np.ceil(15*alpha)))
            yy,xx=np.mgrid[-half:half+1,-half:half+1]; kern=(1+(xx**2+yy**2)/alpha**2)**(-beta); kern/=kern.sum()
            conv=fftconvolve(flux,kern,mode='same')
        final=overlap_flux(conv,oldedges,outedges)
        flux_checks.append(float(final.sum()/before-1))
        rendered.append(np.maximum(final,0)*b['flat_e_s_per_jy'])
    return np.array(rendered),np.array(widths),{'kpc_per_arcsec':kpc_arcsec,'native_pixel_arcsec':native_arcsec,'output_shape':nout,'max_flux_relative_error':max(abs(x) for x in flux_checks),'analysis_radius_arcsec':20/kpc_arcsec}

def gaussian_kernel(sigma):
    if sigma<1e-5: return np.ones((1,1))
    half=int(6*sigma+.5); xx=np.arange(-half,half+1)
    k=np.exp(-.5*(xx/sigma)**2); k/=k.sum()
    return np.outer(k,k)

def aperture_catalog(shape,kpc_per_arcsec,radius_kpc=18,spacing_pix=20):
    mid=shape[-1]//2
    delta=np.arange(-mid+30,mid-29,spacing_pix)
    # Centre the fixed detector-coordinate lattice independently of brightness/truth.
    delta=np.arange(-int(mid/spacing_pix)+2,int(mid/spacing_pix)-1)*spacing_pix
    y,x=np.meshgrid(delta,delta,indexing='ij'); r=np.hypot(x,y)*.1*kpc_per_arcsec
    good=r<radius_kpc
    return np.column_stack([y[good]+mid,x[good]+mid]).astype(int)

def observe_apertures(rates,widths,inst,hours,rng,positions,target_fwhm=.8):
    t=hours*3600; nexp=int(round(t/60)); assert np.isclose(nexp*60,t)
    flux=[]; errors=[]; clean=[]; maxcorr=0; image_example={}
    for j,(rate,b,fw) in enumerate(zip(rates,inst,widths)):
        if fw>target_fwhm+1e-8: raise ValueError('Target PSF narrower than input')
        sigma=np.sqrt(max(target_fwhm**2-fw**2,0))/2.354820045/.1
        kg=gaussian_kernel(sigma); aperture=convolve2d(kg,np.ones((5,5)),mode='full')
        back=b['background_e_s_pixel']+b['dark_e_s']
        # Exact distribution of the sum of nexp independent Poisson draws and nexp independent reads.
        noisy=rng.poisson((rate+back)*t).astype(float)+rng.normal(0,np.sqrt(nexp)*b['read_noise_e'],rate.shape)-back*t
        var=(rate+back)*t+nexp*b['read_noise_e']**2
        factor=1e6/(t*b['flat_e_s_per_jy'])
        obs=fftconvolve(noisy,aperture,mode='same'); sig2=fftconvolve(var,aperture**2,mode='same')
        truth=fftconvolve(rate*t,aperture,mode='same')
        yy,xx=positions.T
        flux.append(obs[yy,xx]*factor); errors.append(np.sqrt(np.maximum(sig2[yy,xx],0))*factor); clean.append(truth[yy,xx]*factor)
        auto=convolve2d(aperture,aperture[::-1,::-1],mode='full'); cy,cx=np.array(auto.shape)//2
        if cy+20<auto.shape[0]: maxcorr=max(maxcorr,float(auto[cy+20,cx]/auto[cy,cx]))
        if b['band'] in ['g','Y','Ks']: image_example[b['band']]=noisy*factor
    return np.array(flux).T,np.array(errors).T,np.array(clean).T,{'nexp':nexp,'dit_s':60,'max_adjacent_background_correlation':maxcorr},image_example

def constant_colour_test(flux,error,index1,index2):
    f=flux[:,index1]; k=flux[:,index2]; ef=error[:,index1]; ek=error[:,index2]
    def score(q): return np.sum((f-q*k)**2/(ef**2+q*q*ek**2))
    fit=minimize_scalar(score,bounds=(.001,100.),method='bounded')
    return {'constant_colour_chi2':float(fit.fun),'constant_colour_dof':max(len(f)-1,0),'constant_colour_ratio':float(fit.x)}
