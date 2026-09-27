"""Post-hoc ordinary plug-in covariance comparator; no coverage claim."""
from __future__ import annotations

from datetime import datetime, timezone
from itertools import combinations
import json
from pathlib import Path
from statistics import NormalDist

import numpy as np

import audit_epa_native_strengthening as native

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'outputs/decision_research_20260926'
PRIVATE = ROOT / 'private/decision_research_20260926'
LEDGER_SHA = 'ba73f7f41de50d4b40edf1fe5be0513120dfb109c9a10730f1007e7f6c3143a2'
NATIVE_SHA = '42c327b7ef629077bf1f11d1562ccee500a9192b236a1add771ff522070d1c09'
ALPHAS = (0.10, 0.05, 0.01)


def covariance(design, variance):
    design = np.asarray(design, dtype=float)
    variance = np.asarray(variance, dtype=float)
    if (design.ndim != 2 or not design.shape[1]
            or variance.shape != (design.shape[0],)
            or not np.all(np.isfinite(design))
            or not np.all(np.isfinite(variance)) or np.any(variance <= 0)):
        raise ValueError('invalid design/variance')
    weighted = design / np.sqrt(variance)[:, None]
    _, singular, vt = np.linalg.svd(weighted, full_matrices=False)
    threshold = np.finfo(float).eps * max(weighted.shape) * singular[0]
    if len(singular) != design.shape[1] or singular[-1] <= threshold:
        raise ValueError('rank-deficient covariance')
    cov = (vt.T * (1.0 / singular**2)) @ vt
    return cov, float(singular[0] / singular[-1])


def contrast_set(contributions, cov, alpha):
    s = np.asarray(contributions, dtype=float)
    cov = np.asarray(cov, dtype=float)
    p = len(s)
    if (not 0 < alpha < 1 or not p or cov.shape != (p, p)
            or not np.all(np.isfinite(s)) or not np.all(np.isfinite(cov))
            or not np.allclose(cov, cov.T, rtol=1e-12, atol=1e-14)):
        raise ValueError('invalid contrast input')
    eigen = np.linalg.eigvalsh(cov)
    cov_tol = 1e-12 * max(1e-300, float(np.max(np.abs(cov))))
    if eigen.min() < -cov_tol:
        raise ValueError('non-positive-semidefinite covariance')
    if p == 1:
        return {'candidates': [0], 'pairs': [], 'critical_z': None,
                'minimum_leader_standardized_margin': None}
    multiplicity = p * (p - 1) // 2
    z = NormalDist().inv_cdf(1 - alpha / (2 * multiplicity))
    candidates = set(range(p))
    pairs = []
    for j, k in combinations(range(p), 2):
        v = float(cov[j, j] + cov[k, k] - 2 * cov[j, k])
        if v < -4 * cov_tol:
            raise ValueError('negative contrast variance')
        se = float(np.sqrt(max(0.0, v)))
        diff = float(s[j] - s[k])
        low, high = diff - z * se, diff + z * se
        if low > 0:
            candidates.discard(k)
        if high < 0:
            candidates.discard(j)
        pairs.append({'j': j, 'k': k, 'difference': diff, 'standard_error': se,
                      'lower': low, 'upper': high})
    leaders = np.flatnonzero(s == s.max()).tolist()
    standardized = []
    if len(leaders) == 1:
        j = leaders[0]
        for pair in pairs:
            if j in (pair['j'], pair['k']) and pair['standard_error'] > 0:
                standardized.append(abs(pair['difference']) / pair['standard_error'])
    return {'candidates': sorted(candidates), 'pairs': pairs, 'critical_z': z,
            'minimum_leader_standardized_margin': min(standardized) if standardized else None}


