#!/usr/bin/env python3
"""Check displayed-table consistency, not fresh source-native CMB fits."""
from pathlib import Path
import csv
import math
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'derived_data'
checks = []

def read(name):
    with (DATA/name).open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))

def check(label, condition):
    checks.append((label, bool(condition)))
    if not condition:
        raise AssertionError(label)

def ranks(values):
    ordered = sorted(enumerate(values), key=lambda pair: pair[1])
    result = [0.0]*len(values)
    i = 0
    while i < len(values):
        j = i+1
        while j < len(values) and ordered[j][1] == ordered[i][1]:
            j += 1
        rank = (i+1+j)/2
        for k in range(i, j):
            result[ordered[k][0]] = rank
        i = j
    return result

def spearman(a, b):
    a, b = ranks(a), ranks(b)
    ma, mb = sum(a)/len(a), sum(b)/len(b)
    numerator = sum((x-ma)*(y-mb) for x,y in zip(a,b))
    denominator = math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))
    return numerator/denominator

land = read('jrc_12set_landscape.csv')
edges = read('jrc_profile_choice_edges_reconstructed.csv')
regret = [float(r['selection_regret_pp_from_published_values']) for r in edges if r['discordance'] == 'True']
check('Primary discordant median regret rounds to 2.18 pp', round(median(regret),2) == 2.18)
check('Primary discordant maximum regret rounds to 4.46 pp', round(max(regret),2) == 4.46)
check('Primary comparison IDs are unique', len({r['edge_id'] for r in edges}) == 30)
check('Every comparison changes one profile family', all((r['profile_a_id'].split('-')[0] == r['profile_b_id'].split('-')[0]) != (r['profile_a_id'].split('-')[1] == r['profile_b_id'].split('-')[1]) for r in edges))
check('Complete grid gives five neighbors per profile set', all(sum(r['profile_a_id'] == s['profile_set'] or r['profile_b_id'] == s['profile_set'] for r in edges) == 5 for s in land))

controller = read('jrc_controller_publication_summary.csv')
check('Controller table has 12 unique profile sets', len(controller) == len({r['profile_set'] for r in controller}) == 12)
ce = [float(r['EL1_percent_reference_mass']) for r in controller]
check('Controller range is 3.13 to 18.03 percent', min(ce) == 3.13 and max(ce) == 18.03)
check('Reported controller 5.77-fold range is compatible with displayed precision', (max(ce)-0.005)/(min(ce)+0.005) < 5.775 and (max(ce)+0.005)/(min(ce)-0.005) >= 5.765)
check('Controller best-reference profile is W5-V2', min(controller,key=lambda r: float(r['EL1_percent_reference_mass']))['profile_set'] == 'W5-V2')
check('Controller chi-square association rounds to 0.8881', round(spearman(ce,[float(r['mean_reduced_chi2']) for r in controller]),4) == 0.8881)
check('Controller instability association rounds to 0.8252', round(spearman(ce,[float(r['IL1_percent_mean_observed_PM']) for r in controller]),4) == 0.8252)

common = read('jrc_common_sample_reported_summary.csv')
check('Common-sample table explicitly has one reported aggregate row', len(common) == 1 and 'Reported aggregate summary' in common[0]['status'])
check('Common-sample count equals 364 minus 2', int(common[0]['shared_sample_count']) == 364-2)
check('Common-sample reported primary comparison remains 9 of 30', int(common[0]['lower_chi2_discordant_comparisons']) == 9 and int(common[0]['total_comparisons']) == 30)
check('Common-sample reported optima are distinct', common[0]['lowest_mean_reduced_chi2_set'] == 'W3-V2' and common[0]['lowest_EL1_set'] == 'W4-V2')

fresno = read('epa_fresno_1989_05_10_publication_summary.csv')
check('Worked Fresno table has one central plus four alternative rows', len(fresno) == 5 and sum(r['is_central'] == 'True' for r in fresno) == 1)
check('All displayed Fresno rows satisfy all three target ranges', all(0.8 <= float(r['R2']) <= 1 and 0 <= float(r['reduced_chi2']) <= 4 and 80 <= float(r['percent_mass']) <= 120 for r in fresno))
central = next(r for r in fresno if r['is_central'] == 'True')
check('Worked central profile is MOVES2 and largest source is AMSUL', central['profile_id'] == 'MOVES2' and central['largest_source_category'] == 'AMSUL')
changed = [r['profile_id'] for r in fresno if r['largest_source_category'] != central['largest_source_category']]
check('Reported largest-source changes are MOVES1 and MOVES5', changed == ['MOVES1','MOVES5'])
check('Worked central MOVES contribution is 0.946465 micrograms per cubic metre', float(central['MOVES_contribution_ug_m3']) == 0.946465)
check('Worked MOVES1 contribution is 1.556044 micrograms per cubic metre', float(next(r for r in fresno if r['profile_id'] == 'MOVES1')['MOVES_contribution_ug_m3']) == 1.556044)

attrition = read('epa_profile_alternatives_and_attrition.csv')
check('Alternative counts sum to 345 eligible and 22 nonconverged', sum(int(r['eligible']) for r in attrition) == 345 and sum(int(r['nonconverged']) for r in attrition) == 22)
check('Alternative counts sum to 323 converged', sum(int(r['converged']) for r in attrition) == 323)
check('Per-alternative eligible equals converged plus nonconverged', all(int(r['eligible']) == int(r['converged'])+int(r['nonconverged']) for r in attrition))
check('283-subset percentages round to 47.0 and 21.9 percent', round(100*133/283,1) == 47.0 and round(100*62/283,1) == 21.9)

for label, passed in checks:
    print('PASS: '+label)
print(f'PASS: {len(checks)}/{len(checks)} publication-summary consistency checks.')
print('BOUNDARY: These checks do not independently rerun or validate the source-native CMB analyses.')
