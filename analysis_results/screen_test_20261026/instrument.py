from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.interpolate import UnivariateSpline
from forward_physics import photon_rate_jy
O=Path(__file__).resolve().parent
BANDS=['g','r','i','z','Y','J','H','Ks']
CENTRES=np.array([.482,.622,.754,.869,1.02,1.26,1.64,2.15])
WIDTHS=np.array([.14,.14,.15,.10,.10,.17,.28,.31])
AREA=np.pi*(8.0819/2)**2*(1-.277**2)
PIXEL=.1

def setup_instrument():
    path=O/'sources/calculator/sensitivity'
    atm=np.loadtxt(path/'MaunaKea_Sky/ultimate/mktrans_zm_16_10.txt')
    components={x['band']:x for x in json.loads((O/'calculator_exact_components.json').read_text())}
    d50=pd.read_csv(path/'D50_am=1.0.csv')
    out=[]
    for j,b in enumerate(BANDS):
        lam=np.linspace(CENTRES[j]-WIDTHS[j]/2,CENTRES[j]+WIDTHS[j]/2,401)
        if j<4:
            tr=np.full(len(lam),.35*.931*.9)
            # Provisional optical dark-sky surface brightness (AB mag/arcsec2), not a calculator output.
            sky_ab=[22.,21.,20.3,19.5][j]
            flat=photon_rate_jy(np.ones_like(lam),lam,tr,AREA)
            sky=3631*10**(-.4*sky_ab)*flat
            thermal=0.; moon=0.; rn=5.; dark=.001
            seeing=.7; glao=.7
            status='analyst optical scenario; not an ULTIMATE optical specification'
        else:
            tr=.45*.95*.98*np.interp(lam,atm[:,0],atm[:,1])
            flat=photon_rate_jy(np.ones_like(lam),lam,tr,AREA)
            cp=components[b]
            sky=cp['sky_e_s_arcsec2_published']*(1-.277**2)
            moon=cp['moon_e_s_arcsec2_published']*(1-.277**2)
            thermal=cp['telescope_e_s_arcsec2_published']
            rn=16.; dark=.01
            seeing=float(UnivariateSpline(d50.Wav,d50.NOAO_M,k=2)(CENTRES[j]))
            glao=float(UnivariateSpline(d50.Wav,d50.GLAO_M,k=2)(CENTRES[j]))
            status='calculator design scenario; D50 treated as Gaussian FWHM; dark current provisional'
        out.append(dict(band=b,lambda_um=CENTRES[j],width_um=WIDTHS[j],area_m2=AREA,pixel_arcsec=PIXEL,
                        flat_e_s_per_jy=flat,sky_e_s_arcsec2=sky,thermal_e_s_arcsec2=thermal,moon_e_s_arcsec2=moon,
                        background_e_s_pixel=(sky+thermal+moon)*PIXEL**2,read_noise_e=rn,dark_e_s=dark,
                        seeing_fwhm_arcsec=seeing,glao_fwhm_arcsec=glao,dit_s=60.,status=status,wave=lam,throughput=tr))
    return out

def write_instrument():
    inst=setup_instrument()
    pd.DataFrame([{k:v for k,v in x.items() if k not in ['wave','throughput']} for x in inst]).to_csv(O/'instrument_parameters.csv',index=False)
    np.savez_compressed(O/'instrument_bandpasses.npz',**{f"{x['band']}_{k}":x[k] for x in inst for k in ['wave','throughput']})
    return inst
if __name__=='__main__':
    write_instrument();print(pd.read_csv(O/'instrument_parameters.csv').to_string(index=False))
