"""Fresh, non-destructive continuation audit of the completed 26-galaxy study.

No existing result is rewritten. Only this directory receives new outputs.
Recompute native statistics and conditional errors independently of the study's
statistics module, replay five O1 simulations, and retain source-null sensitivity.
"""
from pathlib import Path
import base64
import datetime
import hashlib
import io
import json
import sys
import tarfile

import nbformat
import numpy as np
import pandas as pd
from astropy.io import fits

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
DEVELOPMENT = [294866, 167418, 626287, 535051, 638950]
sys.path.insert(0, str(STUDY))


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024**2), b''):
            h.update(block)
    return h.hexdigest()


def bootstrap(values, statistic):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    rng = np.random.default_rng(20261027)
    samples = values[rng.integers(len(values), size=(5000, len(values)))]
    estimator = np.mean if statistic == 'mean' else np.median
    return np.quantile(estimator(samples, axis=1), [.025, .975])


def verify_archives():
    inventory = pd.read_csv(STUDY / 'archive_inventory.csv')
    state = json.loads((ROOT / 'data/TNG50_SKIRT_DR1_extra/download_state.json').read_text())['galaxies']
    rows = []
    for row in inventory.itertuples():
        path = ROOT / row.path
        digest = sha(path)
        assert path.stat().st_size == row.bytes and digest == row.sha256
        if row.subhalo_id != 294866:
            saved = state[str(row.subhalo_id)]
            assert saved['status'] == 'verified'
            assert saved['gzip_CRC'] == saved['tar_read'] == 'passed'
            assert saved['sha256'] == digest and saved['bytes'] == path.stat().st_size
        rows.append(dict(subhalo_id=row.subhalo_id, bytes=path.stat().st_size,
                         sha256=digest, matches_recorded_sha256=True,
                         CRC_basis=row.CRC_evidence))
        print('Archive hash verified:', row.subhalo_id, flush=True)
    pd.DataFrame(rows).to_csv(HERE / 'fresh_archive_integrity.csv', index=False)
    return len(rows)


def verify_manifest():
    # Verify every original study output, including its cache and notebook.
    count = 0
    for line in (STUDY / 'output_manifest.sha256').read_text().splitlines():
        digest, relative = line.split('  ', 1)
        assert sha(STUDY / relative) == digest, relative
        count += 1
    previous = json.loads((STUDY / 'previous_results_sha256.json').read_text())
    for path, digest in previous.items():
        assert sha(ROOT / path) == digest, path
    return count, len(previous)


def verify_native():
    absolute = pd.read_csv(STUDY / 'intrinsic_morphology.csv')
    primary = absolute[absolute.setting.astype(str) == '12']
    keys = ['subhalo_id', 'view', 'band']
    assert not primary.duplicated(keys + ['scene']).any()
    metrics = ['R50', 'C', 'A', 'q', 'flux']
    dusty = primary[primary.scene == 'dusty'].set_index(keys)[metrics]
    clear = primary[primary.scene == 'clear'].set_index(keys)[metrics]
    assert len(dusty) == len(clear) == 2860
    delta = dusty.subtract(clear).rename(columns=lambda x: 'delta_' + x)
    delta['attenuation_mag'] = -2.5 * np.log10(dusty.flux / clear.flux)
    recorded = pd.read_csv(STUDY / 'primary_dust_bias.csv').set_index(keys)
    for metric in ['R50', 'C', 'A', 'q']:
        np.testing.assert_allclose(delta['delta_' + metric], recorded.loc[delta.index, 'delta_' + metric], atol=2e-14, rtol=1e-12)
    galaxy = delta.groupby(level=['subhalo_id', 'band']).mean()
    inventory = pd.read_csv(STUDY / 'galaxy_inventory.csv').set_index('subhalo_id')
    nonzero = inventory.index[inventory.dust_mass_field_Msun > 0]
    rows = []
    for scope, subset in [('all_26', inventory.index), ('nonzero_projected_dust_22', nonzero)]:
        for band in ['LSST_g', '2MASS_Ks']:
            # Match the recorded galaxy-ID order for exact seeded finite-bootstrap reproduction.
            values = galaxy.xs(band, level='band').loc[subset, 'delta_R50'].sort_index()
            lo, hi = bootstrap(values, 'median')
            rows.append(dict(scope=scope, band=band, n_galaxies=len(values),
                             median_delta_R50_kpc=float(values.median()),
                             CI_low=lo, CI_high=hi, n_positive=int((values > 1e-8).sum()),
                             n_negative=int((values < -1e-8).sum()),
                             minimum=values.min(), maximum=values.max()))
    result = pd.DataFrame(rows)
    old = pd.read_csv(STUDY / 'galaxy_bootstrap_summary.csv')
    for row in result[result.scope == 'all_26'].itertuples():
        check = old[(old.scope == 'all_26') & (old.band == row.band) & (old.metric == 'delta_R50')].iloc[0]
        np.testing.assert_allclose([row.median_delta_R50_kpc, row.CI_low, row.CI_high],
                                   [check.galaxy_median, check.median_CI_low, check.median_CI_high], atol=1e-13)
    result.to_csv(HERE / 'independent_native_and_null_sensitivity.csv', index=False)
    return result, nonzero


