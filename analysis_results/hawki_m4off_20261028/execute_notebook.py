from pathlib import Path
import os,sys,json
O=Path(__file__).resolve().parent
kernelroot=Path('/tmp/hawki_m4_jupyter');kp=kernelroot/'kernels/hawki-phd';kp.mkdir(parents=True,exist_ok=True)
(kp/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'Python (phd)','language':'python'}))
os.environ['JUPYTER_PATH']=str(kernelroot);os.environ['MPLCONFIGDIR']='/tmp/hawki_m4_mpl';os.environ['IPYTHONDIR']='/tmp/hawki_m4_ipython'
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
p=O/'empirical_calibration.ipynb';nb=nbformat.read(p,as_version=4);NotebookClient(nb,timeout=180,kernel_name='hawki-phd',resources={'metadata':{'path':str(O)}}).execute();nbformat.validate(nb);nbformat.write(nb,p)
assert all(not any(o.output_type=='error' for o in c.get('outputs',[])) for c in nb.cells)
body,_=HTMLExporter().from_notebook_node(nb);(O/'empirical_calibration.html').write_text(body)
# Save embedded outputs for inspection, without a live notebook server.
import base64
for i,c in enumerate(nb.cells):
 for j,o in enumerate(c.get('outputs',[])):
  if 'image/png' in o.get('data',{}):(O/f'figures/notebook_cell_{i}_{j}.png').write_bytes(base64.b64decode(o.data['image/png']))
print('Executed',sum(c.cell_type=='code' for c in nb.cells),'code cells; saved notebook and self-contained HTML')
