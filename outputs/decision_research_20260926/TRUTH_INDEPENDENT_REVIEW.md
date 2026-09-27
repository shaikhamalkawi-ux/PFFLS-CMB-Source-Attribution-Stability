# Independent review of the frozen truth-index benchmark

Date: 26 September 2026. Status: **implementation review and independent saved-ledger audit PASS**. No blocking mathematical or numerical defect was found. The scientific limitations below remain material.

This is a bounded independent mathematical, semantic, and numerical audit. It is not an endorsement of a new method, environmental source truth, post-selection confidence coverage, or total atmospheric source mass. The target remains the largest modeled integrated signal over the 82 released channels. No producer, frozen input, frozen result, manuscript, or Git state was modified.

## 1. Frozen identities and review scope

The reviewer read the complete v3 protocol, implementation and synthetic tests. The previous v2 protocol remains preserved.

| Artifact | SHA-256 |
|---|---|
| Producer script | `023d4c74f3dd91711e55144c9831059ed622afae3975b5bf64b1b792ea06b1ad` |
| Synthetic tests | `5bcc685d35cec71daf11be792f50761277c896d508a35b0a5acdcf514187e8bc` |
| Protocol v3 | `006e367d6c565af585bd7bf50ff3067a85f25b3bde8c174cfbaca6e33f512c70` |
| Preserved protocol v2 | `5b5ad892f2ca2c44e498deab3e34118d67b85bad8e96ba08e72e5fdac6675ac0` |
| Preserved v2 source inventory | `f4530e2093f143f76d72536f18077bee729ecbc6fcc19094d16f671c5ca67bb0` |
| Unchanged native solver | `42c327b7ef629077bf1f11d1562ccee500a9192b236a1add771ff522070d1c09` |
| Frozen configuration | `8b77f98045f0ffd608de37b357c65107bbdb333d119b13bc22b614fe25e048c9` |
| Frozen numerical-array archive | `78ec90aa3adb31c7d4e83237bcec79643579161d9e6407d9479995ed494581c1` |
| Complete seven-panel result | `e4bf45de87335c853edc15170e3a8706a1540797069766fed552fe5ead49362b` |

The configuration records Python 3.12.14, NumPy 2.3.5, SciPy 1.18.1 and scoped h5py 3.16.0. Each saved numerical ledger is checked against its hash in the final result. No released data are republished here.

## 2. Independent implementation checks

The reviewer reran all **40 supplied synthetic tests: PASS**, through direct unittest discovery, not the producer's test-gate command. Thus the prepared test gate was not replaced.

Additional independent checks used a separately written reduced-QR solver and covariance `inv(R) @ inv(R).T`, not the producer's native least-squares call or inverse Gram-matrix implementation:

- 24 random positive, correlated-profile weighted least-squares designs.
- 144 contrast decisions over the six declared alpha values, using `norm.isf(alpha/(p*(p-1)))` and separately looped pair comparisons.
- Every one of the 992 combinations of 32 possible prediction masks and 31 nonempty truth masks, independently converted to Python sets.

All passed. Maximum absolute discrepancies in the random-design checks were 1.20e-14 for coefficients, 3.23e-16 for covariance, and 2.74e-13 for Q. These checks did not use released benchmark observations or regenerate its controls.

### Mathematical and semantic findings

The implementation correctly uses absolute supplied uncertainty covariance `(P W P.T)^-1`; it does not estimate or multiply an empirical residual scale. Contrast variance includes covariance terms, `Vjj + Vkk - 2 Vjk`. The two-sided Bonferroni threshold is correct for the fitted unordered pairs, conditional on a fixed design and the stated noise assumptions. It is not automatically calibrated after profile selection, admission, misspecification, or correlated error.

Shared nonnegativity and inclusive Q admission are applied to entire fits. The native solver is not constrained or source-pruned in this benchmark; negative coefficients below tolerance exclude the fit. All-rejected rows are empty failures and remain in denominators. Profile selection uses minimum Q within the shared-admissible set, separately from the pre-admission diagnostic winner.

