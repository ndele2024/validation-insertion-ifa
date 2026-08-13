import pytest

from rules.detail_speci import (
    assigner_no_specimen_unique,
    assigner_no_vial,
    coefficient_condition_plausible,
    contenu_stomacal_coherent,
    contenu_stomacal_poisson_autofill,
    emplacement_coherent,
    especes_contenu_stomacal_coherentes,
    etiquettes_genetique_contamination_autofill,
    marquage_coherent,
    panneau_filet_autofill,
    peche_parente_complete,
    types_structure_coherents,
)


# --------------------------------------------------------------------- contenu stomacal
def test_contenu_stomacal_incoherent_quand_vide_et_autre_coche(make_context):
    row = {"dsp_ind_conte_stoma_vide": "oui", "dsp_ind_conte_stoma_insec": "oui"}
    ctx = make_context("detail_speci", row)
    issues = contenu_stomacal_coherent(ctx)
    assert len(issues) == 1
    assert issues[0].code == "DETAIL_SPECI_CONTENU_STOMACAL_INCOHERENT"


def test_contenu_stomacal_coherent_quand_vide_seul(make_context):
    row = {"dsp_ind_conte_stoma_vide": "oui", "dsp_ind_conte_stoma_insec": "non"}
    ctx = make_context("detail_speci", row)
    assert contenu_stomacal_coherent(ctx) == []


def test_contenu_stomacal_poisson_autofill_active_indicateur(make_context):
    row = {"epo_code_stoma_1": "BRBR", "dsp_ind_conte_stoma_poiss": "non"}
    ctx = make_context("detail_speci", row)
    contenu_stomacal_poisson_autofill(ctx)
    assert row["dsp_ind_conte_stoma_poiss"] == "oui"


def test_contenu_stomacal_poisson_autofill_ignore_sans_espece(make_context):
    row = {"epo_code_stoma_1": None, "epo_code_stoma_2": None, "dsp_ind_conte_stoma_poiss": "non"}
    ctx = make_context("detail_speci", row)
    contenu_stomacal_poisson_autofill(ctx)
    assert row["dsp_ind_conte_stoma_poiss"] == "non"


def test_especes_stomacal_identiques_erreur(make_context):
    ctx = make_context("detail_speci", {"epo_code_stoma_1": "BRBR", "epo_code_stoma_2": "BRBR"})
    issues = especes_contenu_stomacal_coherentes(ctx)
    assert any(i.code == "DETAIL_SPECI_ESPECES_STOMACAL_IDENTIQUES" for i in issues)


def test_espece_stomacal_2_sans_1_erreur(make_context):
    ctx = make_context("detail_speci", {"epo_code_stoma_1": None, "epo_code_stoma_2": "BRBR"})
    issues = especes_contenu_stomacal_coherentes(ctx)
    assert any(i.code == "DETAIL_SPECI_ESPECE_STOMACAL_2_SANS_1" for i in issues)


def test_especes_stomacal_differentes_ok(make_context):
    ctx = make_context("detail_speci", {"epo_code_stoma_1": "BRBR", "epo_code_stoma_2": "OMOM"})
    assert especes_contenu_stomacal_coherentes(ctx) == []


# --------------------------------------------------------------------- emplacement
def test_emplacement_requis_si_info_dispo(make_context):
    ctx = make_context("detail_speci", {"dsp_ind_infor_suppl_dispo": "oui", "dsp_val_empla": None})
    issues = emplacement_coherent(ctx)
    assert len(issues) == 1 and issues[0].code == "DETAIL_SPECI_EMPLACEMENT_REQUIS"


def test_indicateur_requis_si_emplacement_saisi(make_context):
    ctx = make_context("detail_speci", {"dsp_ind_infor_suppl_dispo": "non", "dsp_val_empla": "Sous le quai"})
    issues = emplacement_coherent(ctx)
    assert len(issues) == 1 and issues[0].code == "DETAIL_SPECI_INDICATEUR_INFOR_SUPPL_REQUIS"


def test_emplacement_coherent_les_deux_vides(make_context):
    ctx = make_context("detail_speci", {"dsp_ind_infor_suppl_dispo": "non", "dsp_val_empla": None})
    assert emplacement_coherent(ctx) == []


