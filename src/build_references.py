"""Build the numbered reference list for the manuscript.

Method references are hard-coded from Europe PMC records verified in this
session. Module seed sources are read from config/modules_draft.yaml, whose
35 entries were independently re-verified by PMID against Europe PMC.
Generating the list mechanically avoids transcription error.
"""
import json
import pathlib

import yaml

ROOT = pathlib.Path(r"D:\mmc01")
CFG = ROOT / "config"
OUT = ROOT / "paper"

METHODS_REFS = [
    ("guney2016", "Guney, E., Menche, J., Vidal, M., & Barabasi, A. L. (2016). "
     "Network-based in silico drug efficacy screening. *Nature Communications*, 7, 10331. "
     "https://doi.org/10.1038/ncomms10331"),
    ("menche2015", "Menche, J., Sharma, A., Kitsak, M., Ghiassian, S. D., Vidal, M., "
     "Loscalzo, J., & Barabasi, A. L. (2015). Uncovering disease-disease relationships "
     "through the incomplete interactome. *Science*, 347(6224), 1257601. "
     "https://doi.org/10.1126/science.1257601"),
    ("string2023", "Szklarczyk, D., Kirsch, R., Koutrouli, M., Nastou, K., Mehryary, F., "
     "Hachilif, R., Gable, A. L., Fang, T., Doncheva, N. T., Pyysalo, S., Bork, P., "
     "Jensen, L. J., & von Mering, C. (2023). The STRING database in 2023: protein-protein "
     "association networks and functional enrichment analyses for any sequenced genome of "
     "interest. *Nucleic Acids Research*, 51(D1), D638-D646. "
     "https://doi.org/10.1093/nar/gkac1000"),
    ("dgidb2024", "Cannon, M., Stevenson, J., Stahl, K., Basu, R., Coffman, A., Kiwala, S., "
     "McMichael, J. F., Kuzma, K., Morrissey, D., Cotto, K., Mardis, E. R., Griffith, O. L., "
     "Griffith, M., & Wagner, A. H. (2024). DGIdb 5.0: rebuilding the drug-gene interaction "
     "database for precision medicine and drug discovery platforms. *Nucleic Acids Research*, "
     "52(D1), D1227-D1235. https://doi.org/10.1093/nar/gkad1040"),
    ("hgnc2026", "Seal, R. L., Braschi, B., Gray, K., McClay, J., Tweedie, S., & Bruford, E. A. "
     "(2026). Genenames.org: the HGNC and PGNC resources in 2026. *Nucleic Acids Research*, "
     "54(D1), D1098-D1107. https://doi.org/10.1093/nar/gkaf1229"),
    ("zhang2012", "Zhang, S., Liu, X., Bawa-Khalfe, T., Lu, L. S., Lyu, Y. L., Liu, L. F., & "
     "Yeh, E. T. (2012). Identification of the molecular basis of doxorubicin-induced "
     "cardiotoxicity. *Nature Medicine*, 18(11), 1639-1642. https://doi.org/10.1038/nm.2919"),
    ("debaat2022", "de Baat, E. C., Mulder, R. L., Armenian, S., Feijen, E. A., Grotenhuis, H., "
     "Hudson, M. M., Mavinkurve-Groothuis, A. M., Kremer, L. C., & van Dalen, E. C. (2022). "
     "Dexrazoxane for preventing or reducing cardiotoxicity in adults and children with cancer "
     "receiving anthracyclines. *Cochrane Database of Systematic Reviews*, 9, CD014638. "
     "https://doi.org/10.1002/14651858.CD014638.pub2"),
]


def main():
    draft = yaml.safe_load((CFG / "modules_draft.yaml").read_text(encoding="utf-8"))
    lines, keymap = [], {}
    n = 0
    for key, txt in METHODS_REFS:
        n += 1
        keymap[key] = n
        lines.append(f"{n}. {txt}")

    ranges = {}
    for mid in ("M1", "M2", "M3", "M4"):
        srcs = draft["modules"][mid].get("seed_sources", [])
        start = n + 1
        for s in srcs:
            n += 1
            cit = (s.get("citation") or "").strip().rstrip(".")
            doi = (s.get("doi") or "").strip()
            pmid = (s.get("pmid") or "").strip()
            tail = f" https://doi.org/{doi}" if doi else (f" PMID: {pmid}" if pmid else "")
            lines.append(f"{n}. {cit}.{tail}")
        ranges[mid] = (start, n)

    body = "\n".join(lines)
    (OUT / "references.md").write_text(
        "# References\n\n" + body + "\n", encoding="utf-8")
    (OUT / "ref_index.json").write_text(
        json.dumps({"methods": keymap, "module_ranges": ranges, "total": n}, indent=1),
        encoding="utf-8")

    print(f"total references: {n}")
    for k, v in keymap.items():
        print(f"  [{v}] {k}")
    for mid, (a, b) in ranges.items():
        print(f"  {mid} seed sources: [{a}-{b}]  ({b - a + 1} refs)")


if __name__ == "__main__":
    main()
