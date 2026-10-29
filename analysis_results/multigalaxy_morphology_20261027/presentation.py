"""Static publication figures and evidence-backed reports, never changes analysis data."""
from pathlib import Path
import json
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
O=Path(__file__).resolve().parent;F=O/'figures'
COLORS={'LSST_g':'#0072B2','2MASS_Ks':'#D55E00','seeing':'#0072B2','glao':'#D55E00'}
LABELS={'R50':r'$R_{50}$ [kpc]','C':r'$C=5\log_{10}(R_{80}/R_{20})$','A':'Rotational asymmetry','q':'Apparent axis ratio'}
ORDER=['GALEX_FUV','GALEX_NUV','Johnson_U','LSST_u','Johnson_B','LSST_g','Johnson_V','LSST_r','Johnson_R','LSST_i','Johnson_I','Euclid_VIS','LSST_z','LSST_y','Euclid_Y','2MASS_J','Euclid_J','2MASS_H','Euclid_H','2MASS_Ks','WISE_W1','WISE_W2']

def save(fig,name):
 fig.savefig(F/f'{name}.png',dpi=180,bbox_inches='tight');fig.savefig(F/f'{name}.pdf',bbox_inches='tight');plt.close(fig)

def run():
 F.mkdir(exist_ok=True)
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':120,'savefig.facecolor':'white','axes.grid':True,'grid.alpha':.15})
 gal=pd.read_csv(O/'galaxy_level_morphology.csv');base=pd.read_csv(O/'primary_dust_bias.csv');summ=pd.read_csv(O/'galaxy_bootstrap_summary.csv');meta=pd.read_csv(O/'galaxy_inventory.csv');bs=pd.read_csv(O/'GLAO_bootstrap_summary.csv');gain=pd.read_csv(O/'galaxy_GLAO_gains.csv')
 parent=pd.read_csv(O.parents[1]/'data/TNG50_SKIRT_DR1_extra/eligible_catalogue.csv')
 fig,ax=plt.subplots(1,2,figsize=(11,4),layout='constrained')
 ax[0].scatter(parent.log10_stellar_mass,parent.sSFR_yr_inverse,s=8,c='.8',label='Eligible catalogue (1153)')
 for role,m in [('development','s'),('held_out','o')]:
  s=meta[meta.role==role];ax[0].scatter(s.log10_stellar_mass,s.sSFR_yr_inverse,s=38,marker=m,edgecolor='k',lw=.4,label=f'{role}: {len(s)} galaxies')
 ax[0].set(yscale='symlog',ylim=(-1e-12,1e-8),xlabel=r'$\log_{10}(M_*/M_\odot)$',ylabel=r'sSFR [yr$^{-1}$] (zero retained)');ax[0].set_yscale('symlog',linthresh=1e-13);ax[0].set_ylim(-1e-14,parent.sSFR_yr_inverse.max()*1.4);ax[0].legend(fontsize=8)
 cell=pd.read_csv(O/'selection_cells.csv');mat=cell.pivot(index='activity_stratum',columns='mass_stratum',values='eligible_cell_N');im=ax[1].imshow(mat,origin='lower',cmap='Blues',aspect='auto')
 for (i,j),v in np.ndenumerate(mat.to_numpy()):ax[1].text(j,i,str(v),ha='center',va='center',color='white' if v>mat.to_numpy().max()*.65 else 'black')
 ax[1].set(xlabel='Stellar-mass quintile',ylabel='Activity stratum (0 = zero SFR)',title='Eligible counts; one new galaxy selected per cell');fig.colorbar(im,ax=ax[1],label='Eligible galaxies')
 fig.suptitle('A balanced feasibility sample, with unequal selection probabilities');save(fig,'01_sample_selection')
 fig,axs=plt.subplots(2,2,figsize=(13,8),layout='constrained')
 for ax,metric in zip(axs.flat,['R50','C','A','q']):
  s=summ[(summ.scope=='all_26')&(summ.metric=='delta_'+metric)].set_index('band').reindex(ORDER)
  x=np.arange(len(s));ax.axhline(0,color='.4',lw=1);ax.errorbar(x,s.galaxy_median,yerr=[s.galaxy_median-s.median_CI_low,s.median_CI_high-s.galaxy_median],fmt='o',c='#0072B2',capsize=2)
  for ix,b in enumerate(ORDER):
   z=gal[gal.band==b];ax.scatter(np.full(len(z),ix),z['delta_'+metric+'_mean'],s=7,color='.5',alpha=.35,zorder=1)
  ax.set(xticks=x,xticklabels=[b.replace('_',' ') for b in ORDER],ylabel=r'$\Delta_{\rm dust}$ '+LABELS[metric]);ax.tick_params(axis='x',labelrotation=90,labelsize=8)
 fig.suptitle('Dust-induced morphology: 26 galaxy averages; R < 12 kpc\nPoints: galaxy median; intervals: 95% galaxy bootstrap; grey: individual galaxy means');save(fig,'02_wavelength_dependence')
 ids=meta.sort_values('log10_stellar_mass').subhalo_id.to_numpy();fig,axs=plt.subplots(1,4,figsize=(15,10),sharey=True,layout='constrained')
 for ax,metric in zip(axs,['R50','C','A','q']):
  ax.axvline(0,color='.6',lw=1)
  for b,off in [('LSST_g',-.13),('2MASS_Ks',.13)]:
   s=gal[gal.band==b].set_index('subhalo_id').reindex(ids);v=s['delta_'+metric+'_mean'];ax.errorbar(v,np.arange(len(ids))+off,xerr=[v-s['delta_'+metric+'_min'],s['delta_'+metric+'_max']-v],fmt='o',ms=3,c=COLORS[b],elinewidth=.8,label=b.replace('_',' '))
  ax.set(xlabel=r'$\Delta_{\rm dust}$ '+LABELS[metric],yticks=np.arange(len(ids)),yticklabels=ids);ax.legend(fontsize=8)
 axs[0].set_ylabel('Subhalo ID (ordered by stellar mass)');fig.suptitle('Galaxy means and full range over five correlated viewing directions\nAperture-conditioned native morphology, no observational PSF');save(fig,'03_per_galaxy_bias')
 fig,axs=plt.subplots(2,3,figsize=(12,7),layout='constrained')
 for row,metric in enumerate(['R50','C']):
  for col,x in enumerate(['log10_stellar_mass','sSFR_yr_inverse','dust_mass_field_Msun']):
   ax=axs[row,col];s=gal[gal.band=='LSST_g'];ax.axhline(0,c='.6',lw=1)
   sc=ax.scatter(s[x],s['delta_'+metric+'_mean'],c=s.q_clear_mean,cmap='viridis',vmin=0,vmax=1,s=38,edgecolor='k',lw=.3)
   if col==1:ax.set_xscale('symlog',linthresh=1e-13)
   if col==2:
    ax.set_xscale('symlog',linthresh=1e3);ax.set_xticks([0,1e5,1e7,1e9],['0',r'$10^5$',r'$10^7$',r'$10^9$'])
   ax.set(xlabel=[r'$\log_{10}(M_*/M_\odot)$',r'sSFR [yr$^{-1}$]; zero retained',r'Projected field dust mass [$M_\odot$]'][col],ylabel=r'$\Delta_{\rm dust}$ '+LABELS[metric])
 fig.colorbar(sc,ax=axs.ravel().tolist(),label='Mean intrinsic Ks apparent q' if False else 'Mean intrinsic g apparent q',shrink=.8);fig.suptitle('Exploratory galaxy-property dependence (26 objects, no population fit)');save(fig,'04_property_dependence')
 fig,axs=plt.subplots(2,4,figsize=(15,7),layout='constrained')
 for row,target in enumerate(['preservation_abs_error','dust_delta_abs_error']):
  for col,metric in enumerate(['R50','C','A','q']):
   ax=axs[row,col];s=gain[(gain.band=='2MASS_Ks')&(gain.pairing=='independent_clear')&(gain.metric==metric)&(gain.target==target)]
   ax.scatter(s.seeing,s.glao,c=np.where(s.role=='held_out','#0072B2','#D55E00'),s=30,edgecolors='k',linewidths=.3);mx=max(s.seeing.max(),s.glao.max())*1.08;ax.plot([0,mx],[0,mx],'--',c='.5');ax.set(xlim=(0,mx),ylim=(0,mx),xlabel='Seeing mean absolute error',ylabel='GLAO mean absolute error',title=LABELS[metric]);ax.set_aspect('equal',adjustable='box')
   ss=bs[(bs.scope=='all_26')&(bs.band=='2MASS_Ks')&(bs.pairing=='independent_clear')&(bs.metric==metric)&(bs.target==target)].iloc[0]
   ax.text(.04,.95,f"Gain {ss.mean_gain:.3g}\n95% CI [{ss.CI_low:.3g}, {ss.CI_high:.3g}]\n{int(ss.n_improved)}/{int(ss.n_galaxies)} improved",transform=ax.transAxes,va='top',fontsize=8)
   ax.xaxis.set_major_locator(MaxNLocator(4));ax.yaxis.set_major_locator(MaxNLocator(4))
   if metric=='A':ax.set_title('Noise-subtracted asymmetry')
 axs[0,0].text(-.42,.5,'Dusty morphology preservation',transform=axs[0,0].transAxes,rotation=90,va='center');axs[1,0].text(-.42,.5,'Recovery of dusty − clear',transform=axs[1,0].transAxes,rotation=90,va='center')
 fig.suptitle('Conditional Ks performance: fixed-rest-band z = 0.1, 1 h per band\nBelow diagonal favors GLAO; blue held-out / orange development; intervals bootstrap galaxies');save(fig,'05_GLAO_morphology_accuracy')
 sg=pd.read_csv(O/'galaxy_spatial_information.csv');fig,axs=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
 for ax,target in zip(axs,['dusty_morphology','dust_imprint']):
  for mode in ['seeing','glao']:
   ss=sg[(sg.target==target)&(sg.SB_stratum.astype(str)=='all')&(sg['mode']==mode)]
   for sid,g in ss.groupby('subhalo_id'):ax.plot(g.scale_kpc,g.NRMSE,color=COLORS[mode],alpha=.12,lw=.7)
   av=ss.groupby('scale_kpc').NRMSE.median();ax.plot(av.index,av.values,'o-',color=COLORS[mode],label=mode,lw=2)
  ax.set(xlabel='Analysis FWHM [kpc]',ylabel='Normalized RMS structure error',title=target.replace('_',' '),xticks=[.5,1,2]);ax.legend()
 fig.suptitle('Ks spatial information transfer, without optical PSF matching\nR < 8 kpc; weak truth imprints excluded from normalized errors, retained in absolute-error tables');save(fig,'06_spatial_information')
 rb=pd.read_csv(O/'aperture_center_robustness.csv');fig,axs=plt.subplots(2,2,figsize=(10,8),layout='constrained')
 for row,b in enumerate(['LSST_g','2MASS_Ks']):
  for col,setting in enumerate(['30','offset0.2']):
   ss=rb[(rb.band==b)&(rb.setting_alternative.astype(str)==setting)].groupby('subhalo_id')[['delta_R50_primary','delta_R50_alternative']].mean()
   ax=axs[row,col];ax.scatter(ss.delta_R50_primary,ss.delta_R50_alternative,c=COLORS[b],s=25);v=np.concatenate([ss.delta_R50_primary,ss.delta_R50_alternative]);lo,hi=v.min()-.03,v.max()+.03;ax.plot([lo,hi],[lo,hi],'--',c='.5');ax.axhline(0,c='.8');ax.axvline(0,c='.8');ax.set(xlabel='Primary dust ΔR50 [kpc]',ylabel='Alternative dust ΔR50 [kpc]',title=f"{b.replace('_',' ')}: "+('R < 30 kpc' if col==0 else 'Center shifted +0.2 kpc'))
 fig.suptitle('Aperture and center sensitivity: galaxy means');save(fig,'07_measurement_robustness')
 fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
 for ax,b in zip(axs,['LSST_g','2MASS_Ks']):
  for sid,s in base[base.band==b].groupby('subhalo_id'):
   s=s.sort_values('q_clear');ax.plot(s.q_clear,s.delta_R50,color=COLORS[b],alpha=.35,lw=.8);ax.scatter(s.q_clear,s.delta_R50,s=9,c=COLORS[b])
  ax.axhline(0,c='.5');ax.set(xlabel='Intrinsic apparent q (not physical inclination)',ylabel='Dust ΔR50 [kpc]',title=b.replace('_',' '))
 fig.suptitle('Viewing-angle dependence: each connected line is one galaxy');save(fig,'08_orientation_dependence')
 # Deterministic representative cases: largest/worst paired concentration gain and weakest dust object.
 gg=gain[(gain.band=='2MASS_Ks')&(gain.pairing=='independent_clear')&(gain.metric=='C')&(gain.target=='dust_delta_abs_error')].sort_values('gain')
 picks=[(int(gg.iloc[-1].subhalo_id),'Largest C recovery gain'),(int(gg.iloc[0].subhalo_id),'Smallest C recovery gain'),(int(meta.sort_values('dust_mass_field_Msun').iloc[0].subhalo_id),'Weak/zero projected dust')]
 fig,axs=plt.subplots(3,6,figsize=(16,8),layout='constrained');example_rows=[]
 for row,(sid,label) in enumerate(picks):
  with np.load(O/'cache'/str(sid)/'O1_example.npz') as z:
   pix=float(z['pixel_kpc']);extent=np.array([-1,1,-1,1])*z['reference_clear'].shape[-1]/2*pix
   ims=[z['reference_clear'][0],z['reference_dusty'][0],z['reference_clear'][2],z['reference_dusty'][2],z['seeing_dusty_expected'][2],z['glao_dusty_expected'][2]]
   for col,im in enumerate(ims):
    norm=max(ims[0 if col<2 else 2].max(),1e-30);a=axs[row,col];image_artist=a.imshow(np.arcsinh(im/norm*100)/np.arcsinh(100),origin='lower',extent=extent,vmin=0,vmax=1,cmap='magma');a.set(xlim=(-12,12),ylim=(-12,12));a.grid(False)
    if row==0:a.set_title(['g clear reference','g dusty reference','Ks clear reference','Ks dusty reference','Ks dusty seeing','Ks dusty GLAO'][col],fontsize=10)
    if col==0:a.set_ylabel(f'{sid}, O1\n{label}\ny [kpc]',fontsize=9)
    else:a.set_yticklabels([])
    if row==2:a.set_xlabel('x [kpc]')
  example_rows.append(dict(subhalo_id=sid,view='O1',selection=label,basis='galaxy-averaged concentration-error gain; images show fixed O1, not optimized orientation'))
 pd.DataFrame(example_rows).to_csv(O/'representative_cases.csv',index=False)
 fig.colorbar(image_artist,ax=axs.ravel().tolist(),shrink=.7,label='Asinh intensity / clear-band peak scale')
 fig.suptitle('Representative cases include weak and unfavorable results\nAsinh intensity normalized to clear-band peak (same scale within each g or Ks row); conditional noiseless transfer');save(fig,'09_representative_images')
 sensitivity_fig()
 control_figure()
 write_report(meta,base,gal,summ,bs,gain)
 quantitative_addendum()