Numerical ties retain every co-leader. All-co-leader truth coverage means set containment, whereas a singleton that is one true co-leader is not scored as a wrong singleton. These are intentionally different metrics. Wrong-singleton risk is null when its denominator is zero. Strict pair declarations across a true numerical tie are false declarations.

Selected point leaders are contained in selected contrast sets; the union of point leaders is contained in the union of contrast sets. The same numerical tolerance makes these relations coherent. This is an established set construction, not a new theorem. Union pairwise declarations require the same strict direction in every admitted fit.

For omitted source ID 4, truth remains five-dimensional. All ten pair opportunities and six fitted-pair opportunities are recorded separately; the four omitted-source pairs receive no declaration. They are not dropped from the all-source denominator.

The generated-control bootstrap clusters entire replicate IDs and keeps the 24 rows together and methods paired. Undefined risk draws are preserved as undefined and counted, not converted to zero. This review does not independently recompute all 2,000-resample bootstrap quantiles.

## 3. Minor diagnostic-label caveat

The counter named `fits_with_retained_tiny_negative_coefficients` increments whenever a fit contains a coefficient in [-tau, 0), including a fit excluded for another negative coefficient or Q. Its literal scope is **fits containing within-tolerance negative coefficients**, not exclusively admitted fits. This does not change admission or decisions. The saved count is zero in every panel, independently checked: no current numerical result is affected. No frozen scoring change is requested.

## 4. Saved-ledger and actual-design audit

A second reviewer had already checked the producer's saved arrays using a vectorized residual/Gram-identity implementation. The present additional audit intentionally uses a separate code path: explicit Python-set counts, direct null-aware ratio reconstruction, separate pair-sign consensus loops, singular values of weighted profile matrices, and QR representative solves.

It imports neither the truth producer nor its native solver. It reads only the frozen input archive, saved ledgers and final aggregates; it never regenerates observations, runs the producer, or rescores the full fitting benchmark. Representative QR reconstructions are numerical verification of already saved fits, not new benchmark outcomes.

The independent saved-ledger check completed successfully:

- All **4,944 rows** and **98 method aggregate records** reconciled, including every count, ratio, failure and denominator. All **28 undefined wrong-singleton risks** remain null.
- All **69,216 pair-declaration vectors** were independently reconstructed from saved coefficients/covariances, using `norm.isf` thresholds and separately looped all-fit consensus. Each vector contains the ten possible source-pair positions, including omitted-source zero declarations.
- The **44,496 actual design instances** reduce to **3,456 distinct weighted designs** after caching identical profiles, uncertainties and fitted source universes. Singular values were calculated for every distinct design. These are condition numbers of the weighted design itself, not its squared-condition Gram matrix.
- **196 representative actual benchmark fits** were verified with independent QR coefficients, `inv(R) @ inv(R).T` covariance and reconstructed Q: all nine profiles at the first, middle and last row of each panel, plus each panel's worst-conditioned row/profile. These checks include rejected fits and all-rejected regimes; they do not select only successful cases.
- Maximum discrepancies were **1.27e-14** absolute / **4.80e-15** relative for coefficients; **2.02e-17** absolute / **3.40e-14** relative Frobenius for covariance; and **3.64e-11** absolute / **1.14e-14** relative for Q.
- The producer was neither imported nor run; controls were not regenerated. Bootstrap quantiles were not independently recomputed. The complete read-only checking code is preserved in the appendix.

| Panel | Rows | Weighted-design condition range | Median condition | Rows with no admissible fit |
|---|---:|---:|---:|---:|
| Released descriptive | 336 | 8.991–15.823 | 12.542 | 0 |
| Included truth | 768 | 9.076–15.747 | 12.486 | 47 |
| Excluded profile truth | 768 | 9.076–15.747 | 12.486 | 768 |
| Correlated receptor error | 768 | 9.076–15.747 | 12.486 | 3 |
| Underreported uncertainty | 768 | 9.076–15.747 | 12.486 | 768 |
| Omitted source 4 | 768 | 6.024–9.832 | 7.530 | 666 |
| Near-tied leaders | 768 | 9.076–15.747 | 12.486 | 47 |

