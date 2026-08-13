from core.registry import get_rules
from core.rule_base import RuleKind
from rules.forme_descr_habit import NOMBRE_MAX_ENREGISTREMENTS, forme_descr_habit_nombre_max


def _rows(n):
    return [{"une_code_ident": "UE1", "mes_no_seq": 1, "dha_no_stati": 1} for _ in range(n)]


def test_forme_descr_habit_nombre_max_registered_as_layer_kind():
    """RuleKind.LAYER : évaluée une seule fois par couche (voir
    core.engine.run), pas une fois par enregistrement -- sinon un
    dépassement produirait une anomalie dupliquée par ligne."""
    rules = get_rules("forme_descr_habit", kind=RuleKind.LAYER)
    assert any(r.name == "forme_descr_habit_nombre_max" for r in rules)
    assert not any(
        r.name == "forme_descr_habit_nombre_max"
        for r in get_rules("forme_descr_habit", kind=RuleKind.VALIDATION)
    )


def test_aucune_forme_no_error(make_context):
    ctx = make_context("forme_descr_habit", {}, all_rows=[])
    assert forme_descr_habit_nombre_max(ctx) == []


def test_nombre_egal_au_maximum_no_error(make_context):
    rows = _rows(NOMBRE_MAX_ENREGISTREMENTS)
    ctx = make_context("forme_descr_habit", {}, all_rows=rows)
    assert forme_descr_habit_nombre_max(ctx) == []


def test_nombre_superieur_au_maximum_triggers_error(make_context):
    rows = _rows(NOMBRE_MAX_ENREGISTREMENTS + 1)
    ctx = make_context("forme_descr_habit", {}, all_rows=rows)
    issues = forme_descr_habit_nombre_max(ctx)
    assert len(issues) == 1
    assert issues[0].code == "FORME_DESCR_HABIT_NOMBRE_MAX_ENREGISTREMENTS"


def test_nombre_tres_superieur_ne_produit_qu_une_seule_anomalie(make_context):
    """RuleKind.LAYER n'est appelée qu'une seule fois par core.engine.run,
    quel que soit le nombre de lignes : un seul appel à la fonction ici
    représente donc fidèlement le comportement réel, et il ne doit jamais
    produire plus d'une anomalie même très au-dessus du seuil."""
    rows = _rows(50)
    ctx = make_context("forme_descr_habit", {}, all_rows=rows)
    assert len(forme_descr_habit_nombre_max(ctx)) == 1
