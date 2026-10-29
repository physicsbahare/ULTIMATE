"""Execute a supplementary audit notebook without rewriting the primary study."""
from pathlib import Path
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter

HERE = Path(__file__).resolve().parent


def run():
    nb = nbformat.v4.new_notebook()
    md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell
    nb.cells = [
        md('# Continuation: independent multi-galaxy verification\n\n'
           'The existing 26-galaxy study is preserved. This supplement independently '
           'recomputes its main statistics and tests exclusion of the four '
           'zero-projected-dust objects. Exclusion is descriptive sensitivity, '
           'not a correction for unknown source-product systematics. '
           'The complete primary notebook and 22-band tables remain one directory above.'),
        code("from pathlib import Path\nimport json, sys\nimport pandas as pd\n"
             "from IPython.display import display, Image, Markdown\n"
             "HERE = Path.cwd()\nSTUDY = HERE.parent\n"
             "sys.path.insert(0, str(HERE))\nimport verify_existing_study as audit\n"
             "receipt = json.loads((HERE/'verification_receipt.json').read_text())\n"
             "display(receipt)"),
        md('## Independent native paired calculation\n\n'
           'Subtract matched absolute morphologies, average the five views within '
           'each galaxy, then bootstrap independent galaxies. R50 is conditioned '
           'on the fixed R<12-kpc aperture. Intervals describe selected-sample '
           'variation and exclude instrumental/source-model systematics.'),
        code("native, nonzero = audit.verify_native()\ndisplay(native)"),
        md('## Independently reconstructed observing errors\n\n'
           'Use independent clear-versus-dusty observation noise, paired between '
           'strategies. Retain jointly valid draws, require at least six per view, '
           'then average draws, views and galaxies in that order. Positive gain '
           'means seeing absolute error minus GLAO absolute error. This is '
           'fixed-rest-band degradation, not exact observer-frame forecasting.'),
        code("accuracy, difference = audit.verify_accuracy(nonzero)\n"
             "print('Maximum difference from recorded per-galaxy gains:', difference)\n"
             "display(accuracy[(accuracy.band=='2MASS_Ks') & accuracy.metric.isin(['R50','C'])])"),
        md('## Strongest figures and source-product limitation\n\n'
           'These figures are the unchanged primary-study exports. Full '
           'five-galaxy fresh simulation replay and archive integrity evidence '
           'are in the adjacent CSV files and verification receipt.'),
        code("for name in ['03_per_galaxy_bias.png', '05_GLAO_morphology_accuracy.png', '11_source_and_estimator_controls.png']:\n"
             "    display(Image(filename=str(STUDY/'figures'/name)))"),
        md('## Interpretation\n\n'
           'The numerical reproduction and primary-study provenance can be '
           'verified independently. Four zero-projected-dust objects still show '
           'nonzero image-pair residuals; no offset is subtracted. Physical '
           'attribution of the smallest contrasts remains unresolved. '
           'Aperture sensitivity, nonrepresentative selection, eight science '
           'noise draws and provisional PSFs limit generalization. '
           'See the primary scientific report and this directory’s README '
           'for exact results and reproduction commands.'),
    ]
    nb.metadata['kernelspec'] = {'display_name': 'Python (phd)', 'language': 'python', 'name': 'phd'}
    client = NotebookClient(nb, timeout=300, kernel_name='phd', resources={'metadata': {'path': str(HERE)}})
    client.execute()
    nbformat.validate(nb)
    assert not any(o.output_type == 'error' for c in nb.cells if c.cell_type == 'code' for o in c.outputs)
    path = HERE/'independent_verification.ipynb'
    nbformat.write(nb, path)
    html, _ = HTMLExporter().from_notebook_node(nb)
    (HERE/'independent_verification.html').write_text(html)
    print('Executed and saved', path)


if __name__ == '__main__':
    run()
