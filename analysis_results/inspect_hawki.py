"""Read-only structural/data integrity audit and provisional image-plane PSF diagnostics."""
from pathlib import Path
import json, warnings, hashlib
import numpy as np
import pandas as pd
from astropy.io import fits
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
import sep
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path('/home/bahareh/ULTIMATE'); O=R/'analysis_results'; F=O/'figures'; F.mkdir(exist_ok=True)
rows=[]; chips=[]; stars=[]; header_dump={}; examples=[]
expected=pd.read_csv(R/'HAWKI_GRAAL/NGC3256/query_results.csv')
for p in sorted((R/'HAWKI_GRAAL/NGC3256').glob('*.fits')):
 row={'filename':p.name,'bytes':p.stat().st_size,'error':''}
 try:
  with warnings.catch_warnings(record=True) as ws, fits.open(p,memmap=False,checksum=True) as hd:
   hd.verify('exception'); h=hd[0].header
   fields={'DATE-OBS':'date_obs','OBJECT':'object','ESO OBS PROG ID':'programme','ESO INS FILT1 NAME':'filter','ESO DET DIT':'dit_s','ESO DET NDIT':'ndit','EXPTIME':'header_exptime_s','ESO INS PIXSCALE':'pixel_scale_arcsec','ESO DPR CATG':'category','ESO DPR TYPE':'type','ESO DPR TECH':'technique','ESO TEL AMBI FWHM START':'dimm_start_arcsec','ESO TEL AMBI FWHM END':'dimm_end_arcsec','ESO OBS AMBI FWHM':'requested_fwhm_arcsec','ESO TEL IA FWHM':'guide_fwhm_arcsec','ESO AOS HO LOOP ST':'ao_ho_loop','ESO AOS JIT LOOP ST':'ao_jitter_loop','ESO AOS TT LOOP ST':'ao_tt_loop','ESO DET SATLEVEL':'header_satlevel'}
   row.update({v:h.get(k) for k,v in fields.items()}); row['dit_ndit_s']=row['dit_s']*row['ndit']; row['pipeline_pro_keys']=sum(k.startswith('ESO PRO ') for k in h)
   header_dump[p.name]={str(i):dict(x.header) for i,x in enumerate(hd)}
   end=max(x.fileinfo()['datLoc']+x.fileinfo()['datSpan'] for x in hd)
   row['expected_file_bytes']=end; row['size_matches']=end==p.stat().st_size; row['hdu_count']=len(hd)
   row['checksum_hdus']=sum('CHECKSUM' in x.header for x in hd); row['astropy_inmemory_checksum_failures']=sum(x.verify_checksum()==0 for x in hd if 'CHECKSUM' in x.header)
   # Astropy normalizes a non-standard PXSPACE card in memory. Verify the unchanged on-disk HDU bytes instead.
   raw_failures=0
   with p.open('rb') as rawfile:
    for x in hd:
     info=x.fileinfo(); rawfile.seek(info['hdrLoc'])
     raw=rawfile.read(info['datLoc']+info['datSpan']-info['hdrLoc'])
     if 'CHECKSUM' in x.header and int(x._compute_checksum(np.frombuffer(raw,dtype=np.uint8))) != 0xffffffff: raw_failures+=1
   row['raw_checksum_failures']=raw_failures
   row['datasum_failures']=sum(x.verify_datasum()==0 for x in hd if 'DATASUM' in x.header)
   imgs=[x for x in hd if isinstance(x,(fits.ImageHDU,fits.PrimaryHDU)) and x.data is not None]; row['image_hdus']=len(imgs)
   for x in imgs:
    a=np.array(x.data,dtype=np.float32,order='C'); eh=x.header
    c={'filename':p.name,'extension':x.name,'nx':a.shape[1],'ny':a.shape[0],'finite_fraction':float(np.isfinite(a).mean()),'minimum':float(np.nanmin(a)),'maximum':float(np.nanmax(a)),'median_raw':float(np.nanmedian(a)),'bunit':eh.get('BUNIT','not supplied'),'checksum_present':'CHECKSUM' in eh}
    # Raw-image diagnostic only; SEP local background removes gradients for detection, not a science reduction.
    bg=sep.Background(a,bw=64,bh=64); sub=a-bg.back(); rms=bg.globalrms
    objs=sep.extract(sub,8,err=bg.rms(),minarea=8)
    positions=np.column_stack([objs['x'],objs['y']]); nearest=cKDTree(positions).query(positions,k=2)[0][:,1] if len(objs)>1 else np.zeros(len(objs))
    fitted=[]
    for j,s in enumerate(objs):
     xx,yy=s['x'],s['y']; ix,iy=int(round(xx)),int(round(yy)); rad=15
     if not (rad+5<ix<a.shape[1]-rad-5 and rad+5<iy<a.shape[0]-rad-5): continue
     if s['flag']!=0 or s['b']/s['a']<.85 or not 1<s['a']<6 or nearest[j]<35: continue
     cut=sub[iy-rad:iy+rad+1,ix-rad:ix+rad+1].astype(float)
     if a[iy-rad:iy+rad+1,ix-rad:ix+rad+1].max()>20000 or cut.max()<30*rms: continue
     Y,X=np.indices(cut.shape); amp=cut.max()
     def model(t):
      A,cx,cy,alpha,beta,b=t; return A*(1+((X-cx)**2+(Y-cy)**2)/alpha**2)**(-beta)+b
     sol=least_squares(lambda t:((model(t)-cut)/rms).ravel(),[amp,rad,rad,3,2.5,0],bounds=([amp*.3,rad-2,rad-2,.5,1.2,-5*rms],[amp*2,rad+2,rad+2,20,10,5*rms]),max_nfev=180)
     A,cx,cy,alpha,beta,b=sol.x; fw=2*alpha*np.sqrt(2**(1/beta)-1); residual=np.sqrt(np.mean((model(sol.x)-cut)**2))/A
     if not sol.success or not 2<fw<15 or residual>.04 or beta>9.8 or beta<1.21: continue
     v={'filename':p.name,'extension':x.name,'x':xx,'y':yy,'fwhm_pix':fw,'fwhm_arcsec':fw*row['pixel_scale_arcsec'],'beta':beta,'peak_snr':A/rms,'relative_rms':residual,'sep_b_over_a':s['b']/s['a']}; stars.append(v); fitted.append(fw*row['pixel_scale_arcsec'])
     if len(examples)<6: examples.append((cut.copy(),model(sol.x),v))
    c['psf_candidates']=len(fitted); c['candidate_fwhm_median_arcsec']=float(np.median(fitted)) if fitted else np.nan; chips.append(c)
   row['warnings']=' | '.join(str(w.message) for w in ws)
   row['structurally_valid']=bool(row['size_matches'] and row['image_hdus']==4 and not row['raw_checksum_failures'] and not row['datasum_failures'])
   if p==sorted((R/'HAWKI_GRAAL/NGC3256').glob('*.fits'))[0]:
    fig,axes=plt.subplots(2,2,figsize=(10,9),layout='constrained')
    for ax,x in zip(axes.flat,imgs):
     a=np.asarray(x.data); sm=a.reshape(512,4,512,4).mean((1,3)); lo,hi=np.percentile(sm,[5,99.7]); im=ax.imshow(sm,origin='lower',cmap='gray',vmin=lo,vmax=hi,extent=(0,2048,0,2048)); ax.set(title=x.name,xlabel='Detector x (native pixels)',ylabel='Detector y (native pixels)'); fig.colorbar(im,ax=ax,shrink=.7,label='Raw counts (header unit unspecified)')
    fig.suptitle('NGC 3256 | raw Ks exposure | 2018-01-03 08:22:19 UTC\nUncalibrated; separate detector panels; 4×4 means for display only',fontsize=12)
    for ext in ['png','pdf']: fig.savefig(F/f'hawki_raw_preview.{ext}',dpi=240)
    plt.close(fig)
 except Exception as e: row['error']=repr(e); row['structurally_valid']=False
 rows.append(row); print(p.name,row['structurally_valid'],flush=True)
