from core.models import Severity
from rules.common import (
    at_least_one_of,
    cross_field_lte,
    date_within_bounds,
    default_if_empty,
    forbidden_values,
    lookup_assign,
    required_field,
)


# --------------------------------------------------------------------- required_field
def test_required_field_blank_triggers_error(make_context):
    rule = required_field("dsp_no_speci", "Numéro de spécimen", code="X")
    ctx = make_context("detail_speci", {"dsp_no_speci": None})
    issues = rule(ctx)
    assert len(issues) == 1
    assert issues[0].severity == Severity.ERROR
    assert issues[0].fields == ["dsp_no_speci"]


def test_required_field_filled_no_error(make_context):
    rule = required_field("dsp_no_speci", "Numéro de spécimen", code="X")
    ctx = make_context("detail_speci", {"dsp_no_speci": 1})
    assert rule(ctx) == []


def test_required_field_blank_string_triggers_error(make_context):
    rule = required_field("dsp_com", "Commentaire", code="X")
    ctx = make_context("detail_speci", {"dsp_com": "   "})
    assert len(rule(ctx)) == 1


def test_required_field_conditional_when_false_skips(make_context):
    rule = required_field("app_code", "Appareil", code="X", when=lambda ctx: False)
    ctx = make_context("analy_physi_chimi", {"app_code": None})
    assert rule(ctx) == []


def test_required_field_conditional_when_true_applies(make_context):
    rule = required_field("app_code", "Appareil", code="X", when=lambda ctx: True)
    ctx = make_context("analy_physi_chimi", {"app_code": None})
    assert len(rule(ctx)) == 1


# --------------------------------------------------------------------- at_least_one_of
def test_at_least_one_of_all_blank_triggers_error(make_context):
    rule = at_least_one_of(["dsp_long_tot_max_m", "dsp_long_fourc_mm"], "Longueurs", code="X")
    ctx = make_context("detail_speci", {"dsp_long_tot_max_m": None, "dsp_long_fourc_mm": None})
    assert len(rule(ctx)) == 1


def test_at_least_one_of_one_filled_no_error(make_context):
    rule = at_least_one_of(["dsp_long_tot_max_m", "dsp_long_fourc_mm"], "Longueurs", code="X")
    ctx = make_context("detail_speci", {"dsp_long_tot_max_m": 300, "dsp_long_fourc_mm": None})
    assert rule(ctx) == []


# --------------------------------------------------------------------- forbidden_values
def test_forbidden_values_match_triggers_error(make_context):
    rule = forbidden_values("efa_code", "Espèce", {"RIEN", "AU"}, code="X")
    ctx = make_context("detail_speci", {"efa_code": "RIEN"})
    assert len(rule(ctx)) == 1


def test_forbidden_values_no_match_no_error(make_context):
    rule = forbidden_values("efa_code", "Espèce", {"RIEN", "AU"}, code="X")
    ctx = make_context("detail_speci", {"efa_code": "SACA"})
    assert rule(ctx) == []


# --------------------------------------------------------------------- cross_field_lte
def test_cross_field_lte_violation(make_context):
    rule = cross_field_lte("a", "b", "msg", code="X")
    ctx = make_context("t", {"a": 10, "b": 5})
    assert len(rule(ctx)) == 1


def test_cross_field_lte_equal_allowed_by_default(make_context):
    rule = cross_field_lte("a", "b", "msg", code="X")
    ctx = make_context("t", {"a": 5, "b": 5})
    assert rule(ctx) == []


def test_cross_field_lte_strict_rejects_equal(make_context):
    rule = cross_field_lte("a", "b", "msg", code="X", strict=True)
    ctx = make_context("t", {"a": 5, "b": 5})
    assert len(rule(ctx)) == 1


def test_cross_field_lte_ignored_when_blank(make_context):
    rule = cross_field_lte("a", "b", "msg", code="X")
    ctx = make_context("t", {"a": None, "b": 5})
    assert rule(ctx) == []


# --------------------------------------------------------------------- default_if_empty
def test_default_if_empty_assigns_when_blank(make_context):
    rule = default_if_empty("phc_date", default_fn=lambda ctx: "2024-06-01")
    row = {"phc_date": None}
    ctx = make_context("analy_physi_chimi", row)
    rule(ctx)
    assert row["phc_date"] == "2024-06-01"


def test_default_if_empty_does_not_overwrite_existing(make_context):
    rule = default_if_empty("phc_date", default_fn=lambda ctx: "2024-06-01")
    row = {"phc_date": "2024-01-01"}
    ctx = make_context("analy_physi_chimi", row)
    rule(ctx)
    assert row["phc_date"] == "2024-01-01"


def test_default_if_empty_calls_also_check_after_assignment(make_context):
    calls = []
    rule = default_if_empty("phc_date", default_fn=lambda ctx: "2024-06-01",
                             also_check=lambda ctx: calls.append(ctx.row["phc_date"]) or [])
    ctx = make_context("analy_physi_chimi", {"phc_date": None})
    rule(ctx)
    assert calls == ["2024-06-01"]


# --------------------------------------------------------------------- date_within_bounds
def test_date_within_bounds_below_lower_triggers_error(make_context):
    rule = date_within_bounds("phc_date", "ing_date_debut_inven", "ing_date_fin_inven",
                               "La date", code="X", other_layer="infor_gener")
    ctx = make_context(
        "analy_physi_chimi",
        {"une_code_ident": "UE1", "mes_no_seq": 1, "phc_date": "2024-01-01"},
        layers={"infor_gener": [{
            "une_code_ident": "UE1", "mes_no_seq": 1,
            "ing_date_debut_inven": "2024-06-01", "ing_date_fin_inven": "2024-09-01",
        }]},
    )
    assert len(rule(ctx)) == 1


def test_date_within_bounds_within_range_no_error(make_context):
    rule = date_within_bounds("phc_date", "ing_date_debut_inven", "ing_date_fin_inven",
                               "La date", code="X", other_layer="infor_gener")
    ctx = make_context(
        "analy_physi_chimi",
        {"une_code_ident": "UE1", "mes_no_seq": 1, "phc_date": "2024-07-01"},
        layers={"infor_gener": [{
            "une_code_ident": "UE1", "mes_no_seq": 1,
            "ing_date_debut_inven": "2024-06-01", "ing_date_fin_inven": "2024-09-01",
        }]},
    )
    assert rule(ctx) == []


def test_date_within_bounds_no_reference_record_no_error(make_context):
    rule = date_within_bounds("phc_date", "ing_date_debut_inven", "ing_date_fin_inven",
                               "La date", code="X", other_layer="infor_gener")
    ctx = make_context("analy_physi_chimi", {"une_code_ident": "UE1", "mes_no_seq": 1, "phc_date": "2024-07-01"})
    assert rule(ctx) == []


# --------------------------------------------------------------------- lookup_assign
def test_lookup_assign_match_sets_target(make_context):
    table = {("PENT", 25): "PAN1"}
    rule = lookup_assign(["a", "b"], "target", table)
    row = {"a": "PENT", "b": 25}
    ctx = make_context("t", row)
    rule(ctx)
    assert row["target"] == "PAN1"


def test_lookup_assign_no_match_leaves_target_untouched(make_context):
    table = {("PENT", 25): "PAN1"}
    rule = lookup_assign(["a", "b"], "target", table)
    row = {"a": "PENT", "b": 999}
    ctx = make_context("t", row)
    rule(ctx)
    assert "target" not in row
