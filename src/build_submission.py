"""Assemble the complete Cardiovascular Toxicology submission folder.

Produces paper/submission/ containing everything that gets uploaded:
  Manuscript.docx, CoverLetter.docx, GraphicalAbstract.png, Fig1/2/3.png
Figure files are named per the journal's convention ("Fig" + number).
"""
import pathlib
import re
import shutil
import subprocess
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt

ROOT = pathlib.Path(r"D:\mmc01")
PAPER = ROOT / "paper"
FIG = ROOT / "results" / "figures"
OUT = PAPER / "submission"

INLINE = re.compile(r"(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+?`)")
TAGS = re.compile(r"</?(sub|sup|em|strong|i|b)>")


def write_runs(par, text):
    text = TAGS.sub("", text)
    for piece in INLINE.split(text):
        if not piece:
            continue
        if piece.startswith("**") and piece.endswith("**"):
            par.add_run(piece[2:-2]).bold = True
        elif piece.startswith("*") and piece.endswith("*") and len(piece) > 2:
            par.add_run(piece[1:-1]).italic = True
        elif piece.startswith("`") and piece.endswith("`"):
            par.add_run(piece[1:-1])
        else:
            par.add_run(piece)


def md_to_docx(src, dest, title_level0=True):
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(11)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    for line in src.read_text(encoding="utf-8").splitlines():
        line = line.rstrip()
        if line.startswith("# "):
            if title_level0:
                doc.add_heading(TAGS.sub("", line[2:]), level=0)
        elif line.startswith("## "):
            doc.add_heading(TAGS.sub("", line[3:]), level=2)
        elif line.strip() == "---":
            pass
        elif re.match(r"^\d+\.\s", line):
            p = doc.add_paragraph(style="List Number")
            write_runs(p, re.sub(r"^\d+\.\s", "", line))
        elif line.strip():
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(8)
            write_runs(p, line)
        else:
            doc.add_paragraph()
    doc.save(dest)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    # manuscript (built by build_docx.py, which handles tables and figures)
    subprocess.run([sys.executable, "-I", str(ROOT / "src" / "build_docx.py")],
                   check=True, capture_output=True)
    shutil.copy2(PAPER / "MMC01_CardiovascularToxicology_submission.docx",
                 OUT / "Manuscript.docx")

    md_to_docx(PAPER / "cover_letter.md", OUT / "CoverLetter.docx")

    shutil.copy2(FIG / "graphical_abstract.png", OUT / "GraphicalAbstract.png")
    for n, name in enumerate(("fig1_proximity_heatmap.png",
                              "fig2_gate3_positive_control.png",
                              "fig3_gate4_specificity.png"), start=1):
        shutil.copy2(FIG / name, OUT / f"Fig{n}.png")

    print(f"submission folder: {OUT}\n")
    total = 0
    for f in sorted(OUT.iterdir()):
        kb = f.stat().st_size // 1024
        total += kb
        print(f"  {f.name:<28} {kb:>6} KB")
    print(f"  {'TOTAL':<28} {total:>6} KB")


if __name__ == "__main__":
    main()
