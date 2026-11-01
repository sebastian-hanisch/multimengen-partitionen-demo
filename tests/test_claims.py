"""Jede Zahl aus der README und aus den Texten der App, nachgerechnet (DEMO-PLAYBOOK §4). Es gibt keine Zeit als Zahl; die Zahlen sind exakt oder Bänder."""

import math

import mmp_algorithm as A
import mmp_constants as C
import mmp_evaluation as ev


def _series(spec, n, m=None):
    return A.series_product(spec, n, m)[0]


def test_readme_hand_instances():
    assert [len(list(A.partitions(n))) for n in range(1, 11)] == [1, 2, 3, 5, 7, 11, 15, 22, 30, 42]
    assert _series({1: 1, 2: 1, 5: 1}, 5) == [1, 1, 2, 2, 3, 4]
    assert _series({k: 1 for k in range(1, 9)}, 8, 1)[8] == 6 == sum(1 for p in A.partitions(8) if len(set(p)) == len(p))
    assert _series({k: 1 for k in range(1, 9, 2)}, 8)[8] == 6


def test_readme_partition_numbers():
    p = A.partitions_pentagonal(1000)[0]
    assert (p[10], p[50], p[100], p[200]) == (42, 204226, 190569292, 3972999029388)
    assert p[1000] == 24061467864032622473692149727991 and A.digit_count(p[1000]) == 32
    assert sum(p[:51]) == 1295971 == sum(_series({k: 1 for k in range(1, 51)}, 50))


def test_readme_distinct_parts():
    q = _series({k: 1 for k in range(1, 101)}, 100, 1)
    assert (q[10], q[50], q[100]) == (10, 3658, 444793) and sum(q[:51]) == 31583
    assert q == _series({k: 1 for k in range(1, 101, 2)}, 100)


def test_readme_effort_table():
    rows = ev.effort_rows()
    assert [(r["n"], r["Schritte Produkt"], r["Schritte Fünfeckszahlen"]) for r in rows] == [(50, 1275, 345), (100, 5050, 1004), (200, 20100, 2904), (500, 125250, 11709), (1000, 500500, 33475)]
    assert [r["Produkt : Fünfeckszahlen"] for r in rows] == [3.7, 5.0, 6.9, 10.7, 15.0]
    assert 14.9 < 500500 / 33475 < 15.0
    assert [A.digit_count(r["Partitionen (Aufzählen)"]) for r in rows] == [6, 9, 13, 22, 32]
    for n in C.EFFORT_NS:                                                           # die Zählung stimmt mit der wirklichen Rechnung überein
        assert A.series_product({k: 1 for k in range(1, n + 1)}, n)[1] == n * (n + 1) // 2 == A.series_log({k: 1 for k in range(1, n + 1)}, n)[1]
        assert A.partitions_pentagonal(n)[1] == A.pentagonal_steps(n)


def test_readme_compositions_against_partitions():
    rows = ev.composition_rows()
    assert [(r["n"], r["Partitionen"]) for r in rows] == [(10, 42), (30, 5604), (50, 204226), (100, 190569292)]
    assert [r["Zusammensetzungen 2ⁿ⁻¹"] for r in rows] == [512, 536870912, 562949953421312, 2 ** 99]
    assert [round(r["Faktor"], 1) for r in rows][:2] == [12.2, 95801.4] and 2.75e9 < rows[2]["Faktor"] < 2.76e9 and 3.3e21 < rows[3]["Faktor"] < 3.4e21


def test_readme_coins():
    rows = ev.order_rows()
    assert [(r["Betrag"], r["Folgen (Reihenfolge zählt)"], r["Multimengen (Reihenfolge egal)"]) for r in rows] == [
        (5, 9, 4), (10, 128, 10), (15, 1843, 18), (20, 26547, 29), (50, 237139442616, 146), (100, 91197869007632925819218, 541)]
    assert 91 <= rows[-1]["Folgen (Reihenfolge zählt)"] / 10 ** 21 < 92                      # „91 Trilliarden“ in den Texten (Trilliarde = 10²¹)
    assert sum(_series({1: 1, 2: 1, 5: 1}, 100)) == 19006


def test_readme_the_stueck_4_knapsack():
    spec = {}
    for w in [2, 2, 3, 5, 5, 6, 9, 9, 9, 10]:
        spec[w] = spec.get(w, 0) + 1
    assert spec == {2: 2, 3: 1, 5: 2, 6: 1, 9: 3, 10: 1} and [spec.get(k, 0) for k in range(1, 11)] == [0, 2, 1, 0, 2, 1, 0, 0, 3, 1]
    assert _series(spec, 30, 1)[30] == 38 and sum(_series(spec, 30, 1)) == 531
    assert (sum(_series(spec, 30)), sum(_series(spec, 30, 2)), sum(_series(spec, 30, 3))) == (8387, 2580, 4573)


