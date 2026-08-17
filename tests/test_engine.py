"""
Tests d'intégration du moteur (core.engine.run) : utilisent un VRAI
GeoPackage (fixture sample_gpkg) et de VRAIES règles enregistrées
(rules.infor_gener), mais isolent la base de données (db_schema.load_schema
et inserter.insert_all sont remplacés par des doublures de test) pour ne
jamais dépendre d'une connexion PostgreSQL réelle.
"""

from __future__ import annotations

import json

from core import engine
from core.models import LAYER_BASE_DE_DONNEES, LayerSchema
from core.registry import clear_registry, register
from core.rule_base import RuleKind


def test_run_valid_data_triggers_insertion(monkeypatch, sample_gpkg):
    monkeypatch.setattr(engine.db_schema, "load_schema",
                         lambda conn, tables, pg_schema: {
                             t: LayerSchema(table=t) for t in tables
                         })
    inserted = {}
    monkeypatch.setattr(engine.inserter, "insert_all",
                         lambda layers, conn, pg_schema="ifa_data", schemas=None: inserted.setdefault("called", layers))

    report = engine.run(sample_gpkg, conn=object(), apply=True)

    assert report.is_valid
    assert report.inserted is True
    assert "called" in inserted
    assert report.record_counts == {"mesurage": 1, "infor_gener": 1}


def test_run_dry_run_never_inserts(monkeypatch, sample_gpkg):
    monkeypatch.setattr(engine.db_schema, "load_schema",
                         lambda conn, tables, pg_schema: {t: LayerSchema(table=t) for t in tables})
    called = []
    monkeypatch.setattr(engine.inserter, "insert_all", lambda *a, **k: called.append(True))

    report = engine.run(sample_gpkg, conn=object(), apply=False)

    assert report.is_valid
    assert report.inserted is False
    assert called == []


def test_run_blocks_insertion_when_db_rule_violated(monkeypatch, sample_gpkg):
    # infor_gener.ing_nom_plan_eau devient NOT NULL : la fixture sample_gpkg
    # le renseigne ("Lac Test"), donc on cible plutôt un champ qu'elle laisse
    # vide pour déclencher une vraie violation NOT NULL.
    monkeypatch.setattr(
        engine.db_schema, "load_schema",
        lambda conn, tables, pg_schema: {
            t: LayerSchema(table=t, not_null_columns=["champ_volontairement_absent"])
            for t in tables
        },
    )
    called = []
    monkeypatch.setattr(engine.inserter, "insert_all", lambda *a, **k: called.append(True))

    report = engine.run(sample_gpkg, conn=object(), apply=True)

    assert report.is_valid is False
    assert called == []
    assert any(i.code == "DB_NOT_NULL" for i in report.errors)


def test_run_applies_custom_transform_and_validation_rules(monkeypatch, sample_gpkg):
    """Exercice une règle métier réelle (rules.infor_gener) au travers du
    moteur complet, pour vérifier que TRANSFORM puis VALIDATION s'enchaînent
    correctement sur des données lues depuis un vrai GeoPackage."""
    monkeypatch.setattr(engine.db_schema, "load_schema",
                         lambda conn, tables, pg_schema: {t: LayerSchema(table=t) for t in tables})
    monkeypatch.setattr(engine.inserter, "insert_all", lambda *a, **k: None)

    report = engine.run(sample_gpkg, conn=object(), apply=True)

    # La fixture sample_gpkg n'a pas de territoire "LIBRE" -> aucune
    # anomalie liée à rules.infor_gener.territoire_libre_coherent attendue.
    assert not any(i.code == "INFOR_GENER_TERRITOIRE_LIBRE_INCOHERENT" for i in report.issues)


