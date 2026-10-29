from pathlib import Path
import json,shutil
import measure_psf as m
O=Path(__file__).resolve().parent;F=O/'faint_peak_selection';F.mkdir(exist_ok=True)
m.O=F;m.PEAK_MAX=5000;m.RAW_MAX=22000;m.run()
(F/'selection.json').write_text(json.dumps({'peak_above_sky_ADU_max':5000,'raw_product_pixel_ADU_max':22000,'peak_SNR_min':60,'purpose':'conservative fainter product sample; raw-frame saturation history remains unverified'},indent=2))
for pat in ['*_stars.csv','*_profiles.csv','*_stamps.npz','psf_fits.csv','empirical_profiles.csv','image_planes.csv']:
 for p in F.glob(pat):
  if p.is_file():shutil.copyfile(p,O/p.name)
print('Fainter sample promoted; broad sample retained separately',flush=True)
