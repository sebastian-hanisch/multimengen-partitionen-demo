"""Kennzahlen, Experimente und Verdikte. Jedes Verdikt ist eine reine Funktion (Art, Text); die App ruft st.<Art>(Text)."""

import time
from collections import Counter
from dataclasses import dataclass

import mmp_algorithm as A
import mmp_constants as C
from mmp_scenario import effective_n, m_of, parse_table, spec_of

_SUPER = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


@dataclass(frozen=True)
class Settings:
    family: str = C.DEFAULT_FAMILY
    n: int = C.DEFAULT_N
    m: str = C.DEFAULT_M
    table: str = C.DEFAULT_TABLE


@dataclass(frozen=True, eq=False)
class Analysis:
    settings: Settings
    n_eff: int
    m: object                              # None (beliebig) oder Höchstzahl gleicher Bausteine
    spec: object                           # {Größe: Anzahl} oder None (Wurzelbäume)
    table_error: object                    # Meldung zur Bausteintabelle oder None
    series: list                           # Koeffizienten c_0..c_N (Wurzelbäume: t_0 = 0, t_1.., t_N)
    ways: list                             # Rechenwege: {"Weg", "Wert", "Schritte", "Grund"}
    steps: int                             # Schritte des Hauptwegs
    problems: list                         # Meldungen des Vergleichs der Rechenwege


# ----------------------------------------------------------------------------- Formatierung

def de(x: float, digits: int = 2) -> str:
    return f"{x:.{digits}f}".replace(".", ",")


