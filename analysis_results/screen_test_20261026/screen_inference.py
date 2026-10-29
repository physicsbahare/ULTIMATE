"""Marginal likelihoods of global versus aperture-varying extra screens.

Neither intrinsic SKIRT intensities nor dust maps enter this interface.
"""
import numpy as np
from scipy.special import logsumexp,log_ndtr

def hierarchical_screen_evidence(loglike):
    # Axes: shared slope, independent aperture, Av. Stellar choices/amplitudes already marginalized.
    nsl,ncell,nav=loglike.shape
    log_uniform=logsumexp(np.sum(loglike,axis=1))-np.log(nsl*nav)
    log_variable=logsumexp(np.sum(logsumexp(loglike,axis=2)-np.log(nav),axis=1))-np.log(nsl)
    return float(log_uniform),float(log_variable)

def amplitude_marginal_likelihood(flux,variance,shapes,amax_ujy=1e6):
    """Integrate nonnegative amplitude with common proper uniform [0,amax] prior.
    Flux: (cell,band) in uJy. Shapes: (hypothesis,band), normalized at emitted 1um.
    """
    inv=1/variance
    c=inv@(shapes**2).T
    b=(flux*inv)@shapes.T
    d=np.sum(flux**2*inv,axis=1)[:,None]
    mu=b/c; sig=1/np.sqrt(c)
    hi=(amax_ujy-mu)/sig; lo=-mu/sig
    # Upper bound is intentionally many sigma above finite fits in this experiment.
    if np.min(hi)<8: raise ValueError('Amplitude prior bound intrudes into likelihood; enlarge only as a recorded prior change')
    interval=log_ndtr(mu/sig)
    ll=-.5*np.maximum(d-b*b/c,0)-.5*np.log(c)+.5*np.log(2*np.pi)+interval-np.log(amax_ujy)
    ll-=.5*np.sum(np.log(2*np.pi*variance),axis=1)[:,None]
    chi=np.maximum(d-b*b/c,0)
    return ll,chi,mu

def fit_screen_models(flux,variance,shapes,nslopes,nav,npop):
    ll,chi,amp=amplitude_marginal_likelihood(flux,variance,shapes)
    nc=len(flux)
    ll=ll.reshape(nc,nslopes,nav,npop)
    stellar_marg=logsumexp(ll,axis=3)-np.log(npop)
    lu,lv=hierarchical_screen_evidence(stellar_marg.transpose(1,0,2))
    chi=chi.reshape(nc,nslopes,nav,npop)
    minpop=chi.min(axis=3)
    cu=float(minpop.sum(axis=0).min())
    cv=float(minpop.min(axis=2).sum(axis=0).min())
    return {'logZ_uniform':lu,'logZ_variable':lv,'log_B_variable_uniform':lv-lu,
            'chi2_uniform_profile':cu,'chi2_variable_profile':cv,'n_apertures':nc}
