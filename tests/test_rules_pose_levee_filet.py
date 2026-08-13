import datetime as dt

from core.registry import get_rules
from core.rule_base import RuleKind
from rules.pose_levee_filet import (
    date_levee_lendemain_pose,
    effort_peche_coherent,
    pose_avant_levee,
)


def test_date_levee_assignee_au_lendemain_depuis_chaine(make_context):
    row = {"plf_date_pose": "2024-06-01", "plf_date_levee": None}
    ctx = make_context("pose_levee_filet", row)
    date_levee_lendemain_pose(ctx)
    assert row["plf_date_levee"] == dt.date(2024, 6, 2)


def test_date_levee_assignee_au_lendemain_depuis_date(make_context):
    row = {"plf_date_pose": dt.date(2024, 6, 1), "plf_date_levee": None}
    ctx = make_context("pose_levee_filet", row)
    date_levee_lendemain_pose(ctx)
    assert row["plf_date_levee"] == dt.date(2024, 6, 2)


def test_date_levee_non_ecrasee_si_deja_saisie(make_context):
    row = {"plf_date_pose": "2024-06-01", "plf_date_levee": dt.date(2024, 6, 10)}
    ctx = make_context("pose_levee_filet", row)
    date_levee_lendemain_pose(ctx)
    assert row["plf_date_levee"] == dt.date(2024, 6, 10)


def test_date_levee_ignoree_sans_date_pose(make_context):
    row = {"plf_date_pose": None, "plf_date_levee": None}
    ctx = make_context("pose_levee_filet", row)
    date_levee_lendemain_pose(ctx)
    assert row["plf_date_levee"] is None


# --------------------------------------------------------------------- date de pose par défaut + bornes
def _transform(nom):
    return next(r for r in get_rules("pose_levee_filet", kind=RuleKind.TRANSFORM) if r.name == nom)


def test_date_pose_defaut_depuis_infor_gener(make_context):
    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "plf_date_pose": None}
    ctx = make_context("pose_levee_filet", row, layers={
        "infor_gener": [{"une_code_ident": "UE1", "mes_no_seq": 1,
                          "ing_date_debut_inven": "2024-06-01", "ing_date_fin_inven": "2024-09-01"}],
    })
    _transform("default_if_empty_plf_date_pose").run(ctx)
    assert row["plf_date_pose"] == "2024-06-01"


def test_date_pose_hors_bornes_triggers_error(make_context):
    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "plf_date_pose": "2024-12-01"}
    ctx = make_context("pose_levee_filet", row, layers={
        "infor_gener": [{"une_code_ident": "UE1", "mes_no_seq": 1,
                          "ing_date_debut_inven": "2024-06-01", "ing_date_fin_inven": "2024-09-01"}],
    })
    issues = _transform("default_if_empty_plf_date_pose").run(ctx)
    assert len(issues) == 1
    assert issues[0].code == "POSE_LEVEE_DATE_POSE_HORS_BORNES"


def test_date_pose_defaut_precede_calcul_date_levee():
    """La date de pose doit être posée avant que la date de levée n'en soit
    dérivée : c'est l'ordre d'exécution (order) qui le garantit."""
    ordres = {r.name: r.order for r in get_rules("pose_levee_filet", kind=RuleKind.TRANSFORM)}
    assert ordres["default_if_empty_plf_date_pose"] < ordres["date_levee_lendemain_pose"]


# --------------------------------------------------------------------- pose_avant_levee
def test_pose_apres_levee_triggers_error(make_context):
    ctx = make_context("pose_levee_filet", {
        "plf_date_pose": dt.date(2024, 6, 5), "plf_date_levee": dt.date(2024, 6, 2)})
    issues = pose_avant_levee(ctx)
    assert len(issues) == 1
    assert issues[0].code == "POSE_LEVEE_DATES_INCOHERENTES"


def test_pose_avant_levee_no_error(make_context):
    ctx = make_context("pose_levee_filet", {
        "plf_date_pose": dt.date(2024, 6, 1), "plf_date_levee": dt.date(2024, 6, 2)})
    assert pose_avant_levee(ctx) == []


def test_meme_date_heure_pose_apres_levee(make_context):
    ctx = make_context("pose_levee_filet", {
        "plf_date_pose": dt.date(2024, 6, 1), "plf_date_levee": dt.date(2024, 6, 1),
        "plf_val_hre_pose": 18, "plf_val_hre_levee": 9})
    issues = pose_avant_levee(ctx)
    assert len(issues) == 1
    assert issues[0].code == "POSE_LEVEE_HEURES_INCOHERENTES"


def test_meme_date_heure_pose_avant_levee(make_context):
    ctx = make_context("pose_levee_filet", {
        "plf_date_pose": dt.date(2024, 6, 1), "plf_date_levee": dt.date(2024, 6, 1),
        "plf_val_hre_pose": 9, "plf_val_hre_levee": 18})
    assert pose_avant_levee(ctx) == []


