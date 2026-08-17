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


def _ctx_mesurage(make_context, equipes, une="UE1", seq=1):
    """Contexte d'un mesurage donné, avec la couche equipe du lot."""
    return make_context(
        "mesurage",
        {"une_code_ident": une, "mes_no_seq": seq},
        layers={"equipe": equipes},
    )


# --------------------------------------------------------------------- equipe_validation
def test_equipe_validation_enregistree_sur_la_couche_mesurage():
    """Garde-fou : la règle porte sur l'ABSENCE d'équipe pour un mesurage.
    Une VALIDATION est évaluée une fois par enregistrement de sa propre
    couche — enregistrée sur « equipe », elle ne verrait jamais un mesurage
    dépourvu d'équipe. Elle doit donc être rattachée à « mesurage »."""
    noms_mesurage = {r.name for r in get_rules("mesurage", kind=RuleKind.VALIDATION)}
    assert "equipe_validation" in noms_mesurage

    noms_equipe = {r.name for r in get_rules("equipe")}
    assert "equipe_validation" not in noms_equipe


def test_equipe_validation_est_un_avertissement(make_context):
    """L'absence d'équipe est une saisie incomplète, pas une incohérence
    bloquante : elle ne doit pas empêcher l'insertion du lot."""
    ctx = _ctx_mesurage(make_context, equipes=[])
    issues = equipe_validation(ctx)
    assert len(issues) == 1
    assert issues[0].severity == Severity.WARNING
    assert issues[0].code == "EQUIPE_AU_MOINS_UN_ENREGISTEMENT"


def test_mesurage_sans_aucune_equipe(make_context):
    ctx = _ctx_mesurage(make_context, equipes=[])
    assert len(equipe_validation(ctx)) == 1


def test_mesurage_avec_une_equipe_no_warning(make_context):
    ctx = _ctx_mesurage(make_context, equipes=[
        {"une_code_ident": "UE1", "mes_no_seq": 1, "eqr_code_respo": "RESP1"},
    ])
    assert equipe_validation(ctx) == []


def test_equipe_d_un_autre_mesurage_ne_compte_pas(make_context):
    """Le rattachement se fait sur la clé (une_code_ident, mes_no_seq) : une
    équipe saisie pour un autre mesurage ne couvre pas celui-ci."""
    ctx = _ctx_mesurage(make_context, une="UE1", seq=1, equipes=[
        {"une_code_ident": "UE1", "mes_no_seq": 2, "eqr_code_respo": "RESP1"},
        {"une_code_ident": "UE2", "mes_no_seq": 1, "eqr_code_respo": "RESP2"},
    ])
    issues = equipe_validation(ctx)
    assert len(issues) == 1
    assert issues[0].record == {"une_code_ident": "UE1", "mes_no_seq": 1}


def test_equipe_de_la_meme_unite_mais_autre_inventaire_ne_compte_pas(make_context):
    ctx = _ctx_mesurage(make_context, une="UE1", seq=3, equipes=[
        {"une_code_ident": "UE1", "mes_no_seq": 1, "eqr_code_respo": "RESP1"},
    ])
    assert len(equipe_validation(ctx)) == 1


def test_plusieurs_equipes_pour_le_meme_mesurage_no_warning(make_context):
    ctx = _ctx_mesurage(make_context, equipes=[
        {"une_code_ident": "UE1", "mes_no_seq": 1, "eqr_code_respo": "RESP1"},
        {"une_code_ident": "UE1", "mes_no_seq": 1, "tie_code": "TIE1"},
    ])
    assert equipe_validation(ctx) == []


def test_couche_equipe_absente_du_lot(make_context):
    """other_layer retourne une liste vide si la couche n'est pas dans le
    GeoPackage : le mesurage est alors bien signalé."""
    ctx = make_context("mesurage", {"une_code_ident": "UE1", "mes_no_seq": 1})
    assert len(equipe_validation(ctx)) == 1


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
