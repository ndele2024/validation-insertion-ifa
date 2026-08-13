from rules.analy_physi_chimi import (
    appareil_autofill,
    appareil_requis_si_profil,
)


def test_appareil_autofill_sets_autre_when_only_description_given(make_context):
    row = {"app_code": None, "phc_nom_autre_appar": "Sonde XYZ modèle 3"}
    ctx = make_context("analy_physi_chimi", row)
    appareil_autofill(ctx)
    assert row["app_code"] == "AUTRE"
    assert row["phc_nom_autre_appar"] == "Sonde XYZ modèle 3"


def test_appareil_autofill_defaults_description_to_inconnu_when_blank_text(make_context):
    """Un texte composé uniquement d'espaces est considéré "saisi" (l'utilisateur
    a interagi avec le champ) : Appareil passe à AUTRE, et comme le texte
    trimé est vide, la description est remplacée par "inconnu"."""
    row = {"app_code": None, "phc_nom_autre_appar": "   "}
    ctx = make_context("analy_physi_chimi", row)
    appareil_autofill(ctx)
    assert row["app_code"] == "AUTRE"
    assert row["phc_nom_autre_appar"] == "inconnu"


def test_appareil_autofill_does_nothing_when_autre_appareil_empty(make_context):
    row = {"app_code": None, "phc_nom_autre_appar": None}
    ctx = make_context("analy_physi_chimi", row)
    appareil_autofill(ctx)
    assert row["app_code"] is None
    assert row["phc_nom_autre_appar"] is None


def test_appareil_autofill_does_nothing_when_appareil_already_set(make_context):
    row = {"app_code": "SONDE_HACH", "phc_nom_autre_appar": "Autre chose"}
    ctx = make_context("analy_physi_chimi", row)
    appareil_autofill(ctx)
    assert row["app_code"] == "SONDE_HACH"


def test_appareil_requis_si_profil_triggers_error_when_missing(make_context):
    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "phc_no_stati": 1, "app_code": None}
    ctx = make_context("analy_physi_chimi", row, layers={
        "profi_mesur": [{"une_code_ident": "UE1", "mes_no_seq": 1, "phc_no_stati": 1, "pme_profd_m": 0.5}],
    })
    issues = appareil_requis_si_profil(ctx)
    assert len(issues) == 1
    assert issues[0].code == "ANALY_APPAREIL_REQUIS_SI_PROFIL"


def test_appareil_requis_si_profil_no_error_when_appareil_set(make_context):
    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "phc_no_stati": 1, "app_code": "SONDE_HACH"}
    ctx = make_context("analy_physi_chimi", row, layers={
        "profi_mesur": [{"une_code_ident": "UE1", "mes_no_seq": 1, "phc_no_stati": 1, "pme_profd_m": 0.5}],
    })
    assert appareil_requis_si_profil(ctx) == []


def test_appareil_requis_si_profil_no_error_when_no_profile(make_context):
    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "phc_no_stati": 1, "app_code": None}
    ctx = make_context("analy_physi_chimi", row)
    assert appareil_requis_si_profil(ctx) == []
