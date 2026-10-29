"""Observable-only feature extraction, separate operational simulation labels."""
from pathlib import Path
import sys, json, hashlib
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter

OUT = Path(__file__).resolve().parent
PREV = OUT.parent/'multigalaxy_morphology_20261027'
_path = sys.path.copy()
sys.path.insert(0, str(PREV))
import observe as legacy
from morphology import Geometry, measure
sys.path[:] = _path
BANDS = ['g', 'J', 'Ks']
TARGETS = ['A_g', 'A_Ks', 'A_g_p50_1kpc', 'dR50_g', 'dR50_Ks', 'dC_g', 'dC_Ks']


def properties(images, geometry):
    """No clear image, label, physical map or catalogue argument is accepted."""
    aperture = legacy.geometry(geometry)
    result = {}
    for j, band in enumerate(BANDS):
        values = measure(images[j], aperture)
        for key in ['R50', 'C', 'A', 'q']:
            result[f'{band}_{key}'] = values[key]
        jy = values['flux']/legacy.p.INST[j]['flat_e_s_per_jy']
        result[f'{band}_logJy'] = np.log10(jy) if jy > 0 else np.nan
        inner = images[j][geometry['r'] < 3].sum()
        result[f'{band}_inner_fraction'] = inner/values['flux'] if values['flux'] > 0 else np.nan
        for region, flux in [('inner', inner), ('outer', values['flux']-inner)]:
            result[f'{band}_{region}_logJy'] = np.log10(flux/legacy.p.INST[j]['flat_e_s_per_jy']) if flux > 0 else np.nan
    for first, second in [('g', 'J'), ('J', 'Ks'), ('g', 'Ks')]:
        label = first+'_'+second
        result['color_'+label] = -2.5*(result[first+'_logJy']-result[second+'_logJy'])
        result['gradient_'+label] = -2.5*(result[first+'_inner_logJy']-result[second+'_inner_logJy']
                                                   -result[first+'_outer_logJy']+result[second+'_outer_logJy'])
    return result


def make_labels():
    pairs = pd.read_csv(PREV/'primary_dust_bias.csv')
    inventory = pd.read_csv(PREV/'galaxy_inventory.csv').set_index('subhalo_id')
    labels = []
    radius = Geometry(400, .1, 12).r
    for (sid, view), group in pairs.groupby(['subhalo_id', 'view']):
        by_band = group.set_index('band')
        row = dict(subhalo_id=sid, view=view,
                   zero_projected_dust=bool(inventory.loc[sid, 'dust_mass_field_Msun'] == 0),
                   log_stellar_mass=inventory.loc[sid, 'log10_stellar_mass'],
                   aperture_limited=bool(inventory.loc[sid, 'n_aperture_limited'] > 0))
        for band, source in [('g', 'LSST_g'), ('Ks', '2MASS_Ks')]:
            record = by_band.loc[source]
            row['A_'+band] = record.attenuation_mag
            for metric in ['R50', 'C']:
                row['d'+metric+'_'+band] = record['delta_'+metric]
                row['clear_'+metric+'_'+band] = record[metric+'_clear']
                row['dusty_'+metric+'_'+band] = record[metric+'_dusty']
        clear, dusty, _ = legacy.load(sid, view)
        cs = gaussian_filter(clear[0], 1/.1/2.354820045)
        ds = gaussian_filter(dusty[0], 1/.1/2.354820045)
        valid = (radius < 12) & (cs > 1e-4*cs.max()) & (ds > 0) & (cs > 0)
        row['A_g_p50_1kpc'] = np.median(-2.5*np.log10(ds[valid]/cs[valid]))
        row['A_g_p50_valid_pixels'] = int(valid.sum())
        labels.append(row)
    result = pd.DataFrame(labels)
    assert len(result) == 130 and np.isfinite(result[TARGETS]).all().all()
    result.to_csv(OUT/'operational_labels.csv', index=False)
    # Preserve the empirical null and measurement-policy envelopes separately.
    null = pd.read_csv(PREV/'zero_projected_dust_summary.csv')
    null.to_csv(OUT/'source_null_uncertainty_envelopes.csv', index=False)
    robust = pd.read_csv(PREV/'aperture_center_robustness.csv')
    robust.to_csv(OUT/'label_aperture_center_sensitivity.csv', index=False)
    return result


