from core.registry import get_rules
from core.rule_base import RuleKind
from rules.habitat import (
    coordonnees_projetees_coherence,
    profondeur_donnee_courant_defaut,
    superficie_calculee,
    superficie_inferieure_ou_egale_plan_eau,
)


# --------------------------------------------------------------------- profondeur_donnee_courant_defaut
def test_profondeur_vites_coura_assignee_a_zero_si_vitesse_saisie(make_context):
    row = {"hab_val_vites_coura": 1.2, "hab_prfd_vites_coura": None}
    ctx = make_context("habitat", row)
    profondeur_donnee_courant_defaut(ctx)
    assert row["hab_prfd_vites_coura"] == 0


def test_profondeur_vites_coura_non_ecrasee_si_deja_saisie(make_context):
    row = {"hab_val_vites_coura": 1.2, "hab_prfd_vites_coura": 3}
    ctx = make_context("habitat", row)
    profondeur_donnee_courant_defaut(ctx)
    assert row["hab_prfd_vites_coura"] == 3


def test_profondeur_vites_coura_non_assignee_si_vitesse_absente(make_context):
    row = {"hab_val_vites_coura": None, "hab_prfd_vites_coura": None}
    ctx = make_context("habitat", row)
    profondeur_donnee_courant_defaut(ctx)
    assert row["hab_prfd_vites_coura"] is None


# --------------------------------------------------------------------- date d'observation (défaut + bornes)
def test_date_observation_default_and_bounds_via_rule_objects(make_context):
    transform_rules = get_rules("habitat", kind=RuleKind.TRANSFORM)
    date_rule = next(r for r in transform_rules if r.name == "default_if_empty_hab_date_obser")

    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "hab_date_obser": None}
    ctx = make_context("habitat", row, layers={
        "infor_gener": [{"une_code_ident": "UE1", "mes_no_seq": 1,
                          "ing_date_debut_inven": "2024-06-01", "ing_date_fin_inven": "2024-09-01"}],
    })
    date_rule.run(ctx)

    assert row["hab_date_obser"] == "2024-06-01"


def test_date_observation_hors_bornes_triggers_error(make_context):
    transform_rules = get_rules("habitat", kind=RuleKind.TRANSFORM)
    date_rule = next(r for r in transform_rules if r.name == "default_if_empty_hab_date_obser")

    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "hab_date_obser": "2024-01-01"}
    ctx = make_context("habitat", row, layers={
        "infor_gener": [{"une_code_ident": "UE1", "mes_no_seq": 1,
                          "ing_date_debut_inven": "2024-06-01", "ing_date_fin_inven": "2024-09-01"}],
    })
    issues = date_rule.run(ctx)

    assert len(issues) == 1
    assert issues[0].code == "HABITAT_DATE_OBSER_HORS_BORNES"


def test_date_observation_required_field_registered():
    validation_rules = get_rules("habitat", kind=RuleKind.VALIDATION)
    assert any(r.name == "required_field_hab_date_obser" for r in validation_rules)


# --------------------------------------------------------------------- superficie
def test_superficie_calculee_si_longueur_et_largeur(make_context):
    row = {"hab_long_m": 10, "hab_larg_m": 5}
    ctx = make_context("habitat", row)
    superficie_calculee(ctx)
    assert row["hab_suprf_m2"] == 50


def test_superficie_non_calculee_si_largeur_absente(make_context):
    row = {"hab_long_m": 10, "hab_larg_m": None}
    ctx = make_context("habitat", row)
    superficie_calculee(ctx)
    assert "hab_suprf_m2" not in row


def test_superficie_superieure_au_plan_eau_triggers_error(make_context):
    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "hab_suprf_m2": 200000}  # 20 ha
    ctx = make_context("habitat", row, layers={
        "infor_gener": [{"une_code_ident": "UE1", "mes_no_seq": 1, "ing_suprf_plan_eau_m": 10}],
    })
    issues = superficie_inferieure_ou_egale_plan_eau(ctx)
    assert len(issues) == 1
    assert issues[0].code == "HABITAT_SUPERFICIE_SUPERIEURE_PLAN_EAU"


def test_superficie_inferieure_ou_egale_au_plan_eau_no_error(make_context):
    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "hab_suprf_m2": 50000}  # 5 ha
    ctx = make_context("habitat", row, layers={
        "infor_gener": [{"une_code_ident": "UE1", "mes_no_seq": 1, "ing_suprf_plan_eau_m": 10}],
    })
    assert superficie_inferieure_ou_egale_plan_eau(ctx) == []


def test_superficie_sans_reference_infor_gener_no_error(make_context):
    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "hab_suprf_m2": 200000}
    ctx = make_context("habitat", row)
    assert superficie_inferieure_ou_egale_plan_eau(ctx) == []


def test_superficie_absente_no_error(make_context):
    row = {"une_code_ident": "UE1", "mes_no_seq": 1}
    ctx = make_context("habitat", row)
    assert superficie_inferieure_ou_egale_plan_eau(ctx) == []


