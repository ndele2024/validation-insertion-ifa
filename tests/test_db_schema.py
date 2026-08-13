from core.db_schema import _parse_numeric_ranges, check_db_rules
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
