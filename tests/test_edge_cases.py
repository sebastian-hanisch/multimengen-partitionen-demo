"""Randfälle: leere Eingaben, Grenzen der Regler, Fehler in der Tabelle, große Zahlen (die 4300-Stellen-Grenze von `str`)."""

import pytest

import mmp_algorithm as A
import mmp_constants as C
import mmp_evaluation as ev
import mmp_scenario as S


def test_size_zero_has_one_selection_the_empty_one():
    for spec in ({}, {1: 1}, {5: 3}):
        for m in (None, 1, 2):
            assert A.series_product(spec, 0, m)[0] == A.series_log(spec, 0, m)[0] == A.series_brute(spec, 0, m) == [1]


def test_empty_specification_gives_only_the_empty_selection():
    assert A.series_product({}, 6)[0] == A.series_log({}, 6)[0] == A.series_brute({}, 6) == [1, 0, 0, 0, 0, 0, 0]


def test_blocks_larger_than_n_are_ignored():
    assert A.series_product({1: 1, 9: 4}, 5)[0] == A.series_log({1: 1, 9: 4}, 5)[0] == A.series_brute({1: 1, 9: 4}, 5) == [1, 1, 1, 1, 1, 1]


def test_one_block_of_size_one_gives_ones_and_at_most_m_copies_cuts_off():
    assert A.series_product({1: 1}, 6)[0] == [1] * 7
    assert A.series_product({1: 1}, 6, 2)[0] == [1, 1, 1, 0, 0, 0, 0] == A.series_log({1: 1}, 6, 2)[0] == A.series_brute({1: 1}, 6, 2)


def test_many_copies_of_one_block_give_binomials():
    """a_1 = 4 Bausteine der Größe 1 beliebig oft: Multimengen der Größe n aus 4 Sorten, C(n+3, 3)."""
    assert A.series_product({1: 4}, 8)[0] == [1, 4, 10, 20, 35, 56, 84, 120, 165]
    assert A.series_product({1: 4}, 8, 1)[0] == [1, 4, 6, 4, 1, 0, 0, 0, 0]          # Mengen: C(4, n)


def test_trees_of_size_one_and_two():
    assert A.rooted_trees(1) == [0, 1] and A.rooted_trees(2) == [0, 1, 1] and A.rooted_trees(0) == [0]
    assert A.trees_canonical_count(1) == 1 and A.trees_canonical_count(2) == 1


def test_partitions_of_zero_and_one():
    assert list(A.partitions(0)) == [()] and list(A.partitions(1)) == [(1,)] and list(A.partitions(3, 1)) == [(1, 1, 1)]


def test_huge_numbers_never_pass_through_str():
    big = 10 ** 5000 + 7
    assert A.digit_count(big) == 5001
    assert ev.big_text(big).endswith("(5001 Stellen)") and ev.big_text(big).startswith("1,00·10")
    assert abs(A.log10_int(big) - 5000) < 1e-9


def test_large_partition_numbers_are_exact_and_formatted():
    a = ev.analyse(ev.Settings("Partitionen", 1000))
    assert a.series[1000] == 24061467864032622473692149727991 and a.problems == []
    assert "·10³¹" in ev.big_text(a.series[1000])


def test_parse_table_errors():
    default = [1, 1, 0, 0, 1]
    assert S.parse_table("") == (default, "Die Tabelle ist leer.")
    assert S.parse_table(" , ,") == (default, "Die Tabelle ist leer.")
    assert S.parse_table("0,0,0") == (default, "Mindestens ein Eintrag muss größer als 0 sein.")
    assert S.parse_table("1,2,x")[1] == "„x“ ist keine ganze Zahl."
    assert S.parse_table("1,10")[1].startswith("Jeder Eintrag liegt zwischen 0 und 9")
    assert S.parse_table("1,-1")[1].startswith("Jeder Eintrag liegt zwischen 0 und 9")
    assert S.parse_table(",".join(["1"] * 13))[1].startswith("Die Tabelle hat höchstens 12")
    assert S.parse_table("1,1,0,0,1x")[1] == "„1x“ ist keine ganze Zahl."
    assert S.parse_table("1 2;3,0") == ([1, 2, 3, 0], None)