def verify_accuracy(nonzero):
    data = pd.read_csv(STUDY / 'observed_morphology.csv')
    data = data[data.band.isin(['2MASS_Ks', 'LSST_g'])]
    records = []
    for (sid, view, band, mode), group in data.groupby(['subhalo_id', 'view', 'band', 'mode']):
        reference = group[group.phase == 'reference'].set_index('scene')
        noise = group[group.phase == 'noise']
        dusty = noise[(noise.scene == 'dusty') & (noise.pairing == 'common')].set_index('draw')
        clear = noise[(noise.scene == 'clear') & (noise.pairing == 'independent_clear')].set_index('draw')
        for metric in ['R50', 'C', 'A', 'q']:
            preservation = abs(dusty[metric] - reference.loc['dusty', metric])
            recovery = abs(dusty[metric] - clear[metric] - (reference.loc['dusty', metric] - reference.loc['clear', metric]))
            for target, errors in [('preservation_abs_error', preservation), ('dust_delta_abs_error', recovery)]:
                for draw, error in errors.items():
                    records.append(dict(subhalo_id=sid, view=view, band=band, mode=mode,
                                        metric=metric, target=target, draw=draw, error=error))
    errors = pd.DataFrame(records)
    keys = ['subhalo_id', 'view', 'band', 'metric', 'target', 'draw']
    paired = errors.pivot(index=keys, columns='mode', values='error').dropna()
    views = paired.groupby(level=keys[:-1]).agg(['mean', 'count'])
    views = views[(views['seeing', 'count'] >= 6) & (views['glao', 'count'] >= 6)]
    rows = []
    for (sid, band, metric, target), group in views.groupby(level=['subhalo_id', 'band', 'metric', 'target']):
        if len(group) != 5:
            continue
        seeing, glao = group['seeing', 'mean'].mean(), group['glao', 'mean'].mean()
        rows.append(dict(subhalo_id=sid, band=band, metric=metric, target=target,
                         seeing=seeing, glao=glao, gain=seeing-glao))
    galaxy = pd.DataFrame(rows)
    saved = pd.read_csv(STUDY / 'galaxy_GLAO_gains.csv')
    saved = saved[saved.pairing == 'independent_clear']
    joined = galaxy.merge(saved, on=['subhalo_id', 'band', 'metric', 'target'], suffixes=('_fresh', '_saved'), validate='one_to_one')
    max_difference = float(abs(joined.gain_fresh - joined.gain_saved).max())
    assert max_difference < 1e-12
    assert abs(galaxy[galaxy.band == 'LSST_g'].gain).max() == 0
    summaries = []
    for scope, subset in [('all_26', galaxy), ('nonzero_projected_dust_22', galaxy[galaxy.subhalo_id.isin(nonzero)])]:
        for (band, metric, target), group in subset.groupby(['band', 'metric', 'target']):
            lo, hi = bootstrap(group.gain, 'mean')
            summaries.append(dict(scope=scope, band=band, metric=metric, target=target,
                                  n_galaxies=len(group), seeing_mean_error=group.seeing.mean(),
                                  glao_mean_error=group.glao.mean(), mean_gain=group.gain.mean(),
                                  CI_low=lo, CI_high=hi, n_improved=int((group.gain > 1e-10).sum())))
    galaxy.to_csv(HERE / 'independently_recomputed_galaxy_gains.csv', index=False)
    summary = pd.DataFrame(summaries)
    summary.to_csv(HERE / 'independent_accuracy_and_null_sensitivity.csv', index=False)
    return summary, max_difference


