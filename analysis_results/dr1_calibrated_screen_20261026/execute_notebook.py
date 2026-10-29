from pathlib import Path
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
O=Path(__file__).resolve().parent
path=O/'Calibrated_DR1_screen_experiment.ipynb';n=nbformat.read(path,as_version=4)
client=NotebookClient(n,timeout=1800,kernel_name='phd',resources={'metadata':{'path':str(O)}})
try: client.execute()
finally: nbformat.write(n,path)
body,_=HTMLExporter().from_notebook_node(n);(O/'Calibrated_DR1_screen_experiment.html').write_text(body)
print('EXECUTED',len([c for c in n.cells if c.cell_type=='code']),'code cells',flush=True)
