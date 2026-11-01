"""Eigenschaften (ORACLE-PLAYBOOK §5): Aussagen, die für jede Spezifikation gelten, auf festen Zufallsständen."""

import os
import random
import subprocess
import sys
from pathlib import Path

import pytest

import mmp_algorithm as A
import mmp_scenario as S

ROOT = Path(__file__).resolve().parent.parent


def _spec(seed, k_max=8, with_one=False):
    rng = random.Random(seed)
    spec = {k: rng.choice([1, 1, 2, 3]) for k in range(1, k_max + 1) if rng.random() < 0.6}
    if with_one:
        spec[1] = spec.get(1, 0) or 1
    return spec or {2: 1}


def _sequences(spec, n):
    """Folgen mit Reihenfolge aus typisierten Bausteinen: c_n = Summe a_k·c_(n−k)."""
    c = [1] + [0] * n
    for i in range(1, n + 1):
        c[i] = sum(v * c[i - k] for k, v in spec.items() if i >= k)
    return c


@pytest.mark.parametrize("seed", range(40))
def test_coefficients_do_not_fall_when_a_size_one_block_exists(seed):
    c = A.series_product(_spec(seed, with_one=True), 40)[0]
    assert all(c[i] <= c[i + 1] for i in range(40))


@pytest.mark.parametrize("seed", range(40))
def test_set_at_most_multiset_at_most_sequences(seed):
    spec = _spec(seed)
    n = 25
    once, twice, many = (A.series_product(spec, n, m)[0] for m in (1, 2, None))
    seq = _sequences(spec, n)
    assert all(a <= b <= c <= d for a, b, c, d in zip(once, twice, many, seq))


@pytest.mark.parametrize("seed", range(40))
def test_adding_a_block_does_not_lower_any_coefficient(seed):
    spec = _spec(seed)
    bigger = dict(spec)
    k = random.Random(seed).randint(1, 8)
    bigger[k] = bigger.get(k, 0) + 1
    a, b = A.series_product(spec, 30)[0], A.series_product(bigger, 30)[0]
    assert all(x <= y for x, y in zip(a, b))


@pytest.mark.parametrize("seed", range(40))
def test_scaling_all_sizes_scales_the_index(seed):
    spec = _spec(seed)
    c = random.Random(seed).randint(2, 5)
    scaled = {k * c: v for k, v in spec.items()}
    base = A.series_product(spec, 12)[0]
    big = A.series_product(scaled, 12 * c)[0]
    assert all(big[i * c] == base[i] for i in range(13)) and all(big[i] == 0 for i in range(12 * c + 1) if i % c)


@pytest.mark.parametrize("seed", range(40))
def test_order_of_blocks_does_not_matter(seed):
    spec = _spec(seed)
    items = list(spec.items())
    random.Random(seed).shuffle(items)
    assert A.series_product(dict(items), 25)[0] == A.series_product(spec, 25)[0] == A.series_log(dict(reversed(items)), 25)[0]


@pytest.mark.parametrize("seed", range(40))
def test_more_copies_allowed_never_lower_a_coefficient(seed):
    spec = _spec(seed)
    series = [A.series_product(spec, 25, m)[0] for m in (1, 2, 3, 4, None)]
    for lo, hi in zip(series, series[1:]):
        assert all(x <= y for x, y in zip(lo, hi))


@pytest.mark.parametrize("seed", range(20))
def test_recursion_divides_exactly(seed):
    """n·c_n = Summe b_k c_(n−k) geht für jede Spezifikation ohne Rest auf (series_log wirft sonst)."""
    A.series_log(_spec(seed), 60)
    A.series_log(_spec(seed), 60, 1)


@pytest.mark.parametrize("n", range(1, 40))
def test_partitions_with_parts_at_most_k_equal_partitions_into_at_most_k_parts_by_the_product(n):
    """Spiegeln: Teile bis k = höchstens k Teile; die Reihe für k ≥ n ist die der Partitionen."""
    full = A.partitions_pentagonal(n)[0][n]
    assert A.series_product({j: 1 for j in range(1, n + 1)}, n)[0][n] == full
    assert A.series_product({j: 1 for j in range(1, n + 2)}, n)[0][n] == full


@pytest.mark.parametrize("n", range(1, 30))
def test_trees_without_order_never_exceed_trees_with_order(n):
    assert A.rooted_trees(n)[n] <= A.plane_trees_count(n)
    assert all(A.rooted_trees(n, m)[n] <= A.rooted_trees(n)[n] for m in (1, 2, 3))


def test_bounded_trees_grow_with_m():
    t = [A.rooted_trees(30, m) for m in (1, 2, 3, None)]
    for lo, hi in zip(t, t[1:]):
        assert all(x <= y for x, y in zip(lo, hi))


def test_table_parsing_round_trip():
    for seed in range(30):
        text = S.random_table(seed)
        values, error = S.parse_table(text)
        assert error is None and S.table_text(values) == text and any(values)


def test_random_table_does_not_depend_on_the_hash_seed():
    code = "import sys; sys.path.insert(0, %r); import mmp_scenario as S; print(S.random_table(7), S.random_table(8))" % str(ROOT)
    runs = {subprocess.run([sys.executable, "-X", "utf8", "-c", code], capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONHASHSEED": str(h)}).stdout for h in (0, 1, 12345)}
    assert len(runs) == 1 and runs.pop().strip()
