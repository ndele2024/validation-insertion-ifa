from core.registry import (
    clear_registry, discover_rules, get_rules, register, registered_layers,
)
from core.rule_base import RuleKind


def test_register_and_get_rules_roundtrip():
    @register("__test_layer_roundtrip__", kind=RuleKind.VALIDATION)
    def my_rule(ctx):
        return []

    rules = get_rules("__test_layer_roundtrip__")
    assert len(rules) == 1
    assert rules[0].name == "my_rule"
    assert rules[0].kind == RuleKind.VALIDATION

    clear_registry("__test_layer_roundtrip__")
    assert get_rules("__test_layer_roundtrip__") == []


def test_get_rules_filters_by_kind():
    @register("__test_layer_kind__", kind=RuleKind.TRANSFORM)
    def transform_rule(ctx):
        return []

    @register("__test_layer_kind__", kind=RuleKind.VALIDATION)
    def validation_rule(ctx):
        return []

    assert [r.name for r in get_rules("__test_layer_kind__", kind=RuleKind.TRANSFORM)] == ["transform_rule"]
    assert [r.name for r in get_rules("__test_layer_kind__", kind=RuleKind.VALIDATION)] == ["validation_rule"]

    clear_registry("__test_layer_kind__")


def test_get_rules_respects_order():
    @register("__test_layer_order__", order=20)
    def second(ctx):
        return []

    @register("__test_layer_order__", order=10)
    def first(ctx):
        return []

    assert [r.name for r in get_rules("__test_layer_order__")] == ["first", "second"]
    clear_registry("__test_layer_order__")


def test_discover_rules_registers_known_layers():
    """Vérifie que le mécanisme d'auto-découverte importe bien les modules
    de validation_insertion.rules et que les couches métier attendues sont
    enregistrées (preuve que tous les fichiers de règles s'importent sans
    erreur de syntaxe ou de dépendance manquante)."""
    discover_rules()
    layers = registered_layers()
    for expected in ("analy_physi_chimi", "detail_speci", "denom_espec",
                      "autre_obser_fauni", "descr_habit", "infor_gener",
                      "profi_mesur", "pose_levee_filet"):
        assert expected in layers, f"couche '{expected}' absente du registre après discover_rules()"
