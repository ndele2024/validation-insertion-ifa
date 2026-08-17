import json

import pytest

import config
from core import db_schema
from core.db_schema import _parse_numeric_ranges, check_db_rules, column_label
from core.models import LayerSchema, Severity


# --------------------------------------------------------------------- _parse_numeric_ranges
def test_parse_between_clause():
    ranges = _parse_numeric_ranges('CHECK ((pme_profd_m BETWEEN 0 AND 100))')
    assert ranges == {"pme_profd_m": (0.0, 100.0)}


def test_parse_gte_only():
    ranges = _parse_numeric_ranges('CHECK ((des_nb_captu >= 0))')
    assert ranges == {"des_nb_captu": (0.0, None)}


def test_parse_lte_only():
    ranges = _parse_numeric_ranges('CHECK ((dha_pourc_granu_domin <= 100))')
    assert ranges == {"dha_pourc_granu_domin": (None, 100.0)}


def test_parse_gte_and_lte_combined():
    ranges = _parse_numeric_ranges('CHECK ((dha_pourc_granu_domin >= 0) AND (dha_pourc_granu_domin <= 100))')
    assert ranges == {"dha_pourc_granu_domin": (0.0, 100.0)}


def test_parse_unrecognized_clause_returns_empty():
    assert _parse_numeric_ranges('CHECK ((col = ANY (ARRAY[1, 2])))') == {}


# --------------------------------------------------------------------- check_db_rules
def test_not_null_violation_reported():
    schema = LayerSchema(table="detail_speci", primary_key=["dsp_no_speci"], not_null_columns=["efa_code"])
    rows = [{"dsp_no_speci": 1, "efa_code": None}]
    issues = check_db_rules("detail_speci", rows, schema)
    assert len(issues) == 1
    assert issues[0].code == "DB_NOT_NULL"
    assert issues[0].severity == Severity.ERROR
    assert issues[0].record == {"dsp_no_speci": 1}


def test_not_null_satisfied_no_issue():
    schema = LayerSchema(table="detail_speci", not_null_columns=["efa_code"])
    rows = [{"efa_code": "SACA"}]
    assert check_db_rules("detail_speci", rows, schema) == []


def test_range_violation_below_min():
    schema = LayerSchema(table="denom_espec", numeric_ranges={"des_nb_captu": (0.0, None)})
    rows = [{"des_nb_captu": -1}]
    issues = check_db_rules("denom_espec", rows, schema)
    assert len(issues) == 1 and issues[0].code == "DB_RANGE_MIN"


def test_range_violation_above_max():
    schema = LayerSchema(table="x", numeric_ranges={"col": (0.0, 100.0)})
    rows = [{"col": 150}]
    issues = check_db_rules("x", rows, schema)
    assert len(issues) == 1 and issues[0].code == "DB_RANGE_MAX"


def test_range_within_bounds_no_issue():
    schema = LayerSchema(table="x", numeric_ranges={"col": (0.0, 100.0)})
    rows = [{"col": 50}]
    assert check_db_rules("x", rows, schema) == []


def test_range_ignores_non_numeric_gracefully():
    schema = LayerSchema(table="x", numeric_ranges={"col": (0.0, 100.0)})
    rows = [{"col": "non-numérique"}]
    assert check_db_rules("x", rows, schema) == []


def test_enum_invalid_value_reported():
    schema = LayerSchema(table="detail_speci", enum_values={"sex_code": {"M", "F", "I"}})
    rows = [{"sex_code": "XYZ"}]
    issues = check_db_rules("detail_speci", rows, schema)
    assert len(issues) == 1 and issues[0].code == "DB_ENUM_INVALID"


def test_enum_valid_value_no_issue():
    schema = LayerSchema(table="detail_speci", enum_values={"sex_code": {"M", "F", "I"}})
    rows = [{"sex_code": "M"}]
    assert check_db_rules("detail_speci", rows, schema) == []


def test_enum_none_value_skipped():
    schema = LayerSchema(table="detail_speci", enum_values={"sex_code": {"M", "F"}})
    rows = [{"sex_code": None}]
    assert check_db_rules("detail_speci", rows, schema) == []


