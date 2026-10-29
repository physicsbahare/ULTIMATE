"""Fixed grouped benchmark; observable features and truth labels remain separate."""
from pathlib import Path
import json, hashlib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.dummy import DummyRegressor
from sklearn.compose import TransformedTargetRegressor
from sklearn.model_selection import KFold
from sklearn.neighbors import NearestNeighbors
from ml_data import OUT, PREV, TARGETS

MODELS = ['median', 'photometric_ridge', 'morphology_ridge', 'ridge', 'forest']


def feature_columns(bandset, model):
    bands = ['g'] if bandset == 'g_only' else ['g', 'J', 'Ks']
    photometric = ['g_logJy'] + ([] if bandset == 'g_only' else ['color_g_J', 'color_J_Ks'])
    morphology = [b+'_'+m for b in bands for m in ['R50', 'C', 'A', 'q', 'inner_fraction']]
    if model == 'photometric_ridge':
        return photometric
    if model == 'morphology_ridge':
        return morphology
    return photometric + morphology + ([] if bandset == 'g_only' else ['gradient_g_J', 'gradient_J_Ks'])


def estimator(name):
    if name == 'median':
        regression = DummyRegressor(strategy='median')
    elif name == 'forest':
        regression = RandomForestRegressor(n_estimators=80, max_depth=4,
            min_samples_leaf=20, random_state=20261027, n_jobs=1)
    else:
        regression = Ridge(alpha=10.)
    pipeline = make_pipeline(SimpleImputer(strategy='median', keep_empty_features=True),
                             StandardScaler(), regression)
    return TransformedTargetRegressor(regressor=pipeline, transformer=StandardScaler())


def splits(eligible):
    eligible = np.sort(eligible)
    rows = []
    for fold, (remaining, test) in enumerate(KFold(5, shuffle=True, random_state=20261027).split(eligible)):
        available = eligible[remaining]
        calibration = np.random.default_rng(20261027+fold).choice(available, size=5, replace=False)
        train = np.setdiff1d(available, calibration)
        for role, ids in [('fit', train), ('calibration', calibration), ('outer_test', eligible[test])]:
            rows.extend(dict(fold=fold, subhalo_id=int(sid), role=role) for sid in ids)
        assert not set(train) & set(calibration) and not set(train) & set(eligible[test])
        assert not set(calibration) & set(eligible[test])
    result = pd.DataFrame(rows)
    result.to_csv(OUT/'preliminary_cv_splits.csv', index=False)
    return result


def train_predict(features, labels, train_ids, calibration_ids, test_ids, bandset, name):
    columns = feature_columns(bandset, name)
    assert not any('clear' in c or c in TARGETS or 'mass' in c or 'dust' in c for c in columns)
    joined = features.merge(labels, on=['subhalo_id', 'view'], validate='many_to_one')
    train = joined[joined.subhalo_id.isin(train_ids)]
    calibration = joined[joined.subhalo_id.isin(calibration_ids)]
    test = joined[joined.subhalo_id.isin(test_ids)].copy()
    assert not set(train.subhalo_id) & set(test.subhalo_id)
    model = estimator(name)
    model.fit(train[columns], train[TARGETS])
    prediction = model.predict(test[columns])
    q = np.full(len(TARGETS), np.nan)
    if len(calibration):
        residuals = abs(model.predict(calibration[columns])-calibration[TARGETS].to_numpy())
        scores = pd.DataFrame(residuals, columns=TARGETS)
        scores['subhalo_id'] = calibration.subhalo_id.to_numpy()
        galaxy_max = scores.groupby('subhalo_id')[TARGETS].max()
        rank = int(np.ceil((len(galaxy_max)+1)*.8))
        assert rank <= len(galaxy_max)
        q = np.sort(galaxy_max.to_numpy(), axis=0)[rank-1]
    # Observable-space nearest-galaxy distance; metadata are used for diagnostics only.
    preprocess = make_pipeline(SimpleImputer(strategy='median', keep_empty_features=True), StandardScaler())
    xt = preprocess.fit_transform(train[columns])
    center = pd.DataFrame(xt).groupby(train.subhalo_id.to_numpy()).mean()
    distance = NearestNeighbors(n_neighbors=1).fit(center).kneighbors(preprocess.transform(test[columns]))[0][:, 0]
    rows = []
    for j, target in enumerate(TARGETS):
        record = test[['subhalo_id', 'view', 'draw']].copy()
        record['target'] = target
        record['truth'] = test[target].to_numpy()
        record['prediction'] = prediction[:, j]
        record['abs_error'] = abs(record.prediction-record.truth)
        record['interval_halfwidth'] = q[j]
        record['covered'] = record.abs_error <= q[j] if np.isfinite(q[j]) else False
        record['feature_distance'] = distance
        record['mass_outside_fit_range'] = (test.log_stellar_mass < train.log_stellar_mass.min()).to_numpy() | (test.log_stellar_mass > train.log_stellar_mass.max()).to_numpy()
        if target.startswith('dR50_') or target.startswith('dC_'):
            metric, band = target[1:].split('_')
            observed = test[band+'_'+metric].to_numpy()
            truth_clear = test['clear_'+metric+'_'+band].to_numpy()
            record['uncorrected_clear_error'] = abs(observed-truth_clear)
            record['corrected_clear_error'] = abs(observed-prediction[:, j]-truth_clear)
        else:
            record['uncorrected_clear_error'] = np.nan
            record['corrected_clear_error'] = np.nan
        rows.append(record)
    return pd.concat(rows, ignore_index=True)


