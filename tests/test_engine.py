"""
Tests d'intégration du moteur (core.engine.run) : utilisent un VRAI
GeoPackage (fixture sample_gpkg) et de VRAIES règles enregistrées
(rules.infor_gener), mais isolent la base de données (db_schema.load_schema
et inserter.insert_all sont remplacés par des doublures de test) pour ne
jamais dépendre d'une connexion PostgreSQL réelle.
"""

from __future__ import annotations

from core import engine
from core.models import LayerSchema
from core.registry import clear_registry, register
from core.rule_base import RuleKind


def test_run_valid_data_triggers_insertion(monkeypatch, sample_gpkg):
    monkeypatch.setattr(engine.db_schema, "load_schema",
                         lambda conn, tables, pg_schema: {
                             t: LayerSchema(table=t) for t in tables
                         })
    inserted = {}
    monkeypatch.setattr(engine.inserter, "insert_all",
                         lambda layers, conn, pg_schema="ifa_data": inserted.setdefault("called", layers))

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


def test_run_layer_kind_rule_evaluated_even_for_empty_layer(monkeypatch, sample_gpkg):
    """Cas concret motivant RuleKind.LAYER : rules.equipe.equipe_validation
    ("au moins un enregistrement") doit se déclencher pour une couche EQUIPE
    vide, ce qu'une RuleKind.VALIDATION classique ne pourrait jamais faire
    (sa boucle `for row in rows` ne s'exécuterait pas)."""
    import rules.equipe  # noqa: F401 -- déclenche @register

    monkeypatch.setattr(engine.db_schema, "load_schema",
                         lambda conn, tables, pg_schema: {t: LayerSchema(table=t) for t in tables})
    monkeypatch.setattr(engine.inserter, "insert_all", lambda *a, **k: None)

    original_read = engine.gpkg_reader.read_gpkg

    def fake_read(path, layers=None):
        data = original_read(path, layers=layers)
        data["equipe"] = []
        return data

    monkeypatch.setattr(engine.gpkg_reader, "read_gpkg", fake_read)

    report = engine.run(sample_gpkg, conn=object(), apply=True)

    assert report.is_valid is False
    assert any(i.code == "EQUIPE_AU_MOINS_UN_ENREGISTEMENT" for i in report.issues)