# --------------------------------------------------------------------- commentaires requis si type "Autre"
def test_commentaires_requis_si_type_autre():
    validation_rules = get_rules("habitat", kind=RuleKind.VALIDATION)
    rule = next(r for r in validation_rules if r.name == "required_field_hab_com")
    assert rule is not None


def test_commentaires_requis_si_type_autre_via_context(make_context):
    validation_rules = get_rules("habitat", kind=RuleKind.VALIDATION)
    rule = next(r for r in validation_rules if r.name == "required_field_hab_com")

    row = {"tyh_code": "AU", "hab_com": None}
    ctx = make_context("habitat", row)
    issues = rule.run(ctx)
    assert len(issues) == 1
    assert issues[0].code == "HABITAT_COMMENTAIRES_REQUIS_SI_AUTRE"


def test_commentaires_non_requis_si_autre_type(make_context):
    validation_rules = get_rules("habitat", kind=RuleKind.VALIDATION)
    rule = next(r for r in validation_rules if r.name == "required_field_hab_com")

    row = {"tyh_code": "MA", "hab_com": None}
    ctx = make_context("habitat", row)
    assert rule.run(ctx) == []


# --------------------------------------------------------------------- champs obligatoires
def test_champs_obligatoires_enregistres():
    codes = {r.name for r in get_rules("habitat", kind=RuleKind.VALIDATION)}
    for champ in ("hab_no", "tyh_code", "hab_latit", "hab_longi"):
        assert f"required_field_{champ}" in codes


# --------------------------------------------------------------------- coordonnees_projetees_coherence
def test_mtm_champs_manquants_triggers_erreurs(make_context):
    row = {"tcp_code": "MTM_NAD83", "zon_code": None, "hab_val_coord_x": None, "hab_val_coord_y": None}
    ctx = make_context("habitat", row)
    issues = coordonnees_projetees_coherence(ctx)
    codes = [i.code for i in issues]
    assert codes.count("HABITAT_COORD_PROJETEE_REQUISE") == 3


def test_mtm_coordonnees_valides_no_error(make_context):
    row = {"tcp_code": "MTM_NAD83", "zon_code": "7", "hab_val_coord_x": 300000, "hab_val_coord_y": 5000000}
    ctx = make_context("habitat", row)
    assert coordonnees_projetees_coherence(ctx) == []


def test_mtm_coordonnee_x_hors_bornes(make_context):
    row = {"tcp_code": "MTM_NAD83", "zon_code": "7", "hab_val_coord_x": 999999, "hab_val_coord_y": 5000000}
    ctx = make_context("habitat", row)
    issues = coordonnees_projetees_coherence(ctx)
    assert any(i.code == "HABITAT_COORD_X_HORS_BORNES" for i in issues)


def test_utm_coordonnee_y_hors_bornes(make_context):
    row = {"tcp_code": "UTM_NAD83", "zon_code": "18", "hab_val_coord_x": 300000, "hab_val_coord_y": 1}
    ctx = make_context("habitat", row)
    issues = coordonnees_projetees_coherence(ctx)
    assert any(i.code == "HABITAT_COORD_Y_HORS_BORNES" for i in issues)


def test_utm_coordonnees_valides_no_error(make_context):
    row = {"tcp_code": "UTM_NAD83", "zon_code": "18", "hab_val_coord_x": 300000, "hab_val_coord_y": 5000000}
    ctx = make_context("habitat", row)
    assert coordonnees_projetees_coherence(ctx) == []


def test_geo_champs_dms_manquants_triggers_erreurs(make_context):
    row = {"tcp_code": "GEO_NAD83", "hab_latit_dms": None, "hab_longi_dms": None}
    ctx = make_context("habitat", row)
    issues = coordonnees_projetees_coherence(ctx)
    assert [i.code for i in issues].count("HABITAT_COORD_DMS_REQUISE") == 2


def test_geo_champs_projetes_interdits(make_context):
    row = {
        "tcp_code": "GEO_NAD83", "hab_latit_dms": "463000.00", "hab_longi_dms": "713000.00",
        "zon_code": "18", "hab_val_coord_x": 300000, "hab_val_coord_y": 5000000,
    }
    ctx = make_context("habitat", row)
    issues = coordonnees_projetees_coherence(ctx)
    assert [i.code for i in issues].count("HABITAT_COORD_PROJETEE_INTERDITE") == 3


def test_geo_valide_no_error(make_context):
    row = {
        "tcp_code": "GEO_NAD83", "hab_latit_dms": "463000.00", "hab_longi_dms": "713000.00",
        "zon_code": None, "hab_val_coord_x": None, "hab_val_coord_y": None,
    }
    ctx = make_context("habitat", row)
    assert coordonnees_projetees_coherence(ctx) == []


def test_tcp_code_inconnu_no_error(make_context):
    row = {"tcp_code": None, "zon_code": None, "hab_val_coord_x": None, "hab_val_coord_y": None}
    ctx = make_context("habitat", row)
    assert coordonnees_projetees_coherence(ctx) == []
