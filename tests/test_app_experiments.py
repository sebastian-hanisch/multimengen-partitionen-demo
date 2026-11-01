"""AppTest-Durchläufe der Experimente, des Permalinks und der Spielwiese (die allgemeinen Rauchtests stehen in test_app.py)."""

import os
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import mmp_constants as C
from mmp_scenario import parse_table

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))


def _app(query: dict | None = None) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    for key, value in (query or {}).items():
        at.query_params[key] = value
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _all_text(at) -> str:
    return " | ".join(e.value for e in list(at.success) + list(at.info) + list(at.warning) + list(at.error))


def _metrics(at) -> dict:
    return {m.label: m.value for m in at.metric}


def test_standard_case_shows_the_known_values_and_no_error():
    at = _app()
    assert not at.error
    assert _metrics(at) == {"Anzahl bei Größe 50": "204.226", "Anzahl bis Größe 50": "1.295.971", "Stellen der Anzahl": "6", "Schritte der Rechnung": "1.275"}
    assert any("Die Größe 50 lässt sich auf 204.226 Weisen aus den Bausteinen bilden (Partitionen)" in e.value for e in at.success)
    assert any("Alle gerechneten Wege geben dieselbe Zahl." == e.value for e in at.success)


def test_experiments_two_to_five_show_their_verdicts_without_a_click():
    text = _all_text(_app())
    assert "Bei n = 1000 müsste Aufzählen 2,40·10³¹ (32 Stellen) Partitionen anfassen, das Produkt braucht 500.500 Schritte, die Fünfeckszahlen-Rekursion 33.475" in text
    assert "Betrag 100: 9,11·10²² (23 Stellen) Folgen, aber nur 541 Multimengen" in text
    assert "Von 199 auf 200 Knoten wächst die Zahl der Bäume ohne Reihenfolge um den Faktor 2,934, mit Reihenfolge um 3,970" in text
    assert "das kürzeste hat 150 Koeffizienten bei 300 Termen" in text and "22 Partitionen von 8 mit größtem Teil höchstens 8" in text


def test_time_measurement_runs_on_click():
    at = _app()
    at.button(key="time_run").click().run(timeout=TIMEOUT)
    assert not at.exception and any("Gemessen auf diesem Rechner (Python)" in i.value for i in at.info)


def test_stueck_4_knapsack_preset_shows_531():
    at = _app()
    at.sidebar.button(key="preset_Rucksack aus Stück 4 (je Gegenstand einmal)").click().run(timeout=TIMEOUT)
    assert not at.exception and not at.error
    assert _metrics(at) == {"Anzahl bei Größe 30": "38", "Anzahl bis Größe 30": "531", "Stellen der Anzahl": "2", "Schritte der Rechnung": "440"}


def test_trees_preset_shows_the_enumeration_row():
    at = _app()
    at.sidebar.button(key="preset_Wurzelbäume ohne Reihenfolge").click().run(timeout=TIMEOUT)
    assert not at.exception and not at.error
    assert _metrics(at)["Anzahl bei Größe 11"] == "1.842"
    assert any("mit Reihenfolge der Kinder wären es 16.796" in e.value for e in at.success)


def test_large_numbers_show_their_digits():
    at = _app({"family": "Partitionen", "n": "1000"})
    assert not at.exception and _metrics(at)["Stellen der Anzahl"] == "32" and _metrics(at)["Schritte der Rechnung"] == "500.500"
    at.sidebar.button(key="preset_Große Zahl: Wurzelbäume mit 500 Knoten").click().run(timeout=TIMEOUT)
    assert not at.exception and _metrics(at)["Stellen der Anzahl"] == "231" and _metrics(at)["Schritte der Rechnung"] == "124.750"


def test_size_is_capped_with_a_note():
    at = _app({"family": "Ebene Partitionen", "n": "900"})
    assert not at.exception and any("höchstens bis N = 150" in i.value for i in at.info)
    assert "Anzahl bei Größe 150" in _metrics(at)


def test_unreadable_table_shows_a_warning_and_uses_the_default():
    at = _app({"family": "Eigene Bausteine", "table": "a,b", "n": "100"})
    assert not at.exception and any("Die Tabelle ist nicht lesbar" in w.value and "„a“ ist keine ganze Zahl" in w.value for w in at.warning)
    assert _metrics(at)["Anzahl bei Größe 100"] == "541"


def test_permalink_loads_and_clamps_the_values():
    at = _app({"family": "Wurzelbäume", "n": "99999", "m": "2", "table": "1,2,3"})
    assert at.sidebar.selectbox(key="family_select").value == "Wurzelbäume" and at.sidebar.slider(key="n_slider").value == C.N_MAX
    assert at.sidebar.selectbox(key="m_select").value == "2" and at.sidebar.text_input(key="table_input").value == "1,2,3"
    assert _metrics(at)["Anzahl bei Größe 500"]


def test_permalink_with_garbage_is_ignored():
    at = _app({"family": "kein Name", "n": "abc", "m": "17", "table": "x" * 100})
    assert at.sidebar.selectbox(key="family_select").value == C.DEFAULT_FAMILY and at.sidebar.slider(key="n_slider").value == C.DEFAULT_N
    assert at.sidebar.selectbox(key="m_select").value == C.DEFAULT_M and len(at.sidebar.text_input(key="table_input").value) == 40


def test_random_table_button_switches_to_own_blocks():
    at = _app()
    at.sidebar.button[-1].click().run(timeout=TIMEOUT)
    assert not at.exception and at.sidebar.selectbox(key="family_select").value == "Eigene Bausteine"
    assert parse_table(at.sidebar.text_input(key="table_input").value)[1] is None


def test_every_family_and_m_combination_renders_without_error():
    for family in C.FAMILIES:
        for m in C.M_CHOICES:
            at = _app({"family": family, "n": "12", "m": m})
            assert not at.error, (family, m, [e.value for e in at.error])


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_renders_without_error_or_checker_message(name):
    at = _app()
    at.sidebar.button(key=f"preset_{name}").click().run(timeout=TIMEOUT)
    assert not at.exception and not at.error, name


def test_playground_changes_with_its_sliders_and_picks_a_partition():
    at = _app()
    at.slider(key="play_n").set_value(10).run(timeout=TIMEOUT)
    at.slider(key="play_k").set_value(4).run(timeout=TIMEOUT)
    assert not at.exception and any(e.value.startswith("23 Partitionen von 10 mit größtem Teil höchstens 4") for e in at.success)
    pick = next(s for s in at.selectbox if s.label == "Partition")
    pick.set_value(pick.options[-1]).run(timeout=TIMEOUT)
    assert not at.exception and not at.error


def test_pdf_can_be_made_for_the_extreme_settings():
    for query in ({"n": "1"}, {"family": "Partitionen", "n": "1000"}, {"family": "Wurzelbäume", "n": "500", "m": "1"}, {"family": "Eigene Bausteine", "n": "1000", "table": "9,9,9,9,9,9,9,9,9,9,9,9"}):
        at = _app(query)
        at.button(key="pdf_make").click().run(timeout=TIMEOUT)
        assert not at.exception, query
