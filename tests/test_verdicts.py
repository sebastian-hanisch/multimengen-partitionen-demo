"""Verdikte und Formatierung an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier."""

import mmp_algorithm as A
import mmp_constants as C
import mmp_evaluation as ev

S = ev.Settings


def test_formatting():
    assert ev.de(3.14159, 3) == "3,142" and ev.big_text(0) == "0" and ev.big_text(1234567) == "1.234.567" and ev.big_text(10 ** 12) == "1,00·10¹² (13 Stellen)"
    assert ev.times_text(12.19) == "12,2" and ev.times_text(95801.37) == "95.801" and ev.times_text(3.3e21) == "3,30·10²¹ (22 Stellen)" and ev.times_text(999.94) == "999,9"
    assert [ev.m_text(m) for m in (None, 1, 2, 3)] == ["beliebig oft", "höchstens einmal", "höchstens 2-mal", "höchstens 3-mal"]


def test_nouns_per_family_and_m():
    assert ev.noun("Partitionen", None) == "Partitionen" and ev.noun("Partitionen", 1) == "Partitionen in lauter verschiedene Teile"
    assert ev.noun("Partitionen", 2) == "Partitionen, in denen jeder Teil höchstens 2-mal vorkommt"
    assert ev.noun("Ebene Partitionen", None) == "ebene Partitionen" and ev.noun("Ebene Partitionen", 3) == "ebene Partitionen (jeder Baustein höchstens 3-mal)"
    assert ev.noun("Wurzelbäume", None) == "Wurzelbäume ohne Reihenfolge" and ev.noun("Wurzelbäume", 1) == "Wurzelbäume ohne Reihenfolge (alle Geschwister verschieden)"
    assert ev.noun("Wurzelbäume", 2) == "Wurzelbäume ohne Reihenfolge (höchstens 2 gleiche Geschwister)"
    assert ev.noun("Eigene Bausteine", None) == "Multimengen" and ev.noun("Eigene Bausteine", 1) == "Mengen" and ev.noun("Eigene Bausteine", 3) == "Auswahlen (jeder Baustein höchstens 3-mal)"


def test_verdict_answers_standard_case():
    a = ev.analyse(S())
    assert ev.verdict_answers(a) == ("success", "Die Größe 50 lässt sich auf 204.226 Weisen aus den Bausteinen bilden (Partitionen); bis zur Größe 50 gibt es insgesamt 1.295.971. "
                                                "3 Rechenweg(e) (Produkt der Faktoren, Rekursion der logarithmischen Ableitung, Fünfeckszahlen-Rekursion) geben dieselbe Zahl.")


def test_verdict_answers_for_the_stueck_4_knapsack_and_trees():
    kind, text = ev.verdict_answers(ev.analyse(S("Eigene Bausteine", 30, "1", "0,2,1,0,2,1,0,0,3,1")))
    assert kind == "success" and "auf 38 Weisen" in text and "(Mengen)" in text and "insgesamt 531." in text
    kind, text = ev.verdict_answers(ev.analyse(S("Wurzelbäume", 4)))
    assert kind == "success" and text.startswith("Mit 4 Knoten gibt es 4 Wurzelbäume ohne Reihenfolge; mit Reihenfolge der Kinder wären es 5. 2 Rechenweg(e)")


def test_verdict_answers_reports_a_disagreement_as_an_error():
    a = ev.analyse(S())
    broken = ev.Analysis(a.settings, a.n_eff, a.m, a.spec, a.table_error, a.series, a.ways, a.steps, ["Produkt und Rekursion weichen ab"])
    assert ev.verdict_answers(broken) == ("error", "Die Rechenwege widersprechen sich: Produkt und Rekursion weichen ab")


def test_way_rows_for_the_hand_coins():
    a = ev.analyse(S("Eigene Bausteine", 5, "beliebig", "1,1,0,0,1"))
    rows = ev.way_rows(a)
    assert rows[0] == {"Weg": "Produkt der Faktoren", "Anzahl bei N": "4", "Schritte": "10", "Ergebnis": "gleich"}
    assert rows[1] == {"Weg": "Rekursion der logarithmischen Ableitung", "Anzahl bei N": "4", "Schritte": "15", "Ergebnis": "gleich"}
    assert rows[2]["Anzahl bei N"] == "–" and rows[2]["Ergebnis"] == "gilt nur für die Partitionszahl ohne Höchstzahl"
    assert rows[3] == {"Weg": "Aufzählen aller Auswahlen", "Anzahl bei N": "4", "Schritte": "13", "Ergebnis": "gleich"}          # 1 + 1 + 2 + 2 + 3 + 4 Auswahlen bis Größe 5


