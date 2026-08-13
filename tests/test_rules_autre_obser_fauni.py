from core.registry import get_rules
from core.rule_base import RuleKind


def test_required_rules_registered_for_autre_obser_fauni():
    """rules/autre_obser_fauni.py enregistre ses règles via les fabriques
    génériques (required_field, default_if_empty) plutôt que via des
    fonctions nommées : on vérifie donc le comportement au niveau du
    registre plutôt que par import direct de fonctions."""
    import rules.autre_obser_fauni  # noqa: F401 (déclenche les @register)

    validation_codes = set()
    for rule in get_rules("autre_obser_fauni", kind=RuleKind.VALIDATION):
        validation_codes.add(rule.name)

    # Les règles required_field sont nommées required_field_<champ> (voir
    # rules/common.py) -> on vérifie la présence des champs attendus.
    assert "required_field_aof_date_obser" in validation_codes
    assert "required_field_efa_code" in validation_codes
    assert "required_field_cef_code" in validation_codes
    assert "required_field_aof_latit" in validation_codes
    assert "required_field_aof_longit" in validation_codes


def test_date_observation_default_and_bounds_via_rule_objects(make_context):
    import rules.autre_obser_fauni as mod  # noqa: F401

    transform_rules = get_rules("autre_obser_fauni", kind=RuleKind.TRANSFORM)
    assert len(transform_rules) == 1  # default_if_empty(aof_date_obser, ...)

    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "aof_date_obser": None}
    ctx = make_context("autre_obser_fauni", row, layers={
        "infor_gener": [{"une_code_ident": "UE1", "mes_no_seq": 1,
                          "ing_date_debut_inven": "2024-06-01", "ing_date_fin_inven": "2024-09-01"}],
    })
    for rule in transform_rules:
        rule.run(ctx)

    assert row["aof_date_obser"] == "2024-06-01"
