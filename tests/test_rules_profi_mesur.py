import pytest

from core.registry import get_rules
from core.rule_base import RuleKind
from rules.profi_mesur import (
    generer_profondeurs,
    ph_dans_bornes,
    profondeur_obligatoire_positive,
)


# --------------------------------------------------------------------- generer_profondeurs
def test_generer_profondeurs_defaut_20m():
    profondeurs = generer_profondeurs(None)
    assert profondeurs[0] == 0.5
    assert profondeurs[-1] == 20.0


def test_generer_profondeurs_premiers_points_fixes():
    profondeurs = generer_profondeurs(5.0)
    assert profondeurs == [0.5, 1.0, 2.0, 3.0, 4.0, 5.0]


def test_generer_profondeurs_palier_2m_entre_16_et_20():
    profondeurs = generer_profondeurs(20.0)
    assert 17.0 not in profondeurs
    assert 16.0 in profondeurs and 18.0 in profondeurs and 20.0 in profondeurs


def test_generer_profondeurs_palier_4m_apres_20():
    profondeurs = generer_profondeurs(32.0)
    assert profondeurs[-4:] == [20.0, 24.0, 28.0, 32.0]
    assert 21.0 not in profondeurs and 22.0 not in profondeurs


def test_generer_profondeurs_profondeur_max_zero():
    assert generer_profondeurs(0.0) == [0.5]


@pytest.mark.parametrize("profondeur_max,attendu_dernier", [
    (1.0, 1.0), (14.0, 14.0), (15.0, 14.0), (16.0, 16.0),
])
def test_generer_profondeurs_bornes_intermediaires(profondeur_max, attendu_dernier):
    assert generer_profondeurs(profondeur_max)[-1] == attendu_dernier


# --------------------------------------------------------------------- profondeur_obligatoire_positive
def test_profondeur_manquante_erreur(make_context):
    ctx = make_context("profi_mesur", {"pme_profd_m": None})
    issues = profondeur_obligatoire_positive(ctx)
    assert len(issues) == 1 and issues[0].code == "PROFI_MESUR_PROFD_REQUISE"


def test_profondeur_negative_erreur(make_context):
    ctx = make_context("profi_mesur", {"pme_profd_m": -1})
    issues = profondeur_obligatoire_positive(ctx)
    assert len(issues) == 1 and issues[0].code == "PROFI_MESUR_PROFD_INVALIDE"


def test_profondeur_valide_aucune_erreur(make_context):
    ctx = make_context("profi_mesur", {"pme_profd_m": 0.5})
    assert profondeur_obligatoire_positive(ctx) == []


# --------------------------------------------------------------------- ph_dans_bornes
def test_ph_hors_bornes_erreur(make_context):
    for valeur in (4.9, 8.1, 12):
        ctx = make_context("profi_mesur", {"pme_val_ph": valeur})
        issues = ph_dans_bornes(ctx)
        assert len(issues) == 1 and issues[0].code == "PROFI_MESUR_PH_HORS_BORNES"


def test_ph_dans_bornes_aucune_erreur(make_context):
    for valeur in (5, 6.8, 8):
        ctx = make_context("profi_mesur", {"pme_val_ph": valeur})
        assert ph_dans_bornes(ctx) == []


def test_ph_absent_aucune_erreur(make_context):
    """Le pH n'est pas obligatoire en soi : c'est la règle « au moins une
    mesure » qui couvre l'absence totale de mesure."""
    ctx = make_context("profi_mesur", {"pme_val_ph": None})
    assert ph_dans_bornes(ctx) == []


# --------------------------------------------------------------------- au moins une mesure
def _rule_au_moins_une_mesure():
    return next(
        r for r in get_rules("profi_mesur", kind=RuleKind.VALIDATION)
        if r.name.startswith("at_least_one_of_pme_val_oxyge")
    )


def test_aucune_mesure_erreur(make_context):
    ctx = make_context("profi_mesur", {
        "pme_val_oxyge": None, "pme_val_ph": None, "pme_val_tempe_cel": None})
    issues = _rule_au_moins_une_mesure().run(ctx)
    assert len(issues) == 1
    assert issues[0].code == "PROFI_MESUR_AU_MOINS_UNE_MESURE_REQUISE"


@pytest.mark.parametrize("champ", ["pme_val_oxyge", "pme_val_ph", "pme_val_tempe_cel"])
def test_une_seule_mesure_suffit(make_context, champ):
    row = {"pme_val_oxyge": None, "pme_val_ph": None, "pme_val_tempe_cel": None}
    row[champ] = 7
    ctx = make_context("profi_mesur", row)
    assert _rule_au_moins_une_mesure().run(ctx) == []
