"""PDF-Export der aktuellen Aufgabe mit den Rechenwegen und den ersten Werten (fpdf2). Kernschriften sind latin-1: Umlaute gehen, Sonderzeichen werden ersetzt."""

from __future__ import annotations

from fpdf import FPDF

from mmp_evaluation import Analysis, first_values, m_text, verdict_answers, way_rows

_REPLACE = {"→": "->", "–": "-", "—": "-", "−": "-", "≤": "<=", "≥": ">=", "·": "*", "€": "EUR", "„": '"', "“": '"', "ⁿ": "^n", "²": "^2", "ₖ": "k", "∞": "unendlich",
            "⁻": "-", "⁰": "0", "¹": "1", "³": "3", "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9"}


def _s(text) -> str:
    out = str(text)
    for old, new in _REPLACE.items():
        out = out.replace(old, new)
    return out.encode("latin-1", "replace").decode("latin-1")


def build_pdf(a: Analysis) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _s("Multimengen und Partitionen"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    s = a.settings
    bausteine = f", Tabelle {s.table}" if s.family == "Eigene Bausteine" else ""
    pdf.multi_cell(0, 5, _s(f"Familie: {s.family}, Zielgroesse {a.n_eff}, {m_text(a.m)}{bausteine}. Alles gerechnet, keine Messdaten."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.multi_cell(0, 5, _s(verdict_answers(a)[1]), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 9)
    widths = (70, 45, 35, 40)
    heads = ("Weg", "Anzahl bei N", "Schritte", "Ergebnis")
    for h, w in zip(heads, widths):
        pdf.cell(w, 6, _s(h), border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    for row in way_rows(a):
        for key, w in zip(heads, widths):
            pdf.cell(w, 5.5, _s(row[key])[:40], border=1)
        pdf.ln()
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(30, 6, "Groesse", border=1)
    pdf.cell(80, 6, "Anzahl", border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    for row in first_values(a, 20):
        pdf.cell(30, 5.5, _s(row["Größe"]), border=1)
        pdf.cell(80, 5.5, _s(row["Anzahl"])[:50], border=1)
        pdf.ln()
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _s("Quelle: multimengen-partitionen-demo, Sebastian Hanisch."), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
