from pathlib import Path
import json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/hawki_mpl')
import numpy as np,pandas as pd
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import astropy.units as u
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=Path(__file__).resolve().parent
ir=pd.read_csv(O/'irsa_2mass.csv',dtype={'designation':str,'cc_flg':str,'rd_flg':str,'ph_qual':str});s=pd.read_csv(O/'reduced_psf_candidates.csv');s=s[s.accepted].reset_index(drop=True);w=WCS(fits.getheader(O/'reduced_jan6_image.fits'));radec=w.all_pix2world(s[['x','y']].to_numpy(),0);sc=SkyCoord(radec[:,0]*u.deg,radec[:,1]*u.deg);ic=SkyCoord(ir.ra.to_numpy()*u.deg,ir.dec.to_numpy()*u.deg)
ii,sep,_=sc.match_to_catalog_sky(ic);back=ic.match_to_catalog_sky(sc)[0];cat=fits.getdata(O/'eso_jan6_source_catalogue.fits',1);ch=fits.getheader(O/'eso_jan6_source_catalogue.fits',1);cc=SkyCoord(np.asarray(cat['RA'],float)*u.deg,np.asarray(cat['DEC'],float)*u.deg);ci,csep,_=sc.match_to_catalog_sky(cc);rows=[]
for j in range(len(s)):
 z=ir.iloc[ii[j]];k=ci[j];row=s.iloc[j].to_dict();dra,ddec=ic[ii[j]].spherical_offsets_to(sc[j]);flux=float(cat['Aper_flux_3'][k]);err=float(cat['Aper_flux_3_err'][k]);mag=float(ch['PHOTZP']-2.5*np.log10(flux)-ch['APCOR3']) if flux>0 else np.nan
 h,k2=z.h_m,z.k_m;expected=.03*z.j_m+.97*k2
 qual=(str(z.ph_qual).strip().ljust(3)[2] in 'AB') and str(z.cc_flg).zfill(3)[2]=='0' and str(z.rd_flg).zfill(3)[2] in '124' and z.prox>5
 posmatch=bool(sep[j].arcsec<1 and back[ii[j]]==j)
 stellar=cat['Classification'][k]==-1
 photok=bool(posmatch and qual and csep[j].arcsec<.3 and stellar and flux>0 and err/flux<.1 and abs(z.h_m-z.k_m)<1)
 row.update(designation_2mass=z.designation,match_sep_arcsec=sep[j].arcsec,mutual_nearest=bool(back[ii[j]]==j),catalogue_quality_pass=bool(qual),positional_match=posmatch,delta_ra_cosdec_arcsec=dra.arcsec,delta_dec_arcsec=ddec.arcsec,ph_qual=z.ph_qual,cc_flg=z.cc_flg,rd_flg=z.rd_flg,prox_arcsec=z.prox,k_2mass=k2,h_2mass=h,j_2mass=z.j_m,delta_mag_release_H_formula=mag-(.03*h+.97*k2),k_2mass_sigma=z.k_cmsig,eso_catalogue_sep_arcsec=csep[j].arcsec,eso_classification=float(cat['Classification'][k]),eso_peak_ADU=float(cat['Peak_height'][k]),eso_Aper_flux_3_ADU=flux,eso_Aper_flux_3_error_ADU=err,eso_PHOTZP=float(ch['PHOTZP']),eso_APCOR3=float(ch['APCOR3']),hawki_mag_vega=mag,expected_hawki_vega=expected,delta_mag=mag-expected,photometric_pass=photok)
 rows.append(row)
t=pd.DataFrame(rows);t.to_csv(O/'catalogue_crossmatches.csv',index=False);pos=t[t.positional_match&t.catalogue_quality_pass];phot=t[t.photometric_pass]
def stats(x):
 x=np.asarray(x,float);return dict(n=len(x),median=float(np.median(x)) if len(x) else None,robust_sigma=float(1.4826*np.median(abs(x-np.median(x)))) if len(x) else None,rms=float(np.sqrt(np.mean(x*x))) if len(x) else None)
r=dict(reference='NASA/IPAC IRSA2MASS All-Sky PSC, cone0.055deg; same reference family as pipeline calibration,not held-out independent reference',irsa_rows=len(ir),reduced_candidates=len(t),mutual_matches_within1arcsec=int(t.positional_match.sum()),quality_position_matches=len(pos),photometric_matches=len(phot),astrometric_dra_cosdec_arcsec=stats(pos.delta_ra_cosdec_arcsec),astrometric_ddec_arcsec=stats(pos.delta_dec_arcsec),radial_offset_arcsec=stats(pos.match_sep_arcsec),photometric_hawki_minus_transformed_2mass_mag=stats(phot.delta_mag),photometric_convention='m_Vega=PHOTZP-2.5log10(Aper_flux_3)-APCOR3,releaseDescription87p6; sourcecatalogueflux already carries product normalization,so no extra EXPTIME/CASUEXPT division; Ks_HAWKI=.03J_2MASS+.97Ks_2MASS from actual associated PHOTCAL_TAB (releaseDescription87 instead prints H, recorded discrepancy)',selection='mutual match<1arcsec; accepted isolated unsaturated reducedcompactcandidate; Ks qualityA/B,cc0,rd1/2/4,2MASSprox>5arcsec; photometry additionally ESOcatmatch<.3arcsec,ESOstellarclass-1,fluxSNR>10,H-K<1mag absolute',limitation='Recomputed consistency with2MASS,not independent held-out calibration. No proper-motion epoch propagation;2MASS errors/epoch shifts affect residuals. Full103candidatePSFsample not upgraded to catalogconfirmed stars.')
r['quality_matched_psf']={c:{'median':float(phot[c].median()),'p25':float(phot[c].quantile(.25)),'p75':float(phot[c].quantile(.75))} for c in ['fwhm_circularized_arcsec','beta','q','ee50_circularized_arcsec','ee80_circularized_arcsec']}
r['release_H_formula_delta_mag_median']=float(phot.delta_mag_release_H_formula.median())
r['release_H_formula_delta_mag_robust_sigma']=float(1.4826*(phot.delta_mag_release_H_formula-phot.delta_mag_release_H_formula.median()).abs().median())
(O/'catalogue_validation_summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
fig,axs=plt.subplots(1,2,figsize=(9,4),layout='constrained');axs[0].scatter(pos.delta_ra_cosdec_arcsec,pos.delta_dec_arcsec);axs[0].axhline(0,color='gray');axs[0].axvline(0,color='gray');axs[0].set(xlabel='HAWKI -2MASS RA cosDec (arcsec)',ylabel='HAWKI -2MASS Dec (arcsec)',title=f'{len(pos)} quality2MASS matches');axs[1].errorbar(phot.k_2mass,phot.delta_mag,yerr=phot.k_2mass_sigma,fmt='o');axs[1].axhline(0,color='gray');axs[1].set(xlabel='2MASS Ks (Vega)',ylabel='HAWKI - transformed2MASS (mag)',title=f'{len(phot)} isolated photometric matches');fig.suptitle('Recomputed catalogue consistency; reference used by pipeline, not held-out');fig.savefig(O/'catalogue_validation.png',dpi=170);plt.close(fig)
