"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, jedes Preset zeigt etwas anderes."""

import mmp_constants as C
import mmp_evaluation as ev
import mmp_presets as P
from mmp_scenario import parse_table


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_regler_bounds():
    for name, preset in C.PRESETS.items():
        assert preset["family"] in C.FAMILIES and preset["m"] in C.M_CHOICES and C.N_MIN <= preset["n"] <= C.N_MAX, name
        assert parse_table(preset["table"])[1] is None and len(preset["table"]) <= P.SETTING_SPECS["table_input"].max_len, name


def test_preset_sizes_are_inside_the_family_caps():
    for name, preset in C.PRESETS.items():
        assert preset["n"] <= C.N_CAP[preset["family"]], name


def test_every_preset_passes_the_checker():
    for name, preset in C.PRESETS.items():
        a = ev.analyse(ev.Settings(**preset))
        assert a.problems == [] and a.table_error is None and a.n_eff == preset["n"], name


def test_first_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS[next(iter(C.PRESETS))]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_presets_show_what_their_help_says():
    stats = {name: ev.analyse(ev.Settings(**p)) for name, p in C.PRESETS.items()}
    assert stats["Ebene Partitionen"].spec[5] == 5 and stats["Wurzelbäume ohne Reihenfolge"].spec is None
    assert stats["Verschiedene Teile (Menge)"].m == 1 and stats["Standardfall: Partitionen von 50"].m is None
    assert stats["Große Zahl: Wurzelbäume mit 500 Knoten"].n_eff == 500 and stats["Münzen 1, 2, 5: Betrag 100"].spec == {1: 1, 2: 1, 5: 1}
    assert len({(a.settings.family, a.series[a.n_eff], a.m) for a in stats.values()}) == len(C.PRESETS)