def sensitivity_fig():
 path=O/'sensitivity_accuracy.csv'
 if not path.exists():return
 s=pd.read_csv(path);s=s[(s.band=='2MASS_Ks')&(s.pairing=='independent_clear')]
 main=pd.read_csv(O/'measurement_accuracy_draws.csv');main=main[(main.band=='2MASS_Ks')&(main.pairing=='independent_clear')&(main.view=='O1')&(main.subhalo_id.isin(s.subhalo_id.unique()))]
 allx=pd.concat([s,main]);fig,axs=plt.subplots(1,4,figsize=(14,4.3),layout='constrained')
 conds=[(.1,1.,'gaussian'),(.1,1.,'moffat'),(.05,1.,'gaussian'),(.1,.25,'gaussian'),(.1,4.,'gaussian')]
 for ax,m in zip(axs,['R50','C','A','q']):
  rows=[]
  for z,h,k in conds:
   ss=allx[(allx.z==z)&(allx.hours==h)&(allx.kind==k)&(allx.metric==m)].groupby(['subhalo_id','mode']).dust_delta_abs_error.agg(['mean','count']);ss.loc[ss['count']<6,'mean']=np.nan;ss=ss['mean'].unstack('mode');v=ss['seeing']-ss['glao'];rows.append(v)
  for i,v in enumerate(rows):ax.scatter(np.full(len(v),i),v,c='#0072B2',s=25);ax.plot([i-.2,i+.2],[v.mean()]*2,c='k')
  ax.axhline(0,c='.5');ax.set(xticks=range(5),xticklabels=['Baseline','Moffat','z=0.05','0.25 h','4 h'],ylabel='Seeing error − GLAO error',title=LABELS[m]);ax.tick_params(axis='x',labelrotation=45)
 fig.suptitle('Focused sensitivity: up to five development galaxies, O1 only; at least 6/8 joint draws\nKs dust-difference recovery; no universal wings/depth/distance forecast');save(fig,'10_instrument_sensitivity')

