import csv

import pytest

import config
from core.registry import get_rules
from core.rule_base import RuleKind
from rules.infor_gener import (
    allopatrie_coherent_sans_poisson,
    no_plan_eau_officiel_verifie_et_recopie,
    nom_plan_eau_affichage,
    territoire_libre_coherent,
)


# --------------------------------------------------------------------- territoire_libre_coherent
def test_territoire_libre_incoherent(make_context):
    ctx = make_context("infor_gener", {"ing_nom_terri_fauni": "LIBRE", "ing_nom_terri": "Autre chose"})
    issues = territoire_libre_coherent(ctx)
    assert len(issues) == 1
    assert issues[0].code == "INFOR_GENER_TERRITOIRE_LIBRE_INCOHERENT"


def test_territoire_libre_coherent_ok(make_context):
    ctx = make_context("infor_gener", {"ing_nom_terri_fauni": "LIBRE", "ing_nom_terri": "Territoire Libre"})
    assert territoire_libre_coherent(ctx) == []


def test_territoire_non_libre_ignore(make_context):
    ctx = make_context("infor_gener", {"ing_nom_terri_fauni": "02", "ing_nom_terri": "Peu importe"})
    assert territoire_libre_coherent(ctx) == []


# --------------------------------------------------------------------- no_plan_eau_officiel_verifie_et_recopie
def _write_tsv(path, header, rows):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)


@pytest.fixture
def lce_files(tmp_path, monkeypatch):
    """Fabrique de petits fichiers LCE synthétiques (au lieu des vrais
    lac_LCE.txt / cours_eau_LCE.txt, ~25 Mo chacun) pointés via
    config.LAC_LCE_PATH / config.COURS_EAU_LCE_PATH. Un tmp_path différent
    par test -> pas de collision avec le cache lru_cache de _load_lce_index,
    qui est indexé par chemin de fichier."""
    lac_path = tmp_path / "lac_LCE.txt"
    _write_tsv(
        lac_path,
        ["NO_L_LCE", "NOM_L_LCE", "LAT_DDD", "LONG_DDD", "TYPE_TER", "NOM_TER",
         "SUPER_HA", "PROF_MAX_M", "ALTITUDE_M", "PERIM_KM", "NO_BAS_1", "NOM_BAS_1",
         "NO_BAS_2", "NOM_BAS_2", "NO_MRC", "NOM_MRC", "NOM_MUNIC", "FEUILLET", "NO_ZONE_PE"],
        [["00001", "Lac Test", "48.0", "-79.0", "LIB", "Territoire Libre",
          "100", "-99", "265", "42.5", "", "", "", "", "", "", "", "32D12NE", ""]],
    )

    cours_eau_path = tmp_path / "cours_eau_LCE.txt"
    _write_tsv(
        cours_eau_path,
        ["NO_CE_LCE", "NOM_CE_LCE", "LAT_DDD", "LONG_DDD", "TYPE_TER", "NOM_TER",
         "NO_BAS_1", "NOM_BAS_1", "NO_BAS_2", "NOM_BAS_2", "NO_MRC", "NOM_MRC",
         "NOM_MUNIC", "FEUILLET", "NO_ZONE_PE"],
        [["01010011", "Riviere Test", "48.4", "-64.5", "LIB", "Territoire Libre",
          "0101", "GRANDE RIVIERE", "", "", "02", "Le Rocher", "Grande-Riviere", "22A07NE", "01"]],
    )

    monkeypatch.setattr(config, "LAC_LCE_PATH", str(lac_path))
    monkeypatch.setattr(config, "COURS_EAU_LCE_PATH", str(cours_eau_path))
    return lac_path, cours_eau_path


def test_no_plan_eau_officiel_lac_trouve_recopie_champs_vides(make_context, lce_files):
    row = {"ing_no_plan_eau_offic": "00001"}
    ctx = make_context("infor_gener", row)
    issues = no_plan_eau_officiel_verifie_et_recopie(ctx)
    assert issues == []
    assert row["ing_suprf_plan_eau_m"] == 100.0
    assert row["ing_altit_plan_m"] == 265.0
    assert row["ing_val_perim_plan_km"] == 42.5
    assert "ing_profd_max_m" not in row  # -99 dans le fichier LCE -> laissé vide


