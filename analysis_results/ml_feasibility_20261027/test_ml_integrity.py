"""Meaningful information-boundary and partition tests for preliminary ML."""
import unittest
import numpy as np
import pandas as pd
from ml_data import OUT, TARGETS
from ml_benchmark import feature_columns, train_predict, MODELS


class LeakageChecks(unittest.TestCase):
    def test_galaxy_roles_and_source_null_exclusion(self):
        split = pd.read_csv(OUT/'preliminary_cv_splits.csv')
        labels = pd.read_csv(OUT/'operational_labels.csv')
        zero = set(labels.loc[labels.zero_projected_dust, 'subhalo_id'])
        self.assertFalse(zero & set(split.subhalo_id))
        for _, group in split.groupby('fold'):
            self.assertFalse(group.subhalo_id.duplicated().any())
            self.assertEqual(group.subhalo_id.nunique(), 22)
            self.assertEqual(sum(group.role == 'calibration'), 5)
        tested = split[split.role == 'outer_test']
        self.assertEqual(tested.subhalo_id.nunique(), len(tested))

    def test_observable_feature_allowlist(self):
        allowed = set(pd.read_csv(OUT/'observable_features.csv', nrows=1).columns)
        forbidden = set(pd.read_csv(OUT/'operational_labels.csv', nrows=1).columns)
        for bandset in ['g_only', 'g_J_Ks']:
            for model in MODELS:
                used = set(feature_columns(bandset, model))
                self.assertTrue(used <= allowed)
                self.assertFalse(used & forbidden)

    def test_test_truth_cannot_change_predictions_or_intervals(self):
        features = pd.read_csv(OUT/'observable_features.csv')
        features = features[(features.condition == 'noiseless') & (features['mode'] == 'glao') & (features.draw == 0)]
        labels = pd.read_csv(OUT/'operational_labels.csv')
        eligible = np.sort(labels.loc[~labels.zero_projected_dust, 'subhalo_id'].unique())
        train, calibration, test = eligible[:12], eligible[12:17], eligible[17:]
        original = train_predict(features, labels, train, calibration, test, 'g_J_Ks', 'ridge')
        changed = labels.copy()
        changed.loc[changed.subhalo_id.isin(test), TARGETS] += 1000
        perturbed = train_predict(features, changed, train, calibration, test, 'g_J_Ks', 'ridge')
        np.testing.assert_array_equal(original.prediction, perturbed.prediction)
        np.testing.assert_array_equal(original.interval_halfwidth, perturbed.interval_halfwidth)

    def test_final_sample_is_unseen_and_old_objects_are_development(self):
        partition = pd.read_csv(OUT/'expansion/galaxy_partitions.csv')
        # Column names are verified against the frozen expansion table at runtime.
        role = 'partition'
        old = set(pd.read_csv(OUT/'operational_labels.csv').subhalo_id)
        self.assertEqual(len(partition), 120)
        self.assertEqual(partition.subhalo_id.nunique(), 120)
        self.assertEqual(set(partition[partition.subhalo_id.isin(old)][role]), {'development'})
        self.assertFalse(set(partition[partition[role] == 'final_test'].subhalo_id) & old)


if __name__ == '__main__':
    unittest.main()