def write_report(meta,base,gal,summ,bs,gain):
 # Filled from validated tables; report authoring is deterministic and recomputable.
 selection=json.loads((O/'selection_audit.json').read_text());validation=json.loads((O/'numerical_validation.json').read_text())
 lines=['# Dust-induced morphology across 26 TNG50-SKIRT galaxies','', '## Executed scope and central findings','',f"Analysed {len(meta)} independent galaxies, five correlated views each, 22 matched rest-frame broadband pairs: {len(base)} primary galaxy/view/band comparisons. Eight Gaussian noise draws (exact split-read first/second moments) per scene/strategy at one selected observing condition. The original benchmark and four additional galaxies were development objects; the remaining 21 were evaluated with the saved protocol. No new science data, packages, ML, or geometry fits were used.",'']
 for band in ['LSST_g','2MASS_Ks']:
  s=summ[(summ.scope=='all_26')&(summ.band==band)&(summ.metric=='delta_R50')].iloc[0]
  lines.append(f"- {band}: median of galaxy-mean dust ΔR50 = {s.galaxy_median:.4f} kpc; galaxy-bootstrap 95% interval [{s.median_CI_low:.4f}, {s.median_CI_high:.4f}]. Galaxy means are positive / negative / near-zero in {int(s.n_positive)} / {int(s.n_negative)} / {int(s.n_near_zero)} objects. Range [{s.minimum:.4f}, {s.maximum:.4f}] kpc. The median within-galaxy viewing SD is {s.median_within_galaxy_view_SD:.4f} kpc; between-galaxy SD is {s.between_galaxy_SD:.4f} kpc.")
 lines+=['','Dust effects do not have an imposed sign. The wavelength comparison preserves filter identity; 2MASS, Euclid and LSST products are not labelled ULTIMATE filters. Native sizes refer to light within R<12 kpc, not total-galaxy sizes.','', '## Conditional seeing versus GLAO','', 'Predeclared gain = seeing mean absolute error minus GLAO mean absolute error. Each galaxy averages its views after averaging its noise draws. Positive values mean improved preservation/recovery. The following table reports **2MASS Ks only** and uses independent clear versus dusty observation noise; strategy innovations remain paired. The clear counterpart is simulation truth for scoring, not an available observational input.','', '| Metric | Target | Seeing mean error | GLAO mean error | Mean gain [95% galaxy bootstrap] | Improved galaxies |','|---|---|---:|---:|---:|---:|']
 for target in ['preservation_abs_error','dust_delta_abs_error']:
  for metric in ['R50','C','A','q']:
   s=bs[(bs.scope=='all_26')&(bs.band=='2MASS_Ks')&(bs.pairing=='independent_clear')&(bs.metric==metric)&(bs.target==target)].iloc[0]
   lines.append(f"| {metric} | {'Dusty morphology' if target.startswith('preservation') else 'Dusty-minus-clear'} | {s.seeing_mean_error:.5f} | {s.glao_mean_error:.5f} | {s.mean_gain:.5f} [{s.CI_low:.5f}, {s.CI_high:.5f}] | {int(s.n_improved)}/{int(s.n_galaxies)} |")
 lines+=['','Noisy q failures use jointly valid strategy draws; each included galaxy needs at least 6/8 such draws in every view. The last column gives the actual eligible denominator. All original 26 objects remain in noiseless results. galaxy_observing_accuracy.csv records eligibility and valid-draw counts; missing/noisy moments are not repaired by clipping.','', 'R50 errors have kpc units; C, A and q are dimensionless. Raw and noise-corrected asymmetry are both retained. The expected-|noise| subtraction is a defined estimator and can overcorrect genuine asymmetric pixels; neither estimator has a universal unbiasedness guarantee. g has the same seeing PSF and identical innovations in both strategies, providing a zero-gain control. Shared-counterfactual-noise results are separately tabulated and must not be mistaken for uncertainty from independent observations. Monte Carlo SE and between-view/galaxy scatter remain separate in the tables. Eight draws bound computational cost and do not establish tail probabilities.','', '## Sample and independence','', f"The official saved catalogue has {selection['parent_N']} galaxies; {selection['eligible_N']} were eligible for the seeded 25-cell selection. Zero-SFR fraction: parent {selection['parent_zero_SFR_fraction']:.3f}, selected extra sample {selection['selected_zero_SFR_fraction']:.3f}. Selection probabilities vary from {selection['min_selection_probability']:.4f} to {selection['max_selection_probability']:.4f}; there is one new galaxy per mass-quintile/activity cell. Selected extra log stellar mass spans {selection['selected_logmass_range'][0]:.3f}–{selection['selected_logmass_range'][1]:.3f}. The original galaxy is an additional convenience benchmark. The four extra development objects all came from the lowest mass quintile (the first four selected cells), so the held-out 21-object subset has only one object in that quintile and five in each other quintile; it is not a fresh balanced or population-random draw. Equal-weight results describe this balanced sample, not a volume-complete population. The bootstrap is a conditional resampling summary of selected galaxies, not a design-corrected population confidence statement. Five fixed directions do not represent five independent galaxies or a verified isotropic inclination sample.",'', f"There are {int((meta.SFR_Msun_yr==0).sum())} zero-SFR galaxies, of which {int(((meta.SFR_Msun_yr==0)&(meta.dust_mass_field_Msun>0)).sum())} have positive field dust mass. Physical projected dust maps, not SFR, supply these diagnostics. Field masses are mean sums over projections on the 160-kpc FITS field; R12/R30 masses and inter-view scatter are supplied. Tiny signed projection roundoff in physical maps is recorded without altering the images. Apparent light q is not a physical inclination. Stellar half-mass radius is not an assigned morphology class.",'', '## Zero-projected-dust controls and attribution limit','', 'The four zero-projected-dust objects are empirical source-product checks, not assumed perfect nulls for every unresolved attenuation component. They show nonzero pair attenuation and shape residuals; zero_projected_dust_summary.csv quantifies them before and after 0.5/1-kpc smoothing. These differences may reflect source/filter integration, projection, radiative-transfer noise or unresolved components. Their origin cannot be separated with the supplied products. No universal offset is subtracted and no error map is invented. Thus the tables measure operational DR1 dusty-minus-clear contrasts; small values are not validated as pure physical dust effects. Numerical implementation validation passes, but source-product physical-null calibration is unresolved.','', 'Asymmetry preservation gains reverse sign between raw and noise-subtracted estimators in this scenario. Report both, and do not promote a robust asymmetry benefit. Concentration and R50 are the stronger instrumental comparisons; dust-difference recovery remains a separate test.','', '## Methods and quality','', 'All original archives are read only. Current SHA256 and byte lengths are reconciled with the downloader state for the 25 extra archives; the extra archives are byte-identical to the downloader CRC-validated files, and the original archive receives an independent gzip EOF/trailer check. CRC_evidence records whether the check is inherited through identical SHA256 or independent; no redundant extra-archive CRC scan is claimed. All 240 members per galaxy are checked for identity, field/pixel dimensions, centered WCS, units, finite values and complete dusty/clear matching. A compact g/J/Ks/dust cache avoids full FITS extraction. Broadband pixels are nonnegative; physical projection maps allow documented floating-point roundoff only. No failed pairs or inconvenient signs are silently discarded. See archive_inventory.csv, fits_inventory.csv and galaxy_inventory.csv.','', 'Primary measurement uses the same simulation origin, circular R<12 kpc aperture, coordinate grid, PSF and segmentation for each pair. No data-dependent segmentation or center minimization is used. R20/R50/R80 use the first signed cumulative-flux crossing on pixel-center radii; C=5 log10(R80/R20); asymmetry is the full |I−I180| sum divided by flux (no extra factor 1/2); q uses fixed-origin flux-weighted second moments. Noise can make signed curves nonmonotonic; the rule remains fixed and finite/nonpositive-flux failures are recorded. Integrated attenuation uses the aperture flux ratio. Effective local attenuation keeps valid negative values, but is neither optical depth nor a physical dust-mass measurement.','', f"Analytic morphology tests: {validation['analytic_tests_passed']}; original pilot reproduction max absolute error {validation['published_morphology_max_error']:.3g}; maximum tested Gaussian padded flux loss {validation['gaussian_padded_flux_loss']:.3g}. Exact aggregate Poisson plus independent read-noise sampling validates split-exposure moments. The numerical gate passed before held-out evaluation. These tests validate implementation, not the unresolved radiative-transfer/source uncertainty or final instrument calibration.",'', '## Aperture, center, spatial scale and instrument robustness','']
 quality=pd.read_csv(O/'aperture_quality.csv');lines.append(f"{quality[quality.aperture_limited].subhalo_id.nunique()}/26 galaxies have at least one g/Ks view/scene with F12/F30<0.8. These are retained and flagged; interpreting the primary R50 as a total size would be wrong. R20/R30 apertures and ±0.2-kpc center shifts are evaluated for every g/Ks pair in aperture_center_robustness.csv. Figures show the consequences rather than selecting the best aperture after seeing the sample.")
 robust=pd.read_csv(O/'aperture_center_robustness.csv')
 for setting in ['30','offset0.2','offset-0.2']:
  for band in ['LSST_g','2MASS_Ks']:
   s=robust[(robust.setting_alternative.astype(str)==setting)&(robust.band==band)];lines.append(f"- {band}, {setting}: median |change in dust ΔR50| = {abs(s.change_delta_R50).median():.4f} kpc; {int(s.sign_flip_R50.sum())}/{len(s)} material view-level sign flips (>10⁻⁶ kpc in each measurement).")
 lines+=['','Ks fine/broad fractional structure is measured natively at 0.5/1/2-kpc smoothing FWHM, without matching away the finer NIR PSF. Noiseless structure errors and correlations separate dusty morphology preservation from a truth-isolated dusty-minus-clear imprint. R<8 kpc avoids the most severe broad-filter edge sensitivity. Near-zero reference RMS≤10⁻⁵ is excluded from normalized error only; absolute errors remain. Surface-brightness terciles and all excluded normalized cases are tabulated. This is information transfer, not individual dust-feature identification.','', 'Focused sensitivity covers the five development galaxies, O1 only: equal-D50 Moffat beta=2.5, lower distance z=0.05 and 0.25/4h per band. It does not establish sample-wide robustness to all PSF wings or exposure assumptions. The Gaussian spatial comparison has no noise threshold-crossing classifier. Longer exposure cannot recover frequencies eliminated by a PSF.','', '## Physical scope of the observing experiment','', 'Primary physical results are direct z=0 rest-band paired measurements, conditional on the unresolved source-product residuals above. The observing comparison artificially places each unchanged scene at z=0.1, with fixed size, luminosity, populations and dust; Flat LCDM H0=70, Om0=0.3, frequency-specific intensity /(1+z)^3, flux-conserving area resampling and 0.1-arcsec detector pixels. It is not galaxy evolution or exact observer-frame synthetic photometry. Rest 2MASS Ks shifts beyond ordinary observer Ks at this distance. Nominal-band throughput/noise conversion is therefore a conditional proxy; no missing spectral cube, K correction, or final ULTIMATE passband is invented.','', 'Gaussian D50=FWHM widths: g 0.700 arcsec both modes, J 0.658/0.508 arcsec, Ks 0.588/0.390 arcsec. Detector, throughput, sky, thermal, moon, dark and read assumptions are inherited provisionally from the audited pilot. One hour per band uses 60 independent 60-s reads; source and background shot-noise variance plus split-read variance are included in the Gaussian approximation. Independent exact aggregate Poisson plus read draws validate its moments; this is not exact Poisson sampling for every science realization. Sky mean, PSF and registration are known. Sky residuals, flat-field errors, reduced-image covariance, actual detector saturation/DIT constraints and calibrated PSF variability are absent. No universal ULTIMATE sensitivity/resolution forecast follows.','', '## Findings, publication readiness and next requirements','', '1. **Simulation-based contrasts (source-systematic caveat):** the executed matched pairs support dust-induced, wavelength- and viewing-dependent shifts in fixed-aperture light morphology across multiple independent galaxies. Sign, scatter and outliers are retained. Associations with stellar mass, positive sSFR, actual projected dust mass and apparent morphology are exploratory (property_associations.csv); zero sSFR/dust are not logged as finite detections. There are multiple unadjusted comparisons, so no precise scaling law or causal property driver is claimed.','2. **Conditional resolution comparisons:** absolute morphology preservation and dusty-minus-clear recovery are distinct metrics, with galaxy-bootstrap gains in the table. A smaller PSF can preserve structure while offering little or adverse improvement for a weak dust difference. Examine metric-specific gains and finite-noise controls rather than declaring success from resolution alone.','3. **Future observational tests:** measure sizes, concentration, q and spatial NIR light structure at calibrated PSFs and surface brightness; compare against seeing-limited images of the same galaxies. A real clear counterpart is unavailable, so direct observational Δdust requires extra modelling/constraints. No physical geometry, unique feature attribution, or mass recovery is supplied here.','4. **Claims needing more evidence:** population relations require a representative or design-weighted sample and broader orientation handling; a publishable instrument forecast requires actual observer bands or spectral synthesis, PSF/sky/detector calibration, independent observational validation and systematic-error tests. DR1 Monte Carlo image uncertainty and subgrid radiative-transfer assumptions are not quantified here.','', '**Workshop readiness: GO with explicit scope and the zero-projected-dust residual control.** Use Figures 02, 03, 05 and 09, with the sample-selection and aperture limitations. This is a substantial multi-galaxy feasibility result rather than another geometry classifier. **Publication readiness: a methods/results foundation, not yet a validated ULTIMATE forecast.** A paper centered on conditional morphology transfer is plausible after resolving aperture/systematic sensitivity and positioning novelty against prior morphology/radiative-transfer literature. A bounded primary-literature check finds direct overlap with the larger atlas study below; physical morphology trends alone are not a defensible novelty claim.','', '## Prior work and paper positioning','', 'Dust-induced structural-parameter changes were already quantified with radiative-transfer disk/bulge models by [Pastrav et al. (2013)](https://arxiv.org/abs/1301.5602). More directly, [Bokona Tulu et al. (2026)](https://arxiv.org/abs/2605.20886) used the larger TNG50-SKIRT atlas for wavelength-dependent nonparametric morphology and dust effects. Their StatMorph apertures/centers and noise treatment differ from our fixed-origin apertures, so numerical concentrations are not interchangeable. They also report asymmetry instability and identify O4/O5 as antipodal. Our four-view robustness excludes O5 without changing the frozen five-view primary results. The viable distinctive contribution is instrument-specific preservation/recovery calibration with realistic systematics, not rediscovery of dust-dependent morphology in 26 atlas galaxies.','', '## Provenance and prior negative evidence','', 'The four earlier scientific reports were inspected in chronological order, with protocol, validation and code. The 98.4% uniform-screen false-positive case, failed positive-model predictive adequacy, stellar-structure contamination, and noise-assisted area crossings remain valid. No expensive inference grid was rerun. previous_results_sha256.json permits an end-of-run preservation check.','', 'Atlas reference: [Baes et al. (2024), TNG50-SKIRT DR1 methodology and data release](https://arxiv.org/abs/2401.04224). Its z=0 image/map format is checked against the actual FITS headers here. Instrument provenance remains the pinned sources in ../screen_test_20261026/ and the read-only pilot code. No new simulation dataset or package was downloaded.','', 'All calculations and full numerical tables are linked in README.md; PROTOCOL.md records the choices fixed before held-out evaluation.']
 (O/'scientific_report.md').write_text('\n'.join(lines)+'\n')
 workshop=['# Workshop summary: dust changes morphology; resolution benefits depend on the measurement','',f"Executed: {len(meta)} galaxies × 5 correlated views × 22 paired bands. Fixed-rest-band observing comparison, not an exact ULTIMATE forecast.",'']
 for band in ['LSST_g','2MASS_Ks']:
  s=summ[(summ.scope=='all_26')&(summ.band==band)&(summ.metric=='delta_R50')].iloc[0];workshop.append(f"- {band}: median galaxy-mean ΔR50 {s.galaxy_median:.3f} kpc [{s.median_CI_low:.3f}, {s.median_CI_high:.3f}], galaxy-bootstrap 95% interval; signs and individual ranges in Figure 03.")
 workshop+=['','Suggested four-slide sequence:','1. Figure 02: wavelength dependence and honest sample scatter.','2. Figure 03: each galaxy is one sampling unit; show full viewing-angle ranges.','3. Figure 05: distinguish morphology preservation from dust-difference recovery. Gains are conditional on the provisional PSF/noise scenario.','4. Figure 09: show favorable, unfavorable and weak-dust examples; no unique dust-feature claim.','', 'Keep Figure 01 (selection), Figure 07 (aperture/center sensitivity), and Figure 10 (PSF/depth sensitivity) as backup. The prior geometry-inference failures motivate this measurable counterfactual question; they are not hidden.','', 'Caveats on the slides: balanced 26-object feasibility sample; R<12-kpc sizes; correlated directions; clear images are simulation truth; z=0 fixed-rest-band degradation; rest Ks is not observer Ks at z=0.1; provisional PSFs/backgrounds; no calibrated performance promise or dust mass/geometry recovery.','', 'Prior work already covers atlas dust-dependent nonparametric morphology: Bokona Tulu et al. (2026), https://arxiv.org/abs/2605.20886. Distinctive paper value must come from calibrated instrumental transfer and error recovery, with additional independent validation.','', 'The zero-projected-dust source-product residuals must be resolved before claiming small paired differences as physical dust signals. Raw/noise-corrected asymmetry also gives conflicting preservation gains.','', 'Paper path: strengthen aperture and measurement-systematic control, use validated observer-filter synthesis and empirical PSFs/sky, and test independent observational morphology. Current results support a workshop and a conditional simulation-study draft, with these gaps explicit.']
 (O/'workshop_summary.md').write_text('\n'.join(workshop)+'\n')
