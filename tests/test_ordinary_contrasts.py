import sys
from pathlib import Path
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import audit_ordinary_contrasts as audit
import audit_epa_native_strengthening as native


class ContrastTests(unittest.TestCase):
    def test_diagonal_covariance(self):
        cov, _ = audit.covariance(np.eye(2), [4, 9])
        np.testing.assert_allclose(cov, np.diag([4, 9]))

    def test_svd_direct_inverse(self):
        a = np.array([[1., 2.], [3., 1.], [0., 4.]])
        v = np.array([1., 3., 2.])
        cov, _ = audit.covariance(a, v)
        np.testing.assert_allclose(cov, np.linalg.inv(a.T @ np.diag(1/v) @ a))

    def test_covariance_changes_contrast(self):
        pos = audit.contrast_set([5, 2], [[1,.9],[.9,1]], .05)
        neg = audit.contrast_set([5, 2], [[1,-.9],[-.9,1]], .05)
        self.assertEqual(pos['candidates'], [0])
        self.assertEqual(neg['candidates'], [0, 1])

    def test_permutation(self):
        s = np.array([6., 1., 4.]); cov = np.diag([1.,2.,3.]); order = [2,0,1]
        a = audit.contrast_set(s, cov, .05)['candidates']
        b = audit.contrast_set(s[order], cov[np.ix_(order,order)], .05)['candidates']
        self.assertEqual(a, sorted(order[i] for i in b))

    def test_units(self):
        s = np.array([5., 2.]); cov = np.array([[1.,.3],[.3,2.]])
        a = audit.contrast_set(s, cov, .05)
        b = audit.contrast_set(s*100, cov*10000, .05)
        self.assertEqual(a['candidates'], b['candidates'])
        self.assertAlmostEqual(a['pairs'][0]['lower']*100, b['pairs'][0]['lower'])

    def test_tie(self):
        self.assertEqual(audit.contrast_set([2,2], np.eye(2), .05)['candidates'], [0,1])

    def test_single_source(self):
        self.assertEqual(audit.contrast_set([2], [[1]], .05)['candidates'], [0])

    def test_zero_contrast_variance(self):
        self.assertEqual(audit.contrast_set([3,2], np.ones((2,2)), .05)['candidates'], [0])

    def test_singular(self):
        with self.assertRaises(ValueError):
            audit.covariance(np.ones((4,2)), np.ones(4))

    def test_invalid(self):
        for variance in ([0,1], [-1,1], [np.nan,1]):
            with self.assertRaises(ValueError):
                audit.covariance(np.eye(2), variance)
        with self.assertRaises(ValueError):
            audit.contrast_set([2,1], [[1,2],[2,1]], .05)

    def test_final_weight_replay(self):
        species = native.CONFIG['species']
        receptor = {'TMAC':'10'}; profiles = {'a':{}, 'b':{}}
        for i, name in enumerate(species):
            f1, f2 = .01*(i+1), .02*(1 + i % 4)
            receptor[name] = str(3*f1+5*f2)
            receptor[name[:-1]+'U'] = '.01'
            profiles['a'][name], profiles['b'][name] = str(f1), str(f2)
            profiles['a'][name[:-1]+'U'] = '.005'
            profiles['b'][name[:-1]+'U'] = '.003'
        frozen = native.effective_variance_fit(receptor, profiles, ['a','b'])
        self.assertTrue(frozen['converged'])
        s, f, v = audit.replay_last_weights(receptor, profiles, ['a','b'], frozen['iterations'])
        np.testing.assert_allclose(s, list(frozen['source_contributions'].values()), rtol=0, atol=0)
        self.assertTrue(np.all(np.linalg.eigvalsh(audit.covariance(f,v)[0]) > 0))


if __name__ == '__main__':
    unittest.main()