def test_run_skips_table_absent_from_database(monkeypatch, sample_gpkg):
    """Une couche présente dans le GeoPackage mais absente de la base
    (load_schema ne la retourne pas) ne doit pas faire planter le moteur."""
    monkeypatch.setattr(engine.db_schema, "load_schema", lambda conn, tables, pg_schema: {})
    monkeypatch.setattr(engine.inserter, "insert_all", lambda *a, **k: None)

    report = engine.run(sample_gpkg, conn=object(), apply=True)

    assert "mesurage" in report.layers_processed
    assert report.is_valid  # aucune règle DB automatique n'a pu s'appliquer, donc aucune erreur DB


def test_run_layer_kind_rule_evaluated_once_regardless_of_row_count(monkeypatch, sample_gpkg):
    """Contrairement à RuleKind.VALIDATION (une fois PAR ENREGISTREMENT),
    RuleKind.LAYER doit être évaluée une seule fois pour toute la couche,
    même quand celle-ci contient plusieurs lignes."""
    calls = []

    @register("__test_layer_kind_once__", kind=RuleKind.LAYER)
    def _count_calls(ctx):
        calls.append(len(ctx.all_rows))
        return []

    monkeypatch.setattr(engine.db_schema, "load_schema",
                         lambda conn, tables, pg_schema: {t: LayerSchema(table=t) for t in tables})
    monkeypatch.setattr(engine.inserter, "insert_all", lambda *a, **k: None)

    original_read = engine.gpkg_reader.read_gpkg

    def fake_read(path, layers=None):
        data = original_read(path, layers=layers)
        data["__test_layer_kind_once__"] = [{"a": 1}, {"a": 2}, {"a": 3}]
        return data

    monkeypatch.setattr(engine.gpkg_reader, "read_gpkg", fake_read)

    engine.run(sample_gpkg, conn=object(), apply=True)

    assert calls == [3]  # une seule invocation, avec les 3 lignes vues via ctx.all_rows
    clear_registry("__test_layer_kind_once__")


def test_run_transmet_les_schemas_a_l_insertion(monkeypatch, sample_gpkg):
    """Sans les schémas, inserter ne connaît aucune clé primaire et ne peut
    pas construire le ON CONFLICT : un second envoi du même mesurage
    échouerait sur doublon au lieu d'être mis à jour. La régression serait
    silencieuse, d'où ce test."""
    schemas = {t: LayerSchema(table=t, primary_key=["une_code_ident"])
               for t in ("mesurage", "infor_gener")}
    monkeypatch.setattr(engine.db_schema, "load_schema",
                         lambda conn, tables, pg_schema: schemas)

    recu = {}

    def espion(layers, conn, pg_schema="ifa_data", schemas=None):
        recu["schemas"] = schemas
        return {}

    monkeypatch.setattr(engine.inserter, "insert_all", espion)

    engine.run(sample_gpkg, conn=object(), apply=True)

    assert recu["schemas"] is not None, "engine.run doit transmettre les schémas"
    assert recu["schemas"]["mesurage"].primary_key == ["une_code_ident"]


# --------------------------------------------------------------------- erreurs de base de données
class ErreurDriverSimulee(Exception):
    """Tient lieu de psycopg2.Error : core/ ne dépend d'aucun driver précis,
    les tests non plus."""


def test_run_schema_illisible_signale_dans_le_rapport(monkeypatch, sample_gpkg):
    """Une base injoignable au moment de lire le schéma ne doit pas faire
    remonter d'exception : l'incident doit apparaître dans le rapport, seul
    document dont dispose l'utilisateur (les journaux du conteneur ne lui
    sont pas accessibles)."""
    def echec(conn, tables, pg_schema):
        raise ErreurDriverSimulee("server closed the connection unexpectedly")

    monkeypatch.setattr(engine.db_schema, "load_schema", echec)
    monkeypatch.setattr(engine.inserter, "insert_all", lambda *a, **k: None)

    report = engine.run(sample_gpkg, conn=object(), apply=True)

    erreurs = [i for i in report.errors if i.code == "DB_SCHEMA_INDISPONIBLE"]
    assert len(erreurs) == 1
    assert erreurs[0].layer == LAYER_BASE_DE_DONNEES
    assert "ErreurDriverSimulee" in erreurs[0].message
    assert "server closed the connection" in erreurs[0].message


