import pytest

from core.inserter import NON_INSERTABLE_TABLES, _conflict_clause, insert_all
from core.models import LayerSchema


class FakeCursor:
    def __init__(self, recorder):
        self.recorder = recorder
        # Un curseur psycopg2 expose rowcount après chaque execute() : c'est
        # ce que compte insert_all (lignes insérées OU mises à jour).
        self.rowcount = 1

    def execute(self, sql, params):
        self.recorder.append((sql, list(params)))

    def close(self):
        pass


class FakeConnection:
    """Connexion factice qui enregistre les SQL exécutés et l'état
    commit/rollback, sans jamais toucher à une vraie base de données."""
    def __init__(self, fail_on: str | None = None):
        self.executed: list[tuple[str, list]] = []
        self.committed = False
        self.rolled_back = False
        self.fail_on = fail_on

    def cursor(self):
        return _RecordingCursor(self)


class _RecordingCursor(FakeCursor):
    def __init__(self, conn: FakeConnection):
        super().__init__(conn.executed)
        self.conn = conn

    def execute(self, sql, params):
        if self.conn.fail_on and self.conn.fail_on in sql:
            raise RuntimeError("échec simulé d'insertion")
        super().execute(sql, params)

    def __getattr__(self, item):
        return getattr(self.conn, item)


def _patch_commit_rollback(conn: FakeConnection):
    conn.commit = lambda: setattr(conn, "committed", True)
    conn.rollback = lambda: setattr(conn, "rolled_back", True)


def test_insert_all_respects_parent_child_order():
    conn = FakeConnection()
    _patch_commit_rollback(conn)
    layers = {
        "infor_gener": [{"une_code_ident": "UE1", "mes_no_seq": 1}],
        "mesurage": [{"une_code_ident": "UE1", "mes_no_seq": 1}],
    }
    counts = insert_all(layers, conn, pg_schema="ifa_data")

    tables_in_order = [sql for sql, _ in conn.executed]
    assert tables_in_order[0].count('"mesurage"') == 1
    assert tables_in_order[1].count('"infor_gener"') == 1
    assert counts == {"mesurage": 1, "infor_gener": 1}
    assert conn.committed is True
    assert conn.rolled_back is False


def test_insert_all_skips_empty_layers():
    conn = FakeConnection()
    _patch_commit_rollback(conn)
    counts = insert_all({"mesurage": []}, conn)
    assert counts == {"mesurage": 0}
    assert conn.executed == []


def test_insert_all_includes_unlisted_tables_after_known_ones():
    conn = FakeConnection()
    _patch_commit_rollback(conn)
    layers = {
        "une_table_inconnue": [{"x": 1}],
        "mesurage": [{"une_code_ident": "UE1", "mes_no_seq": 1}],
    }
    counts = insert_all(layers, conn)
    assert list(counts.keys()) == ["mesurage", "une_table_inconnue"]


def test_insert_all_rolls_back_and_raises_on_failure():
    conn = FakeConnection(fail_on="infor_gener")
    _patch_commit_rollback(conn)
    layers = {
        "mesurage": [{"une_code_ident": "UE1", "mes_no_seq": 1}],
        "infor_gener": [{"une_code_ident": "UE1", "mes_no_seq": 1}],
    }
    with pytest.raises(RuntimeError):
        insert_all(layers, conn)
    assert conn.rolled_back is True
    assert conn.committed is False


def test_insert_all_nomme_la_table_en_cours_sur_echec():
    """L'exception propagée porte le nom de la table en cours d'insertion,
    pour que engine.run puisse le citer dans le rapport. Le TYPE de
    l'exception reste inchangé (voir le test précédent)."""
    conn = FakeConnection(fail_on="infor_gener")
    _patch_commit_rollback(conn)
    layers = {
        "mesurage": [{"une_code_ident": "UE1", "mes_no_seq": 1}],
        "infor_gener": [{"une_code_ident": "UE1", "mes_no_seq": 1}],
    }
    with pytest.raises(RuntimeError) as info:
        insert_all(layers, conn)
    assert info.value.table_en_cours == "infor_gener"


def test_insert_all_builds_geometry_clause_when_present():
    conn = FakeConnection()
    _patch_commit_rollback(conn)
    layers = {"infor_gener": [{"une_code_ident": "UE1", "geometry": "POINT(1 2)"}]}
    insert_all(layers, conn)
    sql, params = conn.executed[0]
    assert "ST_GeomFromText" in sql
    assert "POINT(1 2)" in params


