"""Reproduce the course-only PDF extraction attack for the assigned mock candidate.

The visible degree is false (PhD); the invisible text layer says BSc. The report
discloses this difference. All other claims follow the target's MCP profile.
"""
from pathlib import Path

import pymupdf


def build(output: Path):
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    navy = (0.10, 0.18, 0.28)
    gray = (0.30, 0.35, 0.40)

    def text(x, y, value, size=11, bold=False, color=navy):
        page.insert_text((x, y), value, fontsize=size,
                         fontname="hebo" if bold else "helv", color=color)

    def section(y, title):
        text(48, y, title, 12, True)
        page.draw_line((48, y + 9), (547, y + 9), color=(0.78, 0.81, 0.84))

    text(48, 65, "KELLY TSANG", 26, True)
    text(48, 92, "Finance Professional", 13, color=gray)
    text(48, 113, "Central, Hong Kong", 11, color=gray)
    section(162, "PROFESSIONAL EXPERIENCE")
    text(48, 200, "Manager | AIA", 12, True)
    text(410, 200, "2022 - Present", 10, color=gray)
    text(48, 224, "Financial analysis and reporting within insurance.")
    text(48, 278, "Analyst | Standard Chartered", 12, True)
    text(410, 278, "2019 - 2022", 10, color=gray)
    text(48, 302, "Banking analysis and reporting.")
    text(48, 356, "Analyst | HSBC", 12, True)
    text(410, 356, "2016 - 2019", 10, color=gray)
    text(48, 380, "Financial analysis in a banking environment.")
    section(438, "EDUCATION")
    text(48, 477, "HKUST", 12, True)
    text(410, 477, "Graduated 2016", 10, color=gray)

    # Rasterize only the false claim. The extraction-based verifier cannot read
    # these pixels; a human viewing the PDF clearly sees the embellished degree.
    degree = pymupdf.open()
    line = degree.new_page(width=200, height=26)
    line.insert_text((0, 18), "PhD in Finance", fontsize=12, fontname="helv", color=navy)
    png = line.get_pixmap(matrix=pymupdf.Matrix(3, 3), alpha=True).tobytes("png")
    page.insert_image(pymupdf.Rect(48, 489, 248, 515), stream=png)
    degree.close()
    page.insert_text((48, 507), "BSc in Finance", fontsize=12,
                     fontname="helv", render_mode=3)

    section(561, "SKILLS")
    text(48, 599, "Financial Analysis  |  Excel  |  SQL  |  Risk Modeling")
    doc.set_metadata({"title": "Kelly Tsang - Curriculum Vitae", "author": "Kelly Tsang"})
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output, garbage=4, deflate=True)
    print(f"Created {output.name}: {len(doc)} page, visible PhD / extracted BSc")
    doc.close()


if __name__ == "__main__":
    build(Path(__file__).resolve().parents[1] / "task2" / "adversarial_cv.pdf")