def control_figure():
 r=pd.read_csv(O/'zero_projected_dust_residuals.csv');r=r[r.smoothing_FWHM_kpc==0]
 b=pd.read_csv(O/'GLAO_bootstrap_summary.csv')
 fig,axs=plt.subplots(1,3,figsize=(13,4.5),layout='constrained')
 for i,band in enumerate(['LSST_g','2MASS_J','2MASS_Ks']):
  ss=r[r.band==band].groupby('subhalo_id').mean(numeric_only=True)
  axs[0].scatter(np.full(len(ss),i),ss.integrated_pair_attenuation_mag,s=35,c='#0072B2')
  axs[1].scatter(np.full(len(ss),i),ss.delta_R50,s=35,c='#0072B2')
 for ax in axs[:2]:
  ax.axhline(0,c='.5');ax.set_xticks(range(3),['LSST g','2MASS J','2MASS Ks'])
 axs[0].set(ylabel='Pair effective attenuation [mag]',title='Zero projected-dust map objects')
 axs[1].set(ylabel='Galaxy-mean paired ΔR50 [kpc]',title='Small morphology residuals remain')
 for i,metric in enumerate(['A','A_raw']):
  ss=b[(b.scope=='all_26')&(b.band=='2MASS_Ks')&(b.pairing=='independent_clear')&(b.metric==metric)&(b.target=='preservation_abs_error')].iloc[0]
  axs[2].errorbar(i,ss.mean_gain,yerr=[[ss.mean_gain-ss.CI_low],[ss.CI_high-ss.mean_gain]],fmt='o',capsize=4,c='#D55E00')
 axs[2].axhline(0,c='.5');axs[2].set(xticks=[0,1],xticklabels=['Noise-subtracted A','Raw A'],ylabel='Seeing error − GLAO error',title='Asymmetry gain depends on estimator');axs[2].tick_params(axis='x',labelrotation=15)
 fig.suptitle('Source-product residuals and estimator sensitivity limit physical claims\nFour objects with zero projected dust; no residual correction applied. Right: 26-galaxy bootstrap intervals')
 save(fig,'11_source_and_estimator_controls')