def test_run_schema_illisible_bloque_insertion(monkeypatch, sample_gpkg):
    """On n'insère jamais des données dont les contraintes de la base n'ont
    pas pu être vérifiées."""
    monkeypatch.setattr(engine.db_schema, "load_schema",
                         lambda conn, tables, pg_schema: (_ for _ in ()).throw(ErreurDriverSimulee("ko")))
    appels = []
    monkeypatch.setattr(engine.inserter, "insert_all", lambda *a, **k: appels.append(True))

    report = engine.run(sample_gpkg, conn=object(), apply=True)

    assert appels == []
    assert report.inserted is False
    assert report.is_valid is False


def test_run_schema_illisible_applique_quand_meme_les_regles_metier(monkeypatch, sample_gpkg):
    """Même sans schéma, les règles métier tournent : l'utilisateur obtient
    un retour utile sur sa saisie plutôt qu'un rapport vide."""
    monkeypatch.setattr(engine.db_schema, "load_schema",
                         lambda conn, tables, pg_schema: (_ for _ in ()).throw(ErreurDriverSimulee("ko")))
    monkeypatch.setattr(engine.inserter, "insert_all", lambda *a, **k: None)

    appels = []

    # Couche factice injectée dans le lot : greffer la règle témoin sur une
    # vraie couche obligerait à vider son entrée du registre ensuite, et
    # clear_registry est définitif pour la session (un module déjà importé ne
    # réexécute pas ses décorateurs @register) — les vraies règles seraient
    # perdues pour tous les tests suivants.
    @register("__test_regles_metier__", kind=RuleKind.VALIDATION)
    def _regle_temoin(ctx):
        appels.append(ctx.layer)
        return []

    original_read = engine.gpkg_reader.read_gpkg

    def fake_read(path, layers=None):
        data = original_read(path, layers=layers)
        data["__test_regles_metier__"] = [{"a": 1}]
        return data

    monkeypatch.setattr(engine.gpkg_reader, "read_gpkg", fake_read)

    try:
        report = engine.run(sample_gpkg, conn=object(), apply=True)
    finally:
        clear_registry("__test_regles_metier__")

    assert appels, "les règles métier doivent être appliquées malgré l'échec du schéma"
    # Les couches réelles restent lues et comptées (la couche factice injectée
    # ci-dessus s'y ajoute, on ne compare donc pas le dictionnaire entier).
    assert report.record_counts["mesurage"] == 1
    assert report.record_counts["infor_gener"] == 1


def test_run_echec_insertion_signale_dans_le_rapport(monkeypatch, sample_gpkg):
    monkeypatch.setattr(engine.db_schema, "load_schema",
                         lambda conn, tables, pg_schema: {t: LayerSchema(table=t) for t in tables})

    def echec(layers, conn, pg_schema="ifa_data", schemas=None):
        raise ErreurDriverSimulee('duplicate key value violates unique constraint')

    monkeypatch.setattr(engine.inserter, "insert_all", echec)

    report = engine.run(sample_gpkg, conn=object(), apply=True)

    erreurs = [i for i in report.errors if i.code == "DB_INSERTION_ECHOUEE"]
    assert len(erreurs) == 1
    assert erreurs[0].layer == LAYER_BASE_DE_DONNEES
    assert "duplicate key" in erreurs[0].message
    assert report.inserted is False
    assert report.is_valid is False


