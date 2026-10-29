"""Re-execute presentation cells after visual refinements, without rerunning fits.
The full computational notebook was executed first by execute_notebook.py.
These replacement cells are self-contained and reproducible in that notebook.
"""
from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient
from nbconvert import HTMLExporter
O=Path(__file__).resolve().parent
n=nbf.read(O/'Calibrated_DR1_screen_experiment.ipynb',as_version=4)
source1="""from pathlib import Path
from IPython.display import display, Image
O=Path('/home/bahareh/ULTIMATE/analysis_results/dr1_calibrated_screen_20261026')
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(O))
import residual_diagnostics
residual_diagnostics.run()
for path in sorted((O/'figures').glob('*.png'))[:4]:
    display(Image(filename=str(path)))
"""
source2="""from pathlib import Path
import pandas as pd
from IPython.display import display, Image
O=Path('/home/bahareh/ULTIMATE/analysis_results/dr1_calibrated_screen_20261026')
for path in sorted((O/'figures').glob('*.png'))[4:]:
    display(Image(filename=str(path)))
display(pd.read_csv(O/'GLAO_power_comparison.csv').query('z==0.3 and bandset=="joint"').round(4))
"""
mini=nbf.v4.new_notebook(cells=[nbf.v4.new_code_cell(source1),nbf.v4.new_code_cell(source2)])
NotebookClient(mini,timeout=180,kernel_name='phd',resources={'metadata':{'path':str(O)}}).execute()
for i,c in enumerate(n.cells):
 if c.cell_type=='code' and ('for path in paths[:4]' in c.source or "glob('*.png'))[:4]" in c.source):n.cells[i]=mini.cells[0]
 elif c.cell_type=='code' and ('for path in paths[4:]' in c.source or "glob('*.png'))[4:]" in c.source):n.cells[i]=mini.cells[1]
n.metadata['presentation_refresh']='Two self-contained figure cells re-executed after full pipeline execution; includes supplementary residual/prior figures.'
nbf.validate(n);nbf.write(n,O/'Calibrated_DR1_screen_experiment.ipynb')
html,_=HTMLExporter().from_notebook_node(n);(O/'Calibrated_DR1_screen_experiment.html').write_text(html)
print('Refreshed executed figure cells; nine embedded PNGs.')
