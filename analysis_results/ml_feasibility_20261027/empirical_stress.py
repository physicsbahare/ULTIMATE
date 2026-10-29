"""Post-protocol HAWK-I-informed PSF-wing/local-covariance sensitivity.

This deliberately retains the provisional ULTIMATE-proxy D50, bandpass and noise
amplitude. It is NOT an empirical ULTIMATE PSF or a complete HAWK-I noise model.
Only Ks uses measured wings and a nearest-neighbor covariance stress. Larger
aperture excess sky noise in the real mosaic is not reproduced by this model.
"""
import json
import numpy as np
import pandas as pd
from scipy.ndimage import convolve1d
from ml_data import OUT, legacy, properties, BANDS
from ml_benchmark import train_predict, bootstrap


def local_kernel(rho):
    # Corr(lag1)=2a/(1+2a²) for [a,1,a] innovations.
    a=(1-np.sqrt(1-2*rho*rho))/(2*rho)
    kernel=np.array([a,1.,a])
    return kernel/np.sqrt(np.sum(kernel**2))


def run():
    empirical=json.loads((OUT/'hawki/empirical_model_inputs.json').read_text())
    beta=empirical['psf']['beta']['median']
    bg=empirical['background']
    kx,ky=local_kernel(bg['rho_adjacent_x']),local_kernel(bg['rho_adjacent_y'])
    feature_file=OUT/'empirical_stress_features.csv'
    if feature_file.exists():
        features=pd.read_csv(feature_file)
    else:
        labels=pd.read_csv(OUT/'operational_labels.csv');rows=[];losses=[]
        original=legacy.p.psf_kernel
        try:
            for label in labels.itertuples():
                _,dusty,_=legacy.load(label.subhalo_id,label.view)
                for mode in ['seeing','glao']:
                    geometry=legacy.p.make_geometry(.1,mode)
                    def kernel(width,pixel,kind):
                        if abs(width-geometry['widths'][2])>1e-9:
                            return original(width,pixel,kind)
                        alpha=width/(2*np.sqrt(2**(1/(beta-1))-1))/pixel
                        axis=np.arange(-int(np.ceil(12*alpha)),int(np.ceil(12*alpha))+1)
                        y,x=np.meshgrid(axis,axis,indexing='ij')
                        result=(1+(x*x+y*y)/alpha**2)**(-beta)
                        return result/result.sum()
                    legacy.p.psf_kernel=kernel
                    rates,loss=legacy.p.render(dusty,geometry)
                    variance=legacy.p.variance(rates,1.)
                    losses.append(dict(subhalo_id=label.subhalo_id,view=label.view,mode=mode,padded_flux_loss=loss))
                    rng=np.random.default_rng(20261027+label.subhalo_id*101+int(label.view[1:])*1000003+100)
                    for draw in range(8):
                        epsilon=rng.standard_normal(rates.shape);rng.standard_normal(epsilon.shape)
                        correlated=epsilon.copy()
                        correlated[2]=convolve1d(convolve1d(epsilon[2],kx,axis=1,mode='wrap'),ky,axis=0,mode='wrap')
                        for case,noise in [('Ks_empirical_wings',epsilon),('Ks_wings_local_covariance',correlated)]:
                            image=rates+np.sqrt(variance)*noise
                            rows.append(dict(subhalo_id=label.subhalo_id,view=label.view,draw=draw,
                                             mode=mode,condition=case,**properties(image,geometry)))
                print('Empirical-informed stress:',label.subhalo_id,label.view,flush=True)
        finally:
            legacy.p.psf_kernel=original
        features=pd.DataFrame(rows);features.to_csv(feature_file,index=False)
        pd.DataFrame(losses).to_csv(OUT/'empirical_stress_transfer.csv',index=False)
    labels=pd.read_csv(OUT/'operational_labels.csv')
    splits=pd.read_csv(OUT/'preliminary_cv_splits.csv')
    predictions=[]
    for (case,mode),subset in features.groupby(['condition','mode']):
        for name in ['ridge','forest']:
            for fold,group in splits.groupby('fold'):
                ids={role:group.loc[group.role==role,'subhalo_id'].to_numpy() for role in ['fit','calibration','outer_test']}
                result=train_predict(subset,labels,ids['fit'],ids['calibration'],ids['outer_test'],'g_J_Ks',name)
                result['case'],result['mode'],result['model'],result['fold']=case,mode,name,fold
                predictions.append(result)
    predictions=pd.concat(predictions,ignore_index=True)
    predictions.to_csv(OUT/'empirical_stress_predictions.csv.gz',index=False)
    galaxy=predictions.groupby(['case','mode','model','target','subhalo_id']).abs_error.mean().reset_index(name='MAE')
    galaxy.to_csv(OUT/'empirical_stress_galaxy_errors.csv',index=False)
    paired=galaxy.pivot(index=['case','model','target','subhalo_id'],columns='mode',values='MAE').reset_index()
    rows=[]
    for values,group in paired.groupby(['case','model','target']):
        gain=group.seeing-group.glao;lo,hi=bootstrap(gain)
        rows.append(dict(zip(['case','model','target'],values),seeing_MAE=group.seeing.mean(),glao_MAE=group.glao.mean(),
                         mean_gain=gain.mean(),CI_low=lo,CI_high=hi,n_galaxies=len(group)))
    pd.DataFrame(rows).to_csv(OUT/'empirical_stress_summary.csv',index=False)
    # Validate the specified nearest-neighbor covariance mechanism separately.
    epsilon=np.random.default_rng(919).normal(size=(1000,1000))
    noise=convolve1d(convolve1d(epsilon,kx,axis=1,mode='wrap'),ky,axis=0,mode='wrap')
    rho_x=float(np.corrcoef(noise[:,:-1].ravel(),noise[:,1:].ravel())[0,1])
    rho_y=float(np.corrcoef(noise[:-1].ravel(),noise[1:].ravel())[0,1])
    assert abs(noise.var()-1)<.01 and abs(rho_x-bg['rho_adjacent_x'])<.01 and abs(rho_y-bg['rho_adjacent_y'])<.01
    (OUT/'empirical_stress_assumptions.json').write_text(json.dumps(dict(
        scope='Exploratory post-protocol sensitivity only, not calibrated ULTIMATE or HAWK-I forecast',
        measured_Ks_beta=beta, Ks_D50='Retain provisional seeing0.588 and GLAO0.390arcsec; do not substitute measured HAWK-I FWHM',
        innovation_variance=float(noise.var()),empirical_rho_x=bg['rho_adjacent_x'],simulated_rho_x=rho_x,
        empirical_rho_y=bg['rho_adjacent_y'],simulated_rho_y=rho_y,
        limitation='Only local pixel covariance and circularized wings; real large-aperture excess noise, anisotropy/field variation not captured',
        noise_amplitude='Provisional simulated electron variance; no transfer of raw ADU amplitudes',
        training='Same frozen grouped folds, no hyperparameter tuning; refit sensitivity models'),indent=2))
    print('Empirical-informed sensitivity completed.',flush=True)


if __name__=='__main__':run()
