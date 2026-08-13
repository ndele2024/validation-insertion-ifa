from rules.descr_habit import (
    profondeur_donnee_courant_defaut,
    superficie_calculee,
)


def test_profondeur_donnee_courant_defaut_assignee(make_context):
    row = {"dha_val_vites_coura": 0.8, "dha_prfd_vites_coura": None}
    ctx = make_context("descr_habit", row)
    profondeur_donnee_courant_defaut(ctx)
    assert row["dha_prfd_vites_coura"] == 0


def test_profondeur_donnee_courant_non_ecrasee(make_context):
    row = {"dha_val_vites_coura": 0.8, "dha_prfd_vites_coura": 2}
    ctx = make_context("descr_habit", row)
    profondeur_donnee_courant_defaut(ctx)
    assert row["dha_prfd_vites_coura"] == 2


def test_profondeur_donnee_courant_ignoree_sans_vitesse(make_context):
    row = {"dha_val_vites_coura": None, "dha_prfd_vites_coura": None}
    ctx = make_context("descr_habit", row)
    profondeur_donnee_courant_defaut(ctx)
    assert row["dha_prfd_vites_coura"] is None


def test_superficie_calculee_longueur_x_largeur(make_context):
    row = {"dha_long": 10, "dha_larg": 4, "dha_suprf": None}
    ctx = make_context("descr_habit", row)
    superficie_calculee(ctx)
    assert row["dha_suprf"] == 40


def test_superficie_non_calculee_si_donnees_incompletes(make_context):
    row = {"dha_long": 10, "dha_larg": None, "dha_suprf": None}
    ctx = make_context("descr_habit", row)
    superficie_calculee(ctx)
    assert row["dha_suprf"] is None