def quantitative_addendum():
 path=O/'scientific_report.md';text=path.read_text()
 null=pd.read_csv(O/'zero_projected_dust_summary.csv');native=null[null.smoothing_FWHM_kpc==0]
 additions=['## Quantitative cross-checks','']
 for row in native.itertuples():
  additions.append(f'- Zero projected-dust controls, {row.band}: median pair attenuation {row.attenuation_median:.4f} mag; median normalized shape-residual RMS {row.median_shape_residual_RMS:.4f}; maximum view-level |ΔR50| {row.max_abs_delta_R50:.4f} kpc. These four objects provide an empirical warning, not a transferable error distribution.')
 additions+=['', 'Held-out evaluation (21 galaxies), median of galaxy-mean paired R50 contrasts:']
 s=pd.read_csv(O/'galaxy_bootstrap_summary.csv')
 for row in s[(s.scope=='held_out_21')&(s.metric=='delta_R50')&s.band.isin(['LSST_g','2MASS_Ks'])].itertuples():
  additions.append(f'- {row.band}: {row.galaxy_median:.4f} kpc [{row.median_CI_low:.4f}, {row.median_CI_high:.4f}], galaxy bootstrap.')
 additions+=['', 'Excluding antipodal O5 (four-view sensitivity), mean Ks gains with independent clear noise:']
 four=pd.read_csv(O/'four_view_GLAO_robustness.csv')
 for row in four[(four.scope=='four_views_no_O5')&(four.band=='2MASS_Ks')&(four.pairing=='independent_clear')&four.metric.isin(['R50','C'])].itertuples():
  additions.append(f'- {row.metric}, {row.target}: {row.mean_gain:.5f} [{row.CI_low:.5f}, {row.CI_high:.5f}].')
 spatial=pd.read_csv(O/'galaxy_spatial_information.csv');spatial=spatial[spatial.SB_stratum.astype(str)=='all']
 additions+=['', 'Native Ks structure transfer at 1-kpc analysis FWHM (median galaxy normalized RMS error):']
 for target,g in spatial[(spatial.scale_kpc==1)&spatial.target.isin(['dusty_morphology','dust_imprint'])].groupby('target'):
  seeing=g[g['mode']=='seeing'].NRMSE;glao=g[g['mode']=='glao'].NRMSE
  additions.append(f'- {target}: seeing {seeing.median():.4f}, GLAO {glao.median():.4f}; valid normalized references {seeing.notna().sum()}/{len(seeing)} and {glao.notna().sum()}/{len(glao)}. A dust-imprint reference is a paired source-product contrast with the same unresolved residual caveat.')
 additions+=['', 'Detector-grid resampling changes are supplied separately in detector_sampling_robustness.csv. All noise failures and valid-draw denominators are retained; no object is removed from the native analysis.','']
 text=text.replace('## Conditional seeing versus GLAO','The paired contrasts include an unresolved source-product residual: zero projected-dust controls have nonzero differences. Small Δdust values must not be called calibrated physical dust effects (Figure 11).\n\n## Conditional seeing versus GLAO',1)
 text=text.replace('## Findings, publication readiness and next requirements','\n'.join(additions)+'\n## Findings, publication readiness and next requirements')
 path.write_text(text)

if __name__=='__main__':run()
