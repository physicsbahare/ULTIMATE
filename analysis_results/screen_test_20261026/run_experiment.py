"""Bounded, restartable static-observation experiment. No machine-learning training."""
from pathlib import Path
import json,time
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from instrument import write_instrument,BANDS
from imaging import make_truths,project_scene,aperture_catalog,observe_apertures,constant_colour_test
from stellar_models import screen_shape_grid
from screen_inference import fit_screen_models
O=Path(__file__).resolve().parent; C=O/'case_results'; C.mkdir(exist_ok=True)
EX=O/'examples'; EX.mkdir(exist_ok=True)
ZLIST=[.1,.3,.6,1.0]; DEPTHS=[.25,1.,4.]; MODES=['seeing','glao']; NREP=3

def run(recompute=False):
    inst=write_instrument(); shapes={}
    for z in ZLIST:
        for prior in ['near_clear','broad']:
            shapes[z,prior]=screen_shape_grid(z,inst,prior)
    allrows=[]; transfer=pd.read_csv(O/'transfer_validation.csv').to_dict('records') if (O/'transfer_validation.csv').exists() and not recompute else []; generative=[]
    for oi,ori in enumerate(['O1','O2','O3','O4','O5']):
        cache=np.load(O/'input_cache'/f'{ori}_structured_broadbands.npz')
        truths,gen=make_truths(cache); generative.append({'orientation':ori,**gen})
        zvalues=ZLIST if ori=='O1' else [.3]
        for zi,z in enumerate(zvalues):
            for mode in MODES:
                casefile=C/f'{ori}_z{z}_{mode}.csv'
                if casefile.exists() and not recompute:
                    allrows.extend(pd.read_csv(casefile).to_dict('records')); print('Resume:',casefile.name,flush=True); continue
                case=[]; rates_by_truth={}; scale=None
                for truth,images in truths.items():
                    rate,widths,scale=project_scene(images,cache['wave_um'],z,inst,mode)
                    rates_by_truth[truth]=rate
                    transfer.append({'orientation':ori,'z':z,'mode':mode,'truth':truth,**scale,'Ks_fwhm_arcsec':widths[-1]})
                # Same fixed coordinate lattice for every truth and mode; observable SNR eligibility below.
                positions=aperture_catalog(rate.shape,scale['kpc_per_arcsec'])
                hours_values=DEPTHS if ori=='O1' else [1.]
                for hours in hours_values:
                    for ti,(truth,rate) in enumerate(rates_by_truth.items()):
                        # Known-population separation is explicitly an oracle upper-bound diagnostic.
                        other=rates_by_truth['uniform_control']; tot=hours*3600; nexp=int(tot/60)
                        oracle=0
                        yy,xx=np.indices(rate.shape[1:]); central=np.hypot(yy-rate.shape[1]/2,xx-rate.shape[2]/2)*.1*scale['kpc_per_arcsec']<20
                        for j,b in enumerate(inst):
                            variance=(rate[j]+b['background_e_s_pixel']+b['dark_e_s'])*tot+nexp*b['read_noise_e']**2
                            a=other[j][central]; y=rate[j][central]; w=tot**2/variance[central]
                            factor=np.sum(a*y*w)/np.sum(a*a*w)
                            if j>=4: oracle+=np.sum((y-factor*a)**2*w)
                        for rep in range(NREP):
                            seed=20261026+oi*100000+int(z*100)*1000+int(hours*100)*10+ti*100+rep*3+(mode=='glao')
                            phot,error,clean,noise,example=observe_apertures(rate,widths,inst,hours,np.random.default_rng(seed),positions)
                            good=(phot[:,1]/error[:,1]>5)&(phot[:,-1]/error[:,-1]>5)
                            if good.sum()<2:
                                case.append({'orientation':ori,'z':z,'mode':mode,'hours':hours,'truth':truth,'rep':rep,'n_apertures':int(good.sum()),'status':'insufficient observable apertures'}); continue
                            # Diagnostic of spatial colour variation: population and dust both contribute.
                            colour=constant_colour_test(phot[good],error[good],1,7)
                            for prior in ['near_clear','broad']:
                                sh,nsl,nav,npop=shapes[z,prior]
                                variance=error[good]**2+(.05*np.maximum(abs(phot[good]),error[good]))**2
                                fit=fit_screen_models(phot[good],variance,sh,nsl,nav,npop)
                                case.append({'orientation':ori,'z':z,'mode':mode,'hours':hours,'truth':truth,'rep':rep,'seed':seed,'population_prior':prior,'model_discrepancy_fraction':.05,'status':'fit',**fit,**colour,**noise,'n_candidate_apertures':len(positions),'oracle_NIR_separation_snr':np.sqrt(oracle),'kpc_per_arcsec':scale['kpc_per_arcsec'],'common_fwhm_arcsec':.8,'Ks_input_fwhm_arcsec':widths[-1]})
                            # Native NIR-only colour comparison at a common NIR PSF, preserving its GLAO resolution benefit.
                            nir_target=max(widths[4:])+.02
                            nirf,nire,nirc,nirnoise,_=observe_apertures(rate[4:],widths[4:],inst[4:],hours,np.random.default_rng(seed+50000),positions,target_fwhm=nir_target)
                            nirgood=(nirf[:,0]/nire[:,0]>5)&(nirf[:,-1]/nire[:,-1]>5)
                            nircol=constant_colour_test(nirf[nirgood],nire[nirgood],0,3) if nirgood.sum()>1 else {}
                            for row in case[-2:]:
                                row.update({'nir_common_fwhm_arcsec':nir_target,'nir_n_apertures':int(nirgood.sum()),**{'nir_'+k:v for k,v in nircol.items()}})
                            if ori=='O1' and z==.3 and hours==1. and rep==0:
                                np.savez_compressed(EX/f'{truth}_{mode}.npz',rate=rate.astype(np.float32),widths=widths,positions=positions,eligible=good,phot_ujy=phot,error_ujy=error,clean_ujy=clean,kpc_per_arcsec=scale['kpc_per_arcsec'],**{f'image_{b}_ujy':a.astype(np.float32) for b,a in example.items()})
                pd.DataFrame(case).to_csv(casefile,index=False); allrows.extend(case)
                print(ori,z,mode,'rows',len(case),'time',time.strftime('%H:%M:%S'),flush=True)
    pd.DataFrame(allrows).to_csv(O/'screen_model_results.csv',index=False)
    pd.DataFrame(transfer).to_csv(O/'transfer_validation.csv',index=False)
    pd.DataFrame(generative).to_csv(O/'screen_control_parameters.csv',index=False)
    print('Completed',len(allrows),'fits',flush=True)
if __name__=='__main__':run()