def build(recompute=False):
    labels = make_labels()
    feature_path = OUT/'observable_features.csv'
    if feature_path.exists() and not recompute:
        return pd.read_csv(feature_path), labels
    rows = []
    geometries = {mode: legacy.p.make_geometry(.1, mode) for mode in ['seeing', 'glao']}
    validation = []
    for row in labels.itertuples():
        _, dusty, _ = legacy.load(row.subhalo_id, row.view)
        rates = {}
        variances = {}
        for mode, geometry in geometries.items():
            rates[mode], loss = legacy.p.render(dusty, geometry)
            variances[mode] = legacy.p.variance(rates[mode], 1.)
            validation.append(dict(subhalo_id=row.subhalo_id, view=row.view, mode=mode, padded_flux_loss=loss))
        common_variance = np.maximum(variances['seeing'], variances['glao'])
        rng = np.random.default_rng(20261027+row.subhalo_id*101+int(row.view[1:])*1000003+100)
        for draw in range(8):
            epsilon = rng.standard_normal(rates['seeing'].shape)
            rng.standard_normal(epsilon.shape)  # Preserve the legacy independent-clear RNG consumption.
            for condition in ['noiseless', 'original_noise', 'equal_noise']:
                for mode, geometry in geometries.items():
                    variance = variances[mode] if condition == 'original_noise' else common_variance
                    image = rates[mode] if condition == 'noiseless' else rates[mode]+np.sqrt(variance)*epsilon
                    rows.append(dict(subhalo_id=row.subhalo_id, view=row.view, draw=draw, mode=mode,
                                     condition=condition, **properties(image, geometry)))
        print('Observable images processed:', row.subhalo_id, row.view, flush=True)
    features = pd.DataFrame(rows)
    assert len(features) == 26*5*8*2*3
    for condition, part in features.groupby('condition'):
        seeing = part[part['mode'] == 'seeing'].set_index(['subhalo_id', 'view', 'draw'])
        glao = part[part['mode'] == 'glao'].set_index(['subhalo_id', 'view', 'draw'])
        for column in [x for x in features if x.startswith('g_')]:
            np.testing.assert_allclose(seeing[column], glao[column], equal_nan=True, atol=1e-12)
    # Verify reconstruction against actual previous noisy dusty properties, all views/draws.
    old = pd.read_csv(PREV/'observed_morphology.csv')
    old = old[(old.phase == 'noise') & (old.scene == 'dusty') & (old.pairing == 'common')]
    recreated = features[features.condition == 'original_noise'].set_index(['subhalo_id', 'view', 'draw', 'mode'])
    for band, source in zip(BANDS, legacy.BANDS):
        reference = old[old.band == source].set_index(['subhalo_id', 'view', 'draw', 'mode']).sort_index()
        candidate = recreated.sort_index()
        for metric in ['R50', 'C', 'q']:
            np.testing.assert_allclose(candidate[band+'_'+metric], reference[metric], rtol=1e-11, atol=1e-11, equal_nan=True)
        np.testing.assert_allclose(candidate[band+'_A'], reference.A_raw, rtol=1e-11, atol=1e-11)
    features.to_csv(feature_path, index=False)
    pd.DataFrame(validation).to_csv(OUT/'feature_render_validation.csv', index=False)
    (OUT/'feature_provenance.json').write_text(json.dumps(dict(
        source='Existing verified DR1 compact image cache; actual dusty images only for X',
        noise_seed='20261027+sid*101+view_number*1000003+100; legacy clear RNG draw consumed',
        targets=TARGETS, independent_total=26, independent_training_eligible=22,
        feature_columns=[x for x in features if x not in ['subhalo_id','view','draw','mode','condition']],
        labels_separate=True, new_images_or_final_test_used=False,
        original_noisy_morphology_reproduced=True, g_strategy_equality=True), indent=2))
    return features, labels


if __name__ == '__main__':
    build()
