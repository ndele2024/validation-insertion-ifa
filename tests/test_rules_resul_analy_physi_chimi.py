from core.registry import get_rules
from core.rule_base import RuleKind
from rules.resul_analy_physi_chimi import (
    appareil_autofill,
    champs_obligatoires_conditionnels,
    indicateur_analyse_laboratoire_autofill,
    laboratoire_autofill,
    ph_dans_bornes,
    profondeurs_defaut,
    resultat_teinte_exclusifs,
    transparence_inferieure_profondeur_max,
    transparence_profondeur_vers_resultat,
    unicite_no_echantillon_laboratoire,
    unicite_parametre_par_station_date_profondeur,
)

LAYER = "resul_analy_physi_chimi"


def _rule(nom, kind=RuleKind.VALIDATION):
    return next(r for r in get_rules(LAYER, kind=kind) if r.name == nom)


# --------------------------------------------------------------------- appareil / laboratoire
def test_appareil_autofill_assigne_autre(make_context):
    row = {"app_code": None, "rpc_nom_autre_appar": "Sonde XYZ"}
    ctx = make_context(LAYER, row)
    appareil_autofill(ctx)
    assert row["app_code"] == "AUTRE"


def test_appareil_autofill_ne_touche_pas_appareil_standard(make_context):
    row = {"app_code": "YSI", "rpc_nom_autre_appar": "Sonde XYZ"}
    ctx = make_context(LAYER, row)
    appareil_autofill(ctx)
    assert row["app_code"] == "YSI"


def test_laboratoire_autofill_assigne_autre(make_context):
    row = {"lab_code": None, "rpc_nom_autre_labor": "Labo Test"}
    ctx = make_context(LAYER, row)
    laboratoire_autofill(ctx)
    assert row["lab_code"] == "AUTRE"


def test_nom_autre_laboratoire_requis_si_labo_autre(make_context):
    rule = _rule("required_field_rpc_nom_autre_labor")
    ctx = make_context(LAYER, {"lab_code": "AUTRE", "rpc_nom_autre_labor": None})
    issues = rule.run(ctx)
    assert len(issues) == 1
    assert issues[0].code == "RESUL_ANALY_NOM_AUTRE_LABORATOIRE_REQUIS"


def test_indicateur_analyse_labo_autofill(make_context):
    row = {"rpc_no_echan_labor": "ECH-1", "rpc_ind_analy_labor": None}
    ctx = make_context(LAYER, row)
    indicateur_analyse_laboratoire_autofill(ctx)
    assert row["rpc_ind_analy_labor"] == "OUI"


def test_indicateur_analyse_labo_inchange_sans_numero(make_context):
    row = {"rpc_no_echan_labor": None, "rpc_ind_analy_labor": "NON"}
    ctx = make_context(LAYER, row)
    indicateur_analyse_laboratoire_autofill(ctx)
    assert row["rpc_ind_analy_labor"] == "NON"


def test_commentaire_requis_si_parametre_autre(make_context):
    rule = _rule("required_field_rpc_com")
    ctx = make_context(LAYER, {"ppc_code": "AU", "rpc_com": None})
    assert len(rule.run(ctx)) == 1


# --------------------------------------------------------------------- transparence (TR)
def test_transparence_profondeur_reportee_dans_resultat(make_context):
    row = {"ppc_code": "TR", "rpc_profd_echan_m": 3.2, "rpc_val_resul": None}
    ctx = make_context(LAYER, row)
    transparence_profondeur_vers_resultat(ctx)
    assert row["rpc_val_resul"] == 3.2
    assert row["rpc_profd_echan_m"] is None


def test_transparence_ignoree_pour_autre_parametre(make_context):
    row = {"ppc_code": "PH", "rpc_profd_echan_m": 3.2, "rpc_val_resul": None}
    ctx = make_context(LAYER, row)
    transparence_profondeur_vers_resultat(ctx)
    assert row["rpc_profd_echan_m"] == 3.2


def test_transparence_superieure_profondeur_max_triggers_error(make_context):
    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "ppc_code": "TR", "rpc_val_resul": 30}
    ctx = make_context(LAYER, row, layers={
        "infor_gener": [{"une_code_ident": "UE1", "mes_no_seq": 1, "ing_profd_max_m": 12}],
    })
    issues = transparence_inferieure_profondeur_max(ctx)
    assert len(issues) == 1
    assert issues[0].code == "RESUL_ANALY_TRANSPARENCE_SUPERIEURE_PROFONDEUR_MAX"


def test_transparence_inferieure_profondeur_max_no_error(make_context):
    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "ppc_code": "TR", "rpc_val_resul": 5}
    ctx = make_context(LAYER, row, layers={
        "infor_gener": [{"une_code_ident": "UE1", "mes_no_seq": 1, "ing_profd_max_m": 12}],
    })
    assert transparence_inferieure_profondeur_max(ctx) == []


