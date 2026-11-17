"""MMC-01 section 6: closest-distance proximity and S_AB, with a degree-matched null.

Primary metric: closest-distance (Guney/Menche). For target set T and module M,
    d_c(T,M) = mean over t in T of min over m in M of shortest_path(t, m)

Null: 1000 random (T', M') pairs drawn by binned degree matching, matching the
degree distribution of T and of M separately. Reported quantity is the z-score.

Secondary: separation S_AB (Menche), reported alongside, never promoted.

Distances come from a full unweighted BFS distance matrix over the LCC, cached
to disk as uint8 (the LCC is connected, so every entry is a real distance).
"""
import json
import pathlib

import numpy as np
from scipy import sparse

ROOT = pathlib.Path(r"D:\mmc01")
RES = ROOT / "results"
CACHE = ROOT / "data" / "dist"

SEED_PRIMARY = 20261117        # frozen; printed in every output
SEED_REPLICATION = 20261118    # frozen now, deliberately unused in this study
N_PERM = 1000
MIN_BIN = 100                  # degree bins hold at least this many nodes


def load_graph(threshold):
    adj = sparse.load_npz(RES / f"graph_{threshold}.npz").tocsr()
    nodes = json.loads((RES / f"graph_{threshold}.json").read_text(encoding="utf-8"))["nodes"]
    return adj, nodes


def distance_matrix(threshold, adj):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"dist_{threshold}.npy"
    n = adj.shape[0]
    if path.exists():
        D = np.load(path, mmap_mode="r")
        if D.shape == (n, n):
            return D
    indptr, indices = adj.indptr, adj.indices
    D = np.full((n, n), 255, dtype=np.uint8)
    for s in range(n):
        dist = D[s]
        dist[s] = 0
        frontier = np.array([s], dtype=np.int64)
        d = 0
        while frontier.size:
            d += 1
            starts = indptr[frontier]
            counts = indptr[frontier + 1] - starts
            total = int(counts.sum())
            if total == 0:
                break
            offsets = np.arange(total) - np.repeat(np.cumsum(counts) - counts, counts)
            nbrs = indices[np.repeat(starts, counts) + offsets]
            nbrs = np.unique(nbrs)
            nbrs = nbrs[dist[nbrs] == 255]
            if nbrs.size == 0:
                break
            dist[nbrs] = d
            frontier = nbrs.astype(np.int64)
    np.save(path, D)
    return D


def degree_bins(adj):
    """Bin node indices by degree, merging adjacent degrees until each bin has MIN_BIN."""
    deg = np.asarray(adj.sum(axis=1)).ravel().astype(np.int64)
    order = np.argsort(deg, kind="stable")
    bins, cur = [], []
    i = 0
    while i < len(order):
        cur.append(order[i])
        # close the bin once it is big enough AND the next node has a higher degree
        if len(cur) >= MIN_BIN and (i + 1 == len(order) or deg[order[i + 1]] != deg[order[i]]):
            bins.append(np.array(cur, dtype=np.int64))
            cur = []
        i += 1
    if cur:
        if bins:
            bins[-1] = np.concatenate([bins[-1], np.array(cur, dtype=np.int64)])
        else:
            bins.append(np.array(cur, dtype=np.int64))
    bin_of = np.empty(len(deg), dtype=np.int64)
    for b, members in enumerate(bins):
        bin_of[members] = b
    return bins, bin_of, deg


def closest_distance(D, T, M):
    """mean over t of min over m of d(t,m)."""
    sub = D[np.ix_(T, M)].astype(np.int16)
    return float(sub.min(axis=1).mean())


def mean_min_within(D, A):
    """mean over a of min distance to another member of A (self excluded)."""
    if len(A) < 2:
        return 0.0
    sub = D[np.ix_(A, A)].astype(np.int16)
    np.fill_diagonal(sub, 10000)
    return float(sub.min(axis=1).mean())


def separation(D, A, B):
    """Menche S_AB = <d_AB> - (<d_AA> + <d_BB>)/2."""
    sa = D[np.ix_(A, B)].astype(np.int16).min(axis=1)
    sb = D[np.ix_(B, A)].astype(np.int16).min(axis=1)
    d_ab = float((sa.sum() + sb.sum()) / (len(A) + len(B)))
    return d_ab - (mean_min_within(D, A) + mean_min_within(D, B)) / 2.0


def flatten_bins(bins):
    """Pack bins into one array + offsets so sampling can be vectorised."""
    flat = np.concatenate(bins)
    sizes = np.array([len(b) for b in bins], dtype=np.int64)
    starts = np.concatenate([[0], np.cumsum(sizes)[:-1]])
    return flat, starts, sizes


def matched_sample(rng, idx, packed, bin_of):
    """Degree-matched set the same size as idx, without replacement.

    Vectorised draw, then a bounded repair pass for any duplicates.
    """
    flat, starts, sizes = packed
    b = bin_of[idx]
    picks = flat[starts[b] + (rng.random(len(idx)) * sizes[b]).astype(np.int64)]
    for _ in range(50):
        _, first = np.unique(picks, return_index=True)
        dup = np.setdiff1d(np.arange(len(picks)), first)
        if dup.size == 0:
            break
        bd = b[dup]
        picks[dup] = flat[starts[bd] + (rng.random(len(dup)) * sizes[bd]).astype(np.int64)]
    return picks.astype(np.int64)


def proximity_z(D, T, M, packed, bin_of, rng, n_perm=N_PERM):
    obs = closest_distance(D, T, M)
    null = np.empty(n_perm, dtype=np.float64)
    for i in range(n_perm):
        t2 = matched_sample(rng, T, packed, bin_of)
        m2 = matched_sample(rng, M, packed, bin_of)
        null[i] = closest_distance(D, t2, m2)
    mu, sd = null.mean(), null.std(ddof=1)
    z = (obs - mu) / sd if sd > 0 else float("nan")
    return {"d_closest": obs, "null_mean": float(mu), "null_sd": float(sd),
            "z": float(z), "n_perm": n_perm}