The modest design condition numbers and close QR agreement do not identify a numerical explanation for the observed failures. They do not validate the generating/noise assumptions either.

### Important scientific limitation: no admitted profile multiplicity

A separate direct saved-ledger check confirmed that every nonempty row has **exactly one admitted profile, always frozen profile index 0**. The corresponding selected and union point decisions are identical, and selected versus union contrast decisions are identical at every alpha, including all pairwise declarations. Nonempty-row counts are respectively 336, 721, 0, 765, 0, 102 and 721 in the panel order above.

Consequently, these frozen results cannot demonstrate a benefit of combining multiple admitted profiles. They compare point versus ordinary uncertainty-aware decisions under the admission rules, and expose failure/attrition under the prescribed misspecifications. Presenting them as evidence that finite-profile union improves over the strong ordinary union comparator would be incorrect. The two all-rejected panels are failures, not successful zero-risk abstentions. The independently checked result should be retained without post-outcome profile/gate tuning.

## 5. Interpretation limits

- The released panel is descriptive construction truth; its released error array is not assumed to equal its generation standard deviation.
- Generated controls impose a new explicit noise law. Their conclusions are conditional on this fixed source/profile/noise design.
- Good conditioning and agreement between numerical implementations are not scientific validation of uncertainty calibration.
- Alpha is an operational threshold in this comparison, not promised post-selection coverage.
- Finite profile alternatives and a finite ensemble do not establish continuous-profile robustness or environmental truth.
- Failure fractions and null risks must remain visible. Low wrong-singleton risk without its reporting coverage is not a sufficient performance claim.
- This bounded review does not create a new novelty claim, select a favorable threshold, or authorize manuscript promotion.

## Appendix: independent saved-ledger checker

The following code was executed from the repository root through standard input in the bundled Python runtime. It does not import either producer, does not modify files, and emits an aggregate JSON result. Keep the private NPZ inputs private when reproducing it.

