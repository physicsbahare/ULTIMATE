from pathlib import Path
import sys,json,hashlib,importlib.metadata,datetime
p=Path('/home/bahareh/ULTIMATE/analysis_results/dr1_calibrated_screen_20261026')
versions={x:importlib.metadata.version(x) for x in ['numpy','scipy','astropy','matplotlib','pandas','nbformat','nbclient']}
files=[*p.glob('*.py'),p/'FINAL_PROTOCOL.md',p/'PLAN.md']
record={'python':sys.version,'executable':sys.executable,'versions':versions,'code_sha256':{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in files},'source_previous_directory':'../screen_test_20261026','no_new_data_downloads':True,'no_package_installation':True,'no_intrinsic_evolution':True,'original_galaxies':1,'orientations_not_independent_galaxies':True,'source_image_units':'MJy/sr','source_native_pixel_pc':100,'source_bands':['LSST_g','LSST_r','LSST_i','LSST_z','2MASS_J','2MASS_H','2MASS_Ks'],'primary_noise_budget':'7 bands x 1h on source; 60s DIT, 60 reads/band','final_random_seed_noise':'510031 + stage*900019 + int(z*100), common across seeing/GLAO/PSF strategy','final_random_seed_population':'904672 + stage*70001, common across observing conditions; stage0 calibration stage1 evaluation','population_field_seed':860142,'original_screen_patch_seed':41523,'final_anchor_seed':'experiment.seed_for(int(z*100),23)','GLAO_bootstrap_seed':833108,'final_ensemble_draws_per_null_or_scene':500,'development_draws_calibration_evaluation':[200,200]}
(p/'execution_provenance.json').write_text(json.dumps(record,indent=2))
# Retain read-only scalar instrument table locally without copying wave objects.
sys.dont_write_bytecode=True;sys.path.insert(0,str(p));import experiment
inst=experiment.setup_instrument();import pandas as pd
pd.DataFrame([{k:v for k,v in x.items() if k not in ['wave','throughput']} for x in inst if x['band'] in ['g','r','i','z','J','H','Ks']]).to_csv(p/'instrument_parameters.csv',index=False)
