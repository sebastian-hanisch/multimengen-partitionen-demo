"""Multimengen und Partitionen – wenn die Reihenfolge egal ist - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 5 der Reihe „Abzählen und erzeugende Funktionen“: Die Multimenge als vierter Baustein der symbolischen Methode. Aus „wie viele Bausteine der Größe k“ wird die Zahl der Multimengen
(Euler-Transformation): Partitionen, Münzwechsel, 0/1-Rucksack, ebene Partitionen und Wurzelbäume ohne Reihenfolge, auf mehreren Rechenwegen gegeneinander geprüft.
Aufbau und Regeln: DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import mmp_constants as C
from mmp_algorithm import conjugate, digit_count
from mmp_evaluation import (
    Settings,
    analyse,
    big_text,
    composition_rows,
    de,
    effort_rows,
    first_values,
    order_rows,
    playground,
    rational_rows,
    time_experiment,
    times_text,
    tree_check,
    tree_ratios,
    tree_rows,
    verdict_answers,
    verdict_effort,
    verdict_order,
    verdict_playground,
    verdict_rational,
    verdict_time,
    verdict_trees,
    way_rows,
)
from mmp_layout import dunkles_design, kopf_css
from mmp_pdf_export import build_pdf
from mmp_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_table,
    sidebar_presets,
    sync_query_params,
)
from mmp_visualization import build_effort, build_ferrers, build_growth, build_order, build_tree_ratio

st.set_page_config(page_title="Multimengen und Partitionen – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _effort():
    return effort_rows()


@st.cache_data(show_spinner=False)
def _order():
    return order_rows(), composition_rows()


@st.cache_data(show_spinner=False)
def _trees():
    return tree_rows(), tree_ratios(), tree_check()


@st.cache_data(show_spinner=False)
def _rational():
    return rational_rows()


@st.cache_data(show_spinner=False)
def _play(n, k):
    return playground(n, k)


def verdict(pair):
    kind, text = pair
    getattr(st, kind)(text)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in mmp_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧮 Multimengen und Partitionen – wenn die Reihenfolge egal ist")
st.markdown(
    """
**Zählen ohne Reihenfolge.** Eine Folge unterscheidet „erst 1, dann 2“ von „erst 2, dann 1“; wo die Reihenfolge egal ist, spricht man von einer **Multimenge**: Bausteine dürfen mehrfach vorkommen, die Anordnung zählt nicht.
Gibt es von jeder Größe $k$ genau $a_k$ verschiedene Bausteine, ist die Zahl der Multimengen der Gesamtgröße $n$ der Koeffizient von $z^n$ im **Produkt** der Faktoren $1/(1-z^k)^{a_k}$ (die **Euler-Transformation**).
Mit „höchstens $m$ gleiche Bausteine“ wird daraus eine Menge ($m=1$). Aus einer Tabelle $a_k$ werden so Zahlpartitionen, Münzwechsel, Rucksack-Teilmengen, ebene Partitionen und Wurzelbäume ohne Reihenfolge.
Die Zahlen kommen auf mehreren Rechenwegen heraus; **der Aufwand ist sehr verschieden**.

