from pathlib import Path
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
from build_notebook import build
O=Path(__file__).resolve().parent
build();nb=nbformat.read(O/'ULTIMATE_multigalaxy_morphology.ipynb',as_version=4)
try:NotebookClient(nb,timeout=3600,kernel_name='phd',resources={'metadata':{'path':str(O)}}).execute()
finally:nbformat.write(nb,O/'ULTIMATE_multigalaxy_morphology.ipynb')
html,_=HTMLExporter().from_notebook_node(nb);(O/'ULTIMATE_multigalaxy_morphology.html').write_text(html)
print('Executed notebook and HTML saved.')
