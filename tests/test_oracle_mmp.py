"""Orakel-Tests: Produkt, Rekursion und Fünfeckszahlen gegen unabhängige Rechenwege (DEMO-PLAYBOOK §12, ORACLE-PLAYBOOK §5).

Unabhängig heißt: Aufzählen aller Auswahlen, eine eigene Partitionsrekursion (Partitionen in genau k Teile), kanonische Formen der Bäume mit Reihenfolge, Aufzählen ebener Partitionen
(Zeilenfolgen), ein zweites Raten der Rekursion über ein Gleichungssystem mit Brüchen und die festgeschriebenen Zahlen aus Stück 4. Feste Zufallsstände."""

import random
from fractions import Fraction
from functools import lru_cache

import pytest

import mmp_algorithm as A


def _random_spec(seed):
    rng = random.Random(seed)
    k_max = rng.randint(2, 7)
    spec = {k: rng.choice([1, 1, 2, 3]) for k in range(1, k_max + 1) if rng.random() < 0.7}
    return spec or {1: 1}


@pytest.mark.parametrize("seed", range(80))
def test_product_equals_recursion_equals_enumeration(seed):
    spec = _random_spec(seed)
    n = 9
    prod = A.series_product(spec, n)[0]
    assert prod == A.series_log(spec, n)[0] == A.series_brute(spec, n)


@pytest.mark.parametrize("seed", range(60))
@pytest.mark.parametrize("m", [1, 2, 3])
def test_bounded_multiplicity_product_equals_recursion_equals_enumeration(seed, m):
    spec = _random_spec(1000 + seed)
    n = 9
    assert A.series_product(spec, n, m)[0] == A.series_log(spec, n, m)[0] == A.series_brute(spec, n, m)


def _partitions_into_exactly_k(n_max):
    """Eigene Rekursion: P(n, k) = P(n − 1, k − 1) + P(n − k, k) (Partitionen von n in genau k Teile), ohne erzeugende Funktion."""
    @lru_cache(maxsize=None)
    def pk(n, k):
        if n == 0 and k == 0:
            return 1
        if n <= 0 or k <= 0:
            return 0
        return pk(n - 1, k - 1) + pk(n - k, k)

    return [sum(pk(n, k) for k in range(0, n + 1)) for n in range(n_max + 1)]


def test_partition_numbers_equal_the_k_part_recursion():
    ref = _partitions_into_exactly_k(120)
    assert A.series_product({k: 1 for k in range(1, 121)}, 120)[0] == ref
    assert A.partitions_pentagonal(120)[0] == ref


def test_partition_numbers_equal_enumeration():
    ref = [sum(1 for _ in A.partitions(n)) for n in range(0, 36)]
    assert A.partitions_pentagonal(35)[0] == ref


def test_distinct_parts_equal_odd_parts_and_enumeration():
    n = 80
    odd = A.series_product({k: 1 for k in range(1, n + 1, 2)}, n)[0]
    assert odd == A.series_product({k: 1 for k in range(1, n + 1)}, n, 1)[0]
    enum = [sum(1 for p in A.partitions(x) if len(set(p)) == len(p)) for x in range(0, 31)]
    assert A.series_product({k: 1 for k in range(1, 31)}, 30, 1)[0] == enum


def test_largest_part_k_equals_number_of_parts_k_by_enumeration():
    for n in range(1, 26):
        by_largest, by_count = {}, {}
        for p in A.partitions(n):
            by_largest[p[0]] = by_largest.get(p[0], 0) + 1
            by_count[len(p)] = by_count.get(len(p), 0) + 1
        assert by_largest == by_count
        assert all(A.conjugate(A.conjugate(p)) == p for p in A.partitions(n))


@pytest.mark.parametrize("n", range(1, 11))
def test_rooted_trees_equal_canonical_forms(n):
    assert A.rooted_trees(n)[n] == A.trees_canonical_count(n)


@pytest.mark.parametrize("m", [1, 2, 3])
@pytest.mark.parametrize("n", range(1, 10))
def test_bounded_rooted_trees_equal_canonical_forms(n, m):
    assert A.rooted_trees(n, m)[n] == A.trees_canonical_count(n, m)


