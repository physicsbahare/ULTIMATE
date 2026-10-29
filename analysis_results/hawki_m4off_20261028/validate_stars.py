from pathlib import Path
import numpy as np,pandas as pd,json
from scipy.spatial import cKDTree
from astropy.io import fits
O=Path(__file__).resolve().parent
s=pd.read_csv(O/'psf_fits.csv');g=pd.read_csv(O/'gaia_dr3.csv');epoch=2019.635;cos=np.cos(np.deg2rad(-26.51));g['ra_epoch']=g.ra+g.pmra.fillna(0)*(epoch-g.ref_epoch)/3.6e6/np.cos(np.deg2rad(g.dec));g['dec_epoch']=g.dec+g.pmdec.fillna(0)*(epoch-g.ref_epoch)/3.6e6
ref=g[(g.ruwe<1.4)&np.isfinite(g.ra_epoch)&np.isfinite(g.dec_epoch)].copy().reset_index(drop=True);pos=np.c_[ref.ra_epoch*cos,ref.dec_epoch]*3600;tree=cKDTree(pos)
with fits.open(O/'tile_catalogue.fits') as hd:
 t=hd[1].data;cat=pd.DataFrame({k:np.asarray(t[k],dtype=float) for k in ['RA','DEC','Classification','Error_bit_flag','Av_conf','Peak_height','Aper_flux_8','Aper_flux_13']})
ctree=cKDTree(np.c_[cat.RA*cos,cat.DEC]*3600);offsets=[];pieces=[]
for field,a in s.groupby('field'):
 a=a.copy();xy=np.c_[a.ra*cos,a.dec]*3600;dist,idx=tree.query(xy);ok=dist<.8;offset=np.median(xy[ok]-pos[idx[ok]],axis=0);corrected=xy-offset;d,ix=tree.query(corrected,k=2);j=ix[:,0];a['gaia_id']=ref.source_id.to_numpy()[j];a['gaia_G']=ref.phot_g_mean_mag.to_numpy()[j];a['gaia_sep_arcsec']=d[:,0];a['gaia_initial_sep_arcsec']=dist;a['gaia_pm_available']=ref.pmra.notna().to_numpy()[j]&ref.pmdec.notna().to_numpy()[j];a['gaia_validated']=(d[:,0]<.35)&(d[:,1]>.7)
 a['registered_ra']=a.ra-offset[0]/3600/cos;a['registered_dec']=a.dec-offset[1]/3600
 cd,ci=ctree.query(xy);a['catalogue_sep_arcsec']=cd;a['ESO_classification']=cat.Classification.to_numpy()[ci];a['ESO_badpixel_count']=cat.Error_bit_flag.to_numpy()[ci];a['ESO_confidence']=cat.Av_conf.to_numpy()[ci];a['catalogue_stellar']=(cd<.8)&(a.ESO_classification==-1)&(a.ESO_badpixel_count==0)
 # Tile catalogue is an image-based consistency check, Gaia is the external reference.
 a['primary_star']=a.accepted&a.gaia_validated&a.catalogue_stellar
 shifted=corrected+np.array([20.,17.]);false=tree.query(shifted)[0]<.35
 offsets.append(dict(field=field,gaia_offset_RAcosDec_arcsec=float(offset[0]),gaia_offset_Dec_arcsec=float(offset[1]),initial_matches=int(ok.sum()),validated=int(a.gaia_validated.sum()),primary=int(a.primary_star.sum()),shifted_chance_match_fraction=float(false.mean()),gaia_magnitude_limit=float(g.phot_g_mean_mag.max()),gaia_query_capped=len(g)==25000))
 pieces.append(a)
s=pd.concat(pieces,ignore_index=True);s.to_csv(O/'validated_stars.csv',index=False);pd.DataFrame(offsets).to_csv(O/'astrometry_and_selection.csv',index=False)
# Match by external identity, not treating two common-exposure products as independent stars.
tile=s[(s.field=='tile0')&s.primary_star].sort_values('gaia_sep_arcsec').drop_duplicates('gaia_id');pw=s[(s['product']=='pawprint')&s.primary_star].copy();pairs=pw.merge(tile,on='gaia_id',suffixes=['_pawprint','_tile'],validate='many_to_one')
for c in ['fwhm_arcsec','q','beta','empirical_R50_R2_arcsec','empirical_R80_R2_arcsec']:
 pairs['delta_'+c]=pairs[c+'_tile']-pairs[c+'_pawprint']
pairs['aperture_magnitude_delta_raw']=-2.5*np.log10(pairs.flux_R2_ADU_tile/pairs.flux_R2_ADU_pawprint)
# Include product zeropoint change; no exposure-time rescaling of calibrated product counts.
pairs['aperture_magnitude_delta_with_ZP']=pairs.aperture_magnitude_delta_raw+28.0850955021825-28.0449210179296
pairs.to_csv(O/'matched_stars.csv',index=False)
print(pd.DataFrame(offsets)[['field','primary','gaia_offset_RAcosDec_arcsec','gaia_offset_Dec_arcsec']].to_string(index=False));print('Matched rows',len(pairs),'unique stars',pairs.gaia_id.nunique());print(pairs.groupby('field_pawprint').size())