def replay():
    import observe
    rows = []
    for sid in DEVELOPMENT:
        measured, spatial, transfer, _ = observe.condition(sid, 'O1')
        new = pd.DataFrame(measured)
        old = pd.read_csv(STUDY / 'cache' / str(sid) / 'O1_observed.csv')
        keys = ['band', 'mode', 'scene', 'phase', 'draw', 'pairing']
        new, old = new.set_index(keys).sort_index(), old.set_index(keys).sort_index()
        assert new.index.equals(old.index)
        error = 0.
        for metric in ['R50', 'C', 'A', 'A_raw', 'q', 'flux']:
            np.testing.assert_allclose(new[metric], old[metric], atol=2e-12, rtol=1e-12, equal_nan=True)
            error = max(error, float(np.nanmax(abs(new[metric] - old[metric]))))
        rows.append(dict(subhalo_id=sid, view='O1', rows=len(new),
                         maximum_absolute_replay_difference=error,
                         maximum_padded_flux_loss=max(x['padded_flux_loss'] for x in transfer)))
        print('Fresh end-to-end observing replay:', sid, flush=True)
    pd.DataFrame(rows).to_csv(HERE / 'five_galaxy_fresh_replay.csv', index=False)
    # Independent radial-shell implementation checks the cached native g/Ks images.
    radii = np.hypot(*np.meshgrid((np.arange(400) + .5 - 200) * .1,
                                  (np.arange(400) + .5 - 200) * .1))
    valid = radii < 12
    shell_radii, indices = np.unique(radii[valid], return_inverse=True)
    saved = pd.read_csv(STUDY / 'intrinsic_morphology.csv')
    checks = []
    for sid in DEVELOPMENT:
        with np.load(STUDY / 'cache' / str(sid) / 'O1.npz') as cache:
            for scene in ['dusty', 'clear']:
                for band in ['LSST_g', '2MASS_Ks']:
                    image = cache[f'{scene}_{band}'].astype(float)
                    cumulative = np.cumsum(np.bincount(indices, weights=image[valid]))
                    r50 = shell_radii[np.searchsorted(cumulative, .5 * cumulative[-1])]
                    match = saved[(saved.subhalo_id == sid) & (saved.view == 'O1') &
                                  (saved.scene == scene) & (saved.band == band) & (saved.setting.astype(str) == '12')].iloc[0]
                    assert abs(r50 - match.R50) < 1e-12
                    checks.append(dict(subhalo_id=sid, scene=scene, band=band, R50_kpc=r50, error_kpc=abs(r50-match.R50)))
    pd.DataFrame(checks).to_csv(HERE / 'independent_radial_shell_R50.csv', index=False)
    return len(rows), len(checks)