def test_effective_n_caps_per_family():
    assert S.effective_n("Partitionen", 5000) == 1000 and S.effective_n("Ebene Partitionen", 1000) == 150 and S.effective_n("Wurzelbäume", 1000) == 500
    assert S.effective_n("Eigene Bausteine", 0) == 1 and S.effective_n("Partitionen", -5) == 1


def test_unknown_family_is_refused():
    with pytest.raises(ValueError):
        S.spec_of("Unsinn", 5, [1])
    with pytest.raises(KeyError):
        S.effective_n("Unsinn", 5)


def test_spec_of_each_family():
    assert S.spec_of("Partitionen", 3, [1]) == {1: 1, 2: 1, 3: 1}
    assert S.spec_of("Ebene Partitionen", 3, [1]) == {1: 1, 2: 2, 3: 3}
    assert S.spec_of("Wurzelbäume", 3, [1]) is None
    assert S.spec_of("Eigene Bausteine", 3, [1, 0, 2, 5]) == {1: 1, 3: 2}                  # Größe 4 und 5 liegen über N = 3


@pytest.mark.parametrize("family", C.FAMILIES)
@pytest.mark.parametrize("n", [1, 2, 3])
@pytest.mark.parametrize("m", C.M_CHOICES)
def test_every_family_works_at_the_smallest_sizes(family, n, m):
    a = ev.analyse(ev.Settings(family, n, m, C.DEFAULT_TABLE))
    assert a.problems == [] and len(a.series) == a.n_eff + 1 and all(x >= 0 for x in a.series)
    assert ev.verdict_answers(a)[0] == "success" and ev.way_rows(a) and ev.first_values(a)


def test_table_with_only_large_blocks_has_no_selection_of_size_n():
    a = ev.analyse(ev.Settings("Eigene Bausteine", 3, "beliebig", "0,0,0,0,1"))
    assert a.series == [1, 0, 0, 0] and a.problems == []


def test_unreadable_table_falls_back_to_the_default_and_says_so():
    a = ev.analyse(ev.Settings("Eigene Bausteine", 10, "beliebig", "kaputt"))
    assert a.table_error == "„kaputt“ ist keine ganze Zahl." and a.series == ev.analyse(ev.Settings("Eigene Bausteine", 10, "beliebig", C.DEFAULT_TABLE)).series
    assert ev.analyse(ev.Settings("Partitionen", 10, "beliebig", "kaputt")).table_error is None          # andere Familien ignorieren die Tabelle


def test_product_is_skipped_over_the_budget_but_recursion_still_runs():
    a = ev.analyse(ev.Settings("Ebene Partitionen", 150, "3"))
    assert A.product_steps(a.spec, 150, 3) > 0
    big = ev.analyse(ev.Settings("Eigene Bausteine", 1000, "beliebig", "9,9,9,9,9,9,9,9,9,9,9,9"))
    assert A.product_steps(big.spec, 1000) < C.PRODUCT_BUDGET                       # klein genug, wird gerechnet
    assert next(w for w in big.ways if w["Weg"] == "Produkt der Faktoren")["Wert"] == big.series[1000]


def test_enumeration_is_skipped_when_too_many_selections():
    a = ev.analyse(ev.Settings("Eigene Bausteine", 12, "beliebig", "9,9,9,9,9,9,9,9,9,9,9,9"))
    row = next(r for r in ev.way_rows(a) if r["Weg"].startswith("Aufzählen"))
    assert row["Anzahl bei N"] == "–" and "nur bis n = 12" in row["Ergebnis"]


def test_pentagonal_row_only_for_unbounded_partitions():
    assert next(w for w in ev.analyse(ev.Settings("Partitionen", 30)).ways if w["Weg"].startswith("Fünfeck"))["Wert"] == 5604
    assert next(w for w in ev.analyse(ev.Settings("Partitionen", 30, "1")).ways if w["Weg"].startswith("Fünfeck"))["Wert"] is None
    assert next(w for w in ev.analyse(ev.Settings("Eigene Bausteine", 30)).ways if w["Weg"].startswith("Fünfeck"))["Wert"] is None


def test_linear_complexity_edge_cases():
    assert A.linear_complexity([]) == 0 and A.guess_order([]) is None
    assert A.guess_order([0, 0, 0, 0, 0, 0]) == 0
