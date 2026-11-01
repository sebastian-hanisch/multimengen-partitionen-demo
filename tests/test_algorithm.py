"""Einheitentests des Rechenkerns an von Hand gerechneten Werten (DEMO-PLAYBOOK §1b)."""

import math

import pytest

import mmp_algorithm as A


def test_hand_coins_all_ways(hand_coins):
    spec, n = hand_coins["spec"], hand_coins["n"]
    assert A.series_product(spec, n)[0] == hand_coins["multisets"]
    assert A.series_log(spec, n)[0] == hand_coins["multisets"]
    assert A.series_brute(spec, n) == hand_coins["multisets"]


def test_hand_knapsack_once_and_many(hand_knapsack):
    spec, n = hand_knapsack["spec"], hand_knapsack["n"]
    for fn in (lambda m: A.series_product(spec, n, m)[0], lambda m: A.series_log(spec, n, m)[0], lambda m: A.series_brute(spec, n, m)):
        assert fn(1) == hand_knapsack["once"] and sum(fn(1)) == 6
        assert fn(None) == hand_knapsack["many"] and sum(fn(None)) == 7


def test_partitions_of_5_listed(hand_partitions_of_5):
    assert list(A.partitions(5)) == hand_partitions_of_5
    assert [len(list(A.partitions(n))) for n in range(1, 11)] == [1, 2, 3, 5, 7, 11, 15, 22, 30, 42]


def test_conjugate_by_hand():
    assert A.conjugate((3, 1, 1)) == (3, 1, 1) and A.conjugate((4, 1)) == (2, 1, 1, 1) and A.conjugate((2, 2, 1)) == (3, 2) and A.conjugate(()) == ()


def test_step_counts_by_hand(hand_coins):
    # Münzen 1, 2, 5 bis 5: Faktor 1 hat 5 Schritte, Faktor 2 hat 4, Faktor 5 hat 1; die Rekursion 1 + 2 + 3 + 4 + 5
    assert A.series_product(hand_coins["spec"], 5)[1] == 10 == A.product_steps(hand_coins["spec"], 5)
    assert A.series_log(hand_coins["spec"], 5)[1] == 15
    # mit m = 1 kommen je Kopie die Subtraktionen dazu: Gewicht 2 hat 4 Additionen (Index 2 bis 5) und 2 Subtraktionen (Index 4 und 5), Gewicht 3 hat 3 Additionen und keine Subtraktion
    assert A.series_product({2: 1, 3: 1}, 5, 1)[1] == A.product_steps({2: 1, 3: 1}, 5, 1) == 9


def test_pentagonal_by_hand():
    p, ops = A.partitions_pentagonal(10)
    assert p == [1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42] and ops == A.pentagonal_steps(10) == 29
    assert A.pentagonal_steps(4) == 7                       # n=1:1, n=2:2, n=3:2, n=4:2 Summanden


def test_rooted_trees_by_hand():
    assert A.rooted_trees(7) == [0, 1, 1, 2, 4, 9, 20, 48]
    assert A.rooted_trees(7, 1) == [0, 1, 1, 1, 2, 3, 6, 12]        # alle Geschwister verschieden
    assert [A.plane_trees_count(n) for n in range(1, 8)] == [1, 1, 2, 5, 14, 42, 132]


def test_trees_with_four_nodes_by_hand():
    """Vier Gestalten ohne Reihenfolge (Kette, Stern, Wurzel mit Kind mit zwei Blättern, Wurzel mit Blatt und Kind mit Blatt); die letzte gibt zwei Anordnungen, also fünf mit Reihenfolge."""
    assert A.rooted_trees(4)[4] == A.trees_canonical_count(4) == 4 and A.plane_trees_count(4) == 5
    assert A.trees_canonical_count(4, 1) == 2 == A.rooted_trees(4, 1)[4]       # nur Kette und die gemischte Gestalt haben lauter verschiedene Geschwister


def test_linear_complexity_by_hand():
    assert A.linear_complexity([1, 1, 2, 3, 5, 8, 13, 21]) == 2
    assert A.linear_complexity([1, 2, 4, 8, 16, 32]) == 1
    assert A.linear_complexity([1, 0, 1, 0, 1, 0, 1, 0]) == 2
    assert A.linear_complexity([0, 0, 0]) == 0 and A.linear_complexity([1]) == 1
    assert A.guess_order([1, 1, 2, 3, 5, 8, 13, 21]) == 2 and A.guess_order([1, 1, 2]) is None


def test_digit_count_and_log10():
    assert A.digit_count(0) == 1 and A.digit_count(999) == 3 and A.digit_count(1000) == 4 and A.digit_count(2 ** 60) == 19 and A.digit_count(10 ** 5000) == 5001
    with pytest.raises(ValueError):
        A.digit_count(-1)
    assert A.log10_int(1) == 0 and abs(A.log10_int(1000) - 3) < 1e-12 and abs(A.log10_int(10 ** 500) - 500) < 1e-9 and abs(A.log10_int(2 * 10 ** 400) - (400 + math.log10(2))) < 1e-9
    with pytest.raises(ValueError):
        A.log10_int(0)


def test_invalid_input_is_refused():
    with pytest.raises(ValueError):
        A.series_product({0: 1}, 5)
    with pytest.raises(ValueError):
        A.series_product({1: 0}, 5)
    with pytest.raises(ValueError):
        A.series_log({1: 1}, 5, 0)
    with pytest.raises(ValueError):
        A.series_brute({1: 1}, 5, True)
    with pytest.raises(ValueError):
        A.rooted_trees(5, 0)


def test_log_weights_by_hand():
    # a_1 = 1, a_2 = 1: b_1 = 1, b_2 = 1 + 2 = 3, b_3 = 1, b_4 = 1 + 2 + 0 (Teiler 1, 2) = 3 + ... Teiler von 4: 1, 2 -> 1 + 2 = 3
    assert A.log_weights({1: 1, 2: 1}, 4) == [0, 1, 3, 1, 3]
    # mit m = 1 wird für 2d | k um 2·d·a_d verringert: d = 1: k = 2, 4; d = 2: k = 4
    assert A.log_weights({1: 1, 2: 1}, 4, 1) == [0, 1, 3 - 2, 1, 3 - 2 - 4]
