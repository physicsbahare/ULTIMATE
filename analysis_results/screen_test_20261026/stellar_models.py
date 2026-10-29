"""External population nuisance SEDs; no access to intrinsic SKIRT maps."""
from pathlib import Path
import numpy as np
from astropy.io import fits
O=Path(__file__).resolve().parent
AV_GRID=np.linspace(0,3,31)
SLOPES=np.array([.7,1.,1.3])

def load_stellar_library(prior='near_clear'):
    base=O/'sources/eazy/templates/fsps_full'
    meta=fits.getdata(base/'fsps_QSF_12_v3.param.fits',1)
    selected=np.flatnonzero(meta['Av']<.15) if prior=='near_clear' else np.arange(12)
    grid=np.geomspace(.12,4.,2500); templates=[]
    for i in selected:
        arr=np.loadtxt(base/f'fsps_QSF_12_v3_noIRdust_{i+1:03d}.dat')
        wave=arr[:,0]/1e4; fnu=arr[:,1]*wave**2
        fnu=np.interp(grid,wave,fnu); fnu/=np.interp(1.,grid,fnu)
        templates.append(fnu)
    templates=np.array(templates)
    mixtures=list(templates)
    # Explicit finite prior, equal probabilities. Contains changing local populations.
    if prior=='near_clear':
        for a in range(len(selected)-1):
            for f in [.25,.5,.75]: mixtures.append(f*templates[a]+(1-f)*templates[-1])
    else:
        rng=np.random.default_rng(6031)
        for _ in range(48):
            pair=rng.choice(len(selected),2,replace=False); f=rng.uniform(.1,.9)
            mixtures.append(f*templates[pair[0]]+(1-f)*templates[pair[1]])
    out=[]
    for sed in mixtures:
        for tilt in [-.15,0.,.15]: out.append(sed*grid**tilt)
    return grid,np.array(out),selected+1

def screen_shape_grid(z,inst,prior='near_clear',nav=31):
    wave,pops,ids=load_stellar_library(prior)
    av=AV_GRID if nav==31 else np.linspace(0,3,nav)
    shapes=np.empty((len(SLOPES),len(av),len(pops),len(inst)))
    for j,b in enumerate(inst):
        rest=b['wave']/(1+z)
        t=np.array([np.interp(rest,wave,p) for p in pops])
        denom=np.trapezoid(b['throughput']/b['wave'],b['wave'])
        for i,sl in enumerate(SLOPES):
            factors=10**(-.4*av[:,None]*(rest/.55)**-sl)
            shapes[i,:,:,j]=np.trapezoid(factors[:,None,:]*t[None,:,:]*b['throughput']/b['wave'],b['wave'],axis=2)/denom
    return shapes.reshape(-1,len(inst)),len(SLOPES),len(av),len(pops)