# --------------------------------------------------------------------- types de structure
def test_types_structure_identiques_erreur(make_context):
    ctx = make_context("detail_speci", {"tsa_code_1": "OT", "tsa_code_2": "OT"})
    issues = types_structure_coherents(ctx)
    assert any(i.code == "DETAIL_SPECI_TYPES_STRUCTURE_IDENTIQUES" for i in issues)


def test_type_structure_2_sans_1_erreur(make_context):
    ctx = make_context("detail_speci", {"tsa_code_1": None, "tsa_code_2": "OT"})
    issues = types_structure_coherents(ctx)
    assert any(i.code == "DETAIL_SPECI_TYPE_STRUCTURE_2_SANS_1" for i in issues)


def test_echantillon_et_age_sans_type_structure_erreur(make_context):
    ctx = make_context("detail_speci", {
        "dsp_no_echan_labor_1": "A12", "dsp_age_1": 5, "tsa_code_1": "AS",
    })
    issues = types_structure_coherents(ctx)
    assert any(i.code == "DETAIL_SPECI_TYPE_STRUCTURE_1_REQUIS" for i in issues)


def test_types_structure_aucune_anomalie(make_context):
    ctx = make_context("detail_speci", {
        "tsa_code_1": "OT", "tsa_code_2": "AS",
        "dsp_no_echan_labor_1": "A12", "dsp_age_1": 5,
    })
    assert types_structure_coherents(ctx) == []


# --------------------------------------------------------------------- marquage
def test_marquage_statut_requis(make_context):
    ctx = make_context("detail_speci", {"tym_code": "CARLIN", "sma_code": None, "cou_code": "ROUGE", "dsp_no_etiqu_marqu": "1"})
    issues = marquage_coherent(ctx)
    assert any(i.code == "DETAIL_SPECI_STATUT_MARQUAGE_REQUIS" for i in issues)


def test_marquage_description_requise_pour_type_avec_description(make_context):
    ctx = make_context("detail_speci", {"tym_code": "CHIM", "sma_code": "OK", "dsp_descr_etiqu_marqu": None})
    issues = marquage_coherent(ctx)
    assert any(i.code == "DETAIL_SPECI_DESCRIPTION_ETIQUETTE_REQUISE" for i in issues)


def test_marquage_couleur_et_numero_requis_pour_type_avec_etiquette(make_context):
    ctx = make_context("detail_speci", {"tym_code": "SPAGH", "sma_code": "OK", "cou_code": None, "dsp_no_etiqu_marqu": None})
    issues = marquage_coherent(ctx)
    codes = {i.code for i in issues}
    assert "DETAIL_SPECI_COULEUR_ETIQUETTE_REQUISE" in codes
    assert "DETAIL_SPECI_NO_ETIQUETTE_REQUIS" in codes


def test_marquage_aucun_type_aucune_anomalie(make_context):
    ctx = make_context("detail_speci", {"tym_code": None})
    assert marquage_coherent(ctx) == []


# --------------------------------------------------------------------- étiquettes génétique/contamination
def test_etiquettes_genetique_contamination_recopiees(make_context):
    row = {"dsp_no_echan_labor_1": "A12", "dsp_no_etiqu_genet": None, "dsp_no_etiqu_conta": None}
    ctx = make_context("detail_speci", row)
    etiquettes_genetique_contamination_autofill(ctx)
    assert row["dsp_no_etiqu_genet"] == "A12"
    assert row["dsp_no_etiqu_conta"] == "A12"


def test_etiquettes_non_ecrasees_si_deja_renseignees(make_context):
    row = {"dsp_no_echan_labor_1": "A12", "dsp_no_etiqu_genet": "DEJA", "dsp_no_etiqu_conta": None}
    ctx = make_context("detail_speci", row)
    etiquettes_genetique_contamination_autofill(ctx)
    assert row["dsp_no_etiqu_genet"] == "DEJA"
    assert row["dsp_no_etiqu_conta"] == "A12"


