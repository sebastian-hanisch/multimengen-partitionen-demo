"""Gemeinsame Fixtures: die Mini-Instanzen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def hand_coins():
    """Münzen 1, 2, 5, Beträge 0 bis 5. Handrechnung der Multimengen: 0: leer; 1: {1}; 2: {2}, {1,1}; 3: {2,1}, {1,1,1}; 4: {2,2}, {2,1,1}, {1,1,1,1}; 5: {5}, {2,2,1}, {2,1,1,1}, {1×5} = 1, 1, 2, 2, 3, 4.
    Als Folgen (Reihenfolge zählt) nach c_n = c_(n−1) + c_(n−2) + c_(n−5): 1, 1, 2, 3, 5, 9."""
    return {"spec": {1: 1, 2: 1, 5: 1}, "n": 5, "multisets": [1, 1, 2, 2, 3, 4], "sequences": [1, 1, 2, 3, 5, 9]}


@pytest.fixture
def hand_knapsack():
    """Gewichte 2, 3, 4, 5, Kapazität 5 (der Handfall aus Stück 4). Jeder Gegenstand höchstens einmal: Gewicht 0: leer; 2: {2}; 3: {3}; 4: {4}; 5: {5}, {2,3} = 1, 0, 1, 1, 1, 2 (Summe 6, wie dort).
    Beliebig oft kommt {2,2} (Gewicht 4) dazu: 1, 0, 1, 1, 2, 2 (Summe 7)."""
    return {"spec": {2: 1, 3: 1, 4: 1, 5: 1}, "n": 5, "once": [1, 0, 1, 1, 1, 2], "many": [1, 0, 1, 1, 2, 2]}


@pytest.fixture
def hand_partitions_of_5():
    """Die sieben Partitionen von 5, von Hand: 5, 4+1, 3+2, 3+1+1, 2+2+1, 2+1+1+1, 1+1+1+1+1."""
    return [(5,), (4, 1), (3, 2), (3, 1, 1), (2, 2, 1), (2, 1, 1, 1), (1, 1, 1, 1, 1)]