Weiter unten: **fünf Experimente** (**🔬**), eine **🎲 Spielwiese**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert die Euler-Transformation", expanded=True):
    st.markdown(
        """
1. **Bausteine festlegen:** Für jede Größe $k$ steht fest, wie viele verschiedene Bausteine es gibt ($a_k$). Bei den Partitionen ist $a_k = 1$ für alle $k$, bei Münzen $a_k = 1$ nur für die Münzwerte, bei den ebenen Partitionen $a_k = k$.
2. **Faktor je Baustein:** Ein Baustein, der beliebig oft vorkommen darf, trägt den Faktor $1 + z^k + z^{2k} + \\dots = 1/(1-z^k)$; höchstens $m$-mal gibt $1 + z^k + \\dots + z^{mk}$.
3. **Multiplizieren:** Das Produkt aller Faktoren hat als Koeffizient von $z^n$ die Zahl der Multimengen der Größe $n$. Die Rechnung ist ein Durchlauf pro Baustein über alle Größen bis $N$.
4. **Zweiter Weg:** Die logarithmische Ableitung des Produkts gibt $n \\cdot c_n = \\sum_k b_k c_{n-k}$ mit $b_k = \\sum_{d \\mid k} d\\, a_d$: dieselben Zahlen, ohne Produkt. Für Partitionen gibt es einen dritten, kürzeren Weg (Fünfeckszahlen).
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Bausteine**")
    family = st.selectbox("Familie", list(C.FAMILIES), key="family_select",
                          help="Partitionen: von jeder Größe ein Baustein. Ebene Partitionen: von der Größe k gibt es k Bausteine. Wurzelbäume: rekursiv, ein Baum ist eine Wurzel mit einer Multimenge von Bäumen. Eigene Bausteine: die Tabelle unten.")
    n = st.slider("Zielgröße N", *bounds("n_slider"), key="n_slider",
                  help=f"Gesamtgröße der Multimenge beziehungsweise Zahl der Knoten. Es wird höchstens bis {', '.join(f'{k} ({v})' for k, v in C.N_CAP.items())} gerechnet.")
    m_choice = st.selectbox("Gleiche Bausteine höchstens", list(C.M_CHOICES), key="m_select",
                            help="beliebig: Multimenge. 1: Menge (jeder Baustein höchstens einmal). 2 oder 3: jeder Baustein höchstens so oft.")
    table = st.text_input("Tabelle a₁, a₂, … (nur bei „Eigene Bausteine“)", key="table_input",
                          help=f"Komma-getrennt, bis zu {C.TABLE_MAX_K} Einträge zwischen 0 und {C.TABLE_MAX_COPIES}: Eintrag k ist die Zahl der Bausteine der Größe k. „1,1,0,0,1“ sind die Münzen 1, 2 und 5.")
    st.button("🎲 Zufällige Bausteine", width="stretch", on_click=randomize_table)

sync_query_params({"family_select": family, "n_slider": int(n), "m_select": m_choice, "table_input": table})

settings = Settings(family, int(n), m_choice, table)
a = _analysis(settings)
if a.n_eff != settings.n:
    st.info(f"Für diese Familie rechnet die App höchstens bis N = {C.N_CAP[family]}: gerechnet wird mit N = {a.n_eff}.")
if a.table_error and family == "Eigene Bausteine":
    st.warning(f"Die Tabelle ist nicht lesbar ({a.table_error}). Gerechnet wird mit der Standardtabelle {C.DEFAULT_TABLE}.")

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
c_n = a.series[a.n_eff]
m1, m2, m3, m4 = st.columns(4)
m1.metric(f"Anzahl bei Größe {a.n_eff}", big_text(c_n), help="Wie viele Multimengen (Mengen, Bäume) die Gesamtgröße N haben.")
m2.metric(f"Anzahl bis Größe {a.n_eff}", big_text(sum(a.series)), help="Summe über alle Größen von 0 bis N (bei Wurzelbäumen von 1 bis N): beim Rucksack die Zahl der Teilmengen bis zur Kapazität.")
m3.metric("Stellen der Anzahl", str(digit_count(c_n)), help="Zahl der Dezimalstellen von „Anzahl bei Größe N“.")
m4.metric("Schritte der Rechnung", big_text(a.steps), help="Additionen beziehungsweise Multiplikationen des Hauptwegs, exakt gezählt.")
st.plotly_chart(build_growth(a.series, 1 if family == "Wurzelbäume" else 0), width="stretch", key="main_chart")
st.caption("Zehnerlogarithmus der Anzahl je Größe. Die Zahlen wachsen so schnell, dass nur die logarithmische Achse sie zeigt.")
with st.expander("Die ersten Werte ansehen"):
    st.dataframe(first_values(a), hide_index=True, width="stretch")

if st.button("📄 PDF der aktuellen Aufgabe erstellen", key="pdf_make"):
    st.session_state["pdf_made"] = (settings, build_pdf(a))
made = st.session_state.get("pdf_made")
if made and made[0] == settings:
    st.download_button("⬇️ PDF herunterladen", data=made[1], file_name="multimengen.pdf", mime="application/pdf", key="pdf_download")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie wird aus „wie viele Bausteine der Größe k“ die Zahl der Multimengen?")
verdict(verdict_answers(a))

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Dieselben Zahlen auf allen Wegen")
st.caption(f"Die eingestellte Aufgabe, gerechnet auf allen Wegen, die für sie gelten. Aufzählen läuft nur, wenn es klein bleibt (Partitionen bis N = {C.PARTITION_ENUM_N}, sonst bis N = {C.BRUTE_N} und {big_text(C.BRUTE_LIMIT)} Auswahlen, "
           f"Wurzelbäume bis N = {C.TREE_ENUM_N}); das Produkt entfällt über {big_text(C.PRODUCT_BUDGET)} Schritten.")
if a.problems:
    st.error("Die Rechenwege widersprechen sich: " + "; ".join(a.problems))
else:
    st.success("Alle gerechneten Wege geben dieselbe Zahl.")
st.dataframe(way_rows(a), hide_index=True, width="stretch")

st.markdown("---")

st.subheader("🔬 Experiment 2: Der Aufwand ist sehr verschieden")
st.caption("Schritte für die Partitionszahl p(n), exakt gezählt: Aufzählen (so viele Partitionen, wie p(n) groß ist), das Produkt der Faktoren und die Fünfeckszahlen-Rekursion. Die Zeit messen Sie auf Klick; sie ist eine Messung dieses Rechners.")
effort = _effort()
st.plotly_chart(build_effort(effort), width="stretch", key="effort_chart")
st.dataframe([{**r, "Partitionen (Aufzählen)": big_text(r["Partitionen (Aufzählen)"]), "Schritte Produkt": big_text(r["Schritte Produkt"]),
               "Schritte Fünfeckszahlen": big_text(r["Schritte Fünfeckszahlen"]), "Produkt : Fünfeckszahlen": de(r["Produkt : Fünfeckszahlen"], 1)} for r in effort], hide_index=True, width="stretch")
verdict(verdict_effort(effort))
if st.button("⏱️ Zeit messen", key="time_run"):
    st.session_state["time_res"] = time_experiment()
timing = st.session_state.get("time_res")
if timing:
    st.dataframe([{"n": r["n"], "Produkt (Sekunden)": de(r["Produkt (Sekunden)"], 3), "Fünfeckszahlen (Sekunden)": de(r["Fünfeckszahlen (Sekunden)"], 3)} for r in timing], hide_index=True, width="stretch")
    verdict(verdict_time(timing))

st.markdown("---")

st.subheader("🔬 Experiment 3: Folge gegen Multimenge")
st.caption(f"Münzen {', '.join(str(c) for c in C.COIN_COINS)}: dieselben Münzen, einmal mit Reihenfolge (Folgen, Stück 3 und 4) und einmal ohne (Multimengen). Darunter: Zahlen als Summe mit und ohne Reihenfolge.")
orders, comps = _order()
st.plotly_chart(build_order(orders), width="stretch", key="order_chart")
st.dataframe([{"Betrag": r["Betrag"], "Folgen (Reihenfolge zählt)": big_text(r["Folgen (Reihenfolge zählt)"]), "Multimengen (Reihenfolge egal)": big_text(r["Multimengen (Reihenfolge egal)"]), "Faktor": times_text(r["Faktor"])} for r in orders],
             hide_index=True, width="stretch")
st.dataframe([{"n": r["n"], "Zusammensetzungen 2ⁿ⁻¹": big_text(r["Zusammensetzungen 2ⁿ⁻¹"]), "Partitionen": big_text(r["Partitionen"]), "Faktor": times_text(r["Faktor"])} for r in comps], hide_index=True, width="stretch")
verdict(verdict_order(orders, comps))

st.markdown("---")

st.subheader("🔬 Experiment 4: Bäume mit und ohne Reihenfolge")
st.caption("Ein Wurzelbaum ohne Reihenfolge ist eine Wurzel mit einer Multimenge von Bäumen darunter, $T = z \\cdot \\mathrm{MSET}(T)$. Stück 3 hat die Bäume mit Reihenfolge der Kinder gezählt (Catalan-Zahlen). "
           f"Die Rekursion wird gegen das Aufzählen kanonischer Formen bis n = {C.TREE_ENUM_N} geprüft, auch mit „höchstens ein gleiches Geschwister“.")
tree_table, ratios, tree_problems = _trees()
st.plotly_chart(build_tree_ratio(ratios), width="stretch", key="tree_chart")
st.dataframe([{"Knoten n": r["Knoten n"], "ohne Reihenfolge": big_text(r["ohne Reihenfolge"]), "mit Reihenfolge (Catalan, Stück 3)": big_text(r["mit Reihenfolge (Catalan, Stück 3)"]), "Verhältnis": de(r["Verhältnis"], 2)} for r in tree_table],
             hide_index=True, width="stretch")
verdict(verdict_trees(ratios, tree_problems))

st.markdown("---")

st.subheader("🔬 Experiment 5: Wann ist die Reihe rational?")
st.caption(f"Das Raten aus Stück 1 sucht eine Rekursion mit festen Koeffizienten. Teile bis k haben endlich viele Faktoren und damit eine rationale Reihe (Stück 2); alle Partitionen haben unendlich viele. "
           f"{C.RATIONAL_TERMS} Terme bei Teile bis k, {C.RATIONAL_P_TERMS} Terme bei p(n).")
rat = _rational()
st.dataframe([{"Reihe": r["Reihe"], "Terme": r["Terme"], "kürzestes Rezept (Ordnung)": "keines gefunden" if r["kürzestes Rezept (Ordnung)"] is None else str(r["kürzestes Rezept (Ordnung)"]),
               "Grad des Nenners": "–" if r["Grad des Nenners"] is None else str(r["Grad des Nenners"])} for r in rat], hide_index=True, width="stretch")
verdict(verdict_rational(rat))

st.markdown("---")

# --- Spielwiese ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🎲 Spielwiese: Partitionen ansehen")
st.caption("Alle Partitionen einer kleinen Zahl, ihr Ferrers-Diagramm und das gespiegelte (konjugierte) Diagramm. Spiegeln vertauscht „größter Teil“ und „Zahl der Teile“.")
p1, p2 = st.columns(2)
play_n = p1.slider("Zahl n", 1, C.PLAY_N_MAX, 8, key="play_n", help="Die Zahl, die in Teile zerlegt wird.")
play_k = p2.slider("Größter Teil höchstens", 1, C.PLAY_N_MAX, C.PLAY_N_MAX, key="play_k", help="Begrenzt den größten Teil; bei n oder mehr sind es alle Partitionen.")
play = _play(int(play_n), int(play_k))
labels = [" + ".join(str(x) for x in p) for p in play["partitions"][: C.LIST_MAX]]
pick = st.selectbox("Partition", labels, help=f"Die ersten {C.LIST_MAX} Partitionen; die Zahl aller steht im Ergebnis unten.")
if pick in labels:
    parts = play["partitions"][labels.index(pick)]
    f1, f2 = st.columns(2)
    f1.plotly_chart(build_ferrers(parts, "Partition " + pick), width="stretch", key="ferrers_a")
    f2.plotly_chart(build_ferrers(conjugate(parts), "Konjugierte Partition"), width="stretch", key="ferrers_b")
st.dataframe(play["rows"], hide_index=True, width="stretch")
verdict(verdict_playground(play))

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    f"""
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Die Reihenfolge ist egal** | Wenn sie zählt, ist es eine Folge: Münzen 1, 2, 5 und Betrag 100 geben 91 Trilliarden Folgen statt 541 Multimengen (Experiment 3). Das Modell muss festlegen, was „dieselbe Lösung“ heißt. | Stück 3 (Folge), Stück 4 |
| **Gleiche Bausteine sind austauschbar, verschiedene nicht** | Zwei Münzen gleichen Werts zählt die Tabelle als einen Baustein; zwei Gegenstände gleichen Gewichts als zwei verschiedene (Eintrag 2). Wer das anders meint, braucht eine andere Tabelle. | – |
| **Keine Symmetrie außer dem Vertauschen gleicher Bausteine** | Halsketten, Graphen bis auf Isomorphie und Ähnliches haben mehr Symmetrie; dafür braucht man Burnside und Pólya. | Stück 11 der Reihe |
| **Die Bausteine tragen keine Beschriftung** | Mit Beschriftung (Marken auf den Bausteinen) zählt man anders (exponentielle erzeugende Funktion: Stirling-Zahlen, Bell-Zahlen). | Stück 6 der Reihe |
| **Die Fünfeckszahlen-Rekursion** | Gilt nur für die Partitionszahl ohne Höchstzahl; für andere Tabellen $a_k$ gibt es sie nicht. | – |
| **Rational ist nicht alles** | Endlich viele Faktoren geben eine rationale Reihe; die Partitionszahl nicht (Experiment 5). Ihr Wachstum ist eine Frage der Asymptotik. | Stück 2, Stück 9 der Reihe |
| **Zielgröße begrenzt** | Je Familie rechnet die App nur bis zu einer Obergrenze ({', '.join(f'{k}: {v}' for k, v in C.N_CAP.items())}); darüber wird gekappt und das gesagt. | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Multimengen.** Gibt es $a_k$ verschiedene Bausteine der Größe $k$, ist die erzeugende Funktion der Multimengen
$$\mathrm{MSET}(z) = \prod_{k \ge 1} (1 - z^k)^{-a_k}, \qquad \text{Mengen: } \prod_{k \ge 1} (1 + z^k)^{a_k}, \qquad \text{höchstens } m \text{ gleiche: } \prod_{k \ge 1} (1 + z^k + \dots + z^{mk})^{a_k}.$$
Der Koeffizient $c_n = [z^n]\,\mathrm{MSET}(z)$ ist die Zahl der Multimengen der Gesamtgröße $n$. Diese Abbildung von $(a_k)$ auf $(c_n)$ heißt Euler-Transformation.

**Rekursion.** Die logarithmische Ableitung des Produkts gibt $n\, c_n = \sum_{k=1}^{n} b_k\, c_{n-k}$ mit $b_k = \sum_{d \mid k} d\, a_d$ (Multimengen); bei höchstens $m$ gleichen Bausteinen wird $b_k$ um $-(m+1)\, d\, a_d$ für jedes $d$ mit $(m+1)\,d \mid k$ verringert. Beide Wege haben $n(n+1)/2$ beziehungsweise (Produkt) $\sum_k a_k (n-k+1)$ Schritte.

**Partitionen.** $a_k = 1$: $p(n) = [z^n] \prod_k (1-z^k)^{-1}$. Eulers Fünfeckszahlensatz $\prod_k (1-z^k) = \sum_{j} (-1)^j z^{j(3j-1)/2}$ gibt $p(n) = \sum_{j \ge 1} (-1)^{j+1} \big[p(n - j(3j-1)/2) + p(n - j(3j+1)/2)\big]$ mit etwa $\sqrt{n}$ Termen je $n$.
Ungerade Teile und verschiedene Teile geben dieselbe Zahl: $\prod_k (1+z^k) = \prod_k (1 - z^{2k-1})^{-1}$. Spiegeln des Ferrers-Diagramms vertauscht größten Teil und Zahl der Teile.

**Wurzelbäume.** $T(z) = z \cdot \mathrm{MSET}(T)(z)$, das heißt $a_k = t_k$ rückgekoppelt: $t_{n+1} = c_n$ mit $c = \prod_k (1 - z^k)^{-t_k}$. Mit Reihenfolge der Kinder gilt $T = z/(1 - T)$ (Stück 3), die Catalan-Zahlen.

**Rationalität.** Endlich viele Faktoren $(1-z^k)^{-a_k}$ geben $1/Q(z)$ mit einem Polynom $Q$, also eine Rekursion mit festen Koeffizienten (Stück 2); bei Teilen bis $k$ hat $Q = \prod_{j \le k} (1 - z^j)$ den Grad $k(k+1)/2$.

**Literatur** (Titel und Fundstelle aus dem Gedächtnis, nicht eingesehen).
G. E. Andrews: *The Theory of Partitions*, Addison-Wesley, 1976 (Euler-Produkt, Fünfeckszahlensatz, Konjugation).
P. Flajolet und R. Sedgewick: *Analytic Combinatorics*, Cambridge University Press, 2009 (Multimengen-Konstruktion, unbeschriftete Strukturen).
M. Bernstein und N. J. A. Sloane: *Some canonical sequences of integers*, Linear Algebra and its Applications 226–228, 1995, S. 57–72 (Euler-Transformation).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
