"""MMC-01 section 5: assemble cardioprotectant target sets from DGIdb.

Matching is by an explicit allow-list of spellings per drug (DGIdb stores salt
forms, metabolites and fixed-dose combinations under many names). Fuzzy matching
is deliberately avoided: every accepted spelling is written down here and is
auditable. Combination products containing an unrelated second drug are excluded,
except sacubitril/valsartan, which section 5 declares a single combination entry.

Writes results/targets.json with, per drug: mapped target symbols, the DGIdb
source db and interaction type behind every gene (protocol 2.5 provenance), and
direction_coverage (protocol section 5 rule 2).
"""
import csv
import json
import pathlib
from collections import defaultdict

ROOT = pathlib.Path(r"D:\mmc01")
RAW = ROOT / "data" / "raw"
RES = ROOT / "results"

DIRECTIONAL = {"inhibitor", "antagonist", "agonist", "blocker", "activator",
               "partial agonist", "inverse agonist", "suppressor", "inducer",
               "channel blocker", "antibody", "positive allosteric modulator",
               "negative allosteric modulator"}

# Explicit spelling allow-lists (uppercase). Matched against drug_name and
# drug_claim_name. Metabolites that are the active moiety are included and noted.
PROTECTANTS = {
    "dexrazoxane":          ["DEXRAZOXANE"],
    "enalapril":            ["ENALAPRIL", "ENALAPRIL MALEATE", "ENALAPRILAT",
                             "ENALAPRILAT ANHYDROUS"],
    "lisinopril":           ["LISINOPRIL", "LISINOPRIL HYDRATE", "LISINOPRIL ANHYDROUS"],
    "candesartan":          ["CANDESARTAN", "CANDESARTAN CILEXETIL"],
    "valsartan":            ["VALSARTAN"],
    "carvedilol":           ["CARVEDILOL"],
    "metoprolol":           ["METOPROLOL", "METOPROLOL TARTRATE",
                             "METOPROLOL SUCCINATE", "METOPROLOL FUMARATE"],
    "nebivolol":            ["NEBIVOLOL", "NEBIVOLOL HYDROCHLORIDE"],
    "bisoprolol":           ["BISOPROLOL", "BISOPROLOL FUMARATE"],
    "spironolactone":       ["SPIRONOLACTONE"],
    "eplerenone":           ["EPLERENONE"],
    "atorvastatin":         ["ATORVASTATIN", "ATORVASTATIN CALCIUM",
                             "ATORVASTATIN CALCIUM TRIHYDRATE"],
    "rosuvastatin":         ["ROSUVASTATIN", "ROSUVASTATIN CALCIUM"],
    "sacubitril/valsartan": ["SACUBITRIL", "SACUBITRILAT", "SACUBITRIL/VALSARTAN",
                             "VALSARTAN"],
    "dapagliflozin":        ["DAPAGLIFLOZIN", "DAPAGLIFLOZIN PROPANEDIOL",
                             "DAPAGLIFLOZIN PROPYLENE GLYCOL"],
    "empagliflozin":        ["EMPAGLIFLOZIN"],
}

# Section 5 negative controls. The fifth agent is declared here, before any
# proximity is computed: ranitidine, with finasteride as the stated fallback if
# ranitidine has no mapped target in the LCC.
NEGATIVE_CONTROLS = {
    "loratadine":    ["LORATADINE"],
    "omeprazole":    ["OMEPRAZOLE", "OMEPRAZOLE SODIUM", "OMEPRAZOLE MAGNESIUM"],
    "levothyroxine": ["LEVOTHYROXINE", "LEVOTHYROXINE SODIUM"],
    "montelukast":   ["MONTELUKAST", "MONTELUKAST SODIUM"],
    "ranitidine":    ["RANITIDINE", "RANITIDINE HYDROCHLORIDE"],
    "finasteride":   ["FINASTERIDE"],   # declared fallback only
}

EXCLUDED_NOTES = {
    "atorvastatin": "excluded: 2-hydroxyatorvastatin (metabolite), "
                    "'Atorvastatin lactole derivative 1', "
                    "'amlodipine / atorvastatin / perindopril arginine' (combination)",
    "lisinopril": "excluded: LISINOPRIL-TRYPTOPHAN (distinct entity)",
    "bisoprolol": "excluded: 'bisoprolol fumarate / perindopril arginine' (combination)",
    "dapagliflozin": "excluded: 'Dapagliflozin Propanediol; Saxagliptin Hydrochloride' (combination)",
    "enalapril": "enalaprilat included: active moiety of enalapril",
    "sacubitril/valsartan": "union of both components per section 5 rule 3; flagged combination",
}