# --------------------------------------------------------------------- couches non insérables
def test_rapport_validation_est_exclu_de_l_insertion():
    """La table rapport_validation est produite par la validation elle-même et
    n'existe que dans le GeoPackage. Relue au run suivant, elle serait sinon
    réinjectée vers une relation PostgreSQL inexistante, ce qui annulerait
    tout le lot à chaque synchronisation."""
    conn = FakeConnection()
    _patch_commit_rollback(conn)
    layers = {
        "mesurage": [{"une_code_ident": "UE1"}],
        "rapport_validation": [{"statut": "INVALIDE", "message": "..."}],
    }
    counts = insert_all(layers, conn)

    assert "rapport_validation" not in counts
    assert all("rapport_validation" not in sql for sql, _ in conn.executed)
    assert counts == {"mesurage": 1}
    assert conn.committed is True


def test_toutes_les_tables_non_insérables_sont_ignorees():
    conn = FakeConnection()
    _patch_commit_rollback(conn)
    layers = {t: [{"x": 1}] for t in NON_INSERTABLE_TABLES}
    counts = insert_all(layers, conn)
    assert counts == {}
    assert conn.executed == []


# --------------------------------------------------------------------- upsert (ON CONFLICT)
def test_conflict_clause_met_a_jour_les_colonnes_hors_cle():
    clause = _conflict_clause(["une_code_ident"], ["une_code_ident", "mes_com"], has_geom=False)
    assert 'ON CONFLICT ("une_code_ident")' in clause
    assert 'DO UPDATE SET "mes_com" = EXCLUDED."mes_com"' in clause
    assert "une_code_ident\" = EXCLUDED" not in clause  # la clé n'est pas réécrite


def test_conflict_clause_do_nothing_si_table_reduite_a_sa_cle():
    clause = _conflict_clause(["a", "b"], ["a", "b"], has_geom=False)
    assert clause.strip() == 'ON CONFLICT ("a", "b") DO NOTHING'


def test_conflict_clause_vide_sans_cle_primaire():
    assert _conflict_clause([], ["a", "b"], has_geom=False) == ""


def test_conflict_clause_vide_si_cle_incomplete_dans_le_gpkg():
    """Clé primaire à séquence non fournie par le GeoPackage : chaque insertion
    crée légitimement une nouvelle ligne, il n'y a pas de conflit à arbitrer."""
    assert _conflict_clause(["id_seq"], ["une_code_ident"], has_geom=False) == ""


def test_conflict_clause_inclut_la_geometrie():
    clause = _conflict_clause(["k"], ["k", "v"], has_geom=True)
    assert '"shape" = EXCLUDED."shape"' in clause


def test_insert_all_construit_l_upsert_depuis_les_schemas():
    conn = FakeConnection()
    _patch_commit_rollback(conn)
    layers = {"mesurage": [{"une_code_ident": "UE1", "mes_no_seq": 1, "mes_com": "x"}]}
    schemas = {"mesurage": LayerSchema(table="mesurage",
                                        primary_key=["une_code_ident", "mes_no_seq"])}

    insert_all(layers, conn, schemas=schemas)

    sql = conn.executed[0][0]
    assert 'ON CONFLICT ("une_code_ident", "mes_no_seq") DO UPDATE' in sql
    assert '"mes_com" = EXCLUDED."mes_com"' in sql


def test_insert_all_sans_schemas_reste_un_insert_nu():
    """Rétrocompatibilité : sans schémas, aucun ON CONFLICT n'est émis."""
    conn = FakeConnection()
    _patch_commit_rollback(conn)
    insert_all({"mesurage": [{"une_code_ident": "UE1"}]}, conn)
    assert "ON CONFLICT" not in conn.executed[0][0]


def test_insert_all_compte_les_lignes_affectees():
    """Le décompte suit cur.rowcount : une mise à jour compte autant qu'une
    insertion, un ON CONFLICT DO NOTHING sans effet ne compte pas."""
    conn = FakeConnection()
    _patch_commit_rollback(conn)

    class CurseurSansEffet(_RecordingCursor):
        def __init__(self, c):
            super().__init__(c)
            self.rowcount = 0

    conn.cursor = lambda: CurseurSansEffet(conn)
    counts = insert_all({"mesurage": [{"une_code_ident": "UE1"}]}, conn)
    assert counts == {"mesurage": 0}