def test_run_echec_insertion_nomme_la_table_fautive(monkeypatch, sample_gpkg):
    """insert_all renseigne `table_en_cours` sur l'exception : le rapport
    doit reprendre ce nom, sinon l'utilisateur ignore quelle table pose
    problème."""
    monkeypatch.setattr(engine.db_schema, "load_schema",
                         lambda conn, tables, pg_schema: {t: LayerSchema(table=t) for t in tables})

    def echec(layers, conn, pg_schema="ifa_data", schemas=None):
        exc = ErreurDriverSimulee("null value in column violates not-null constraint")
        exc.table_en_cours = "infor_gener"
        raise exc

    monkeypatch.setattr(engine.inserter, "insert_all", echec)

    report = engine.run(sample_gpkg, conn=object(), apply=True)

    message = next(i.message for i in report.errors if i.code == "DB_INSERTION_ECHOUEE")
    assert "infor_gener" in message


def test_run_erreur_bd_est_serialisable_en_json(monkeypatch, sample_gpkg):
    """Le rapport doit rester sérialisable : c'est sous cette forme que
    l'anomalie parvient à l'utilisateur."""
    monkeypatch.setattr(engine.db_schema, "load_schema",
                         lambda conn, tables, pg_schema: (_ for _ in ()).throw(ErreurDriverSimulee("ko")))
    monkeypatch.setattr(engine.inserter, "insert_all", lambda *a, **k: None)

    report = engine.run(sample_gpkg, conn=object(), apply=True)
    charge = json.loads(json.dumps(report.to_dict(), ensure_ascii=False, default=str))

    codes = [i["code"] for i in charge["issues"]]
    assert "DB_SCHEMA_INDISPONIBLE" in codes
    assert charge["is_valid"] is False
    assert charge["inserted"] is False


def test_run_layer_kind_rule_evaluated_even_for_empty_layer(monkeypatch, sample_gpkg):
    """Propriété qui motive RuleKind.LAYER : la règle s'exécute même sur une
    couche à ZÉRO ligne. Une RuleKind.VALIDATION ne le pourrait jamais, sa
    boucle `for row in rows` ne s'exécutant pas — c'est exactement le cas que
    doivent détecter les règles « au plus 15 enregistrements » et les
    contrôles d'unicité."""
    vues = []

    @register("__test_couche_vide__", kind=RuleKind.LAYER)
    def _regle_couche(ctx):
        vues.append(len(ctx.all_rows))
        return []

    monkeypatch.setattr(engine.db_schema, "load_schema",
                         lambda conn, tables, pg_schema: {t: LayerSchema(table=t) for t in tables})
    monkeypatch.setattr(engine.inserter, "insert_all", lambda *a, **k: None)

    original_read = engine.gpkg_reader.read_gpkg

    def fake_read(path, layers=None):
        data = original_read(path, layers=layers)
        data["__test_couche_vide__"] = []
        return data

    monkeypatch.setattr(engine.gpkg_reader, "read_gpkg", fake_read)

    try:
        engine.run(sample_gpkg, conn=object(), apply=True)
    finally:
        clear_registry("__test_couche_vide__")

    assert vues == [0], "la règle LAYER doit être évaluée une fois, avec 0 ligne"


def test_run_mesurage_sans_equipe_avertit_sans_bloquer(monkeypatch, sample_gpkg):
    """La fixture contient un mesurage et aucune couche equipe : le moteur
    doit produire un AVERTISSEMENT, qui n'empêche pas l'insertion."""
    monkeypatch.setattr(engine.db_schema, "load_schema",
                         lambda conn, tables, pg_schema: {t: LayerSchema(table=t) for t in tables})
    monkeypatch.setattr(engine.inserter, "insert_all", lambda *a, **k: None)

    report = engine.run(sample_gpkg, conn=object(), apply=True)

    avertissements = [i for i in report.warnings
                      if i.code == "EQUIPE_AU_MOINS_UN_ENREGISTEMENT"]
    assert len(avertissements) == 1
    assert avertissements[0].layer == "mesurage"
    assert report.is_valid is True
    assert report.inserted is True