# --------------------------------------------------------------------- profondeurs_defaut
def test_profondeurs_cd_valeurs_par_defaut(make_context):
    row = {"ppc_code": "CD", "rpc_profd_echan_m": None, "rpc_val_profd_2_m": None}
    ctx = make_context(LAYER, row)
    profondeurs_defaut(ctx)
    assert row["rpc_profd_echan_m"] == 0
    assert row["rpc_val_profd_2_m"] == 5


def test_profondeurs_cd_non_ecrasees_si_deja_saisies(make_context):
    row = {"ppc_code": "CD", "rpc_profd_echan_m": 2, "rpc_val_profd_2_m": None}
    ctx = make_context(LAYER, row)
    profondeurs_defaut(ctx)
    assert row["rpc_profd_echan_m"] == 2


def test_profondeur_2_recopiee_pour_autre_parametre(make_context):
    row = {"ppc_code": "OD", "rpc_profd_echan_m": 4.5, "rpc_val_profd_2_m": None}
    ctx = make_context(LAYER, row)
    profondeurs_defaut(ctx)
    assert row["rpc_val_profd_2_m"] == 4.5


def test_profondeurs_incoherentes_triggers_error(make_context):
    rule = _rule("cross_field_lte_rpc_profd_echan_m_rpc_val_profd_2_m")
    ctx = make_context(LAYER, {"rpc_profd_echan_m": 9, "rpc_val_profd_2_m": 3})
    issues = rule.run(ctx)
    assert len(issues) == 1
    assert issues[0].code == "RESUL_ANALY_PROFONDEURS_INCOHERENTES"


# --------------------------------------------------------------------- résultat / teinte
def test_resultat_interdit_si_parametre_teinte(make_context):
    ctx = make_context(LAYER, {"ppc_code": "TI", "rpc_val_resul": 3, "res_code": "BRUN"})
    issues = resultat_teinte_exclusifs(ctx)
    assert len(issues) == 1
    assert issues[0].code == "RESUL_ANALY_RESULTAT_INTERDIT_SI_TEINTE"


def test_teinte_seule_valide_pour_parametre_teinte(make_context):
    ctx = make_context(LAYER, {"ppc_code": "TI", "rpc_val_resul": None, "res_code": "BRUN"})
    assert resultat_teinte_exclusifs(ctx) == []


def test_teinte_interdite_pour_autre_parametre(make_context):
    ctx = make_context(LAYER, {"ppc_code": "PH", "rpc_val_resul": 7, "res_code": "BRUN"})
    issues = resultat_teinte_exclusifs(ctx)
    assert len(issues) == 1
    assert issues[0].code == "RESUL_ANALY_TEINTE_INTERDITE"


def test_resultat_seul_valide_pour_autre_parametre(make_context):
    ctx = make_context(LAYER, {"ppc_code": "PH", "rpc_val_resul": 7, "res_code": None})
    assert resultat_teinte_exclusifs(ctx) == []


# --------------------------------------------------------------------- pH
def test_ph_hors_bornes_triggers_error(make_context):
    ctx = make_context(LAYER, {"ppc_code": "PH", "rpc_val_resul": 9.5})
    issues = ph_dans_bornes(ctx)
    assert len(issues) == 1
    assert issues[0].code == "RESUL_ANALY_PH_HORS_BORNES"


def test_ph_dans_bornes_no_error(make_context):
    for valeur in (5, 6.5, 8):
        ctx = make_context(LAYER, {"ppc_code": "PH", "rpc_val_resul": valeur})
        assert ph_dans_bornes(ctx) == []


def test_ph_ignore_pour_autre_parametre(make_context):
    ctx = make_context(LAYER, {"ppc_code": "OD", "rpc_val_resul": 12})
    assert ph_dans_bornes(ctx) == []


# --------------------------------------------------------------------- date de prise de l'échantillon
def test_date_echantillon_hors_bornes(make_context):
    rule = _rule("date_within_bounds_rpc_date_echan")
    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "rpc_date_echan": "2023-01-01"}
    ctx = make_context(LAYER, row, layers={
        "infor_gener": [{"une_code_ident": "UE1", "mes_no_seq": 1,
                          "ing_date_debut_inven": "2024-06-01", "ing_date_fin_inven": "2024-09-01"}],
    })
    issues = rule.run(ctx)
    assert len(issues) == 1
    assert issues[0].code == "RESUL_ANALY_DATE_ECHAN_HORS_BORNES"


# --------------------------------------------------------------------- unicité (RuleKind.LAYER)
def test_unicite_regles_enregistrees_en_layer_kind():
    """Les règles d'unicité portent sur la couche entière : elles doivent
    être évaluées une seule fois (RuleKind.LAYER), pas une fois par ligne."""
    noms = {r.name for r in get_rules(LAYER, kind=RuleKind.LAYER)}
    assert "unicite_parametre_par_station_date_profondeur" in noms
    assert "unicite_no_echantillon_laboratoire" in noms


