"""Rechenkern: Multimengen und Mengen aus Bausteinen (Euler-Transformation), Zahlpartitionen, Wurzelbäume ohne Reihenfolge, Raten der Rekursion.

Eine Spezifikation ist ein Wörterbuch `a`: Größe k -> Zahl der verschiedenen Bausteine dieser Größe (k >= 1, Anzahl >= 1). `m` ist die Höchstzahl gleicher Bausteine in einer
Auswahl: `None` heißt beliebig oft (Multimenge), 1 jeder Baustein höchstens einmal (Menge). Die Reihe c_0, c_1, ... zählt die Auswahlen der Gesamtgröße n; c_0 = 1 (die leere Auswahl).
Alles mit ganzen Zahlen (`int`) und `Fraction`; keine Gleitkommazahlen im Zählen."""

import math
from fractions import Fraction
from functools import lru_cache


# ----------------------------------------------------------------------------- Zahlen

def digit_count(x: int) -> int:
    """Zahl der Dezimalstellen einer ganzen Zahl x >= 0, ohne sie in einen String zu wandeln (Python begrenzt die Umwandlung auf 4300 Stellen)."""
    if x < 0:
        raise ValueError("x darf nicht negativ sein")
    d = max(1, int(x.bit_length() * 0.30102999566398))
    while 10 ** d <= x:
        d += 1
    while d > 1 and 10 ** (d - 1) > x:
        d -= 1
    return d


