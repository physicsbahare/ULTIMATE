from pathlib import Path
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
O=Path(__file__).resolve().parent
nb=nbformat.read(O/'ULTIMATE_spatial_structure_pilot.ipynb',as_version=4)
try:NotebookClient(nb,timeout=1800,kernel_name='phd',resources={'metadata':{'path':str(O)}}).execute()
finally:nbformat.write(nb,O/'ULTIMATE_spatial_structure_pilot.ipynb')
html,_=HTMLExporter().from_notebook_node(nb);(O/'ULTIMATE_spatial_structure_pilot.html').write_text(html)
print('Notebook executed successfully.')