def replay_last_weights(receptor, profiles, source_ids, iterations):
    if not 1 <= iterations <= native.CONFIG['max_iterations']:
        raise ValueError('invalid frozen iteration count')
    species = native.CONFIG['species']
    c = np.asarray([float(receptor[name]) for name in species])
    uc = np.asarray([float(receptor[name[:-1] + 'U']) for name in species])
    f = np.asarray([[float(profiles[sid][name]) for sid in source_ids] for name in species])
    uf = np.asarray([[float(profiles[sid][name[:-1] + 'U']) for sid in source_ids] for name in species])
    if (not all(np.all(np.isfinite(a)) for a in (c, uc, f, uf))
            or np.any(uc <= 0) or np.any(uf < 0)):
        raise ValueError('invalid native arrays')
    s = np.zeros(len(source_ids))
    for _ in range(iterations):
        variance = uc**2 + uf**2 @ s**2
        s, _, rank, _ = np.linalg.lstsq(f / np.sqrt(variance)[:, None],
                                       c / np.sqrt(variance), rcond=None)
        if rank != len(source_ids) or not np.all(np.isfinite(s)):
            raise ValueError('invalid replay')
    return s, f, variance


def cross_tab(rows, alpha, eligible, flag):
    selected = [row for row in rows if eligible(row)]
    valid = [row for row in selected if row['covariance_status'] == 'VALID_PLUGIN']
    singletons = [row for row in valid if len(row['alphas'][str(alpha)]['candidates']) == 1]
    witnesses = [row for row in selected if flag(row)]
    joint = [row for row in singletons if flag(row)]
    return {'denominator': len(selected), 'covariance_valid': len(valid),
            'covariance_unresolved': len(selected) - len(valid),
            'conditional_singleton': len(singletons), 'existing_joint_witness': len(witnesses),
            'conditional_singleton_and_joint_witness': len(joint),
            'no_conditional_singleton_and_joint_witness': len(witnesses) - len(joint)}


