import datetime as dt

from core.registry import get_rules
from core.rule_base import RuleKind
from rules.amenagement import (
    annee_activite_coherente_avec_inventaire,
    superficie_calculee,
    type_activite_coherent,
)


# --------------------------------------------------------------------- superficie_calculee
def test_superficie_calculee_si_longueur_et_largeur(make_context):
    row = {"ame_long_m": 12, "ame_larg_m": 3}
    ctx = make_context("amenagement", row)
    superficie_calculee(ctx)
    assert row["ame_suprf_m2"] == 36


def test_superficie_non_calculee_si_largeur_absente(make_context):
    row = {"ame_long_m": 12, "ame_larg_m": None}
    ctx = make_context("amenagement", row)
    superficie_calculee(ctx)
    assert "ame_suprf_m2" not in row


# --------------------------------------------------------------------- type_activite_coherent
def test_activite_valide_pour_amenagement_ip(make_context):
    ctx = make_context("amenagement", {"tam_code": "IP", "aam_code": "CNC"})
    assert type_activite_coherent(ctx) == []


def test_activite_invalide_pour_amenagement_ip(make_context):
    """« CO » appartient à la liste des autres aménagements, pas à celle de IP."""
    ctx = make_context("amenagement", {"tam_code": "IP", "aam_code": "CO"})
    issues = type_activite_coherent(ctx)
    assert len(issues) == 1
    assert issues[0].code == "AMENAGEMENT_TYPE_ACTIVITE_INVALIDE"


def test_activite_valide_pour_autre_amenagement(make_context):
    ctx = make_context("amenagement", {"tam_code": "FR", "aam_code": "EN"})
    assert type_activite_coherent(ctx) == []


def test_activite_invalide_pour_autre_amenagement(make_context):
    ctx = make_context("amenagement", {"tam_code": "FR", "aam_code": "CNC"})
    assert len(type_activite_coherent(ctx)) == 1


def test_activite_n_partagee_par_les_deux_listes(make_context):
    """« N » figure dans les deux listes : valide quel que soit le type."""
    for tam_code in ("IP", "FR"):
        ctx = make_context("amenagement", {"tam_code": tam_code, "aam_code": "N"})
        assert type_activite_coherent(ctx) == []


def test_activite_absente_no_error(make_context):
    """Obligation de saisie couverte séparément par required_field."""
    ctx = make_context("amenagement", {"tam_code": "IP", "aam_code": None})
    assert type_activite_coherent(ctx) == []


# --------------------------------------------------------------------- annee_activite_coherente_avec_inventaire
def _ctx_avec_inventaire(make_context, date_activ, date_debut="2024-06-01"):
    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "ame_date_activ": date_activ}
    return make_context("amenagement", row, layers={
        "infor_gener": [{"une_code_ident": "UE1", "mes_no_seq": 1,
                          "ing_date_debut_inven": date_debut}],
    })


def test_annee_activite_identique_no_error(make_context):
    ctx = _ctx_avec_inventaire(make_context, "2024-08-15")
    assert annee_activite_coherente_avec_inventaire(ctx) == []


def test_annee_activite_differente_triggers_error(make_context):
    ctx = _ctx_avec_inventaire(make_context, "2023-08-15")
    issues = annee_activite_coherente_avec_inventaire(ctx)
    assert len(issues) == 1
    assert issues[0].code == "AMENAGEMENT_ANNEE_ACTIVITE_INCOHERENTE"


def test_annee_activite_accepte_objet_date(make_context):
    ctx = _ctx_avec_inventaire(make_context, dt.date(2024, 8, 15))
    assert annee_activite_coherente_avec_inventaire(ctx) == []


def test_annee_activite_sans_date_no_error(make_context):
    ctx = _ctx_avec_inventaire(make_context, None)
    assert annee_activite_coherente_avec_inventaire(ctx) == []


def test_annee_activite_sans_reference_infor_gener_no_error(make_context):
    ctx = make_context("amenagement", {"une_code_ident": "UE1", "mes_no_seq": 1,
                                        "ame_date_activ": "2023-08-15"})
    assert annee_activite_coherente_avec_inventaire(ctx) == []


# --------------------------------------------------------------------- champs obligatoires
def test_champs_obligatoires_enregistres():
    codes = {r.name for r in get_rules("amenagement", kind=RuleKind.VALIDATION)}
    for champ in ("tam_code", "aam_code", "ame_date_activ"):
        assert f"required_field_{champ}" in codes
