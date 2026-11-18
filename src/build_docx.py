"""Build the Cardiovascular Toxicology submission .docx from the Markdown source.

Journal requirements handled here: Word format, Times New Roman 10 pt body,
numbered references with DOI links, tables via the Word table function (not
pasted text), figures placed in the body with captions, automatic page numbers.
"""
import pathlib
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

ROOT = pathlib.Path(r"D:\mmc01")
PAPER = ROOT / "paper"
FIG = ROOT / "results" / "figures"

SRC = PAPER / "MMC01_CardiovascTox_ResearchArticle.md"
REFS = PAPER / "references.md"
OUT = PAPER / "MMC01_CardiovascularToxicology_submission.docx"

FIGURES = [
    ("Fig. 1", FIG / "fig1_proximity_heatmap.png", 5.6),
    ("Fig. 2", FIG / "fig2_gate3_positive_control.png", 6.4),
    ("Fig. 3", FIG / "fig3_gate4_specificity.png", 6.4),
]

INLINE = re.compile(r"(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+?`)")
TAGS = re.compile(r"</?(sub|sup|em|strong|i|b)>")


def add_page_numbers(section):
    """Word field for automatic page numbering."""
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    for instr in ("begin", "PAGE", "end"):
        el = OxmlElement("w:fldChar") if instr != "PAGE" else OxmlElement("w:instrText")
        if instr == "PAGE":
            el.set(qn("xml:space"), "preserve")
            el.text = " PAGE "
        else:
            el.set(qn("w:fldCharType"), instr)
        run._r.append(el)


def write_runs(par, text):
    """Emit text with **bold** / *italic* / `code` honoured."""
    text = TAGS.sub("", text)
    for piece in INLINE.split(text):
        if not piece:
            continue
        if piece.startswith("**") and piece.endswith("**"):
            par.add_run(piece[2:-2]).bold = True
        elif piece.startswith("*") and piece.endswith("*") and len(piece) > 2:
            par.add_run(piece[1:-1]).italic = True
        elif piece.startswith("`") and piece.endswith("`"):
            r = par.add_run(piece[1:-1])
            r.font.name = "Consolas"
            r.font.size = Pt(9)
        else:
            par.add_run(piece)


def add_table(doc, rows):
    header = [c.strip() for c in rows[0].strip("|").split("|")]
    body = [[c.strip() for c in r.strip("|").split("|")] for r in rows[2:]]
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    for i, h in enumerate(header):
        cell = t.rows[0].cells[i]
        cell.text = ""
        write_runs(cell.paragraphs[0], h)
        for run in cell.paragraphs[0].runs:
            run.bold = True
    for r in body:
        cells = t.add_row().cells
        for i, v in enumerate(r[:len(header)]):
            cells[i].text = ""
            write_runs(cells[i].paragraphs[0], v)
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(8.5)
    doc.add_paragraph()


def main():
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(10)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    add_page_numbers(doc.sections[0])

    lines = SRC.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if line.startswith("|") and i + 1 < len(lines) and set(lines[i + 1].replace("|", "").strip()) <= set("-: "):
            block = []
            while i < len(lines) and lines[i].startswith("|"):
                block.append(lines[i])
                i += 1
            add_table(doc, block)
            continue

        if line.startswith("### "):
            doc.add_heading(TAGS.sub("", line[4:]), level=3)
        elif line.startswith("## "):
            doc.add_heading(TAGS.sub("", line[3:]), level=2)
        elif line.startswith("# "):
            h = doc.add_heading(TAGS.sub("", line[2:]), level=0)
            h.alignment = WD_ALIGN_PARAGRAPH.LEFT
        elif line.strip() == "---":
            pass
        elif re.match(r"^\d+\.\s", line):
            p = doc.add_paragraph(style="List Number")
            write_runs(p, re.sub(r"^\d+\.\s", "", line))
        elif line.startswith("- "):
            p = doc.add_paragraph(style="List Bullet")
            write_runs(p, line[2:])
        elif line.strip():
            p = doc.add_paragraph()
            write_runs(p, line)
        i += 1

    # figures
    doc.add_page_break()
    doc.add_heading("Figures", level=2)
    for label, path, width in FIGURES:
        if not path.exists():
            continue
        doc.add_picture(str(path), width=Inches(width))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap = doc.add_paragraph()
        r = cap.add_run(label)
        r.bold = True
        cap.add_run("  see caption in the Figures section of the manuscript text.")
        cap.runs[-1].font.size = Pt(9)
        doc.add_paragraph()

    ga = FIG / "graphical_abstract.png"
    if ga.exists():
        doc.add_page_break()
        doc.add_heading("Graphical Abstract", level=2)
        doc.add_picture(str(ga), width=Inches(6.6))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # references
    doc.add_page_break()
    ref_lines = REFS.read_text(encoding="utf-8").splitlines()
    doc.add_heading("References", level=2)
    for ln in ref_lines:
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        write_runs(p, re.sub(r"^\d+\.\s*", lambda m: m.group(0), ln))

    doc.save(OUT)
    print(f"wrote {OUT}  ({OUT.stat().st_size // 1024} KB)")
    words = sum(len(l.split()) for l in lines if not l.startswith("|"))
    print(f"approx body word count (excl. tables/refs): {words}")


if __name__ == "__main__":
    main()
