"""Verify the saved continuation artifacts and record their hashes."""
from pathlib import Path
import base64
import hashlib
import json
import nbformat
import pandas as pd
import verify_existing_study as audit

HERE = Path(__file__).resolve().parent


def run():
    receipt = json.loads((HERE/'verification_receipt.json').read_text())
    assert audit.verify_manifest() == (receipt['study_files_hash_checked'], receipt['previous_result_files_unchanged'])
    tests = (HERE/'unit_tests.log').read_text()
    assert 'Ran 10 tests' in tests and '\nOK\n' in tests
    noise = pd.read_csv(HERE/'fresh_noise_moment_validation.csv')
    assert len(noise) == 3 and noise.passed.all()
    notebook = nbformat.read(HERE/'independent_verification.ipynb', as_version=4)
    nbformat.validate(notebook)
    code = [c for c in notebook.cells if c.cell_type == 'code']
    assert all(c.execution_count is not None for c in code)
    assert not any(o.output_type == 'error' for c in code for o in c.outputs)
    embedded = {hashlib.sha256(base64.b64decode(o.data['image/png'])).hexdigest()
                for c in code for o in c.outputs if 'image/png' in o.get('data', {})}
    for name in ['03_per_galaxy_bias.png', '05_GLAO_morphology_accuracy.png', '11_source_and_estimator_controls.png']:
        assert audit.sha(HERE.parent/'figures'/name) in embedded
    assert (HERE/'independent_verification.html').stat().st_size > 100000
    receipt.update(unit_tests_passed=10, fresh_noise_moment_checks_passed=3,
                   supplementary_executed_code_cells=len(code), supplementary_embedded_figures=len(embedded),
                   supplementary_HTML_exported=True,
                   fresh_visual_inspection=['02_wavelength_dependence.png', '03_per_galaxy_bias.png',
                                            '05_GLAO_morphology_accuracy.png', '09_representative_images.png',
                                            '11_source_and_estimator_controls.png'],
                   HTML_browser_rendering='Not separately inspected; matching embedded PNGs visually inspected',
                   all_preexisting_study_and_prior_result_hashes_still_match=True)
    (HERE/'verification_receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    files = sorted(p for p in HERE.rglob('*') if p.is_file()
                   and '__pycache__' not in p.parts and p.name != 'output_manifest.sha256')
    (HERE/'output_manifest.sha256').write_text(''.join(f'{audit.sha(p)}  {p.relative_to(HERE)}\n' for p in files))
    print(json.dumps(receipt, indent=2))
    print('Supplementary output manifest:', len(files), 'files')


if __name__ == '__main__':
    run()