def bootstrap(values):
    values = np.asarray(values, dtype=float)
    sample = np.random.default_rng(20261027).integers(len(values), size=(5000, len(values)))
    return np.quantile(values[sample].mean(axis=1), [.025, .975])


def summarize(predictions):
    keys = ['condition', 'mode', 'bandset', 'model', 'target', 'subhalo_id']
    galaxy = predictions.groupby(keys).agg(MAE=('abs_error', 'mean'),
        bias=('prediction', 'mean'), truth_mean=('truth', 'mean'),
        row_coverage=('covered', 'mean'), entire_galaxy_covered=('covered', 'all'),
        halfwidth=('interval_halfwidth', 'first'), feature_distance=('feature_distance', 'mean'),
        mass_OOD=('mass_outside_fit_range', 'any'),
        uncorrected_clear_MAE=('uncorrected_clear_error', 'mean'),
        corrected_clear_MAE=('corrected_clear_error', 'mean')).reset_index()
    galaxy['bias'] -= galaxy.truth_mean
    galaxy['correction_gain'] = galaxy.uncorrected_clear_MAE-galaxy.corrected_clear_MAE
    galaxy.to_csv(OUT/'galaxy_heldout_errors.csv', index=False)
    rows = []
    for values, group in galaxy.groupby(keys[:-1]):
        low, high = bootstrap(group.MAE)
        rows.append(dict(zip(keys[:-1], values), n_galaxies=len(group), MAE=group.MAE.mean(),
            MAE_CI_low=low, MAE_CI_high=high, median_galaxy_MAE=group.MAE.median(),
            row_coverage=group.row_coverage.mean(), simultaneous_galaxy_coverage=group.entire_galaxy_covered.mean(),
            mean_interval_width=2*group.halfwidth.mean(),
            mean_uncorrected_clear_error=group.uncorrected_clear_MAE.mean(),
            mean_corrected_clear_error=group.corrected_clear_MAE.mean(),
            mean_correction_gain=group.correction_gain.mean()))
    pd.DataFrame(rows).to_csv(OUT/'heldout_summary.csv', index=False)
    paired = galaxy.pivot(index=['condition', 'bandset', 'model', 'target', 'subhalo_id'], columns='mode', values='MAE').reset_index()
    paired['gain'] = paired.seeing-paired.glao
    paired.to_csv(OUT/'galaxy_GLAO_ML_gains.csv', index=False)
    gains = []
    for values, group in paired.groupby(['condition', 'bandset', 'model', 'target']):
        low, high = bootstrap(group.gain)
        gains.append(dict(zip(['condition', 'bandset', 'model', 'target'], values),
                          n_galaxies=len(group), seeing_MAE=group.seeing.mean(), glao_MAE=group.glao.mean(),
                          mean_gain=group.gain.mean(), CI_low=low, CI_high=high,
                          n_improved=int((group.gain > 1e-10).sum()), n_worsened=int((group.gain < -1e-10).sum())))
    pd.DataFrame(gains).to_csv(OUT/'GLAO_ML_gain_summary.csv', index=False)
    g_only = paired[paired.bandset == 'g_only']
    assert abs(g_only.gain).max() < 1e-12, 'Identical g control must have zero strategy gain'
    # Within-galaxy repeated-noise spread is not between-galaxy uncertainty.
    dispersion = predictions.groupby(['condition','mode','bandset','model','target','subhalo_id','view']).prediction.std().reset_index(name='noise_prediction_SD')
    dispersion.to_csv(OUT/'within_scene_noise_prediction_spread.csv', index=False)
    return galaxy


