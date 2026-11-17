"""MMC-01 section 4: validate and freeze the mechanism modules.

Takes the blinded builder's config/modules_draft.yaml and enforces, in code:
  - the two-source rule (a gene enters only if >=2 of that module's seed sources name it)
  - HGNC normalisation to one namespace, with mapping loss reported per module
  - no gene in more than one module
  - LCC filtering at each threshold
Writes config/modules.yaml (frozen, with a hash) and results/module_stats.json.
"""
import csv
import hashlib
import json
import pathlib
import sys

import yaml

ROOT = pathlib.Path(r"D:\mmc01")
RAW = ROOT / "data" / "raw"
RES = ROOT / "results"
CFG = ROOT / "config"


def load_hgnc_map():
    mapping, approved = {}, set()
    path = RAW / "hgnc_complete_set.txt"
    with open(path, "r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            if row.get("status") != "Approved":
                continue
            s = (row.get("symbol") or "").strip()
            if s:
                approved.add(s)
                mapping[s] = s
    with open(path, "r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            if row.get("status") != "Approved":
                continue
            s = (row.get("symbol") or "").strip()
            for field in ("alias_symbol", "prev_symbol"):
                for alt in (row.get(field) or "").split("|"):
                    alt = alt.strip()
                    if alt and alt not in approved and alt not in mapping:
                        mapping[alt] = s
    return mapping


def load_lcc(threshold):
    return set(json.loads((RES / f"graph_{threshold}.json").read_text(encoding="utf-8"))["nodes"])


def main():
    draft = yaml.safe_load((CFG / "modules_draft.yaml").read_text(encoding="utf-8"))
    hgnc = load_hgnc_map()
    lcc = {t: load_lcc(t) for t in (400, 700, 900)}

    staged = {}
    for mid, m in draft["modules"].items():
        declared = m.get("genes") or []
        n_declared = len(declared)

        # two-source rule, enforced here rather than trusted
        two_src = [g for g in declared if len(set(g.get("sources") or [])) >= 2]
        dropped_one_source = [g["symbol"] for g in declared
                              if len(set(g.get("sources") or [])) < 2]

        # HGNC normalisation
        mapped, unmapped = {}, []
        for g in two_src:
            sym = hgnc.get(g["symbol"].strip())
            if sym is None:
                unmapped.append(g["symbol"])
            else:
                mapped.setdefault(sym, set()).update(g.get("sources") or [])

        staged[mid] = {
            "mechanism": m.get("mechanism", ""),
            "seed_sources": m.get("seed_sources", []),
            "n_declared": n_declared,
            "dropped_one_source": dropped_one_source,
            "n_two_source": len(two_src),
            "unmapped_by_hgnc": unmapped,
            "genes": mapped,          # approved symbol -> set(source ids)
        }

    # no gene in more than one module: resolve by majority of seed sources
    owners = {}
    for mid, m in staged.items():
        for g in m["genes"]:
            owners.setdefault(g, []).append(mid)
    overlaps = []
    for g, mids in owners.items():
        if len(mids) < 2:
            continue
        counts = {mid: len(staged[mid]["genes"][g]) for mid in mids}
        best = max(counts.values())
        winners = [mid for mid, c in counts.items() if c == best]
        if len(winners) == 1:
            keep = winners[0]
            for mid in mids:
                if mid != keep:
                    del staged[mid]["genes"][g]
            overlaps.append({"symbol": g, "claimed_by": mids, "assigned_to": keep,
                             "source_counts": counts})
        else:
            for mid in mids:
                del staged[mid]["genes"][g]
            overlaps.append({"symbol": g, "claimed_by": mids, "assigned_to": None,
                             "source_counts": counts, "reason": "tied, dropped from both"})

    out_modules, stats = {}, {}
    for mid, m in staged.items():
        genes = sorted(m["genes"])
        n_mapped = len(genes)
        in_lcc = {t: sorted(g for g in genes if g in lcc[t]) for t in lcc}
        loss = 1.0 - (n_mapped / m["n_two_source"]) if m["n_two_source"] else 1.0
        out_modules[mid] = {
            "mechanism": m["mechanism"],
            "seed_sources": m["seed_sources"],
            "genes": {g: sorted(m["genes"][g]) for g in genes},
            "genes_in_lcc_700": in_lcc[700],
        }
        stats[mid] = {
            "mechanism": m["mechanism"],
            "n_seed_sources": len(m["seed_sources"]),
            "n_declared": m["n_declared"],
            "n_dropped_one_source": len(m["dropped_one_source"]),
            "dropped_one_source": m["dropped_one_source"],
            "n_two_source": m["n_two_source"],
            "n_unmapped_by_hgnc": len(m["unmapped_by_hgnc"]),
            "unmapped_by_hgnc": m["unmapped_by_hgnc"],
            "n_mapped": n_mapped,
            "mapping_loss": round(loss, 4),
            "n_in_lcc": {str(t): len(in_lcc[t]) for t in in_lcc},
            "genes_in_lcc_700": in_lcc[700],
        }

    frozen = {"modules": out_modules, "overlaps_resolved": overlaps}
    text = yaml.safe_dump(frozen, sort_keys=True, default_flow_style=False)
    (CFG / "modules.yaml").write_text(text, encoding="utf-8")
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    (CFG / "MODULES_HASH.txt").write_text(
        f"config/modules.yaml sha256: {h}\n", encoding="utf-8")

    payload = {"modules": stats, "overlaps_resolved": overlaps, "modules_sha256": h}
    (RES / "module_stats.json").write_text(json.dumps(payload, indent=1), encoding="utf-8")

    print(f"{'module':<6} {'srcs':>5} {'decl':>5} {'2src':>5} {'mapped':>7} "
          f"{'LCC700':>7} {'loss':>7}")
    for mid, s in stats.items():
        print(f"{mid:<6} {s['n_seed_sources']:>5} {s['n_declared']:>5} "
              f"{s['n_two_source']:>5} {s['n_mapped']:>7} "
              f"{s['n_in_lcc']['700']:>7} {s['mapping_loss']:>7.3f}")
    print(f"\noverlaps resolved: {len(overlaps)}")
    print(f"modules.yaml sha256: {h}")
    for mid, s in stats.items():
        if s["n_in_lcc"]["700"] < 15:
            print(f"WARNING {mid}: only {s['n_in_lcc']['700']} genes in LCC700 "
                  f"(section 4 minimum is 15)")
        if s["mapping_loss"] > 0.10:
            print(f"WARNING {mid}: mapping loss {s['mapping_loss']:.1%} exceeds 10%")


if __name__ == "__main__":
    sys.exit(main())
