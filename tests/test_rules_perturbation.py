from core.registry import get_rules
from core.rule_base import RuleKind
from rules.perturbation import superficie_calculee


def _rule(nom, kind=RuleKind.VALIDATION):
    return next(r for r in get_rules("perturbation", kind=kind) if r.name == nom)


# --------------------------------------------------------------------- date d'observation
def test_date_observation_defaut_depuis_infor_gener(make_context):
    rule = _rule("default_if_empty_per_date_obser", RuleKind.TRANSFORM)
    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "per_date_obser": None}
    ctx = make_context("perturbation", row, layers={
        "infor_gener": [{"une_code_ident": "UE1", "mes_no_seq": 1,
                          "ing_date_debut_inven": "2024-06-01", "ing_date_fin_inven": "2024-09-01"}],
    })
    rule.run(ctx)
    assert row["per_date_obser"] == "2024-06-01"


def test_date_observation_hors_bornes_triggers_error(make_context):
    rule = _rule("default_if_empty_per_date_obser", RuleKind.TRANSFORM)
    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "per_date_obser": "2025-01-01"}
    ctx = make_context("perturbation", row, layers={
        "infor_gener": [{"une_code_ident": "UE1", "mes_no_seq": 1,
                          "ing_date_debut_inven": "2024-06-01", "ing_date_fin_inven": "2024-09-01"}],
    })
    issues = rule.run(ctx)
    assert len(issues) == 1
    assert issues[0].code == "PERTURBATION_DATE_OBSER_HORS_BORNES"


# --------------------------------------------------------------------- superficie_calculee
def test_superficie_calculee_si_absente(make_context):
    row = {"per_suprf_m": None, "per_long_m": 10, "per_larg_m": 4}
    ctx = make_context("perturbation", row)
    superficie_calculee(ctx)
    assert row["per_suprf_m"] == 40


def test_superficie_non_ecrasee_si_deja_saisie(make_context):
    row = {"per_suprf_m": 7, "per_long_m": 10, "per_larg_m": 4}
    ctx = make_context("perturbation", row)
    superficie_calculee(ctx)
    assert row["per_suprf_m"] == 7


def test_superficie_non_calculee_si_largeur_absente(make_context):
    row = {"per_suprf_m": None, "per_long_m": 10, "per_larg_m": None}
    ctx = make_context("perturbation", row)
    superficie_calculee(ctx)
    assert row["per_suprf_m"] is None


# --------------------------------------------------------------------- commentaire si type "AU"
def test_commentaire_requis_si_type_autre(make_context):
    rule = _rule("required_field_per_com")
    ctx = make_context("perturbation", {"tpe_code": "AU", "per_com": None})
    issues = rule.run(ctx)
    assert len(issues) == 1
    assert issues[0].code == "PERTURBATION_COMMENTAIRE_REQUIS_SI_AUTRE"


def test_commentaire_non_requis_pour_autre_type(make_context):
    rule = _rule("required_field_per_com")
    ctx = make_context("perturbation", {"tpe_code": "BAR", "per_com": None})
    assert rule.run(ctx) == []


# --------------------------------------------------------------------- champs obligatoires
def test_champs_obligatoires_enregistres():
    codes = {r.name for r in get_rules("perturbation", kind=RuleKind.VALIDATION)}
    for champ in ("per_no_stati", "per_date_obser", "tpe_code", "per_latit", "per_longi"):
        assert f"required_field_{champ}" in codes
