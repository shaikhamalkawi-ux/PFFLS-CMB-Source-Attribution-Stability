#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'derived_data'
checks=[]
def ck(name, cond):
    checks.append((name,bool(cond)))
    if not cond: raise AssertionError(name)

land=pd.read_csv(D/'jrc_12set_landscape.csv')
ref=pd.read_csv(D/'jrc_campaign_point_reference.csv')
edges=pd.read_csv(D/'jrc_profile_choice_edges_reconstructed.csv')
epa=pd.read_csv(D/'epa_primary_outcome_summary.csv')

ck('JRC 12 sets',len(land)==12)
ck('EL1 min 2.27',abs(land.EL1_percent_reference_mass.min()-2.27)<1e-12)
ck('EL1 max 24.24',abs(land.EL1_percent_reference_mass.max()-24.24)<1e-12)
ck('JRC reference sum 43.09',abs(ref.published_mean_ug_m3.sum()-43.09)<1e-12)
ck('30 local edges',len(edges)==30)
ck('9 lower-chi2 discordant',int(edges.discordance.sum())==9)
ck('EPA eligible 345',int(epa.loc[epa['subset']=='Eligible substitutions','n'].iloc[0])==345)
ck('EPA converged 323',int(epa.loc[epa['subset']=='Converged substitutions','n'].iloc[0])==323)
row=epa.loc[epa['subset'].str.startswith('Central + alternative R2 and reduced')].iloc[0]
ck('EPA 283 two-diagnostic subset',int(row['n'])==283)
ck('EPA 133 ordering changes',int(row['any_ordering_change'])==133)
ck('EPA 62 largest-source changes',int(row['largest_source_change'])==62)
row=epa.loc[epa['subset'].str.contains('percent mass')].iloc[0]
ck('EPA 26 three-diagnostic subset',int(row['n'])==26)
ck('EPA 10 ordering changes in 26',int(row['any_ordering_change'])==10)
ck('EPA 2 largest-source changes in 26',int(row['largest_source_change'])==2)

for name, ok in checks:
    print(('PASS' if ok else 'FAIL')+': '+name)
print(f'PASS: {sum(x for _,x in checks)}/{len(checks)} scientific release checks.')

manifest = ROOT / 'SHA256SUMS.txt'
manifest_checks = []
if not manifest.exists():
    raise AssertionError('SHA256SUMS.txt missing')
for raw in manifest.read_text().splitlines():
    if not raw.strip():
        continue
    expected, rel = raw.split(maxsplit=1)
    rel = rel.strip()
    if rel.startswith('./'):
        rel = rel[2:]
    fp = ROOT / rel
    if not fp.exists():
        raise AssertionError(f'manifest file missing: {rel}')
    h = hashlib.sha256(fp.read_bytes()).hexdigest()
    ok = (h == expected)
    manifest_checks.append((rel, ok))
    if not ok:
        raise AssertionError(f'SHA256 mismatch: {rel}')
print(f'PASS: {sum(ok for _, ok in manifest_checks)}/{len(manifest_checks)} SHA256 manifest entries.')