```python
import hashlib, itertools, json, math
from pathlib import Path
import numpy as np
from scipy.stats import norm

root=Path.cwd(); pub=root/'outputs/decision_research_20260926'; priv=root/'private/decision_research_20260926'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check(ok,msg):
    if not ok: raise RuntimeError(msg)
def close(x,y,msg):
    check((x is None and y is None) or (x is not None and y is not None and math.isclose(x,y,rel_tol=1e-13,abs_tol=1e-13)),msg)
summary=json.loads((pub/'truth_results.json').read_text()); freeze=json.loads((pub/'truth_input_freeze.json').read_text())
check(digest(pub/'truth_results.json')=='e4bf45de87335c853edc15170e3a8706a1540797069766fed552fe5ead49362b','results identity')
check(digest(priv/'truth_frozen_arrays.npz')=='78ec90aa3adb31c7d4e83237bcec79643579161d9e6407d9479995ed494581c1','arrays identity')
check(digest(pub/'truth_configuration_frozen.json')=='8b77f98045f0ffd608de37b357c65107bbdb333d119b13bc22b614fe25e048c9','config identity')
with np.load(priv/'truth_frozen_arrays.npz',allow_pickle=False) as z: arrays={k:z[k] for k in z.files}
pairs=list(itertools.combinations(range(5),2)); cache={}; panels=[]; qr_count=0; methods_count=0; orders_count=0; null_risks=0
maximum={'beta_abs':0.,'beta_relative':0.,'covariance_abs':0.,'covariance_relative_frobenius':0.,'Q_abs':0.,'Q_relative':0.}
for panel_no, panel in enumerate(summary['panels']):
    name=panel['panel']; path=priv/f'truth_ledger_{name}.npz'
    check(digest(path)==panel['private_ledger_sha256'],'ledger identity')
    with np.load(path,allow_pickle=False) as z: saved={k:z[k] for k in z.files}
    if panel_no==0:
        x,sigma,truth=arrays['released_x'],arrays['released_sigma'],arrays['M0']
    else:
        x=arrays['generated_x'][panel_no-1].reshape(-1,82)
        sigma=arrays['generated_sigma'][panel_no-1].reshape(-1,82)
        truth=arrays['generated_truth'][panel_no-1].reshape(-1,5)
    ids=panel['source_ids_fitted']; p=len(ids); n=len(x)
    true_sets=[]; true_signs=[]
    for row in truth:
        tau=1e-10*max(1.,max(abs(row)))
        true_sets.append({j for j in range(5) if max(row)-row[j]<=tau})
        true_signs.append([1 if row[j]-row[k]>tau else -1 if row[j]-row[k]<-tau else 0 for j,k in pairs])
    true_signs=np.asarray(true_signs)
    check(np.array_equal(true_signs,saved['truth_orders']),'truth pair signs')
    check(np.array_equal([sum(1<<j for j in s) for s in true_sets],saved['truth_masks']),'truth leaders')
    check(int(saved['accepted'].sum())==panel['admissible_fits'],'admission count')
    check(int(saved['numeric'].sum())==panel['numerical_fits'],'numerical count')
    check(int(np.sum(~saved['accepted'].any(axis=1)))==panel['samples_without_admissible_fit'],'all rejected')
    check(sum(panel['first_exclusion_or_accepted_counts'].values())==n*len(arrays['candidates']),'exclusive gate counts')
    check(panel['fits_with_retained_tiny_negative_coefficients']==0,'tiny negative caveat has effect')
    for mi,method in enumerate(panel['methods']):
        masks=saved['predicted_masks'][mi]; orders=saved['orders'][mi]
        sizes=[]; wrong=covered=0
        for row,mask in enumerate(masks):
            prediction={j for j in range(5) if int(mask)&(1<<j)}
            sizes.append(len(prediction)); wrong+=len(prediction)==1 and not prediction<=true_sets[row]; covered+=true_sets[row]<=prediction
        sizes=np.asarray(sizes); declared=orders!=0
        counts={'samples':n,'singletons':int(np.sum(sizes==1)),'wrong_singletons':int(wrong),'truth_all_coleaders_covered':int(covered),
                'empty_failures':int(np.sum(sizes==0)),'nonempty_ambiguous':int(np.sum(sizes>1)),
                'nonempty':int(np.sum(sizes>0)),'set_size_sum':int(sizes.sum()),'pair_declarations':int(declared.sum()),
                'false_pair_declarations':int(np.sum(declared&(orders!=true_signs))),
                'all_pair_opportunities':10*n,'fitted_pair_opportunities':p*(p-1)//2*n}
        for key,value in counts.items(): check(method[key]==value,name+' '+key)
        ratios={'singleton_coverage':('singletons','samples'),'wrong_singleton_risk':('wrong_singletons','singletons'),
                'truth_in_set_all_coleaders_coverage':('truth_all_coleaders_covered','samples'),
                'empty_failure_fraction':('empty_failures','samples'),'mean_set_size_all_samples':('set_size_sum','samples'),
                'mean_set_size_nonempty':('set_size_sum','nonempty'),'pair_declaration_coverage_all_ten':('pair_declarations','all_pair_opportunities'),
                'pair_declaration_coverage_fitted':('pair_declarations','fitted_pair_opportunities'),'false_pair_declaration_risk':('false_pair_declarations','pair_declarations')}
        for key,(a,b) in ratios.items(): close(method[key],counts[a]/counts[b] if counts[b] else None,name+' '+key)
        null_risks+=method['wrong_singleton_risk'] is None
        if p==4:
            check(np.all(masks<16),'omitted source appeared')
            check(np.all(orders[:,[j for j,pa in enumerate(pairs) if 4 in pa]]==0),'omitted pair declaration')
        methods_count+=1
    # Reconstruct ALL pair declarations independently, including finite union consensus.
    for row in range(n):
        admitted=np.flatnonzero(saved['accepted'][row]); selected=int(saved['selected_index'][row])
        for mi,method in enumerate(panel['methods']):
            expected=np.zeros(10,dtype=int)
            use=[selected] if method['family'].startswith('selected') and selected>=0 else admitted
            if len(use):
                for pi,(j,k) in enumerate(pairs):
                    if j not in ids or k not in ids: continue
                    signs=[]
                    for model in use:
                        b=saved['contributions'][row,model]; v=saved['covariance'][row,model]
                        tau=1e-10*max(1.,np.max(np.abs(b[ids]))); delta=b[j]-b[k]
                        width=0. if method['alpha'] is None else norm.isf(method['alpha']/(p*(p-1)))*math.sqrt(max(0.,v[j,j]+v[k,k]-2*v[j,k]))
                        signs.append(1 if delta-width>tau else -1 if delta+width< -tau else 0)
                    expected[pi]=1 if all(s==1 for s in signs) else -1 if all(s==-1 for s in signs) else 0
            check(np.array_equal(expected,saved['orders'][mi,row]),name+' pair decision mismatch')
            orders_count+=1
    # Every actual weighted design; cache identical inputs across replicates/panels.
    conds=np.empty((n,len(arrays['candidates'])))
    for row in range(n):
        for model,profile in enumerate(arrays['candidates']):
            key=(tuple(ids),model,sigma[row].tobytes())
            if key not in cache:
                weighted=profile[ids].T/sigma[row,:,None]
                singular=np.linalg.svd(weighted,compute_uv=False)
                cache[key]=float(singular[0]/singular[-1])
            conds[row,model]=cache[key]
    worst=np.unravel_index(np.argmax(conds),conds.shape)
    representative={(row,model) for row in (0,n//2,n-1) for model in range(len(arrays['candidates']))}
    representative.add(tuple(map(int,worst)))
    for row,model in sorted(representative):
        f=arrays['candidates'][model,ids].T
        q,r=np.linalg.qr(f/sigma[row,:,None],mode='reduced')
        beta=np.linalg.solve(r,q.T@(x[row]/sigma[row])); ri=np.linalg.inv(r); covariance=ri@ri.T
        stored_beta=saved['contributions'][row,model,ids]
        stored_cov=saved['covariance'][row,model][np.ix_(ids,ids)]
        q_value=float(np.sum(((x[row]-f@beta)/sigma[row])**2)); stored_q=float(saved['Q'][row,model])
        discrepancies={'beta_abs':float(np.max(np.abs(beta-stored_beta))),
                       'beta_relative':float(np.linalg.norm(beta-stored_beta)/max(1.,np.linalg.norm(beta))),
                       'covariance_abs':float(np.max(np.abs(covariance-stored_cov))),
                       'covariance_relative_frobenius':float(np.linalg.norm(covariance-stored_cov)/np.linalg.norm(covariance)),
                       'Q_abs':abs(q_value-stored_q),'Q_relative':abs(q_value-stored_q)/max(1.,abs(q_value))}
        for key,value in discrepancies.items(): maximum[key]=max(maximum[key],value)
        check(np.allclose(beta,stored_beta,rtol=1e-9,atol=1e-8),'QR coefficients')
        check(np.allclose(covariance,stored_cov,rtol=1e-9,atol=1e-8),'QR covariance')
        check(math.isclose(q_value,stored_q,rel_tol=1e-9,abs_tol=1e-8),'QR Q')
        qr_count+=1
    panels.append({'panel':name,'rows':n,'fits':n*len(arrays['candidates']),'condition_min':float(conds.min()),
                   'condition_median':float(np.median(conds)),'condition_max':float(conds.max()),
                   'QR_checks':len(representative),'all_rejected':panel['samples_without_admissible_fit']})
print(json.dumps({'status':'PASS','panels':panels,'total_rows':sum(p['rows'] for p in panels),'total_design_instances':sum(p['fits'] for p in panels),
                  'distinct_weighted_designs':len(cache),'method_aggregate_records':methods_count,'pair_decision_vectors':orders_count,
                  'representative_QR_checks':qr_count,'maximum_discrepancies':maximum,'undefined_wrong_singleton_risks':null_risks,
                  'bootstrap_interval_recomputation':False,'producer_imported_or_run':False},indent=2))
```