def test_parametre_duplique_triggers_error(make_context):
    rows = [
        {"phc_no_stati": 1, "rpc_date_echan": "2024-06-05", "rpc_profd_echan_m": 2, "ppc_code": "PH"},
        {"phc_no_stati": 1, "rpc_date_echan": "2024-06-05", "rpc_profd_echan_m": 2, "ppc_code": "PH"},
    ]
    ctx = make_context(LAYER, {}, all_rows=rows)
    issues = unicite_parametre_par_station_date_profondeur(ctx)
    assert len(issues) == 1
    assert issues[0].code == "RESUL_ANALY_PARAMETRE_DUPLIQUE"


def test_parametres_distincts_no_error(make_context):
    rows = [
        {"phc_no_stati": 1, "rpc_date_echan": "2024-06-05", "rpc_profd_echan_m": 2, "ppc_code": "PH"},
        {"phc_no_stati": 1, "rpc_date_echan": "2024-06-05", "rpc_profd_echan_m": 2, "ppc_code": "OD"},
        {"phc_no_stati": 1, "rpc_date_echan": "2024-06-05", "rpc_profd_echan_m": 5, "ppc_code": "PH"},
    ]
    ctx = make_context(LAYER, {}, all_rows=rows)
    assert unicite_parametre_par_station_date_profondeur(ctx) == []


def test_no_echantillon_laboratoire_duplique(make_context):
    rows = [{"rpc_no_echan_labor": "ECH-1"}, {"rpc_no_echan_labor": "ECH-1"}]
    ctx = make_context(LAYER, {}, all_rows=rows)
    issues = unicite_no_echantillon_laboratoire(ctx)
    assert len(issues) == 1
    assert issues[0].code == "RESUL_ANALY_NO_ECHAN_LABOR_DUPLIQUE"


def test_no_echantillon_laboratoire_vides_ignores(make_context):
    """Plusieurs enregistrements sans numéro de laboratoire ne sont pas des doublons."""
    rows = [{"rpc_no_echan_labor": None}, {"rpc_no_echan_labor": None}, {"rpc_no_echan_labor": ""}]
    ctx = make_context(LAYER, {}, all_rows=rows)
    assert unicite_no_echantillon_laboratoire(ctx) == []


# --------------------------------------------------------------------- champs obligatoires
def test_champs_obligatoires_simples_enregistres():
    codes = {r.name for r in get_rules(LAYER, kind=RuleKind.VALIDATION)}
    assert "required_field_rpc_no" in codes
    assert "required_field_ppc_code" in codes


def test_appareil_ou_autre_appareil_requis(make_context):
    ctx = make_context(LAYER, {"app_code": None, "rpc_nom_autre_appar": None})
    issues = champs_obligatoires_conditionnels(ctx)
    assert any(i.code == "RESUL_ANALY_APPAREIL_REQUIS" for i in issues)


def test_appareil_renseigne_no_error(make_context):
    ctx = make_context(LAYER, {"app_code": "YSI", "rpc_ind_analy_labor": "NON", "rpc_val_resul": 7})
    assert champs_obligatoires_conditionnels(ctx) == []


def test_resultat_ou_teinte_requis_si_analyse_terrain(make_context):
    ctx = make_context(LAYER, {"app_code": "YSI", "rpc_ind_analy_labor": "NON",
                                "rpc_val_resul": None, "res_code": None})
    issues = champs_obligatoires_conditionnels(ctx)
    assert any(i.code == "RESUL_ANALY_RESULTAT_OU_TEINTE_REQUIS" for i in issues)


def test_teinte_suffit_si_analyse_terrain(make_context):
    ctx = make_context(LAYER, {"app_code": "YSI", "rpc_ind_analy_labor": "NON",
                                "rpc_val_resul": None, "res_code": "BRUN"})
    assert champs_obligatoires_conditionnels(ctx) == []


def test_no_echantillon_et_laboratoire_requis_si_analyse_labo(make_context):
    ctx = make_context(LAYER, {"app_code": "YSI", "rpc_ind_analy_labor": "OUI",
                                "rpc_no_echan_labor": None, "lab_code": None,
                                "rpc_nom_autre_labor": None})
    codes = {i.code for i in champs_obligatoires_conditionnels(ctx)}
    assert "RESUL_ANALY_NO_ECHAN_LABOR_REQUIS" in codes
    assert "RESUL_ANALY_LABORATOIRE_REQUIS" in codes


def test_analyse_labo_complete_no_error(make_context):
    ctx = make_context(LAYER, {"app_code": "YSI", "rpc_ind_analy_labor": "OUI",
                                "rpc_no_echan_labor": "ECH-1", "lab_code": "LAB1"})
    assert champs_obligatoires_conditionnels(ctx) == []