def run(recompute=False):
    features = pd.read_csv(OUT/'observable_features.csv')
    labels = pd.read_csv(OUT/'operational_labels.csv')
    eligible = labels.loc[~labels.zero_projected_dust, 'subhalo_id'].unique()
    zero = labels.loc[labels.zero_projected_dust, 'subhalo_id'].unique()
    assert len(eligible) == 22 and len(zero) == 4
    split = splits(eligible)
    cache = OUT/'prediction_checkpoints'
    cache.mkdir(exist_ok=True)
    parts = []
    for (condition, mode), subset in features.groupby(['condition', 'mode']):
        for bandset in ['g_only', 'g_J_Ks']:
            for model_name in MODELS:
                path = cache/f'{condition}_{mode}_{bandset}_{model_name}.csv.gz'
                if path.exists() and not recompute:
                    parts.append(pd.read_csv(path)); continue
                records = []
                for fold, roles in split.groupby('fold'):
                    ids = {role: roles.loc[roles.role == role, 'subhalo_id'].to_numpy() for role in ['fit','calibration','outer_test']}
                    predicted = train_predict(subset, labels, ids['fit'], ids['calibration'], ids['outer_test'], bandset, model_name)
                    predicted['fold'] = fold
                    records.append(predicted)
                result = pd.concat(records, ignore_index=True)
                result['condition'], result['mode'], result['bandset'], result['model'] = condition, mode, bandset, model_name
                result.to_csv(path, index=False)
                parts.append(result)
                print('Grouped CV:', condition, mode, bandset, model_name, flush=True)
    predictions = pd.concat(parts, ignore_index=True)
    predictions.to_csv(OUT/'heldout_predictions.csv.gz', index=False)
    summarize(predictions)
    # Deliberate OOD challenge, fit on lower-mass galaxies only; no calibration claim.
    metadata = labels.groupby('subhalo_id').first()
    eligible_meta = metadata.loc[eligible]
    boundary = eligible_meta.log_stellar_mass.quantile(.75)
    high_mass = eligible_meta.index[eligible_meta.log_stellar_mass >= boundary].to_numpy()
    low_mass = np.setdiff1d(eligible, high_mass)
    original = features[(features.condition == 'original_noise') & (features['mode'] == 'glao')]
    challenges = []
    challenge_splits = []
    for name, fit_ids, test_ids in [('high_mass_quartile', low_mass, high_mass), ('zero_projected_dust_controls', eligible, zero)]:
        for role, ids in [('fit',fit_ids),('challenge',test_ids)]:
            challenge_splits.extend(dict(challenge=name, role=role, subhalo_id=int(sid)) for sid in ids)
        for model_name in ['median','ridge','forest']:
            prediction = train_predict(original, labels, fit_ids, [], test_ids, 'g_J_Ks', model_name)
            prediction['challenge'], prediction['model'] = name, model_name
            challenges.append(prediction)
    pd.DataFrame(challenge_splits).to_csv(OUT/'OOD_split_provenance.csv', index=False)
    challenge = pd.concat(challenges, ignore_index=True)
    challenge.to_csv(OUT/'OOD_predictions.csv.gz', index=False)
    cgal = challenge.groupby(['challenge','model','target','subhalo_id']).abs_error.mean().reset_index(name='MAE')
    cgal.to_csv(OUT/'OOD_galaxy_errors.csv', index=False)
    cgal.groupby(['challenge','model','target']).agg(n_galaxies=('subhalo_id','nunique'), MAE=('MAE','mean')).to_csv(OUT/'OOD_summary.csv')
    provenance = dict(protocol_sha256=hashlib.sha256((OUT/'PROTOCOL.md').read_bytes()).hexdigest(),
        original_explored_galaxies=26, excluded_source_null_training_galaxies=[int(x) for x in sorted(zero)],
        grouped_CV_eligible=22, outer_folds=5, calibration_galaxies_per_fold=5,
        fit_galaxies_per_fold=split[split.role=='fit'].groupby('fold').size().to_dict(),
        model_hyperparameters_fixed=True, alpha=.2, interval_score='maximum residual over views/draws per calibration galaxy',
        model_names=MODELS, targets=TARGETS, preliminary_only=True, final_120_sample_used=False,
        observable_features={f'{b}/{m}':feature_columns(b,m) for b in ['g_only','g_J_Ks'] for m in MODELS},
        systematic_label_uncertainty='Unresolved source-product residuals and aperture sensitivity; no offset subtraction',
        interval_limit='Conditional diagnostic; exchangeability and physical-label accuracy not established')
    (OUT/'train_test_provenance.json').write_text(json.dumps(provenance, indent=2))
    print('Finished grouped CV and OOD challenges.', flush=True)


if __name__ == '__main__':
    run()