def test_no_plan_eau_officiel_ne_pas_ecraser_valeur_existante(make_context, lce_files):
    row = {"ing_no_plan_eau_offic": "00001", "ing_suprf_plan_eau_m": 5}
    ctx = make_context("infor_gener", row)
    no_plan_eau_officiel_verifie_et_recopie(ctx)
    assert row["ing_suprf_plan_eau_m"] == 5


def test_no_plan_eau_officiel_cours_eau_trouve_sans_champs_numeriques(make_context, lce_files):
    row = {"ing_no_plan_eau_offic": "01010011"}
    ctx = make_context("infor_gener", row)
    issues = no_plan_eau_officiel_verifie_et_recopie(ctx)
    assert issues == []
    assert "ing_suprf_plan_eau_m" not in row


def test_no_plan_eau_officiel_introuvable_triggers_error(make_context, lce_files):
    row = {"ing_no_plan_eau_offic": "99999"}
    ctx = make_context("infor_gener", row)
    issues = no_plan_eau_officiel_verifie_et_recopie(ctx)
    assert len(issues) == 1
    assert issues[0].code == "INFOR_GENER_NO_PLAN_EAU_OFFICIEL_INTROUVABLE"


def test_no_plan_eau_officiel_longueur_invalide_triggers_error(make_context, lce_files):
    row = {"ing_no_plan_eau_offic": "123"}
    ctx = make_context("infor_gener", row)
    issues = no_plan_eau_officiel_verifie_et_recopie(ctx)
    assert len(issues) == 1
    assert issues[0].code == "INFOR_GENER_NO_PLAN_EAU_OFFICIEL_INTROUVABLE"


def test_no_plan_eau_officiel_vide_no_error(make_context, lce_files):
    row = {"ing_no_plan_eau_offic": None}
    ctx = make_context("infor_gener", row)
    assert no_plan_eau_officiel_verifie_et_recopie(ctx) == []


# --------------------------------------------------------------------- nom_plan_eau_affichage
def test_nom_plan_eau_affichage_depuis_officiel(make_context):
    row = {"ing_nom_plan_eau_offic": "Lac Officiel", "ing_nom_plan_eau": "Lac Régional"}
    ctx = make_context("infor_gener", row)
    nom_plan_eau_affichage(ctx)
    assert row["ing_nom_plan_eau_affic"] == "Lac Officiel"


def test_nom_plan_eau_affichage_depuis_regional_si_officiel_absent(make_context):
    row = {"ing_nom_plan_eau_offic": None, "ing_nom_plan_eau": "Lac Régional"}
    ctx = make_context("infor_gener", row)
    nom_plan_eau_affichage(ctx)
    assert row["ing_nom_plan_eau_affic"] == "Lac Régional"


def test_nom_plan_eau_affichage_absent_si_aucun_nom(make_context):
    row = {"ing_nom_plan_eau_offic": None, "ing_nom_plan_eau": None}
    ctx = make_context("infor_gener", row)
    nom_plan_eau_affichage(ctx)
    assert "ing_nom_plan_eau_affic" not in row


# --------------------------------------------------------------------- au moins une coordonnée saisie
def _coordonnees_rule():
    rules = get_rules("infor_gener", kind=RuleKind.VALIDATION)
    return next(r for r in rules if r.name.startswith("at_least_one_of_ing_latit_bd_lce"))


def test_coordonnees_toutes_absentes_triggers_error(make_context):
    row = {"ing_latit_bd_lce": None, "ing_longi_bd_lce": None, "ing_latit_centr": None, "ing_longi_centr": None}
    ctx = make_context("infor_gener", row)
    issues = _coordonnees_rule().run(ctx)
    assert len(issues) == 1
    assert issues[0].code == "INFOR_GENER_COORDONNEES_REQUISES"


