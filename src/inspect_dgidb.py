"""Count DGIdb target rows for the section 5 candidate drugs and the negative controls."""
import csv
import pathlib
from collections import defaultdict

RAW = pathlib.Path(r"D:\mmc01\data\raw")

WANTED = [
    "DEXRAZOXANE", "ENALAPRIL", "ENALAPRILAT", "LISINOPRIL", "CANDESARTAN",
    "CANDESARTAN CILEXETIL", "VALSARTAN", "CARVEDILOL", "METOPROLOL",
    "NEBIVOLOL", "BISOPROLOL", "SPIRONOLACTONE", "EPLERENONE",
    "ATORVASTATIN", "ROSUVASTATIN", "SACUBITRIL", "DAPAGLIFLOZIN",
    "EMPAGLIFLOZIN",
    # negative control candidates
    "LORATADINE", "OMEPRAZOLE", "LEVOTHYROXINE", "MONTELUKAST",
    "FINASTERIDE", "ACYCLOVIR", "CETIRIZINE", "LATANOPROST", "RANITIDINE",
]

rows = defaultdict(list)
with open(RAW / "dgidb_interactions.tsv", "r", encoding="utf-8", newline="") as fh:
    rdr = csv.DictReader(fh, delimiter="\t")
    for r in rdr:
        name = (r.get("drug_name") or "").strip().upper()
        if name in WANTED:
            g = (r.get("gene_name") or "").strip()
            if g:
                rows[name].append((g, (r.get("interaction_type") or "NULL").strip()))

print(f"{'drug':<26} {'rows':>5} {'genes':>6} {'typed':>6} {'dir_cov':>8}")
DIRECTIONAL = {"inhibitor", "antagonist", "agonist", "blocker", "activator",
               "partial agonist", "inverse agonist", "positive allosteric modulator",
               "negative allosteric modulator", "channel blocker", "suppressor",
               "inducer", "inhibitory allosteric modulator", "antibody",
               "binder", "modulator"}
for d in WANTED:
    recs = rows.get(d, [])
    genes = {g for g, _ in recs}
    typed = {g for g, t in recs if t.lower() in DIRECTIONAL}
    cov = (len(typed) / len(genes)) if genes else 0.0
    print(f"{d:<26} {len(recs):>5} {len(genes):>6} {len(typed):>6} {cov:>8.2f}")

print("\nDistinct interaction_type values seen:")
seen = sorted({t for recs in rows.values() for _, t in recs})
print(seen)
