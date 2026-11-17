"""MMC-01 section 3: build one undirected STRING graph per confidence threshold.

Reads the frozen raw downloads (untrusted data, parsed only as text/TSV),
normalises every symbol through HGNC, and writes per-threshold artefacts:
  results/graph_<thr>.npz   sparse adjacency of the largest connected component
  results/graph_<thr>.json  node list + stats

Usage: python -I src/build_graph.py
"""
import gzip
import json
import pathlib
import csv
import sys

import numpy as np
from scipy import sparse
from scipy.sparse import csgraph

ROOT = pathlib.Path(r"D:\mmc01")
RAW = ROOT / "data" / "raw"
RES = ROOT / "results"
THRESHOLDS = [400, 700, 900]


def load_hgnc():
    """Approved symbol map: any known alias/previous/approved symbol -> approved."""
    path = RAW / "hgnc_complete_set.txt"
    mapping = {}
    approved = set()
    with open(path, "r", encoding="utf-8", newline="") as fh:
        rdr = csv.DictReader(fh, delimiter="\t")
        for row in rdr:
            if row.get("status") != "Approved":
                continue
            sym = (row.get("symbol") or "").strip()
            if not sym:
                continue
            approved.add(sym)
            mapping[sym] = sym
    # second pass for alias/prev, never overriding an approved symbol
    with open(path, "r", encoding="utf-8", newline="") as fh:
        rdr = csv.DictReader(fh, delimiter="\t")
        for row in rdr:
            if row.get("status") != "Approved":
                continue
            sym = (row.get("symbol") or "").strip()
            for field in ("alias_symbol", "prev_symbol"):
                raw = (row.get(field) or "").strip()
                if not raw:
                    continue
                for alt in raw.split("|"):
                    alt = alt.strip()
                    if alt and alt not in approved and alt not in mapping:
                        mapping[alt] = sym
    return mapping, approved


def load_ensp_to_symbol():
    """STRING protein id -> preferred_name."""
    path = RAW / "9606.protein.info.v12.0.txt.gz"
    out = {}
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        header = fh.readline()
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2:
                continue
            out[parts[0]] = parts[1]
    return out


def build(threshold, ensp2sym, hgnc_map):
    path = RAW / "9606.protein.links.v12.0.txt.gz"
    edges = set()
    unmapped = set()
    n_lines = 0
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        fh.readline()  # header: protein1 protein2 combined_score
        for line in fh:
            p1, p2, score = line.split()
            if int(score) < threshold:
                continue
            n_lines += 1
            s1 = ensp2sym.get(p1)
            s2 = ensp2sym.get(p2)
            if s1 is None or s2 is None:
                continue
            a = hgnc_map.get(s1)
            b = hgnc_map.get(s2)
            if a is None:
                unmapped.add(s1)
                continue
            if b is None:
                unmapped.add(s2)
                continue
            if a == b:
                continue
            edges.add((a, b) if a < b else (b, a))

    nodes = sorted({n for e in edges for n in e})
    idx = {n: i for i, n in enumerate(nodes)}
    rows = np.fromiter((idx[a] for a, _ in edges), dtype=np.int32, count=len(edges))
    cols = np.fromiter((idx[b] for _, b in edges), dtype=np.int32, count=len(edges))
    data = np.ones(len(edges), dtype=np.int8)
    n = len(nodes)
    adj = sparse.coo_matrix((data, (rows, cols)), shape=(n, n)).tocsr()
    adj = adj + adj.T
    adj.data[:] = 1

    ncomp, labels = csgraph.connected_components(adj, directed=False)
    sizes = np.bincount(labels)
    giant = int(np.argmax(sizes))
    keep = np.where(labels == giant)[0]
    lcc_nodes = [nodes[i] for i in keep]
    lcc = adj[keep][:, keep].tocsr()

    stats = {
        "threshold": threshold,
        "edges_above_threshold_raw_directed_lines": n_lines,
        "nodes_total": n,
        "edges_total_undirected": int(len(edges)),
        "n_components": int(ncomp),
        "lcc_nodes": int(lcc.shape[0]),
        "lcc_edges_undirected": int(lcc.nnz // 2),
        "string_symbols_unmapped_by_hgnc": len(unmapped),
    }
    sparse.save_npz(RES / f"graph_{threshold}.npz", lcc)
    (RES / f"graph_{threshold}.json").write_text(
        json.dumps({"stats": stats, "nodes": lcc_nodes}), encoding="utf-8"
    )
    return stats


if __name__ == "__main__":
    RES.mkdir(parents=True, exist_ok=True)
    hgnc_map, approved = load_hgnc()
    print(f"HGNC approved symbols: {len(approved)}; total mappable keys: {len(hgnc_map)}")
    ensp2sym = load_ensp_to_symbol()
    print(f"STRING proteins: {len(ensp2sym)}")
    all_stats = []
    for thr in THRESHOLDS:
        s = build(thr, ensp2sym, hgnc_map)
        all_stats.append(s)
        print(json.dumps(s))
        sys.stdout.flush()
    (RES / "graph_stats.json").write_text(json.dumps(all_stats, indent=2), encoding="utf-8")
    print("DONE")