def big_text(x: int) -> str:
    """Ganze Zahl lesbar: bis 12 Stellen mit Tausenderpunkt, darüber Mantisse mal Zehnerpotenz mit Stellenzahl (ohne Stringumwandlung der ganzen Zahl)."""
    if x < 10 ** 12:
        return f"{x:,}".replace(",", ".")
    d = A.digit_count(x)
    s = str(x // 10 ** (d - 3))
    return f"{s[0]},{s[1:3]}·10{str(d - 1).translate(_SUPER)} ({d} Stellen)"


def times_text(x: float) -> str:
    """Faktor lesbar: bis 1000 mit einer Nachkommastelle, darüber als Tausenderzahl, sehr große als Zehnerpotenz."""
    if x < 1000:
        return de(x, 1)
    if x < 10 ** 12:
        return f"{round(x):,}".replace(",", ".")
    return big_text(round(x))


def m_text(m) -> str:
    return "beliebig oft" if m is None else "höchstens einmal" if m == 1 else f"höchstens {m}-mal"


def noun(family: str, m) -> str:
    """Name des Gezählten für die Texte (mit der Höchstzahl gleicher Bausteine)."""
    if family == "Partitionen":
        return "Partitionen" if m is None else "Partitionen in lauter verschiedene Teile" if m == 1 else f"Partitionen, in denen jeder Teil {m_text(m)} vorkommt"
    if family == "Ebene Partitionen":
        return "ebene Partitionen" if m is None else f"ebene Partitionen (jeder Baustein {m_text(m)})"
    if family == "Wurzelbäume":
        return "Wurzelbäume ohne Reihenfolge" if m is None else "Wurzelbäume ohne Reihenfolge (alle Geschwister verschieden)" if m == 1 else f"Wurzelbäume ohne Reihenfolge (höchstens {m} gleiche Geschwister)"
    return "Multimengen" if m is None else "Mengen" if m == 1 else f"Auswahlen (jeder Baustein {m_text(m)})"


# ----------------------------------------------------------------------------- Analyse der eingestellten Aufgabe

def _enum_partitions(n: int, m) -> int:
    return sum(1 for p in A.partitions(n) if m is None or max(Counter(p).values()) <= m)


def analyse(s: Settings) -> Analysis:
    n = effective_n(s.family, s.n)
    m = m_of(s.m)
    table_values, table_error = parse_table(s.table) if s.family == "Eigene Bausteine" else (parse_table(C.DEFAULT_TABLE)[0], None)
    spec = spec_of(s.family, n, table_values)
    ways, problems = [], []

    def add(name, value, steps, reason=""):
        ways.append({"Weg": name, "Wert": value, "Schritte": steps, "Grund": reason})

    if s.family == "Wurzelbäume":
        series = A.rooted_trees(n, m)
        main_steps = n * (n - 1) // 2
        add("Rekursion T = z·MSET(T)", series[n], main_steps)
        if n <= C.TREE_ENUM_N:
            count = A.trees_canonical_count(n, m)
            add("Aufzählen kanonischer Formen", count, A.plane_trees_count(n))
            if count != series[n]:
                problems.append(f"Aufzählen ({count}) und Rekursion ({series[n]}) weichen bei n = {n} ab")
        else:
            add("Aufzählen kanonischer Formen", None, None, f"nur bis n = {C.TREE_ENUM_N}")
        return Analysis(s, n, m, spec, table_error, series, ways, main_steps, problems)

    steps_planned = A.product_steps(spec, n, m)
    log_series, log_steps = A.series_log(spec, n, m)
    if steps_planned <= C.PRODUCT_BUDGET:
        series, prod_steps = A.series_product(spec, n, m)
        add("Produkt der Faktoren", series[n], prod_steps)
        if series != log_series:
            problems.append(f"Produkt und Rekursion weichen ab (erste Abweichung bei n = {next(i for i, (x, y) in enumerate(zip(series, log_series)) if x != y)})")
        main_steps = prod_steps
    else:
        series, main_steps = log_series, log_steps
        add("Produkt der Faktoren", None, None, f"übersprungen: {big_text(steps_planned)} Schritte wären zu viel")
    add("Rekursion der logarithmischen Ableitung", log_series[n], log_steps)
    if s.family == "Partitionen" and m is None:
        pent, pent_steps = A.partitions_pentagonal(n)
        add("Fünfeckszahlen-Rekursion", pent[n], pent_steps)
        if pent != series:
            problems.append("Fünfeckszahlen-Rekursion und Produkt weichen ab")
    else:
        add("Fünfeckszahlen-Rekursion", None, None, "gilt nur für die Partitionszahl ohne Höchstzahl")
    total = sum(series)
    if s.family == "Partitionen" and n <= C.PARTITION_ENUM_N:
        count = _enum_partitions(n, m)
        add("Aufzählen aller Partitionen", count, count)
        if count != series[n]:
            problems.append(f"Aufzählen ({count}) und Produkt ({series[n]}) weichen bei n = {n} ab")
    elif n <= C.BRUTE_N and total <= C.BRUTE_LIMIT:
        brute = A.series_brute(spec, n, m)
        add("Aufzählen aller Auswahlen", brute[n], total)
        if brute != series:
            problems.append("Aufzählen und Produkt weichen ab")
    else:
        add("Aufzählen aller Auswahlen", None, None, f"nur bis n = {C.BRUTE_N} und {big_text(C.BRUTE_LIMIT)} Auswahlen" + (f" (Partitionen: bis n = {C.PARTITION_ENUM_N})" if s.family == "Partitionen" else ""))
    return Analysis(s, n, m, spec, table_error, series, ways, main_steps, problems)


def way_rows(a: Analysis) -> list[dict]:
    """Tabelle der Rechenwege: Wert bei N, Schritte, Übereinstimmung."""
    rows = []
    reference = a.series[a.n_eff]
    for w in a.ways:
        if w["Wert"] is None:
            rows.append({"Weg": w["Weg"], "Anzahl bei N": "–", "Schritte": "–", "Ergebnis": w["Grund"]})
        else:
            rows.append({"Weg": w["Weg"], "Anzahl bei N": big_text(w["Wert"]), "Schritte": big_text(w["Schritte"]), "Ergebnis": "gleich" if w["Wert"] == reference else "weicht ab"})
    return rows


def first_values(a: Analysis, count: int = 16) -> list[dict]:
    """Die ersten Koeffizienten der Reihe (und der letzte), als Tabelle."""
    start = 1 if a.settings.family == "Wurzelbäume" else 0
    idx = list(range(start, min(a.n_eff, start + count - 1) + 1))
    if a.n_eff not in idx:
        idx.append(a.n_eff)
    return [{"Größe": i, "Anzahl": big_text(a.series[i])} for i in idx]


def verdict_answers(a: Analysis):
    s = a.settings
    c = a.series[a.n_eff]
    total = sum(a.series)
    what = noun(s.family, a.m)
    if s.family == "Wurzelbäume":
        head = f"Mit {a.n_eff} Knoten gibt es {big_text(c)} {what}; mit Reihenfolge der Kinder wären es {big_text(A.plane_trees_count(a.n_eff))}."
    else:
        head = f"Die Größe {a.n_eff} lässt sich auf {big_text(c)} Weisen aus den Bausteinen bilden ({what}); bis zur Größe {a.n_eff} gibt es insgesamt {big_text(total)}."
    if a.problems:
        return "error", "Die Rechenwege widersprechen sich: " + "; ".join(a.problems)
    checked = [w["Weg"] for w in a.ways if w["Wert"] is not None]
    return "success", f"{head} {len(checked)} Rechenweg(e) ({', '.join(checked)}) geben dieselbe Zahl."


# ----------------------------------------------------------------------------- Experiment 2: Aufwand

def effort_rows() -> list[dict]:
    pentagonal, _ = A.partitions_pentagonal(max(C.EFFORT_NS))
    rows = []
    for n in C.EFFORT_NS:
        spec = {k: 1 for k in range(1, n + 1)}
        prod, pent = A.product_steps(spec, n), A.pentagonal_steps(n)
        rows.append({"n": n, "Partitionen (Aufzählen)": pentagonal[n], "Schritte Produkt": prod, "Schritte Fünfeckszahlen": pent, "Produkt : Fünfeckszahlen": round(prod / pent, 1)})
    return rows


def verdict_effort(rows: list[dict]):
    last = rows[-1]
    return "success", (f"Bei n = {last['n']} müsste Aufzählen {big_text(last['Partitionen (Aufzählen)'])} Partitionen anfassen, "
                       f"das Produkt braucht {big_text(last['Schritte Produkt'])} Schritte, die Fünfeckszahlen-Rekursion {big_text(last['Schritte Fünfeckszahlen'])} (etwa {de(last['Produkt : Fünfeckszahlen'], 1)}-mal weniger). "
                       "Die Rekursion der logarithmischen Ableitung braucht wie das Produkt n(n+1)/2 Schritte: gleiche Zahlen, gleicher Aufwand; nur die Fünfeckszahlen sparen, und nur bei der Partitionszahl.")


def time_experiment() -> list[dict]:
    rows = []
    for n in C.TIME_NS:
        spec = {k: 1 for k in range(1, n + 1)}
        t0 = time.perf_counter()
        A.series_product(spec, n)
        t1 = time.perf_counter()
        A.partitions_pentagonal(n)
        t2 = time.perf_counter()
        rows.append({"n": n, "Produkt (Sekunden)": t1 - t0, "Fünfeckszahlen (Sekunden)": t2 - t1})
    return rows


def verdict_time(rows: list[dict]):
    first, last = rows[0], rows[-1]
    return "info", (f"Gemessen auf diesem Rechner (Python): n = {first['n']}: Produkt {de(first['Produkt (Sekunden)'], 3)} s, Fünfeckszahlen {de(first['Fünfeckszahlen (Sekunden)'], 3)} s; "
                    f"n = {last['n']}: Produkt {de(last['Produkt (Sekunden)'], 3)} s, Fünfeckszahlen {de(last['Fünfeckszahlen (Sekunden)'], 3)} s. Eine Messung, keine Garantie.")


# ----------------------------------------------------------------------------- Experiment 3: Folge gegen Multimenge

def compositions_with_parts(parts: tuple, n_max: int) -> list[int]:
    """Folgen (Reihenfolge zählt) aus den Teilen: c_n = Summe c_(n−p)."""
    c = [1] + [0] * n_max
    for n in range(1, n_max + 1):
        c[n] = sum(c[n - p] for p in parts if n - p >= 0)
    return c


def order_rows() -> list[dict]:
    top = max(C.COIN_TOTALS)
    folge = compositions_with_parts(C.COIN_COINS, top)
    multi, _ = A.series_product({k: 1 for k in C.COIN_COINS}, top)
    return [{"Betrag": n, "Folgen (Reihenfolge zählt)": folge[n], "Multimengen (Reihenfolge egal)": multi[n], "Faktor": folge[n] / multi[n]} for n in C.COIN_TOTALS]


def composition_rows() -> list[dict]:
    top = max(C.COMPOSITION_NS)
    p, _ = A.partitions_pentagonal(top)
    return [{"n": n, "Zusammensetzungen 2ⁿ⁻¹": 2 ** (n - 1), "Partitionen": p[n], "Faktor": (2 ** (n - 1)) / p[n]} for n in C.COMPOSITION_NS]


def verdict_order(rows: list[dict], comp: list[dict]):
    last, c_last = rows[-1], comp[-1]
    return "warning", (f"Münzen {', '.join(str(c) for c in C.COIN_COINS)}, Betrag {last['Betrag']}: {big_text(last['Folgen (Reihenfolge zählt)'])} Folgen, aber nur {big_text(last['Multimengen (Reihenfolge egal)'])} Multimengen. "
                       f"Bei Zahlen als Summe sind es für n = {c_last['n']} {big_text(c_last['Zusammensetzungen 2ⁿ⁻¹'])} Zusammensetzungen gegen {big_text(c_last['Partitionen'])} Partitionen. "
                       "Welche Zahl stimmt, hängt davon ab, ob die Reihenfolge einen Unterschied macht; das Modell muss das festlegen.")


# ----------------------------------------------------------------------------- Experiment 4: Bäume mit und ohne Reihenfolge

def tree_rows() -> list[dict]:
    t = A.rooted_trees(C.TREE_TABLE_N)
    return [{"Knoten n": n, "ohne Reihenfolge": t[n], "mit Reihenfolge (Catalan, Stück 3)": A.plane_trees_count(n), "Verhältnis": A.plane_trees_count(n) / t[n]} for n in range(1, C.TREE_TABLE_N + 1)]


def tree_ratios() -> dict:
    """Verhältnis a(n+1)/a(n) für n = 2..TREE_RATIO_N − 1, ohne und mit Reihenfolge."""
    t = A.rooted_trees(C.TREE_RATIO_N)
    ns = list(range(2, C.TREE_RATIO_N))
    return {"n": ns, "ohne": [t[n + 1] / t[n] for n in ns], "mit": [A.plane_trees_count(n + 1) / A.plane_trees_count(n) for n in ns]}


def tree_check() -> list[str]:
    """Rekursion gegen Aufzählen kanonischer Formen für n = 1..TREE_ENUM_N, ohne Beschränkung und mit höchstens einem gleichen Geschwister."""
    problems = []
    for m in (None, 1):
        t = A.rooted_trees(C.TREE_ENUM_N, m)
        for n in range(1, C.TREE_ENUM_N + 1):
            if A.trees_canonical_count(n, m) != t[n]:
                problems.append(f"n = {n}, m = {m}: Aufzählen und Rekursion weichen ab")
    return problems


def verdict_trees(ratios: dict, problems: list[str]):
    if problems:
        return "error", "Aufzählen und Rekursion widersprechen sich: " + "; ".join(problems)
    i = C.TREE_RATIO_AT[-1] - 2
    return "success", (f"Von {ratios['n'][i]} auf {ratios['n'][i] + 1} Knoten wächst die Zahl der Bäume ohne Reihenfolge um den Faktor {de(ratios['ohne'][i], 3)}, mit Reihenfolge um {de(ratios['mit'][i], 3)} (Messung). "
                       f"Rekursion und Aufzählen kanonischer Formen stimmen für n = 1 bis {C.TREE_ENUM_N} überein, auch mit der Einschränkung „höchstens ein gleiches Geschwister“.")


# ----------------------------------------------------------------------------- Experiment 5: wann ist die Reihe rational?

def rational_rows() -> list[dict]:
    rows = []
    for k in C.RATIONAL_KS:
        seq, _ = A.series_product({j: 1 for j in range(1, k + 1)}, C.RATIONAL_TERMS - 1)
        rows.append({"Reihe": f"Teile bis {k}", "Terme": len(seq), "kürzestes Rezept (Ordnung)": A.guess_order(seq), "Grad des Nenners": k * (k + 1) // 2})
    p, _ = A.partitions_pentagonal(C.RATIONAL_P_TERMS - 1)
    length = A.linear_complexity(p)
    rows.append({"Reihe": "alle Partitionen p(n)", "Terme": len(p), "kürzestes Rezept (Ordnung)": A.guess_order(p), "Grad des Nenners": None, "Länge": length})
    return rows


def verdict_rational(rows: list[dict]):
    small, p = rows[:-1], rows[-1]
    if any(r["kürzestes Rezept (Ordnung)"] != r["Grad des Nenners"] for r in small):
        return "error", "Die geratene Ordnung weicht vom Grad des Nenners ab."
    return "warning", (f"Teile bis k haben eine rationale Reihe: das geratene Rezept hat genau die Ordnung k(k+1)/2 (k = 1 bis {C.RATIONAL_KS[-1]}). "
                       f"Für alle Partitionen findet das Raten bei {p['Terme']} Termen kein kurzes Rezept (das kürzeste hat {p['Länge']} Koeffizienten bei {p['Terme']} Termen, es merkt sich die Folge nur, statt sie zu erklären): p(n) ist nicht rational.")


# ----------------------------------------------------------------------------- Spielwiese: Partitionen ansehen

def playground(n: int, kmax: int) -> dict:
    """Alle Partitionen von n mit größtem Teil höchstens kmax; Zähler nach größtem Teil und nach Zahl der Teile (Konjugation)."""
    n = max(1, min(n, C.PLAY_N_MAX))
    kmax = max(1, min(kmax, n))
    shown = [p for p in A.partitions(n, kmax)]
    series, _ = A.series_product({j: 1 for j in range(1, kmax + 1)}, n)
    every = list(A.partitions(n))
    rows = [{"k": k, "größter Teil höchstens k": sum(1 for p in every if p[0] <= k), "höchstens k Teile": sum(1 for p in every if len(p) <= k)} for k in range(1, n + 1)]
    return {"n": n, "kmax": kmax, "partitions": shown, "expected": series[n], "rows": rows}


def verdict_playground(res: dict):
    if len(res["partitions"]) != res["expected"]:
        return "error", f"Aufzählen ({len(res['partitions'])}) und Produkt ({res['expected']}) weichen ab."
    same = all(r["größter Teil höchstens k"] == r["höchstens k Teile"] for r in res["rows"])
    if not same:
        return "error", "Die Konjugation stimmt nicht."
    note = f" Es werden die ersten {C.LIST_MAX} gezeigt." if len(res["partitions"]) > C.LIST_MAX else ""
    return "success", (f"{big_text(res['expected'])} Partitionen von {res['n']} mit größtem Teil höchstens {res['kmax']}, aufgezählt und mit dem Produkt aus den Faktoren 1/(1 − zʲ), j ≤ {res['kmax']}, gleich.{note} "
                       "Die Zahl der Partitionen mit größtem Teil höchstens k ist für jedes k gleich der mit höchstens k Teilen (Spiegeln des Ferrers-Diagramms).")
