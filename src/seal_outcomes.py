"""MMC-01 section 8: seal the ground truth.

Hashes sealed/outcomes.json and writes sealed/OUTCOMES_HASH.txt.
This script writes the hash only. It does not expose outcome content.
"""
import hashlib
import datetime
import pathlib

SEALED = pathlib.Path(r"D:\mmc01\sealed")

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

if __name__ == "__main__":
    out = SEALED / "outcomes.json"
    rules = SEALED / "CODING_RULES.md"
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "MMC-01 sealed ground truth",
        f"sealed_utc: {ts}",
        f"outcomes.json sha256: {sha256(out)}",
        f"CODING_RULES.md sha256: {sha256(rules)}",
        "",
        "This file is committed at the same time as outcomes.json.",
        "outcomes.json must not be read by any analysis code until",
        "results/COMMITMENT.txt exists and verifies (protocol 2.2 step 4).",
    ]
    (SEALED / "OUTCOMES_HASH.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