def test_readme_trees():
    t = A.rooted_trees(200)
    assert t[1:15] == [1, 1, 2, 4, 9, 20, 48, 115, 286, 719, 1842, 4766, 12486, 32973]
    assert [A.plane_trees_count(n) for n in range(1, 13)] == [1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862, 16796, 58786]
    assert [round(t[n + 1] / t[n], 4) for n in C.TREE_RATIO_AT] == [2.8691, 2.9119, 2.9336]
    assert [round(A.catalan(n) / A.catalan(n - 1), 4) for n in C.TREE_RATIO_AT] == [3.8824, 3.9406, 3.9700]     # mit Reihenfolge ist a(n) = Catalan(n−1), also a(n+1)/a(n) = Catalan(n)/Catalan(n−1)
    assert A.digit_count(t[200]) == 91
    assert A.rooted_trees(10, 1)[1:] == [1, 1, 1, 2, 3, 6, 12, 25, 52, 113]


def test_readme_plane_partitions_and_trees_presets():
    c = _series({k: k for k in range(1, 16)}, 15)
    assert c == [1, 1, 3, 6, 13, 24, 48, 86, 160, 282, 500, 859, 1479, 2485, 4167, 6879]
    a = ev.analyse(ev.Settings(**{k: v for k, v in C.PRESETS["Ebene Partitionen"].items()}))
    assert a.series[12] == 1479 and sum(a.series) == 3462
    b = ev.analyse(ev.Settings(**C.PRESETS["Wurzelbäume ohne Reihenfolge"]))
    assert b.series[11] == 1842 and A.plane_trees_count(11) == 16796


def test_readme_rational_series():
    assert [A.guess_order(_series({j: 1 for j in range(1, k + 1)}, 399)) for k in range(1, 7)] == [1, 3, 6, 10, 15, 21]
    assert _series({1: 1, 2: 1}, 400) == [n // 2 + 1 for n in range(401)]
    assert _series({1: 1, 2: 1, 3: 1}, 400) == [round((n + 3) ** 2 / 12) for n in range(401)]
    assert A.linear_complexity(A.partitions_pentagonal(299)[0]) == 150
    for k, expected in ((3, 1.006), (4, 1.0151), (5, 1.0303)):
        lead = 1000 ** (k - 1) / (math.factorial(k) * math.factorial(k - 1))
        assert round(_series({j: 1 for j in range(1, k + 1)}, 1000)[1000] / lead, 4) == expected


def test_readme_growth_against_hardy_ramanujan():
    p = A.partitions_pentagonal(1000)[0]
    errors = [p[n] / (math.exp(math.pi * math.sqrt(2 * n / 3)) / (4 * n * math.sqrt(3))) - 1 for n in (10, 100, 1000)]
    assert [round(e, 4) for e in errors] == [-0.1269, -0.0437, -0.014]


def test_preset_help_numbers():
    s = ev.Settings
    assert ev.analyse(s(**C.PRESETS["Standardfall: Partitionen von 50"])).series[50] == 204226
    assert ev.analyse(s(**C.PRESETS["Verschiedene Teile (Menge)"])).series[100] == 444793
    assert ev.analyse(s(**C.PRESETS["Münzen 1, 2, 5: Betrag 100"])).series[100] == 541
    assert sum(ev.analyse(s(**C.PRESETS["Rucksack aus Stück 4 (je Gegenstand einmal)"])).series) == 531
    big = ev.analyse(s(**C.PRESETS["Große Zahl: Wurzelbäume mit 500 Knoten"]))
    assert A.digit_count(big.series[500]) == 231 and big.steps == 124750 and A.digit_count(A.plane_trees_count(500)) == 297
    assert ev.analyse(s("Partitionen", 1000)).steps == 500500


def test_app_text_limits_come_from_the_constants():
    assert (C.N_CAP, C.TABLE_MAX_K, C.TABLE_MAX_COPIES, C.PRODUCT_BUDGET) == ({"Partitionen": 1000, "Ebene Partitionen": 150, "Wurzelbäume": 500, "Eigene Bausteine": 1000}, 12, 9, 3_000_000)
    assert (C.BRUTE_LIMIT, C.BRUTE_N, C.PARTITION_ENUM_N, C.TREE_ENUM_N, C.LIST_MAX, C.PLAY_N_MAX) == (200_000, 12, 40, 11, 40, 30)
    assert (C.EFFORT_NS, C.COIN_COINS, C.COIN_TOTALS, C.COMPOSITION_NS, C.RATIONAL_KS, C.RATIONAL_TERMS, C.RATIONAL_P_TERMS) == (
        (50, 100, 200, 500, 1000), (1, 2, 5), (5, 10, 15, 20, 50, 100), (10, 30, 50, 100), (1, 2, 3, 4, 5, 6), 400, 300)