def load_lcc(threshold):
    data = json.loads((RES / f"graph_{threshold}.json").read_text(encoding="utf-8"))
    return set(data["nodes"])


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


def collect(spelling_map, hgnc):
    """drug -> gene -> list of (source_db, interaction_type)"""
    lookup = {}
    for drug, spellings in spelling_map.items():
        for sp in spellings:
            lookup.setdefault(sp.upper(), []).append(drug)

    found = defaultdict(lambda: defaultdict(list))
    unmapped = defaultdict(set)
    with open(RAW / "dgidb_interactions.tsv", "r", encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            names = {(r.get("drug_name") or "").strip().upper(),
                     (r.get("drug_claim_name") or "").strip().upper()}
            drugs = set()
            for n in names:
                drugs.update(lookup.get(n, []))
            if not drugs:
                continue
            raw_gene = (r.get("gene_name") or "").strip()
            if not raw_gene:
                continue
            sym = hgnc.get(raw_gene)
            itype = (r.get("interaction_type") or "NULL").strip()
            src = (r.get("interaction_source_db_name") or "?").strip()
            for d in drugs:
                if sym is None:
                    unmapped[d].add(raw_gene)
                else:
                    found[d][sym].append([src, itype])
    return found, unmapped


def summarise(found, unmapped, lcc, spelling_map):
    out = {}
    for drug in spelling_map:
        genes = found.get(drug, {})
        all_syms = sorted(genes)
        in_lcc = sorted(g for g in all_syms if g in lcc)
        typed = [g for g in in_lcc
                 if any(t.lower() in DIRECTIONAL for _, t in genes[g])]
        out[drug] = {
            "accepted_spellings": spelling_map[drug],
            "n_targets_mapped": len(all_syms),
            "n_targets_in_lcc": len(in_lcc),
            "targets_in_lcc": in_lcc,
            "dropped_not_in_lcc": sorted(set(all_syms) - set(in_lcc)),
            "unmapped_by_hgnc": sorted(unmapped.get(drug, [])),
            "direction_coverage": round(len(typed) / len(in_lcc), 3) if in_lcc else 0.0,
            "provenance": {g: genes[g] for g in in_lcc},
            "note": EXCLUDED_NOTES.get(drug, ""),
        }
    return out


if __name__ == "__main__":
    hgnc = load_hgnc_map()
    lcc700 = load_lcc(700)

    prot_found, prot_unmapped = collect(PROTECTANTS, hgnc)
    neg_found, neg_unmapped = collect(NEGATIVE_CONTROLS, hgnc)

    protectants = summarise(prot_found, prot_unmapped, lcc700, PROTECTANTS)
    negatives = summarise(neg_found, neg_unmapped, lcc700, NEGATIVE_CONTROLS)

    # resolve the declared fifth negative control
    fifth = "ranitidine" if negatives["ranitidine"]["n_targets_in_lcc"] > 0 else "finasteride"
    used_negatives = ["loratadine", "omeprazole", "levothyroxine", "montelukast", fifth]

    payload = {
        "threshold_for_lcc_filter": 700,
        "protectants": protectants,
        "negative_controls": negatives,
        "negative_controls_used": used_negatives,
        "fifth_control_rule": "ranitidine declared first; finasteride is the stated "
                              "fallback if ranitidine has no target in the LCC",
    }
    (RES / "targets.json").write_text(json.dumps(payload, indent=1), encoding="utf-8")

    print(f"{'drug':<22} {'mapped':>7} {'in_LCC':>7} {'dir_cov':>8}  note")
    for d, v in protectants.items():
        print(f"{d:<22} {v['n_targets_mapped']:>7} {v['n_targets_in_lcc']:>7} "
              f"{v['direction_coverage']:>8.2f}")
    print()
    for d in used_negatives:
        v = negatives[d]
        print(f"[neg] {d:<16} {v['n_targets_mapped']:>7} {v['n_targets_in_lcc']:>7} "
              f"{v['direction_coverage']:>8.2f}")

    mapped_ok = sum(1 for v in protectants.values() if v["n_targets_in_lcc"] > 0)
    import statistics
    covs = [v["direction_coverage"] for v in protectants.values()
            if v["n_targets_in_lcc"] > 0]
    median_cov = statistics.median(covs) if covs else 0.0
    print(f"\nGATE 1 INPUT: {mapped_ok}/16 protectants with >=1 target in LCC700; "
          f"median direction_coverage = {median_cov:.3f}")
    print(f"fifth negative control used: {fifth}")