def log10_int(x: int) -> float:
    """Zehnerlogarithmus einer ganzen Zahl x >= 1 (auch weit über der Gleitkommagrenze), auf etwa 15 Stellen genau."""
    if x < 1:
        raise ValueError("x muss mindestens 1 sein")
    d = digit_count(x)
    if d <= 15:
        return math.log10(x)
    shift = d - 15
    return shift + math.log10(x // 10 ** shift)


def validate_spec(a: dict) -> None:
    for k, v in a.items():
        if not (isinstance(k, int) and k >= 1 and isinstance(v, int) and v >= 1):
            raise ValueError(f"Baustein {k!r}: {v!r} ist keine Größe >= 1 mit Anzahl >= 1")


def validate_m(m) -> None:
    if m is not None and (not isinstance(m, int) or isinstance(m, bool) or m < 1):
        raise ValueError("m muss None (beliebig) oder eine ganze Zahl >= 1 sein")


# ----------------------------------------------------------------------------- Hauptweg: Produkt

def product_steps(a: dict, n_max: int, m=None) -> int:
    """Zahl der Additionen und Subtraktionen des Produkts, ohne zu rechnen (Summe über alle Kopien)."""
    steps = 0
    for k, copies in a.items():
        if k > n_max:
            continue
        per = n_max - k + 1
        if m is not None:
            per += max(0, n_max - (m + 1) * k + 1)
        steps += copies * per
    return steps


def series_product(a: dict, n_max: int, m=None):
    """Koeffizienten c_0..c_n_max des Produkts über alle Kopien von 1/(1 − zᵏ) (m = None) beziehungsweise 1 + zᵏ + … + z^(mk); dazu die Zahl der Additionen."""
    validate_spec(a)
    validate_m(m)
    c = [0] * (n_max + 1)
    c[0] = 1
    ops = 0
    for k in sorted(a):
        if k > n_max:
            continue
        for _ in range(a[k]):
            if m is not None:
                step = (m + 1) * k
                for n in range(n_max, step - 1, -1):
                    c[n] -= c[n - step]
                    ops += 1
            for n in range(k, n_max + 1):
                c[n] += c[n - k]
                ops += 1
    return c, ops


# ----------------------------------------------------------------------------- Zweiter Weg: logarithmische Ableitung

def log_weights(a: dict, n_max: int, m=None) -> list[int]:
    """b_k = Summe über d | k von d·a_d, abzüglich (m+1)·d·a_d für (m+1)·d | k (nur bei endlichem m); n·c_n = Summe b_k·c_(n−k)."""
    b = [0] * (n_max + 1)
    for d, copies in a.items():
        if d > n_max:
            continue
        for k in range(d, n_max + 1, d):
            b[k] += d * copies
        if m is not None:
            for k in range((m + 1) * d, n_max + 1, (m + 1) * d):
                b[k] -= (m + 1) * d * copies
    return b


def series_log(a: dict, n_max: int, m=None):
    """Dieselben Koeffizienten über die Rekursion n·c_n = b_1·c_(n−1) + … + b_n·c_0 (logarithmische Ableitung des Produkts); dazu die Zahl der Multiplikationen (n(n+1)/2)."""
    validate_spec(a)
    validate_m(m)
    b = log_weights(a, n_max, m)
    c = [0] * (n_max + 1)
    c[0] = 1
    ops = 0
    for n in range(1, n_max + 1):
        s = sum(b[k] * c[n - k] for k in range(1, n + 1))
        ops += n
        if s % n:
            raise ArithmeticError(f"n·c_n ist nicht durch n teilbar bei n = {n}")
        c[n] = s // n
    return c, ops


# ----------------------------------------------------------------------------- Aufzählen

def series_brute(a: dict, n_max: int, m=None) -> list[int]:
    """Zählt alle Auswahlen durch Aufzählen (je Baustein eine Vielfachheit 0..m), geordnet nach Gesamtgröße."""
    validate_spec(a)
    validate_m(m)
    items = [k for k in sorted(a) for _ in range(a[k]) if k <= n_max]
    res = [0] * (n_max + 1)

    def rec(i, total):
        if i == len(items):
            res[total] += 1
            return
        k = items[i]
        mult = 0
        while total + mult * k <= n_max and (m is None or mult <= m):
            rec(i + 1, total + mult * k)
            mult += 1

    rec(0, 0)
    return res


def partitions(n: int, maxpart: int | None = None):
    """Alle Zahlpartitionen von n als absteigende Tupel."""
    if maxpart is None:
        maxpart = n
    if n == 0:
        yield ()
        return
    for k in range(min(n, maxpart), 0, -1):
        for rest in partitions(n - k, k):
            yield (k,) + rest


def conjugate(parts: tuple) -> tuple:
    """Konjugierte Partition (Ferrers-Diagramm an der Diagonalen gespiegelt)."""
    return tuple(sum(1 for p in parts if p > j) for j in range(parts[0])) if parts else ()


# ----------------------------------------------------------------------------- Fünfeckszahlen (nur Partitionszahl)

def partitions_pentagonal(n_max: int):
    """p(0)..p(n_max) über p(n) = Summe (−1)^(j+1)·[p(n − j(3j−1)/2) + p(n − j(3j+1)/2)] (Eulers Fünfeckszahlensatz); dazu die Zahl der Additionen."""
    p = [0] * (n_max + 1)
    p[0] = 1
    ops = 0
    for n in range(1, n_max + 1):
        s = 0
        j = 1
        while j * (3 * j - 1) // 2 <= n:
            sign = 1 if j % 2 else -1
            s += sign * p[n - j * (3 * j - 1) // 2]
            ops += 1
            g2 = j * (3 * j + 1) // 2
            if g2 <= n:
                s += sign * p[n - g2]
                ops += 1
            j += 1
        p[n] = s
    return p, ops


def pentagonal_steps(n_max: int) -> int:
    """Additionen der Fünfeckszahlen-Rekursion bis n_max, ohne zu rechnen."""
    steps = 0
    for n in range(1, n_max + 1):
        j = 1
        while j * (3 * j - 1) // 2 <= n:
            steps += 1 + (1 if j * (3 * j + 1) // 2 <= n else 0)
            j += 1
    return steps


# ----------------------------------------------------------------------------- Wurzelbäume ohne Reihenfolge

def rooted_trees(n_max: int, m=None) -> list[int]:
    """t[0] = 0, t[n] = Zahl der Wurzelbäume mit n Knoten, deren Kinder ohne Reihenfolge stehen (höchstens m gleiche Geschwister, m = None: beliebig).
    Gleichung T = z·MSET(T): Mit c = Reihe der Auswahlen aus Bäumen gilt t[n+1] = c[n], c wächst mit jedem fertigen t[k]."""
    validate_m(m)
    t = [0, 1] if n_max >= 1 else [0]
    c = [1]
    for size in range(1, n_max):
        b = [0] * (size + 1)
        for d in range(1, size + 1):
            if t[d]:
                for k in range(d, size + 1, d):
                    b[k] += d * t[d]
                if m is not None:
                    for k in range((m + 1) * d, size + 1, (m + 1) * d):
                        b[k] -= (m + 1) * d * t[d]
        s = sum(b[k] * c[size - k] for k in range(1, size + 1))
        if s % size:
            raise ArithmeticError(f"Division geht nicht auf bei {size}")
        c.append(s // size)
        t.append(c[size])
    return t


def catalan(n: int) -> int:
    return math.comb(2 * n, n) // (n + 1)


def plane_trees_count(n: int) -> int:
    """Wurzelbäume mit n Knoten MIT Reihenfolge der Kinder (Stück 3): Catalan(n − 1)."""
    return catalan(n - 1)


@lru_cache(maxsize=None)
def _forests(total: int):
    """Alle Wälder (geordnete Folgen von Bäumen mit Reihenfolge) der Gesamtgröße total; ein Baum ist das Tupel seiner Kinder."""
    if total == 0:
        return [()]
    out = []
    for s in range(1, total + 1):
        for tree in _forests(s - 1):
            for rest in _forests(total - s):
                out.append((tree,) + rest)
    return out


def _plane_trees(n: int):
    return _forests(n - 1)


def _canon(tree):
    return tuple(sorted(_canon(child) for child in tree))


def _max_equal_siblings(tree) -> int:
    best = 0
    counts: dict = {}
    for child in tree:
        counts[child] = counts.get(child, 0) + 1
        best = max(best, _max_equal_siblings(child))
    return max(best, max(counts.values(), default=0))


def trees_canonical_count(n: int, m=None) -> int:
    """Zahl der Wurzelbäume ohne Reihenfolge durch Aufzählen: alle Bäume mit Reihenfolge erzeugen, die Kinder sortieren und gleiche Formen zusammenfassen."""
    forms = {_canon(t) for t in _plane_trees(n)}
    if m is not None:
        forms = {f for f in forms if _max_equal_siblings(f) <= m}
    return len(forms)


# ----------------------------------------------------------------------------- Raten einer Rekursion mit festen Koeffizienten (wie Stück 1)

def linear_complexity(seq) -> int:
    """Kleinste Ordnung L, für die s_n = Summe_{i=1..L} r_i·s_(n−i) mit festen Koeffizienten r_i für alle n >= L gilt (Berlekamp–Massey über Brüchen)."""
    s = [Fraction(x) for x in seq]
    c = [Fraction(1)]
    b = [Fraction(1)]
    length, gap, bd = 0, 1, Fraction(1)
    for n in range(len(s)):
        d = s[n] + sum(c[i] * s[n - i] for i in range(1, length + 1))
        if d == 0:
            gap += 1
            continue
        coef = d / bd
        t = c[:]
        need = len(b) + gap
        if len(c) < need:
            c = c + [Fraction(0)] * (need - len(c))
        for i, bi in enumerate(b):
            c[i + gap] -= coef * bi
        if 2 * length <= n:
            length = n + 1 - length
            b, bd, gap = t, d, 1
        else:
            gap += 1
    return length


def guess_order(seq, margin: int = 2):
    """Ordnung der Rekursion, wenn sie sich zeigt (Ordnung + Sicherheitsabstand passt in die Folge), sonst None."""
    length = linear_complexity(seq)
    return length if 2 * length + margin <= len(seq) else None