def check_fits_and_notebook():
    inventory = pd.read_csv(STUDY / 'fits_inventory.csv')
    assert len(inventory) == 6240 and inventory.valid.all()
    assert not inventory.duplicated(['subhalo_id', 'view', 'product']).any()
    assert inventory.groupby('subhalo_id').size().eq(240).all()
    # Reopen one actual raw member in each of two development archives; no extraction.
    raw_checks = []
    for sid in [167418, 535051]:
        path = ROOT / f'data/TNG50_SKIRT_DR1_extra/TNG50_DR1_{sid}.tar.gz'
        with tarfile.open(path, 'r|gz') as archive:
            for member in archive:
                if not member.isfile() or not member.name.endswith('_O1_LSST_g.fits'):
                    continue
                raw = archive.extractfile(member).read()
                row = inventory[(inventory.subhalo_id == sid) & (inventory.member == member.name)].iloc[0]
                assert hashlib.sha256(raw).hexdigest() == row.member_sha256
                with fits.open(io.BytesIO(raw), memmap=False) as hdus:
                    hdus.verify('exception')
                    h, image = hdus[0].header, hdus[0].data
                    assert image.shape == (1600, 1600) and h['BUNIT'] == 'MJy/sr'
                    assert h['CDELT1'] == h['CDELT2'] == 100 and h['CUNIT1'] == 'pc'
                    assert h['CRPIX1'] == h['CRPIX2'] == 800.5
                    with np.load(STUDY / 'cache' / str(sid) / 'O1.npz') as cache:
                        np.testing.assert_array_equal(image[600:1000, 600:1000], cache['dusty_LSST_g'])
                    raw_checks.append(dict(subhalo_id=sid, member=member.name, unit=h['BUNIT'], pixel_pc=100, raw_matches_cache=True))
                break
            else:
                raise AssertionError(f'Member absent: {sid}')
    pd.DataFrame(raw_checks).to_csv(HERE / 'fresh_raw_FITS_spotchecks.csv', index=False)
    notebook = nbformat.read(STUDY / 'ULTIMATE_multigalaxy_morphology.ipynb', as_version=4)
    nbformat.validate(notebook)
    code = [c for c in notebook.cells if c.cell_type == 'code']
    assert all(c.execution_count is not None for c in code)
    assert not any(o.output_type == 'error' for c in code for o in c.outputs)
    embedded = {hashlib.sha256(base64.b64decode(o.data['image/png'])).hexdigest()
                for c in code for o in c.outputs if 'image/png' in o.get('data', {})}
    assert {sha(p) for p in (STUDY / 'figures').glob('*.png')} <= embedded
    return len(raw_checks), len(code), len(embedded)


def main():
    print('Non-destructive verification; no existing study outputs will be rewritten.', flush=True)
    receipt = dict(executed_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   executable=sys.executable, primary_results='Existing frozen protocol retained',
                   new_sensitivity='Exclude zero-projected-dust objects, descriptively only; not a physical-null correction')
    receipt['study_files_hash_checked'], receipt['previous_result_files_unchanged'] = verify_manifest()
    receipt['fresh_archive_hashes'] = verify_archives()
    native, nonzero = verify_native()
    accuracy, receipt['independent_galaxy_gain_max_difference'] = verify_accuracy(nonzero)
    receipt['observing_replay_galaxies'], receipt['independent_native_R50_checks'] = replay()
    receipt['raw_FITS_spotchecks'], receipt['original_executed_notebook_cells'], receipt['original_embedded_figures'] = check_fits_and_notebook()
    assert verify_manifest() == (receipt['study_files_hash_checked'], receipt['previous_result_files_unchanged'])
    receipt['status'] = 'Numerical reproduction PASS; source-product physical-null calibration UNRESOLVED'
    (HERE / 'verification_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(native.to_string(index=False), flush=True)
    print(accuracy[(accuracy.scope == 'all_26') & (accuracy.band == '2MASS_Ks')].to_string(index=False), flush=True)
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == '__main__':
    main()