def test_meme_date_meme_heure_minute_pose_apres_levee(make_context):
    ctx = make_context("pose_levee_filet", {
        "plf_date_pose": dt.date(2024, 6, 1), "plf_date_levee": dt.date(2024, 6, 1),
        "plf_val_hre_pose": 9, "plf_val_hre_levee": 9,
        "plf_val_mi_pose": 45, "plf_val_mi_levee": 15})
    issues = pose_avant_levee(ctx)
    assert len(issues) == 1
    assert issues[0].code == "POSE_LEVEE_MINUTES_INCOHERENTES"


def test_meme_date_meme_heure_minute_pose_avant_levee(make_context):
    ctx = make_context("pose_levee_filet", {
        "plf_date_pose": dt.date(2024, 6, 1), "plf_date_levee": dt.date(2024, 6, 1),
        "plf_val_hre_pose": 9, "plf_val_hre_levee": 9,
        "plf_val_mi_pose": 15, "plf_val_mi_levee": 45})
    assert pose_avant_levee(ctx) == []


def test_minutes_egales_triggers_error(make_context):
    """Pose et levée strictement simultanées : la minute de pose doit être
    inférieure (et non égale) à la minute de levée."""
    ctx = make_context("pose_levee_filet", {
        "plf_date_pose": dt.date(2024, 6, 1), "plf_date_levee": dt.date(2024, 6, 1),
        "plf_val_hre_pose": 9, "plf_val_hre_levee": 9,
        "plf_val_mi_pose": 30, "plf_val_mi_levee": 30})
    assert len(pose_avant_levee(ctx)) == 1


def test_dates_absentes_no_error(make_context):
    ctx = make_context("pose_levee_filet", {"plf_date_pose": None, "plf_date_levee": None})
    assert pose_avant_levee(ctx) == []


# --------------------------------------------------------------------- effort_peche_coherent
def _ctx_effort(make_context, effort, superficie, tpc_code="PENT"):
    row = {"une_code_ident": "UE1", "mes_no_seq": 1, "pex_no_peche": 1, "ifd_effort": effort}
    return make_context("pose_levee_filet", row, layers={
        "peche_exper": [{"une_code_ident": "UE1", "mes_no_seq": 1, "pex_no_peche": 1,
                          "tpc_code": tpc_code}],
        "infor_gener": [{"une_code_ident": "UE1", "mes_no_seq": 1,
                          "ing_suprf_plan_eau_m": superficie}],
    })


def test_effort_insuffisant_petit_plan_eau(make_context):
    """Superficie <= 150 ha : l'effort doit être STRICTEMENT supérieur à 5."""
    ctx = _ctx_effort(make_context, effort=5, superficie=100)
    issues = effort_peche_coherent(ctx)
    assert len(issues) == 1
    assert issues[0].code == "POSE_LEVEE_EFFORT_INSUFFISANT"


def test_effort_suffisant_petit_plan_eau(make_context):
    ctx = _ctx_effort(make_context, effort=6, superficie=100)
    assert effort_peche_coherent(ctx) == []


def test_effort_minimum_inclusif_palier_300(make_context):
    """150 < superficie <= 300 : minimum de 8, inclusif."""
    assert effort_peche_coherent(_ctx_effort(make_context, effort=8, superficie=200)) == []
    assert len(effort_peche_coherent(_ctx_effort(make_context, effort=7, superficie=200))) == 1


def test_effort_palier_1000(make_context):
    assert effort_peche_coherent(_ctx_effort(make_context, effort=10, superficie=800)) == []
    assert len(effort_peche_coherent(_ctx_effort(make_context, effort=9, superficie=800))) == 1


def test_effort_borne_superieure_palier_5000(make_context):
    """1000 < superficie <= 5000 : effort compris entre 10 et 50."""
    assert effort_peche_coherent(_ctx_effort(make_context, effort=30, superficie=3000)) == []
    issues = effort_peche_coherent(_ctx_effort(make_context, effort=60, superficie=3000))
    assert len(issues) == 1
    assert issues[0].code == "POSE_LEVEE_EFFORT_EXCESSIF"


def test_effort_grand_plan_eau(make_context):
    assert effort_peche_coherent(_ctx_effort(make_context, effort=50, superficie=9000)) == []
    assert len(effort_peche_coherent(_ctx_effort(make_context, effort=49, superficie=9000))) == 1


def test_effort_ignore_si_type_peche_different(make_context):
    ctx = _ctx_effort(make_context, effort=1, superficie=100, tpc_code="PENOF")
    assert effort_peche_coherent(ctx) == []


def test_effort_ignore_sans_superficie(make_context):
    ctx = _ctx_effort(make_context, effort=1, superficie=None)
    assert effort_peche_coherent(ctx) == []


def test_effort_absent_no_error(make_context):
    ctx = _ctx_effort(make_context, effort=None, superficie=100)
    assert effort_peche_coherent(ctx) == []


# --------------------------------------------------------------------- champs obligatoires
def test_champs_obligatoires_enregistres():
    codes = {r.name for r in get_rules("pose_levee_filet", kind=RuleKind.VALIDATION)}
    for champ in ("plf_no_pose_levee", "plf_no_stati", "plf_date_pose", "plf_latit", "plf_longi"):
        assert f"required_field_{champ}" in codes