def test_way_rows_flag_a_deviation():
    a = ev.analyse(S("Eigene Bausteine", 5, "beliebig", "1,1,0,0,1"))
    ways = [dict(w) for w in a.ways]
    ways[0]["Wert"] = 5
    assert ev.way_rows(ev.Analysis(a.settings, a.n_eff, a.m, a.spec, a.table_error, a.series, ways, a.steps, []))[0]["Ergebnis"] == "weicht ab"


def test_first_values():
    a = ev.analyse(S("Eigene Bausteine", 5, "beliebig", "1,1,0,0,1"))
    assert ev.first_values(a) == [{"Größe": i, "Anzahl": str(v)} for i, v in enumerate([1, 1, 2, 2, 3, 4])]
    big = ev.first_values(ev.analyse(S("Partitionen", 40)))
    assert [r["Größe"] for r in big] == list(range(16)) + [40] and big[-1]["Anzahl"] == "37.338"
    trees = ev.first_values(ev.analyse(S("Wurzelbäume", 4)))
    assert [r["Größe"] for r in trees] == [1, 2, 3, 4] and [r["Anzahl"] for r in trees] == ["1", "1", "2", "4"]


def test_effort_rows_and_verdict():
    rows = ev.effort_rows()
    assert [r["n"] for r in rows] == list(C.EFFORT_NS)
    assert [r["Schritte Produkt"] for r in rows] == [n * (n + 1) // 2 for n in C.EFFORT_NS]
    assert [r["Schritte Fünfeckszahlen"] for r in rows] == [345, 1004, 2904, 11709, 33475]
    assert rows[-1]["Partitionen (Aufzählen)"] == 24061467864032622473692149727991 and rows[-1]["Produkt : Fünfeckszahlen"] == 15.0
    kind, text = ev.verdict_effort(rows)
    assert kind == "success" and text.startswith("Bei n = 1000 müsste Aufzählen 2,40·10³¹ (32 Stellen) Partitionen anfassen, das Produkt braucht 500.500 Schritte, die Fünfeckszahlen-Rekursion 33.475 (etwa 15,0-mal weniger).")


def test_time_experiment_shape_and_verdict_text():
    rows = [{"n": 1000, "Produkt (Sekunden)": 0.1234, "Fünfeckszahlen (Sekunden)": 0.0156}, {"n": 3000, "Produkt (Sekunden)": 1.5, "Fünfeckszahlen (Sekunden)": 0.1}]
    assert ev.verdict_time(rows) == ("info", "Gemessen auf diesem Rechner (Python): n = 1000: Produkt 0,123 s, Fünfeckszahlen 0,016 s; n = 3000: Produkt 1,500 s, Fünfeckszahlen 0,100 s. Eine Messung, keine Garantie.")
    res = ev.time_experiment()
    assert [r["n"] for r in res] == list(C.TIME_NS) and all(r["Produkt (Sekunden)"] >= 0 and r["Fünfeckszahlen (Sekunden)"] >= 0 for r in res)


def test_order_rows_and_verdict():
    rows, comp = ev.order_rows(), ev.composition_rows()
    assert [(r["Betrag"], r["Folgen (Reihenfolge zählt)"], r["Multimengen (Reihenfolge egal)"]) for r in rows][:4] == [(5, 9, 4), (10, 128, 10), (15, 1843, 18), (20, 26547, 29)]
    assert [(r["n"], r["Zusammensetzungen 2ⁿ⁻¹"], r["Partitionen"]) for r in comp][:2] == [(10, 512, 42), (30, 536870912, 5604)]
    assert abs(rows[1]["Faktor"] - 12.8) < 1e-12 and abs(comp[0]["Faktor"] - 512 / 42) < 1e-12
    assert ev.verdict_order(rows, comp) == ("warning", "Münzen 1, 2, 5, Betrag 100: 9,11·10²² (23 Stellen) Folgen, aber nur 541 Multimengen. Bei Zahlen als Summe sind es für n = 100 "
                                                       "6,33·10²⁹ (30 Stellen) Zusammensetzungen gegen 190.569.292 Partitionen. Welche Zahl stimmt, hängt davon ab, ob die Reihenfolge einen Unterschied macht; das Modell muss das festlegen.")


def test_tree_rows_ratios_and_verdict():
    rows = ev.tree_rows()
    assert [r["ohne Reihenfolge"] for r in rows][:8] == [1, 1, 2, 4, 9, 20, 48, 115] and [r["mit Reihenfolge (Catalan, Stück 3)"] for r in rows][:8] == [1, 1, 2, 5, 14, 42, 132, 429]
    assert rows[3]["Verhältnis"] == 5 / 4 and len(rows) == C.TREE_TABLE_N
    ratios = ev.tree_ratios()
    assert ratios["n"][0] == 2 and ratios["n"][-1] == C.TREE_RATIO_N - 1 and abs(ratios["ohne"][0] - 2.0) < 1e-12 and abs(ratios["mit"][0] - 2.0) < 1e-12 and abs(ratios["mit"][1] - 5 / 2) < 1e-12 and abs(ratios["mit"][2] - 14 / 5) < 1e-12
    assert ev.verdict_trees(ratios, []) == ("success", "Von 199 auf 200 Knoten wächst die Zahl der Bäume ohne Reihenfolge um den Faktor 2,934, mit Reihenfolge um 3,970 (Messung). "
                                                      "Rekursion und Aufzählen kanonischer Formen stimmen für n = 1 bis 11 überein, auch mit der Einschränkung „höchstens ein gleiches Geschwister“.")
    assert ev.verdict_trees(ratios, ["n = 5, m = None: Aufzählen und Rekursion weichen ab"])[0] == "error"
    assert ev.tree_check() == []


def test_rational_rows_and_verdict():
    rows = ev.rational_rows()
    assert [(r["Reihe"], r["kürzestes Rezept (Ordnung)"], r["Grad des Nenners"], r["Terme"]) for r in rows[:-1]] == [(f"Teile bis {k}", k * (k + 1) // 2, k * (k + 1) // 2, 400) for k in range(1, 7)]
    assert rows[-1]["Reihe"] == "alle Partitionen p(n)" and rows[-1]["Terme"] == 300 and rows[-1]["kürzestes Rezept (Ordnung)"] is None and rows[-1]["Länge"] == 150
    kind, text = ev.verdict_rational(rows)
    assert kind == "warning" and "genau die Ordnung k(k+1)/2 (k = 1 bis 6)" in text and "das kürzeste hat 150 Koeffizienten bei 300 Termen" in text
    broken = [dict(rows[0], **{"kürzestes Rezept (Ordnung)": 2})] + rows[1:]
    assert ev.verdict_rational(broken)[0] == "error"


def test_playground_and_verdict():
    res = ev.playground(8, 30)
    assert res["n"] == 8 and res["kmax"] == 8 and len(res["partitions"]) == res["expected"] == 22
    assert [(r["k"], r["größter Teil höchstens k"], r["höchstens k Teile"]) for r in res["rows"]][:4] == [(1, 1, 1), (2, 5, 5), (3, 10, 10), (4, 15, 15)]
    kind, text = ev.verdict_playground(res)
    assert kind == "success" and text.startswith("22 Partitionen von 8 mit größtem Teil höchstens 8, aufgezählt und mit dem Produkt") and "Es werden die ersten" not in text
    small = ev.playground(8, 3)
    assert small["kmax"] == 3 and len(small["partitions"]) == small["expected"] == 10 and all(p[0] <= 3 for p in small["partitions"])
    assert "Es werden die ersten 40 gezeigt." in ev.verdict_playground(ev.playground(30, 30))[1]
    assert ev.verdict_playground(dict(res, expected=23))[0] == "error"
    assert ev.verdict_playground(dict(res, rows=[dict(res["rows"][0], **{"höchstens k Teile": 2})]))[0] == "error"


def test_playground_clamps_its_input():
    res = ev.playground(500, 0)
    assert res["n"] == C.PLAY_N_MAX and res["kmax"] == 1 and len(res["partitions"]) == 1
    assert ev.playground(-3, 99)["n"] == 1
