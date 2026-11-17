"""Design fact, not a result: what two-sided exact p-values are ATTAINABLE
for given group sizes, independent of any z-score values.

Wilcoxon rank-sum: enumerate every assignment of ranks, find the smallest
two-sided exact p the test can ever produce.
Fisher exact on the 2x2: best-case complete separation.
"""
from itertools import combinations
from math import comb


def min_attainable_wilcoxon_p(n1, n2):
    """Smallest two-sided exact p achievable by rank-sum with these group sizes."""
    N = n1 + n2
    ranks = list(range(1, N + 1))
    sums = [sum(c) for c in combinations(ranks, n1)]
    total = len(sums)
    # most extreme observed statistic = smallest possible rank sum
    obs = min(sums)
    mean = n1 * (N + 1) / 2
    # two-sided: count assignments at least as extreme in either direction
    dev = abs(obs - mean)
    cnt = sum(1 for s in sums if abs(s - mean) >= dev - 1e-9)
    return cnt / total, total


def min_attainable_fisher_p(n1, n2):
    """Two-sided Fisher p under complete separation (all n1 predicted, none of n2)."""
    # 2x2 with row margins n1, n2 and column margin n1 (perfect separation)
    N = n1 + n2
    # hypergeometric prob of the observed perfect table
    p_obs = comb(n1, n1) * comb(n2, 0) / comb(N, n1)
    # two-sided = sum of all tables with prob <= p_obs
    p = 0.0
    for k in range(0, min(n1, n1) + 1):
        if k > n1 or (n1 - k) > n2:
            continue
        pk = comb(n1, k) * comb(n2, n1 - k) / comb(N, n1)
        if pk <= p_obs + 1e-12:
            p += pk
    return p


scenarios = [
    ("PRIMARY as specified (MIXED excluded)", 4, 3),
    ("Sensitivity 3a: MIXED -> NULL", 4, 9),
    ("Sensitivity 3b: MIXED -> POSITIVE", 10, 3),
    ("Sensitivity 4: drop surrogate-only (sacubitril/valsartan)", 3, 3),
]

print(f"{'scenario':<58} {'POS':>4} {'NULL':>5} {'minWilcoxonP':>13} {'minFisherP':>11} {'can reach .05?':>15}")
for name, a, b in scenarios:
    wp, total = min_attainable_wilcoxon_p(a, b)
    fp = min_attainable_fisher_p(a, b)
    ok = "YES" if min(wp, fp) < 0.05 else "NO"
    print(f"{name:<58} {a:>4} {b:>5} {wp:>13.4f} {fp:>11.4f} {ok:>15}")