def run():
    targets = [PUBLIC / 'ordinary_contrast_configuration.json',
               PUBLIC / 'ordinary_contrast_results.json',
               PUBLIC / 'ORDINARY_CONTRAST_REPORT.md',
               PRIVATE / 'ordinary_contrast_ledger.json']
    if any(p.exists() for p in targets):
        raise FileExistsError('never overwrite a frozen audit')
    if native.sha256(Path(native.__file__).read_bytes()) != NATIVE_SHA:
        raise ValueError('native solver identity changed')
    payload = (PRIVATE / 'joint_profile_ledger.json').read_bytes()
    if native.sha256(payload) != LEDGER_SHA:
        raise ValueError('joint ledger identity changed')
    config = {'created_utc': datetime.now(timezone.utc).isoformat(),
              'status': 'POST_HOC_PLAN_BEFORE_THIS_BASELINE_SCORES',
              'plan_sha256': native.sha256((PUBLIC / 'ORDINARY_CONTRAST_BASELINE_PLAN.md').read_bytes()),
              'script_sha256': native.sha256(Path(__file__).read_bytes()),
              'test_sha256': native.sha256((ROOT / 'tests/test_ordinary_contrasts.py').read_bytes()),
              'native_script_sha256': NATIVE_SHA, 'joint_ledger_sha256': LEDGER_SHA,
              'alphas': ALPHAS, 'primary_descriptive_alpha': 0.05,
              'sigma_scaling': 'absolute supplied variances; no residual-Q rescaling',
              'scope': 'selected retained-source central model; fixed final EVLS weights; nominal plugin only'}
    with targets[0].open('xb') as stream:
        stream.write(native.json_bytes(config))
    inventory = native.archive_inventory(native.DEFAULT_INPUT)
    native.verify_recovery_identities(inventory, ROOT / 'outputs/strengthening_20260926/source_recovery.json')
    receptors, profiles, _ = native.load_inputs(native.DEFAULT_INPUT)
    samples = json.loads(payload)['samples']
    if len(receptors) != 35 or len(samples) != 35:
        raise ValueError('fixed sample count changed')
    rows = []
    max_replay_difference = 0.0
    for receptor, sample in zip(receptors, samples):
        if sample['sample'] != {k: receptor[k] for k in native.CONFIG['case_identity']}:
            raise ValueError('sample order/identity mismatch')
        central = sample['central']
        if not central['converged']:
            raise ValueError('unexpected central nonconvergence')
        s, f, variance = replay_last_weights(receptor, profiles, central['source_ids'], central['iterations'])
        expected = np.asarray([central['source_contributions'][sid] for sid in central['source_ids']])
        difference = float(np.max(np.abs(s - expected)))
        max_replay_difference = max(max_replay_difference, difference)
        if not np.allclose(s, expected, rtol=1e-12, atol=1e-12):
            raise ValueError('replay differs from frozen central fit')
        row = {'sample': sample['sample'], 'source_ids': central['source_ids'],
               'central_basic': native.fit_targets(central),
               'central_strict': native.fit_targets(central, True),
               'existing': {screen: sample['summaries'][screen]['top'] for screen in ('basic', 'strict')}}
        try:
            cov, condition = covariance(f, variance)
            row.update(covariance_status='VALID_PLUGIN', weighted_design_condition=condition,
                       alphas={str(alpha): contrast_set(s, cov, alpha) for alpha in ALPHAS},
                       source_covariance=cov.tolist(), final_solve_variance=variance.tolist())
        except ValueError as exc:
            row.update(covariance_status='UNRESOLVED', reason=str(exc))
        rows.append(row)
    aggregates = {}
    for alpha in ALPHAS:
        panels = {}
        for scope in ('all35', 'central_basic', 'central_strict'):
            eligible = lambda row, scope=scope: scope == 'all35' or row[scope]
            for screen in ('basic', 'strict'):
                for flag in ('joint_changed_count', 'observed_local_stable_joint_witness',
                             'complete_local_stable_joint_witness'):
                    key = '/'.join((scope, screen, flag))
                    panels[key] = cross_tab(rows, alpha, eligible,
                        lambda row, screen=screen, flag=flag: bool(row['existing'][screen][flag]))
        aggregates[str(alpha)] = panels
    private = native.json_bytes({'configuration': config, 'samples': rows})
    with targets[3].open('xb') as stream:
        stream.write(private)
    result = {'status': 'COMPLETED_POST_HOC_PLUGIN_BASELINE_NOT_COVERAGE_VALIDATION',
              'completed_utc': datetime.now(timezone.utc).isoformat(),
              'configuration': config, 'sample_count': len(rows),
              'max_replay_contribution_difference': max_replay_difference,
              'valid_covariances': sum(r['covariance_status'] == 'VALID_PLUGIN' for r in rows),
              'private_ledger_sha256': native.sha256(private), 'aggregates': aggregates,
              'limitations': ['No field source truth or nominal coverage guarantee',
                'Estimated effective weights and central source pruning treated as fixed',
                'Covariance ignores correlations/systematic errors and profile-family selection',
                'Joint grid retains unresolved alternatives; no full-grid certificate',
                'Post-hoc diagnostic overlap, not a new uncertainty method']}
    with targets[1].open('xb') as stream:
        stream.write(native.json_bytes(result))
    lines = ['# Ordinary joint-contrast comparator — post-hoc diagnostic audit', '',
             'This is a nominal plug-in WLS summary, not validated coverage or field source truth.',
             f"All35 replayed central fits agree; maximum contribution difference {max_replay_difference:.3g}.",
             '', 'Primary nominal alpha0.05 panel (Bonferroni across within-fit source pairs):', '',
             '| Sample scope / existing witness flag | n | Conditional singleton | Witness | Both |',
             '|---|---:|---:|---:|---:|']
    for key, v in aggregates['0.05'].items():
        if (key.startswith('all35/basic/') or key == 'central_strict/strict/joint_changed_count'):
            lines.append(f"| {key} | {v['denominator']} | {v['conditional_singleton']} | "
                         f"{v['existing_joint_witness']} | {v['conditional_singleton_and_joint_witness']} |")
    lines += ['', 'All alpha0.10/0.05/0.01 tables and eligibility denominators are in ordinary_contrast_results.json.',
              'A central covariance warning may already reveal uncertainty that a point-fit comparison misses.',
              'A central conditional singleton plus a profile-choice reversal shows different uncertainty scopes;',
              'it is not evidence that either side knows the environmental truth.', '',
              'Limitations:'] + ['- ' + x for x in result['limitations']]
    with targets[2].open('x', encoding='utf-8', newline='\n') as stream:
        stream.write('\n'.join(lines) + '\n')
    return result


if __name__ == '__main__':
    output = run()
    print(json.dumps({'status': output['status'], 'valid_covariances': output['valid_covariances'],
                      'max_replay_difference': output['max_replay_contribution_difference']}, indent=2))
