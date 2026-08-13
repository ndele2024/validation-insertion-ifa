import pytest

from core.models import Severity
from core.registry import get_rules
from core.rule_base import RuleKind
from rules.equipe import equipe_validation


@pytest.fixture
def responsable_ou_tie_rule():
    """La règle at_least_one_of(eqr_code_respo, tie_code) est enregistrée
    génériquement (rules/common.py) plutôt qu'exportée comme fonction
    nommée : on la récupère donc via le registre."""
    rules = get_rules("equipe", kind=RuleKind.VALIDATION)
    return next(r for r in rules if r.name == "at_least_one_of_eqr_code_respo_tie_code")


# --------------------------------------------------------------------- equipe_validation (au moins un enregistrement)
def test_equipe_validation_registered_as_layer_kind():
    """Garde-fou : equipe_validation doit être enregistrée en RuleKind.LAYER,
    pas RuleKind.VALIDATION. core.engine.run invoque les règles VALIDATION
    une fois PAR ENREGISTREMENT (voir core/engine.py) : pour une couche
    equipe vide, la boucle `for row in rows` ne s'exécuterait jamais et la
    règle « au moins un enregistrement » ne se déclencherait donc jamais en
    pratique -- c'est le bug que RuleKind.LAYER corrige."""
    rules = get_rules("equipe", kind=RuleKind.LAYER)
    assert any(r.name == "equipe_validation" for r in rules)
    assert not any(r.name == "equipe_validation" for r in get_rules("equipe", kind=RuleKind.VALIDATION))


def test_aucune_equipe(make_context):
    ctx = make_context("equipe", {}, all_rows=[])
    issues = equipe_validation(ctx)
    assert len(issues) == 1
    assert issues[0].severity == Severity.ERROR
    assert issues[0].code == "EQUIPE_AU_MOINS_UN_ENREGISTEMENT"


def test_au_moins_une_equipe_no_error(make_context):
    row = {"eqr_code_respo": "RESP1"}
    ctx = make_context("equipe", row, all_rows=[row])
    assert equipe_validation(ctx) == []


# --------------------------------------------------------------------- at_least_one_of(eqr_code_respo, tie_code)
def test_responsable_et_intervenant_absents_triggers_error(make_context, responsable_ou_tie_rule):
    row = {"eqr_code_respo": None, "tie_code": None}
    ctx = make_context("equipe", row)
    issues = responsable_ou_tie_rule.run(ctx)
    assert len(issues) == 1
    assert issues[0].code == "NOM_RESPONSABLE_EQUIPE_REQUIS"


def test_responsable_renseigne_no_error(make_context, responsable_ou_tie_rule):
    row = {"eqr_code_respo": "RESP1", "tie_code": None}
    ctx = make_context("equipe", row)
    assert responsable_ou_tie_rule.run(ctx) == []


def test_intervenant_externe_renseigne_no_error(make_context, responsable_ou_tie_rule):
    row = {"eqr_code_respo": None, "tie_code": "TIE1"}
    ctx = make_context("equipe", row)
    assert responsable_ou_tie_rule.run(ctx) == []
     