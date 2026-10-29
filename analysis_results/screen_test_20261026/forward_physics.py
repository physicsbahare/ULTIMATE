"""Static radiometric transfer; adapted from the inspected exact-overlap reference."""
import numpy as np
from scipy import sparse
from astropy.cosmology import FlatLambdaCDM
cosmology=FlatLambdaCDM(H0=70.,Om0=.3,Tcmb0=2.725)
H=6.62607015e-34
ARCSEC_PER_RAD=206264.80624709636

def specific_intensity_transfer(intensity,z):
    return np.asarray(intensity)/(1+z)**3

def interpolate_sed(wavelengths,values,target,kind='log'):
    w=np.asarray(wavelengths); t=np.asarray(target)
    if t.min()<w.min() or t.max()>w.max(): raise ValueError('Target wavelength lacks bracketing source bands; extrapolation forbidden')
    k=np.clip(np.searchsorted(w,t)-1,0,len(w)-2)
    f=(np.log(t)-np.log(w[k]))/(np.log(w[k+1])-np.log(w[k]))
    v=np.asarray(values)
    extra=(None,)*(v.ndim-1)
    f=f[(slice(None),)+extra]
    if kind=='log':
        floor=max(float(np.max(v))*1e-15,1e-30)
        return np.exp(np.log(np.maximum(v[k],floor))*(1-f)+np.log(np.maximum(v[k+1],floor))*f)
    return v[k]*(1-f)+v[k+1]*f

def photon_rate_jy(fnu_jy,wave_um,throughput,area_m2):
    return area_m2*1e-26/H*np.trapezoid(np.asarray(fnu_jy)*np.asarray(throughput)/np.asarray(wave_um),wave_um,axis=0)

def overlap_matrix(output_edges,input_edges):
    o0=np.asarray(output_edges[:-1])[:,None]; o1=np.asarray(output_edges[1:])[:,None]
    i0=np.asarray(input_edges[:-1])[None,:]; i1=np.asarray(input_edges[1:])[None,:]
    return sparse.csr_matrix(np.maximum(0.,np.minimum(o1,i1)-np.maximum(o0,i0)))

def overlap_flux(image,input_edges,output_edges):
    mat=overlap_matrix(output_edges,input_edges)/np.diff(input_edges)[0]
    return np.asarray((mat@np.asarray(image))@mat.T)

def draw_exposures(source_rate,bg_rate,dark_rate,dit,nexp,read_noise,rng):
    if dit<=0 or int(nexp)!=nexp or nexp<1: raise ValueError('Positive integer exposure count and DIT required')
    src=np.asarray(source_rate,dtype=float)
    if not np.isfinite(src).all() or np.any(src<0): raise ValueError('Nonnegative finite expected electron rates required')
    mean=(src+bg_rate+dark_rate)*dit
    out=np.zeros(src.shape)
    for _ in range(int(nexp)):
        out+=rng.poisson(mean)+rng.normal(0,read_noise,src.shape)-(bg_rate+dark_rate)*dit
    variance=(src+bg_rate+dark_rate)*dit*nexp+nexp*read_noise**2
    return out,variance
