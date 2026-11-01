"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

FAMILIES = ("Partitionen", "Ebene Partitionen", "Wurzelbäume", "Eigene Bausteine")
DEFAULT_FAMILY = "Partitionen"
N_MIN, N_MAX, DEFAULT_N = 1, 1000, 50           # Zielgröße N (Summe der Größen beziehungsweise Zahl der Knoten)
N_CAP = {"Partitionen": 1000, "Ebene Partitionen": 150, "Wurzelbäume": 500, "Eigene Bausteine": 1000}   # größtes N je Familie, das die App rechnet
M_CHOICES = ("beliebig", "1", "2", "3")          # Höchstzahl gleicher Bausteine; „beliebig“ = Multimenge, 1 = Menge
DEFAULT_M = "beliebig"
TABLE_MAX_K, TABLE_MAX_COPIES = 12, 9            # Bausteintabelle: Größen 1 bis 12, je Größe höchstens 9 verschiedene Bausteine
DEFAULT_TABLE = "1,1,0,0,1"                      # Münzen 1, 2, 5 (je ein Baustein der Größe 1, 2 und 5)
PRODUCT_BUDGET = 3_000_000                       # darüber rechnet die App das Produkt nicht mit (nur die Rekursion)

BRUTE_LIMIT = 200_000                            # Aufzählen aller Auswahlen nur, wenn es höchstens so viele gibt (Summe der Koeffizienten bis N)
BRUTE_N = 12                                     # ... und nur bis zu dieser Zielgröße
PARTITION_ENUM_N = 40                            # Partitionszahl durch Aufzählen der Partitionen bis hier
TREE_ENUM_N = 11                                 # Wurzelbäume durch Aufzählen kanonischer Formen bis hier
LIST_MAX = 40                                    # Spielwiese: so viele Partitionen werden höchstens aufgelistet
PLAY_N_MAX = 30                                  # Spielwiese: Zahl n bis hier

EFFORT_NS = (50, 100, 200, 500, 1000)            # Experiment 2: n für p(n)
TIME_NS = (1000, 2000, 3000)                     # ... gemessene Zeit (nur auf Klick, nicht getestet)
COIN_COINS = (1, 2, 5)                           # Experiment 3: Münzen
COIN_TOTALS = (5, 10, 15, 20, 50, 100)
COMPOSITION_NS = (10, 30, 50, 100)               # ... Zusammensetzungen gegen Partitionen
TREE_TABLE_N = 14                                # Experiment 4: Tabelle der Bäume bis hier
TREE_RATIO_N = 200                               # ... Verhältnis a(n+1)/a(n) bis hier
TREE_RATIO_AT = (50, 100, 199)
RATIONAL_KS = (1, 2, 3, 4, 5, 6)                 # Experiment 5: Teile bis k
RATIONAL_TERMS = 400                             # ... Terme für Teile bis k
RATIONAL_P_TERMS = 300                           # ... Terme für p(n)

COLOR_MAIN = "#2F6B65"
COLOR_ALL = "rgba(150,150,150,0.75)"
COLOR_WARN = "#c0504d"
COLOR_LINE = "#4c78a8"

PRESETS = {
    "Standardfall: Partitionen von 50": {"family": "Partitionen", "n": 50, "m": "beliebig", "table": DEFAULT_TABLE},
    "Verschiedene Teile (Menge)": {"family": "Partitionen", "n": 100, "m": "1", "table": DEFAULT_TABLE},
    "Münzen 1, 2, 5: Betrag 100": {"family": "Eigene Bausteine", "n": 100, "m": "beliebig", "table": "1,1,0,0,1"},
    "Rucksack aus Stück 4 (je Gegenstand einmal)": {"family": "Eigene Bausteine", "n": 30, "m": "1", "table": "0,2,1,0,2,1,0,0,3,1"},
    "Ebene Partitionen": {"family": "Ebene Partitionen", "n": 12, "m": "beliebig", "table": DEFAULT_TABLE},
    "Wurzelbäume ohne Reihenfolge": {"family": "Wurzelbäume", "n": 11, "m": "beliebig", "table": DEFAULT_TABLE},
    "Große Zahl: Wurzelbäume mit 500 Knoten": {"family": "Wurzelbäume", "n": 500, "m": "beliebig", "table": DEFAULT_TABLE},
}
PRESET_HELP = {
    "Standardfall: Partitionen von 50": "Auf wie viele Weisen ist 50 eine Summe ohne Reihenfolge? 204.226. Aufzählen, Produkt, Rekursion und Fünfeckszahlen geben dieselbe Zahl.",
    "Verschiedene Teile (Menge)": "Jeder Teil höchstens einmal: 444.793 Partitionen von 100 in lauter verschiedene Teile (gleich der Zahl der Partitionen in ungerade Teile).",
    "Münzen 1, 2, 5: Betrag 100": "Ein Baustein je Münzwert, beliebig oft: 541 Multimengen. Als Folge mit Reihenfolge wären es 91 Trilliarden.",
    "Rucksack aus Stück 4 (je Gegenstand einmal)": "Die zehn Gewichte des Standardfalls aus Stück 4, Kapazität 30, je Gegenstand höchstens einmal: 531 Teilmengen bis zum Gewicht 30, dieselbe Zahl wie das Netz dort.",
    "Ebene Partitionen": "Von jeder Größe k gibt es k Bausteine (a_k = k): die ebenen Partitionen, 1.479 für N = 12.",
    "Wurzelbäume ohne Reihenfolge": "Rekursiv: ein Baum ist eine Wurzel mit einer Multimenge von Bäumen darunter. 1.842 Bäume mit 11 Knoten (mit Reihenfolge wären es 16.796).",
    "Große Zahl: Wurzelbäume mit 500 Knoten": "Die Rekursion braucht 124.750 Schritte; die Zahl der Bäume hat 231 Stellen (mit Reihenfolge der Kinder wären es 297 Stellen).",
}