def test_coordonnees_bd_lce_seule_suffit(make_context):
    row = {"ing_latit_bd_lce": 48.5, "ing_longi_bd_lce": -79.0, "ing_latit_centr": None, "ing_longi_centr": None}
    ctx = make_context("infor_gener", row)
    assert _coordonnees_rule().run(ctx) == []


def test_coordonnees_centre_seule_suffit(make_context):
    row = {"ing_latit_bd_lce": None, "ing_longi_bd_lce": None, "ing_latit_centr": 48.5, "ing_longi_centr": -79.0}
    ctx = make_context("infor_gener", row)
    assert _coordonnees_rule().run(ctx) == []


# --------------------------------------------------------------------- allopatrie_coherent_sans_poisson
def test_allopatrie_oui_sans_poisson_non_incoherent(make_context):
    row = {"ing_ind_allop": "oui", "ing_ind_lac_sans_poiss": "oui"}
    ctx = make_context("infor_gener", row)
    issues = allopatrie_coherent_sans_poisson(ctx)
    assert len(issues) == 1
    assert issues[0].code == "INFOR_GENER_ALLOPATRIE_INCOHERENTE"


def test_allopatrie_oui_sans_poisson_non_ok(make_context):
    row = {"ing_ind_allop": "oui", "ing_ind_lac_sans_poiss": "non"}
    ctx = make_context("infor_gener", row)
    assert allopatrie_coherent_sans_poisson(ctx) == []


def test_allopatrie_non_ignore(make_context):
    row = {"ing_ind_allop": "non", "ing_ind_lac_sans_poiss": None}
    ctx = make_context("infor_gener", row)
    assert allopatrie_coherent_sans_poisson(ctx) == []


# --------------------------------------------------------------------- dates d'inventaire
def test_dates_inventaire_incoherentes(make_context):
    rules = get_rules("infor_gener", kind=RuleKind.VALIDATION)
    rule = next(r for r in rules if r.name == "cross_field_lte_ing_date_debut_inven_ing_date_fin_inven")
    row = {"ing_date_debut_inven": "2024-09-01", "ing_date_fin_inven": "2024-06-01"}
    ctx = make_context("infor_gener", row)
    issues = rule.run(ctx)
    assert len(issues) == 1
    assert issues[0].code == "INFOR_GENER_DATES_INVENTAIRE_INCOHERENTES"


def test_dates_inventaire_coherentes_no_error(make_context):
    rules = get_rules("infor_gener", kind=RuleKind.VALIDATION)
    rule = next(r for r in rules if r.name == "cross_field_lte_ing_date_debut_inven_ing_date_fin_inven")
    row = {"ing_date_debut_inven": "2024-06-01", "ing_date_fin_inven": "2024-09-01"}
    ctx = make_context("infor_gener", row)
    assert rule.run(ctx) == []


# --------------------------------------------------------------------- champs obligatoires
def test_champs_obligatoires_enregistres():
    codes = {r.name for r in get_rules("infor_gener", kind=RuleKind.VALIDATION)}
    for champ in ("ing_date_debut_inven", "ing_date_fin_inven", "tpl_code"):
        assert f"required_field_{champ}" in codes


def test_no_plan_eau_officiel_ou_regional_requis(make_context):
    rules = get_rules("infor_gener", kind=RuleKind.VALIDATION)
    rule = next(r for r in rules if r.name == "at_least_one_of_ing_no_plan_eau_offic_ing_no_plan_eau")

    row = {"ing_no_plan_eau_offic": None, "ing_no_plan_eau": None}
    ctx = make_context("infor_gener", row)
    issues = rule.run(ctx)
    assert len(issues) == 1
    assert issues[0].code == "INFOR_GENER_NO_PLAN_EAU_REQUIS"


def test_no_plan_eau_regional_seul_suffit(make_context):
    rules = get_rules("infor_gener", kind=RuleKind.VALIDATION)
    rule = next(r for r in rules if r.name == "at_least_one_of_ing_no_plan_eau_offic_ing_no_plan_eau")

    row = {"ing_no_plan_eau_offic": None, "ing_no_plan_eau": "12345"}
    ctx = make_context("infor_gener", row)
    assert rule.run(ctx) == []