# --------------------------------------------------------------------- panneau du filet
def test_panneau_filet_autofill_assigne_selon_maille(make_context):
    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "pex_no_peche": 1, "dsp_val_grand_maill_mm": 38}
    ctx = make_context("detail_speci", row, layers={
        "peche_exper": [{"une_code_ident": "UE1", "mes_no_seq": 1, "pex_no_peche": 1, "tpc_code": "PENT"}],
    })
    panneau_filet_autofill(ctx)
    assert row["cde_code"] == "PAN2"


def test_panneau_filet_autofill_groupe_pecpm(make_context):
    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "pex_no_peche": 1, "dsp_val_grand_maill_mm": 13}
    ctx = make_context("detail_speci", row, layers={
        "peche_exper": [{"une_code_ident": "UE1", "mes_no_seq": 1, "pex_no_peche": 1, "tpc_code": "PECPM"}],
    })
    panneau_filet_autofill(ctx)
    assert row["cde_code"] == "PAN4"


def test_panneau_filet_autofill_sans_peche_parente_ne_fait_rien(make_context):
    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "pex_no_peche": 1, "dsp_val_grand_maill_mm": 38}
    ctx = make_context("detail_speci", row)
    panneau_filet_autofill(ctx)
    assert "cde_code" not in row


def test_panneau_filet_autofill_maille_inconnue_ne_fait_rien(make_context):
    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "pex_no_peche": 1, "dsp_val_grand_maill_mm": 9999}
    ctx = make_context("detail_speci", row, layers={
        "peche_exper": [{"une_code_ident": "UE1", "mes_no_seq": 1, "pex_no_peche": 1, "tpc_code": "PENT"}],
    })
    panneau_filet_autofill(ctx)
    assert "cde_code" not in row


# --------------------------------------------------------------------- coefficient de condition
def test_coefficient_condition_hors_bornes_avertissement(make_context):
    # Masse trop faible pour la longueur -> coefficient sous la borne basse.
    row = {"efa_code": "CACA", "dsp_long_tot_max_m": 300, "dsp_val_masse_g": 100}
    ctx = make_context("detail_speci", row)
    issues = coefficient_condition_plausible(ctx)
    assert len(issues) == 1
    assert issues[0].severity.value == "warning"


def test_coefficient_condition_dans_les_bornes_aucune_anomalie(make_context):
    # K = masse*100000/longueur^3 ; viser ~1.0 pour CACA (bornes 0.8-1.3).
    longueur = 300.0
    masse = 1.0 * (longueur ** 3) / 100000
    row = {"efa_code": "CACA", "dsp_long_tot_max_m": longueur, "dsp_val_masse_g": masse}
    ctx = make_context("detail_speci", row)
    assert coefficient_condition_plausible(ctx) == []


def test_coefficient_condition_espece_non_couverte_ignoree(make_context):
    row = {"efa_code": "SACA", "dsp_long_tot_max_m": 300, "dsp_val_masse_g": 1}
    ctx = make_context("detail_speci", row)
    assert coefficient_condition_plausible(ctx) == []


@pytest.mark.parametrize("espece,bornes", [
    ("CACA", (0.8, 1.3)), ("COAR", (0.6, 1.1)), ("COCL", (0.6, 1.4)),
    ("ESLU", (0.5, 0.9)),
    # PEFL / SAFO / CACO partagent les mêmes bornes selon DETAIL_SPECI.groovy.
    ("PEFL", (0.8, 1.4)), ("SAFO", (0.8, 1.4)), ("CACO", (0.8, 1.4)),
    ("SANA", (0.6, 1.2)), ("SASA", (0.7, 1.4)),
    # SAAL / SAVI partagent également les mêmes bornes.
    ("SAAL", (0.5, 0.9)), ("SAVI", (0.5, 0.9)),
])
def test_coefficient_condition_bornes_par_espece(make_context, espece, bornes):
    """Vérifie que chaque espèce listée dans DETAIL_SPECI.groovy est couverte
    avec les bonnes bornes : un coefficient au centre de la plage ne déclenche
    rien, un coefficient sous la borne basse déclenche un avertissement."""
    low, high = bornes
    longueur = 300.0

    milieu = (low + high) / 2
    row_ok = {"efa_code": espece, "dsp_long_tot_max_m": longueur,
              "dsp_val_masse_g": milieu * (longueur ** 3) / 100000}
    assert coefficient_condition_plausible(make_context("detail_speci", row_ok)) == []

    row_bas = {"efa_code": espece, "dsp_long_tot_max_m": longueur,
               "dsp_val_masse_g": (low - 0.1) * (longueur ** 3) / 100000}
    assert len(coefficient_condition_plausible(make_context("detail_speci", row_bas))) == 1

    row_haut = {"efa_code": espece, "dsp_long_tot_max_m": longueur,
                "dsp_val_masse_g": (high + 0.1) * (longueur ** 3) / 100000}
    assert len(coefficient_condition_plausible(make_context("detail_speci", row_haut))) == 1


