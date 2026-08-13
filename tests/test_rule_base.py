from core.models import LayerSchema
from core.rule_base import RuleContext


def test_other_layer_returns_empty_list_when_absent(make_context):
    ctx = make_context("detail_speci", {"dsp_no_speci": 1})
    assert ctx.other_layer("inexistant") == []


def test_other_layer_returns_rows(make_context):
    ctx = make_context("detail_speci", {"dsp_no_speci": 1},
                        layers={"peche_exper": [{"tpc_code": "PENT"}]})
    assert ctx.other_layer("peche_exper") == [{"tpc_code": "PENT"}]


def test_record_key_uses_default_composite_key(make_context):
    ctx = make_context("detail_speci", {"une_code_ident": "UE1", "mes_no_seq": 2, "dsp_no_speci": 5})
    assert ctx.record_key() == {"une_code_ident": "UE1", "mes_no_seq": 2}


def test_record_key_uses_schema_primary_key_when_available(make_context):
    schema = LayerSchema(table="detail_speci", primary_key=["une_code_ident", "mes_no_seq", "dsp_no_speci"])
    ctx = make_context("detail_speci", {"une_code_ident": "UE1", "mes_no_seq": 2, "dsp_no_speci": 5},
                        schemas={"detail_speci": schema})
    assert ctx.record_key() == {"une_code_ident": "UE1", "mes_no_seq": 2, "dsp_no_speci": 5}


def test_record_key_explicit_fields_override_everything(make_context):
    ctx = make_context("detail_speci", {"a": 1, "b": 2})
    assert ctx.record_key(key_fields=["a"]) == {"a": 1}
