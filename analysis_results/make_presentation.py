from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LogNorm, TwoSlopeNorm
from astropy.io import fits
O=Path('/home/bahareh/ULTIMATE/analysis_results'); F=O/'figures'
plt.rcParams.update({'font.size':16,'pdf.fonttype':42})
s=pd.read_csv(O/'tng_orientation_summary.csv')
fig,axes=plt.subplots(2,5,figsize=(16,6),layout='constrained')
for j,ori in enumerate(s.orientation):
 with fits.open(O/'attenuation_maps'/f'{ori}_maps_500pc.fits') as hd:
  sl=np.s_[120:200,120:200]; mask=hd['VALID_R20'].data[sl].astype(bool)
  ag=np.ma.masked_where(~mask,hd['A_G'].data[sl]); d=np.ma.masked_less_equal(hd['SIGMA_DUST'].data[sl],0)
  for i,a in enumerate([ag,d]):
   im=axes[i,j].imshow(a,origin='lower',extent=(-20,20,-20,20),cmap='RdBu_r' if i==0 else 'cividis',norm=TwoSlopeNorm(0,vmin=-.2,vmax=1.5) if i==0 else LogNorm(.002,1))
   axes[i,j].set(title=ori if i==0 else '',xlabel='x (kpc)',ylabel='y (kpc)'); axes[i,j].tick_params(labelsize=11)
   if j==4: fig.colorbar(im,ax=axes[i,:],shrink=.8,label=['g attenuation (mag)','Projected dust (M☉/pc²)'][i],extend='both')
fig.suptitle('Same galaxy, same physical fields and scales | 0.5-kpc bins')
for ext in ['png','pdf']: fig.savefig(F/f'talk_g_dust_maps.{ext}',dpi=260)
plt.close(fig)
notes=[]
def slide(pdf,title,seconds,body=None,img=None,note='',footer='Preliminary | TNG50-SKIRT DR1 | one galaxy, five views'):
 fig=plt.figure(figsize=(16,9),facecolor='white')
 fig.text(.05,.93,title,fontsize=27,weight='bold',va='top',color='#173451')
 if img:
  ax=fig.add_axes([.04,.15,.92,.69]); ax.imshow(plt.imread(F/img)); ax.axis('off')
 if body:
  for y,line in zip(np.linspace(.77,.28,len(body)),body): fig.text(.07,y,line,fontsize=22,va='top',linespacing=1.45)
 fig.text(.05,.055,footer,fontsize=12,color='#555555'); fig.text(.95,.055,str(len(notes)+1),ha='right',fontsize=12)
 pdf.savefig(fig); plt.close(fig)
 notes.append((title,seconds,note))
