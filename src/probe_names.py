"""Find how DGIdb spells our drugs: substring match across all name fields."""
import csv
import pathlib
from collections import defaultdict

RAW = pathlib.Path(r"D:\mmc01\data\raw")
NEEDLES = ["ATORVASTATIN", "ENALAPRIL", "LISINOPRIL", "CANDESARTAN", "NEBIVOLOL",
           "DAPAGLIFLOZIN", "MONTELUKAST", "CETIRIZINE", "RANITIDINE",
           "SACUBITRIL", "VALSARTAN", "DEXRAZOXANE", "METOPROLOL", "BISOPROLOL"]

hits = defaultdict(lambda: defaultdict(set))  # needle -> field -> spellings
with open(RAW / "dgidb_interactions.tsv", "r", encoding="utf-8", newline="") as fh:
    rdr = csv.DictReader(fh, delimiter="\t")
    for r in rdr:
        for field in ("drug_name", "drug_claim_name", "drug_concept_id"):
            v = (r.get(field) or "").strip()
            up = v.upper()
            for nd in NEEDLES:
                if nd in up:
                    hits[nd][field].add(v)

for nd in NEEDLES:
    print(f"\n=== {nd} ===")
    if not hits[nd]:
        print("  NO MATCH ANYWHERE")
        continue
    for field, vals in hits[nd].items():
        shown = sorted(vals)[:12]
        print(f"  {field} ({len(vals)} distinct): {shown}")
