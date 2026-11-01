"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import mmp_algorithm as A
import mmp_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_growth(series: list[int], first_index: int = 0):
    """Zehnerlogarithmus der Anzahl je Größe (die Zahlen sprengen jede lineare Achse)."""
    xs = [n for n in range(first_index, len(series)) if series[n] >= 1]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=[A.log10_int(series[n]) for n in xs], mode="lines+markers" if len(xs) <= 60 else "lines", name="Anzahl", line=dict(color=C.COLOR_MAIN)))
    fig.update_xaxes(title_text="Größe n")
    fig.update_yaxes(title_text="Anzahl (Zehnerlogarithmus)")
    return _base(fig, 320)


def build_effort(rows: list[dict]):
    """Schritte des Produkts, der Fünfeckszahlen-Rekursion und des Aufzählens gegen n (logarithmische Achse)."""
    fig = go.Figure()
    names = [str(r["n"]) for r in rows]
    fig.add_trace(go.Bar(x=names, y=[r["Schritte Fünfeckszahlen"] for r in rows], name="Fünfeckszahlen", marker_color=C.COLOR_MAIN))
    fig.add_trace(go.Bar(x=names, y=[r["Schritte Produkt"] for r in rows], name="Produkt", marker_color=C.COLOR_LINE))
    fig.add_trace(go.Bar(x=names, y=[float(r["Partitionen (Aufzählen)"]) for r in rows], name="Aufzählen", marker_color=C.COLOR_ALL))
    fig.update_layout(barmode="group")
    fig.update_xaxes(title_text="n")
    fig.update_yaxes(title_text="Schritte (logarithmisch)", type="log")
    return _base(fig, 380)


def build_order(rows: list[dict]):
    """Folgen gegen Multimengen je Betrag (logarithmische Achse)."""
    fig = go.Figure()
    names = [str(r["Betrag"]) for r in rows]
    fig.add_trace(go.Bar(x=names, y=[float(r["Folgen (Reihenfolge zählt)"]) for r in rows], name="Folgen", marker_color=C.COLOR_ALL))
    fig.add_trace(go.Bar(x=names, y=[float(r["Multimengen (Reihenfolge egal)"]) for r in rows], name="Multimengen", marker_color=C.COLOR_MAIN))
    fig.update_layout(barmode="group")
    fig.update_xaxes(title_text="Betrag")
    fig.update_yaxes(title_text="Anzahl (logarithmisch)", type="log")
    return _base(fig, 340)


def build_tree_ratio(ratios: dict):
    """Wachstumsverhältnis a(n+1)/a(n) der Wurzelbäume ohne und mit Reihenfolge."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ratios["n"], y=ratios["mit"], mode="lines", name="mit Reihenfolge", line=dict(color=C.COLOR_ALL)))
    fig.add_trace(go.Scatter(x=ratios["n"], y=ratios["ohne"], mode="lines", name="ohne Reihenfolge", line=dict(color=C.COLOR_MAIN)))
    fig.update_xaxes(title_text="Knoten n")
    fig.update_yaxes(title_text="a(n+1) / a(n)")
    return _base(fig, 340)


def build_ferrers(parts: tuple, title: str):
    """Ferrers-Diagramm: eine Zeile pro Teil, ein Quadrat pro Einheit (Zeilen von oben nach unten)."""
    fig = go.Figure()
    for row, length in enumerate(parts):
        for col in range(length):
            fig.add_shape(type="rect", x0=col, x1=col + 1, y0=-row, y1=-row - 1, line=dict(color="white", width=1), fillcolor=C.COLOR_MAIN)
    width = max(parts) if parts else 1
    fig.add_trace(go.Scatter(x=[0, width], y=[0, -len(parts)], mode="markers", marker=dict(opacity=0), showlegend=False, hoverinfo="skip"))
    fig.update_xaxes(visible=False, range=[-0.2, width + 0.2])
    fig.update_yaxes(visible=False, range=[-len(parts) - 0.2, 0.2])
    fig.update_layout(title=dict(text=title, font=dict(size=14)))
    return _base(fig, min(520, 80 + 26 * max(len(parts), 3)))