# --------------------------------------------------------------------- pêche parente complète
def test_peche_parente_incomplete_erreur(make_context):
    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "pex_no_peche": 1, "plf_no_pose_levee": 1}
    ctx = make_context("detail_speci", row, layers={
        "peche_exper": [{"une_code_ident": "UE1", "mes_no_seq": 1, "pex_no_peche": 1,
                          "tpc_code": None, "efa_code": "SACA", "teg_code": "FILET"}],
    })
    issues = peche_parente_complete(ctx)
    assert any(i.code == "DETAIL_SPECI_PECHE_PARENTE_INCOMPLETE" for i in issues)


def test_pose_levee_parente_incomplete_erreur(make_context):
    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "pex_no_peche": 1, "plf_no_pose_levee": 1}
    ctx = make_context("detail_speci", row, layers={
        "pose_levee_filet": [{"une_code_ident": "UE1", "mes_no_seq": 1, "pex_no_peche": 1,
                               "plf_no_pose_levee": 1, "plf_date_pose": "2024-06-01", "plf_date_levee": None}],
    })
    issues = peche_parente_complete(ctx)
    assert any(i.code == "DETAIL_SPECI_POSE_LEVEE_PARENTE_INCOMPLETE" for i in issues)


def test_peche_et_pose_completes_aucune_erreur(make_context):
    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "pex_no_peche": 1, "plf_no_pose_levee": 1}
    ctx = make_context("detail_speci", row, layers={
        "peche_exper": [{"une_code_ident": "UE1", "mes_no_seq": 1, "pex_no_peche": 1,
                          "tpc_code": "PENT", "efa_code": "SACA", "teg_code": "FILET"}],
        "pose_levee_filet": [{"une_code_ident": "UE1", "mes_no_seq": 1, "pex_no_peche": 1,
                               "plf_no_pose_levee": 1, "plf_date_pose": "2024-06-01", "plf_date_levee": "2024-06-02"}],
    })
    assert peche_parente_complete(ctx) == []


# --------------------------------------------------------------------- utilitaires de numérotation
def test_assigner_no_vial_retourne_none_si_pas_otolithe():
    assert assigner_no_vial([], {"type_structure_1": "EC"}) is None


def test_assigner_no_vial_incremente_le_plus_grand_numero():
    specimens = [
        {"echantillon_1": "A10", "type_structure_1": "OT"},
        {"echantillon_1": "A25", "type_structure_1": "OT"},
        {"echantillon_1": "5", "type_structure_1": "OT"},
    ]
    nouveau = assigner_no_vial(specimens, {"type_structure_1": "OT"})
    assert nouveau == "A26"


def test_assigner_no_vial_sans_lettre():
    specimens = [{"echantillon_1": "10", "type_structure_1": "OT"}]
    nouveau = assigner_no_vial(specimens, {"type_structure_1": "OT"})
    assert nouveau == "11"


def test_assigner_no_specimen_unique_vide_retourne_vide():
    assert assigner_no_specimen_unique([]) == []


def test_assigner_no_specimen_unique_incremente_et_copie_espece():
    specimens = [
        {"no_seq": 1.0, "espece": "SACA"},
        {"no_seq": 2.0, "espece": "CACA"},
        {"no_seq": 0.0, "espece": ""},  # nouveau spécimen à compléter
    ]
    resultat = assigner_no_specimen_unique(specimens)
    assert resultat[-1]["no_seq"] == 3.0
    # "Avant-dernier" = index -2 = le spécimen "CACA", pas le premier.
    assert resultat[-1]["espece"] == "CACA"
