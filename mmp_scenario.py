"""Szenario: aus den Einstellungen (Familie, Zielgröße, Bausteintabelle) die Spezifikation `a` bauen; Bausteintabelle lesen."""

import random

import mmp_constants as C


def effective_n(family: str, n: int) -> int:
    """Die Zielgröße, mit der die App wirklich rechnet (je Familie begrenzt)."""
    return max(C.N_MIN, min(n, C.N_CAP[family], C.N_MAX))


def parse_table(text: str):
    """Bausteintabelle `a_1,a_2,…` lesen. Rückgabe (Liste, Fehlertext oder None); bei einem Fehler die Standardtabelle."""
    default = [int(x) for x in C.DEFAULT_TABLE.split(",")]
    parts = [p for p in text.replace(";", ",").replace(" ", ",").split(",") if p != ""]
    if not parts:
        return default, "Die Tabelle ist leer."
    if len(parts) > C.TABLE_MAX_K:
        return default, f"Die Tabelle hat höchstens {C.TABLE_MAX_K} Einträge (Größen 1 bis {C.TABLE_MAX_K})."
    values = []
    for p in parts:
        try:
            v = int(p)
        except ValueError:
            return default, f"„{p}“ ist keine ganze Zahl."
        if not 0 <= v <= C.TABLE_MAX_COPIES:
            return default, f"Jeder Eintrag liegt zwischen 0 und {C.TABLE_MAX_COPIES} (gelesen: {v})."
        values.append(v)
    if not any(values):
        return default, "Mindestens ein Eintrag muss größer als 0 sein."
    return values, None


def table_text(values) -> str:
    return ",".join(str(v) for v in values)


def random_table(seed: int) -> str:
    """Zufällige Bausteintabelle (Größen 1 bis 8, je 0 bis 2 Bausteine, mindestens einer)."""
    rng = random.Random(seed)
    values = [rng.choice([0, 0, 1, 1, 2]) for _ in range(8)]
    if not any(values):
        values[rng.randrange(8)] = 1
    return table_text(values)


def spec_of(family: str, n: int, table_values) -> dict | None:
    """Bausteine {Größe: Anzahl} für die Familie; Wurzelbäume haben keine feste Spezifikation (sie hängt von der Lösung ab): None."""
    if family == "Partitionen":
        return {k: 1 for k in range(1, n + 1)}
    if family == "Ebene Partitionen":
        return {k: k for k in range(1, n + 1)}
    if family == "Wurzelbäume":
        return None
    if family == "Eigene Bausteine":
        return {k + 1: v for k, v in enumerate(table_values) if v and k + 1 <= n}
    raise ValueError(f"unbekannte Familie {family!r}")


def m_of(choice: str):
    """Höchstzahl gleicher Bausteine aus der Auswahl: None = beliebig."""
    return None if choice == "beliebig" else int(choice)
