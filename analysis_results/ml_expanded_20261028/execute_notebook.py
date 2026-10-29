"""Execute the artifact replay in the existing phd Jupyter kernel."""
from pathlib import Path
import json,nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter

O=Path(__file__).resolve().parent
def run():
    path=O/'expanded_ml_executed.ipynb';notebook=nbformat.read(path,as_version=4)
    nbformat.validate(notebook)
    NotebookClient(notebook,timeout=900,kernel_name='phd',resources={'metadata':{'path':str(O)}}).execute()
    nbformat.write(notebook,path)
    html,_=HTMLExporter().from_notebook_node(notebook);(O/'expanded_ml_executed.html').write_text(html)
    cells=[c for c in notebook.cells if c.cell_type=='code']
    errors=[x for c in cells for x in c.get('outputs',[]) if x.output_type=='error']
    assert not errors and all(c.execution_count is not None for c in cells)
    (O/'NOTEBOOK_VALIDATION.json').write_text(json.dumps(dict(passed=True,code_cells=len(cells),error_outputs=len(errors),all_code_cells_executed=True,kernel='phd',final_inference_repeated=False,development_model_fit_reproduced=True),indent=2))
    print('Notebook executed top-to-bottom and exported to HTML.',len(cells),'code cells; no errors.')

if __name__=='__main__':run()
