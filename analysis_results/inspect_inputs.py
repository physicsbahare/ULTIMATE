from pathlib import Path
import tarfile, json, importlib, sys
from astropy.io import fits
R=Path('/home/bahareh/ULTIMATE'); O=R/'analysis_results'
# Inventory only relevant project files, excluding virtual environments.
files=[p for d in [R/'TNG50_SKIRT',R/'HAWKI_GRAAL'] for p in d.rglob('*') if p.is_file() and '.venv' not in p.parts]
(O/'input_inventory.json').write_text(json.dumps([{'path':str(p.relative_to(R)),'bytes':p.stat().st_size} for p in files],indent=2))
with tarfile.open(R/'TNG50_SKIRT/downloads/TNG50_DR1_294866.tar.gz','r|gz') as t:
 names=[]; selected=[]
 suffixes=['LSST_g','LSST_g_nodust','2MASS_Ks','2MASS_Ks_nodust','dustmass']
 wanted={f'TNG294866_O{i}_{s}.fits' for i in range(2,6) for s in suffixes}
 for m in t:
  names.append({'name':m.name,'bytes':m.size})
  if Path(m.name).name in wanted and m.isfile():
   p=O/'extracted_294866'/Path(m.name).name; p.parent.mkdir(exist_ok=True)
   if not p.exists():
    with t.extractfile(m) as src,p.open('xb') as dst:
     import shutil; shutil.copyfileobj(src,dst)
   selected.append(m.name)
 assert len(selected)==20,selected
(O/'archive_inventory.json').write_text(json.dumps(names,indent=2)); (O/'extraction_manifest.json').write_text(json.dumps(selected,indent=2))
print('Archive fully streamed successfully:',len(names),'members; selected',len(selected))
print('Selected headers:')
for p in sorted((O/'extracted_294866').glob('*dustmass.fits')):
 h=fits.getheader(p); print(p.name,dict(h))