# --------------------------------------------------------------------- column_label / alias
@pytest.fixture
def alias_json(tmp_path, monkeypatch):
    """Table d'alias synthétique, pour ne pas dépendre du contenu exact du
    classeur de référence (qui peut être régénéré) dans les assertions."""
    chemin = tmp_path / "aliases.json"
    chemin.write_text(json.dumps({
        "tables": {
            "detail_speci": {"efa_code": "Espèce", "dsp_val_masse_g": "Masse (g)"},
            "peche_exper": {"efa_code": "Espèce visée"},
        }
    }, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(config, "COLUMN_ALIASES_PATH", str(chemin))
    db_schema._load_column_aliases.cache_clear()
    yield chemin
    db_schema._load_column_aliases.cache_clear()


def test_column_label_retourne_alias(alias_json):
    assert column_label("detail_speci", "efa_code") == "Espèce"


def test_column_label_depend_de_la_table(alias_json):
    """Une même colonne porte un libellé différent selon la table : c'est
    pourquoi la table d'alias est indexée par (table, colonne)."""
    assert column_label("detail_speci", "efa_code") == "Espèce"
    assert column_label("peche_exper", "efa_code") == "Espèce visée"


def test_column_label_insensible_a_la_casse(alias_json):
    assert column_label("DETAIL_SPECI", "EFA_CODE") == "Espèce"


def test_column_label_repli_sur_nom_colonne(alias_json):
    assert column_label("detail_speci", "colonne_inconnue") == "colonne_inconnue"
    assert column_label("table_inconnue", "efa_code") == "efa_code"


def test_column_label_fichier_absent_ne_leve_pas(tmp_path, monkeypatch):
    """Une table d'alias manquante ne doit jamais empêcher une validation :
    on retombe simplement sur les noms techniques."""
    monkeypatch.setattr(config, "COLUMN_ALIASES_PATH", str(tmp_path / "absent.json"))
    db_schema._load_column_aliases.cache_clear()
    try:
        assert column_label("detail_speci", "efa_code") == "efa_code"
    finally:
        db_schema._load_column_aliases.cache_clear()


def test_column_label_fichier_invalide_ne_leve_pas(tmp_path, monkeypatch):
    chemin = tmp_path / "invalide.json"
    chemin.write_text("{ ceci n'est pas du JSON", encoding="utf-8")
    monkeypatch.setattr(config, "COLUMN_ALIASES_PATH", str(chemin))
    db_schema._load_column_aliases.cache_clear()
    try:
        assert column_label("detail_speci", "efa_code") == "efa_code"
    finally:
        db_schema._load_column_aliases.cache_clear()


# --------------------------------------------------------------------- alias dans les messages
def test_message_not_null_utilise_alias(alias_json):
    schema = LayerSchema(table="detail_speci", not_null_columns=["efa_code"])
    issues = check_db_rules("detail_speci", [{"efa_code": None}], schema)
    assert "« Espèce »" in issues[0].message
    assert "efa_code" not in issues[0].message


def test_message_range_utilise_alias(alias_json):
    schema = LayerSchema(table="detail_speci", numeric_ranges={"dsp_val_masse_g": (0.0, 100.0)})
    issues = check_db_rules("detail_speci", [{"dsp_val_masse_g": 500}], schema)
    assert "« Masse (g) »" in issues[0].message


def test_message_enum_utilise_alias(alias_json):
    schema = LayerSchema(table="detail_speci", enum_values={"efa_code": {"SACA"}})
    issues = check_db_rules("detail_speci", [{"efa_code": "XYZ"}], schema)
    assert "« Espèce »" in issues[0].message


def test_fields_conserve_le_nom_technique(alias_json):
    """`fields` est lu par l'interface QField/QGIS pour mettre le bon champ
    en évidence : il doit rester le nom technique, seul le message change."""
    schema = LayerSchema(table="detail_speci", not_null_columns=["efa_code"])
    issues = check_db_rules("detail_speci", [{"efa_code": None}], schema)
    assert issues[0].fields == ["efa_code"]


def test_message_repli_sur_nom_colonne_si_alias_absent(alias_json):
    schema = LayerSchema(table="detail_speci", not_null_columns=["col_sans_alias"])
    issues = check_db_rules("detail_speci", [{"col_sans_alias": None}], schema)
    assert "« col_sans_alias »" in issues[0].message
