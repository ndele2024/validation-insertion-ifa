from core.registry import get_rules
from core.rule_base import RuleKind
from rules.peche_exper import (
    CARACTERISTIQUES_PAR_TYPE_PECHE,
    caracteristiques_engin_autofill,
    subdivision_coherente,
)


# --------------------------------------------------------------------- caracteristiques_engin_autofill
def test_caracteristiques_assignees_selon_type_peche(make_context):
    row = {"tpc_code": "PENDJ"}
    ctx = make_context("peche_exper", row)
    caracteristiques_engin_autofill(ctx)
    assert row["efa_code"] == "SAVI"
    assert row["teg_code"] == "FX"
    assert "8 panneaux" in row["pex_descr_carac"]


def test_caracteristiques_penof_vise_safo(make_context):
    row = {"tpc_code": "PENOF"}
    ctx = make_context("peche_exper", row)
    caracteristiques_engin_autofill(ctx)
    assert row["efa_code"] == "SAFO"


def test_caracteristiques_pecpm_vise_multi(make_context):
    row = {"tpc_code": "PECPM"}
    ctx = make_context("peche_exper", row)
    caracteristiques_engin_autofill(ctx)
    assert row["efa_code"] == "MULTI"


def test_caracteristiques_inchangees_si_type_peche_inconnu(make_context):
    row = {"tpc_code": "INCONNU", "efa_code": "SACA"}
    ctx = make_context("peche_exper", row)
    caracteristiques_engin_autofill(ctx)
    assert row["efa_code"] == "SACA"
    assert "pex_descr_carac" not in row


def test_tous_les_types_peche_assignent_les_trois_champs(make_context):
    """Chaque entrée de la table doit fournir les 3 valeurs prescrites."""
    for tpc_code in CARACTERISTIQUES_PAR_TYPE_PECHE:
        row = {"tpc_code": tpc_code}
        ctx = make_context("peche_exper", row)
        caracteristiques_engin_autofill(ctx)
        assert row["pex_descr_carac"] and row["efa_code"] and row["teg_code"]


# --------------------------------------------------------------------- subdivision_coherente
def test_subdivision_requise_pour_pendj(make_context):
    ctx = make_context("peche_exper", {"tpc_code": "PENDJ", "sub_code": None})
    issues = subdivision_coherente(ctx)
    assert len(issues) == 1
    assert issues[0].code == "PECHE_EXPER_SUBDIVISION_INVALIDE"


def test_subdivision_invalide_pour_pendj(make_context):
    ctx = make_context("peche_exper", {"tpc_code": "PENDJ", "sub_code": "3E"})
    assert len(subdivision_coherente(ctx)) == 1


def test_subdivision_valide_pour_pendj(make_context):
    for valeur in ("1ÈRE", "2E", "COMPLÈTE"):
        ctx = make_context("peche_exper", {"tpc_code": "PENDJ", "sub_code": valeur})
        assert subdivision_coherente(ctx) == []


def test_subdivision_ignoree_pour_autre_type_peche(make_context):
    ctx = make_context("peche_exper", {"tpc_code": "PENT", "sub_code": None})
    assert subdivision_coherente(ctx) == []


# --------------------------------------------------------------------- caractéristiques requises si engin "AU"
def _rule(nom):
    return next(r for r in get_rules("peche_exper", kind=RuleKind.VALIDATION) if r.name == nom)


def test_caracteristiques_requises_si_engin_autre(make_context):
    rule = _rule("required_field_pex_descr_carac")
    ctx = make_context("peche_exper", {"teg_code": "AU", "pex_descr_carac": None})
    issues = rule.run(ctx)
    assert len(issues) == 1
    assert issues[0].code == "PECHE_EXPER_CARACTERISTIQUES_REQUISES"


def test_caracteristiques_non_requises_si_engin_standard(make_context):
    rule = _rule("required_field_pex_descr_carac")
    ctx = make_context("peche_exper", {"teg_code": "FX", "pex_descr_carac": None})
    assert rule.run(ctx) == []


# --------------------------------------------------------------------- espèce visée interdite
def test_espece_visee_interdite(make_context):
    rule = _rule("forbidden_values_efa_code")
    for code in ("AU", "RIEN", "NI", "POIS"):
        ctx = make_context("peche_exper", {"efa_code": code})
        assert len(rule.run(ctx)) == 1


def test_espece_visee_autorisee(make_context):
    rule = _rule("forbidden_values_efa_code")
    ctx = make_context("peche_exper", {"efa_code": "SAVI"})
    assert rule.run(ctx) == []


# --------------------------------------------------------------------- champs obligatoires
def test_champs_obligatoires_enregistres():
    codes = {r.name for r in get_rules("peche_exper", kind=RuleKind.VALIDATION)}
    for champ in ("pex_no_peche", "tpc_code", "efa_code", "teg_code"):
        assert f"required_field_{champ}" in codes