with PdfPages(O/'workshop_10min.pdf',metadata={'Title':'ULTIMATE–Subaru: Beyond the Foreground Screen','Subject':'Verified preliminary results and planned feasibility test'}) as pdf:
 slide(pdf,'Beyond the Foreground Screen',45,body=['ULTIMATE–Subaru: machine-learning dust geometry','Question: what dust-related information survives realistic imaging?','Verified pilot: five views of TNG50 subhalo 294866','Bahareh | PhD progress / ULTIMATE workshop | November 2026'],note='Frame the research question. These are preliminary results, not a trained dust-geometry model. Establish the distinction between information in ideal images and information recoverable in observations.')
 slide(pdf,'First establish a reproducible measurement',60,body=['Aλ = −2.5 log₁₀(Iwith dust / Iwithout dust)','O1 reproduced: Ag = 0.334442 mag; AKs = 0.020562 mag','Spatial test: 1-kpc means, R < 20 kpc, shared faint mask','ρg = 0.924164; ρKs = 0.548340; 1,264 bins'],note='Integrated attenuation is a ratio of full-frame sums; the spatial statistic uses a different aperture. Intensities are MJy/sr, dust columns M☉/pc², grid 100 pc. Explain the relative 10⁻⁴ threshold in both dust-free bands. Negative attenuation is retained; the twin exists only in simulation.')
 slide(pdf,'The projection changes across viewing directions',90,img='talk_g_dust_maps.png',note='Explain rows: effective g attenuation and projected dust column. Every view uses the same physical field and colour scale. Red/blue retain negative attenuation; colour limits clip display only. Orientations are related views, not five galaxies. A column density is a line-of-sight integral; it does not specify where the dust sits relative to the stars.')
 slide(pdf,'Integrated attenuation and association depend on view',90,img='viewing_dependence.png',note='Read the g range 0.231–0.604 mag and Ks range 0.0066–0.0831 mag. g association stays strong under the pilot mask, while Ks varies greatly. The right panel spans 27 analyst choices per view: bin sizes 0.5/1/2 kpc, thresholds 10⁻⁵/10⁻⁴/10⁻³, radii 10/20/30 kpc. Shading is an analysis-choice range, not error bars or population uncertainty.')
 slide(pdf,'Ks is not a universal monotonic dust tracer',90,img='five_orientation_correlations.png',note='Focus on O2: Ks rho −0.076 compared with positive O3–O5 values. Do not interpret it as dust causing negative extinction: effective attenuation incorporates scattering, and faint Monte Carlo fluctuations matter when Ks attenuation is small. Keep negative values. Correlations are descriptive and spatially correlated; no independent-pixel p-values. Radius alone does not fully explain the strong optical association, but that is not proof of causal geometry recovery.')
 slide(pdf,'Real-data anchor: raw HAWK-I/GRAAL Ks observations',75,body=['22/22 exposures complete; raw-byte checksums and data sums pass','2018 January 3 and 6 | DIT × NDIT = 1.7 × 18 = 30.6 s','Four 2048² chips per frame | 0.10643 arcsec/pixel','Provisional frame median widths: 0.258–0.417 arcsec\nCalibration, sky subtraction and final-stack PSF still required'],note='Show the separately supplied raw preview if time permits. The accepted widths are from 677 compact-source Moffat fits, repeated detections, not unique confirmed stars. Raw gradients and flat-field artifacts remain. Total nominal duration 673.2 s is not uniform coverage. No local reduced stack/calibrations. This is an empirical imaging anchor, not dust-free truth or a 0.2-arcsec image.',footer='Measured on raw frames | provisional PSF estimates | see HAWK-I inspection report')
 slide(pdf,'Next: a small forward-modelling feasibility test',90,body=['Convolve intensities → angular scaling → pixel integration → noise','Design scenarios: K-band FWHM 0.2–0.3 arcsec; WFI 0.1 arcsec/pixel','Resolution limit: 100 pc at assumed DA = 100 Mpc is 0.206 arcsec\nFiner output pixels cannot supply unresolved structure','Test observable colours against radius / brightness baselines\nFilter curves and a verified noise budget are still needed'],note='Instrument numbers are design references from the project instrument plan and WFI design slides, not guarantees. Match optical/NIR PSFs before forming colours. Select distance and resolution honestly, then calibrate sky, throughput, read noise and exposure assumptions. Keep dust-free twins for evaluation only. Planned test is not yet an executed recovery result.',footer='Planned, not executed | design references: ultimate.naoj.org/instrument.html; WFI-Motohara-v2s.pdf')
 slide(pdf,'What is established — and the next decision',60,body=['Established: reproducible attenuation and viewing dependence','Established: complete HAWK-I data; provisional measured widths','Open: recoverable dust information at realistic depth and resolution','Then: independent galaxies and explicit 3D geometry labels\nNo large training run before this feasibility gate'],note='Close on the actual result and request scientific feedback: which distance regime and geometry target matter most? More independent galaxies are needed before generalization. A projected dust map cannot alone identify vertical thickness, clumping or star–dust separation. No unique 3D recovery or ML accuracy is claimed.')
assert sum(x[1] for x in notes)==600
lines=['# Workshop talk: 10-minute draft','', 'Eight slides, 600 seconds total. PDF: `workshop_10min.pdf`. All measured values derive from the executed local analysis; forward modelling remains planned.','']
for i,(title,sec,note) in enumerate(notes,1): lines += [f'## {i}. {title} — {sec} seconds','',note,'']
lines += ['## Backup material','', 'Use `figures/hawki_raw_preview.*` for the labelled raw detector view, `hawki_psf_diagnostics.*` for fit examples, and `tng_orientation_summary.csv` for the exact table. Main figures are also available independently in PNG/PDF. Add presenter affiliation and workshop session details before presenting; no affiliation was inferred. Instrument references and assumptions are documented in `next_experiments.md`.']
(O/'workshop_talk_outline.md').write_text('\n'.join(lines))
print('Presentation saved; eight slides, 600 seconds.')