def _plane_partition_count(n):
    """Ebene Partitionen von n als Folge nicht aufsteigender Zeilen, jede Zeile eine Partition, die in der vorherigen liegt (elementweise kleiner oder gleich)."""
    @lru_cache(maxsize=None)
    def rows(remaining, prev):
        out = []

        def rec(i, left, cur, last):
            if cur:
                out.append(tuple(cur))
            if prev is not None and i >= len(prev):
                return
            hi = min(last, left, prev[i] if prev is not None else left)
            for v in range(hi, 0, -1):
                cur.append(v)
                rec(i + 1, left - v, cur, v)
                cur.pop()

        rec(0, remaining, [], remaining)
        return out

    @lru_cache(maxsize=None)
    def count(remaining, prev):
        if remaining == 0:
            return 1
        return sum(count(remaining - sum(r), r) for r in rows(remaining, prev))

    return count(n, None)


def test_plane_partitions_equal_enumeration():
    ref = [_plane_partition_count(n) for n in range(0, 11)]
    assert ref[:7] == [1, 1, 3, 6, 13, 24, 48]
    assert A.series_product({k: k for k in range(1, 11)}, 10)[0] == ref == A.series_log({k: k for k in range(1, 11)}, 10)[0]


def test_numbers_from_stueck_4_are_reproduced():
    """Festgeschriebene Zahlen aus Stück 4: Münzwechsel 4, 10, 18, 29 (Multimengen) und 9, 128, 1.843, 26.547 (Folgen), 531 Teilmengen im Standardfall."""
    coins = A.series_product({1: 1, 2: 1, 5: 1}, 20)[0]
    assert [coins[n] for n in (5, 10, 15, 20)] == [4, 10, 18, 29]
    seq = [1] + [0] * 20
    for n in range(1, 21):
        seq[n] = sum(seq[n - c] for c in (1, 2, 5) if n >= c)
    assert [seq[n] for n in (5, 10, 15, 20)] == [9, 128, 1843, 26547]
    weights = [2, 2, 3, 5, 5, 6, 9, 9, 9, 10]
    spec = {}
    for w in weights:
        spec[w] = spec.get(w, 0) + 1
    assert sum(A.series_product(spec, 30, 1)[0]) == 531


def _guess_by_solving(seq, d_max):
    """Zweites Raten: kleinste Ordnung d, für die das Gleichungssystem aus den Zeilen n = d..2d−1 lösbar ist und die Lösung die ganze Folge trifft."""
    for d in range(1, d_max + 1):
        if 2 * d + 2 > len(seq):
            return None
        m = [[Fraction(seq[n - j]) for j in range(1, d + 1)] + [Fraction(seq[n])] for n in range(d, 2 * d)]
        ok = True
        for col in range(d):
            piv = next((r for r in range(col, d) if m[r][col] != 0), None)
            if piv is None:
                ok = False
                break
            m[col], m[piv] = m[piv], m[col]
            inv = 1 / m[col][col]
            m[col] = [x * inv for x in m[col]]
            for r in range(d):
                if r != col and m[r][col] != 0:
                    f = m[r][col]
                    m[r] = [x - f * y for x, y in zip(m[r], m[col])]
        if not ok:
            continue
        sol = [m[i][d] for i in range(d)]
        if all(sum(sol[j - 1] * seq[n - j] for j in range(1, d + 1)) == seq[n] for n in range(d, len(seq))):
            return d
    return None


@pytest.mark.parametrize("k", range(1, 7))
def test_guessed_order_of_parts_up_to_k_equals_the_second_guess_and_the_denominator_degree(k):
    seq = A.series_product({j: 1 for j in range(1, k + 1)}, 200)[0]
    assert A.guess_order(seq) == _guess_by_solving(seq, 30) == k * (k + 1) // 2


def test_partition_numbers_have_no_short_recurrence():
    p = A.partitions_pentagonal(119)[0]
    assert A.guess_order(p) is None and _guess_by_solving(p, 40) is None
