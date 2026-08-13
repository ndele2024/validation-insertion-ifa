from rules.denom_espec import (
    categorie_denombrement_defaut,
    champs_obligatoires_conditionnels,
    nombre_capture_positif_si_espece_comptee,
    nombre_capture_zero_si_aucune_espece,
)


def test_nombre_capture_force_a_zero_si_aucune_espece(make_context):
    row = {"efa_code": "RIEN", "des_nb_captu": 15}
    ctx = make_context("denom_espec", row)
    nombre_capture_zero_si_aucune_espece(ctx)
    assert row["des_nb_captu"] == 0


def test_nombre_capture_inchange_si_espece_renseignee(make_context):
    row = {"efa_code": "SACA", "des_nb_captu": 15}
    ctx = make_context("denom_espec", row)
    nombre_capture_zero_si_aucune_espece(ctx)
    assert row["des_nb_captu"] == 15


def test_categorie_denombrement_defaut_assignee(make_context):
    row = {"cde_code": None}
    ctx = make_context("denom_espec", row)
    categorie_denombrement_defaut(ctx)
    assert row["cde_code"] == "-"


def test_categorie_denombrement_non_ecrasee(make_context):
    row = {"cde_code": "PAN1"}
    ctx = make_context("denom_espec", row)
    categorie_denombrement_defaut(ctx)
    assert row["cde_code"] == "PAN1"


def test_nb_captu_requis_si_espece_renseignee(make_context):
    ctx = make_context("denom_espec", {"efa_code": "SACA", "des_nb_captu": None})
    issues = champs_obligatoires_conditionnels(ctx)
    assert any(i.code == "DENOM_ESPEC_NB_CAPTU_REQUIS" for i in issues)


def test_nb_captu_non_requis_si_aucune_espece(make_context):
    ctx = make_context("denom_espec", {"efa_code": "RIEN", "des_nb_captu": None})
    issues = champs_obligatoires_conditionnels(ctx)
    assert not any(i.code == "DENOM_ESPEC_NB_CAPTU_REQUIS" for i in issues)


def test_nb_pese_requis_si_masse_saisie(make_context):
    ctx = make_context("denom_espec", {"efa_code": "RIEN", "des_val_masse_total_g": 120, "des_nb_pese": None})
    issues = champs_obligatoires_conditionnels(ctx)
    assert any(i.code == "DENOM_ESPEC_NB_PESE_REQUIS" for i in issues)


def test_masse_requise_si_nb_pese_saisi(make_context):
    ctx = make_context("denom_espec", {"efa_code": "RIEN", "des_nb_pese": 4, "des_val_masse_total_g": None})
    issues = champs_obligatoires_conditionnels(ctx)
    assert any(i.code == "DENOM_ESPEC_MASSE_REQUISE" for i in issues)


def test_aucune_anomalie_quand_tout_coherent(make_context):
    ctx = make_context("denom_espec", {
        "efa_code": "SACA", "des_nb_captu": 4, "des_nb_pese": 4, "des_val_masse_total_g": 240,
    })
    assert champs_obligatoires_conditionnels(ctx) == []


# --------------------------------------------------------------------- nombre_capture_positif_si_espece_comptee
def test_nb_captu_zero_triggers_error_pour_espece_ordinaire(make_context):
    ctx = make_context("denom_espec", {"efa_code": "SACA", "des_nb_captu": 0})
    issues = nombre_capture_positif_si_espece_comptee(ctx)
    assert len(issues) == 1
    assert issues[0].code == "DENOM_ESPEC_NB_CAPTU_DOIT_ETRE_POSITIF"


def test_nb_captu_positif_no_error(make_context):
    ctx = make_context("denom_espec", {"efa_code": "SACA", "des_nb_captu": 3})
    assert nombre_capture_positif_si_espece_comptee(ctx) == []


def test_nb_captu_absent_no_error(make_context):
    """Couvert séparément par DENOM_ESPEC_NB_CAPTU_REQUIS (champs_obligatoires_conditionnels)."""
    ctx = make_context("denom_espec", {"efa_code": "SACA", "des_nb_captu": None})
    assert nombre_capture_positif_si_espece_comptee(ctx) == []


def test_nb_captu_zero_ignore_si_espece_rien(make_context):
    ctx = make_context("denom_espec", {"efa_code": "RIEN", "des_nb_captu": 0})
    assert nombre_capture_positif_si_espece_comptee(ctx) == []


def test_nb_captu_zero_ignore_pour_especes_nilab(make_context):
    for code in ("NILAB1", "NILAB2", "NILAB3"):
        ctx = make_context("denom_espec", {"efa_code": code, "des_nb_captu": 0})
        assert nombre_capture_positif_si_espece_comptee(ctx) == []


def test_nb_captu_ignore_si_aucune_espece_visee(make_context):
    ctx = make_context("denom_espec", {"efa_code": None, "des_nb_captu": 0})
    assert nombre_capture_positif_si_espece_comptee(ctx) == []