pd.DataFrame(rows).to_csv(O/'hawki_metadata.csv',index=False); pd.DataFrame(chips).to_csv(O/'hawki_detector_metadata.csv',index=False); pd.DataFrame(stars).to_csv(O/'hawki_psf_candidates.csv',index=False)
(O/'hawki_headers.json').write_text(json.dumps(header_dump,indent=2,default=str))
actual={Path(x['filename']).stem for x in rows}; wanted=set(expected['dp_id']); (O/'hawki_completeness.json').write_text(json.dumps({'expected':len(wanted),'actual':len(actual),'missing':sorted(wanted-actual),'unexpected':sorted(actual-wanted)},indent=2))
fig,axes=plt.subplots(2,3,figsize=(10,7),layout='constrained')
for ax,(cut,model,v) in zip(axes.flat,examples):
 ax.imshow(cut,origin='lower',cmap='gray'); ax.contour(model,levels=[model.max()*.5],colors='cyan',linewidths=.8); ax.set(title=f"{v['extension']} candidate\nMoffat FWHM {v['fwhm_arcsec']:.3f} arcsec",xlabel='Cutout x (pixels)',ylabel='Cutout y (pixels)')
fig.suptitle('Provisional compact-source PSF fits on raw frames\nCyan: half-maximum model contour; stellar identities not externally confirmed',fontsize=12)
for ext in ['png','pdf']: fig.savefig(F/f'hawki_psf_diagnostics.{ext}',dpi=240)
plt.close(fig)
print('Accepted compact-source fits',len(stars))
