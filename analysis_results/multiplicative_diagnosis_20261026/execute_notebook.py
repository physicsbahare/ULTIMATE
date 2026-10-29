from pathlib import Path
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
O=Path(__file__).resolve().parent;n=nbformat.read(O/'ULTIMATE_targeted_positive_model.ipynb',as_version=4)
try:NotebookClient(n,timeout=1800,kernel_name='phd',resources={'metadata':{'path':str(O)}}).execute()
finally:nbformat.write(n,O/'ULTIMATE_targeted_positive_model.ipynb')
html,_=HTMLExporter().from_notebook_node(n);(O/'ULTIMATE_targeted_positive_model.html').write_text(html)
print('Notebook executed successfully.',flush=True)
