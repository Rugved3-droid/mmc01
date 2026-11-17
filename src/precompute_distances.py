"""Precompute and cache the BFS distance matrix for each STRING threshold arm."""
import time
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from proximity import load_graph, distance_matrix

for thr in (700, 400, 900):
    t0 = time.time()
    adj, nodes = load_graph(thr)
    D = distance_matrix(thr, adj)
    print(f"threshold {thr}: n={D.shape[0]} cached in {time.time()-t0:.1f}s "
          f"max_finite={int(D[D < 255].max())}")
    sys.stdout.flush()
print("DONE")
