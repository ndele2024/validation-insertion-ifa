import pytest

from core.inserter import insert_all


class FakeCursor:
    def __init__(self, recorder):
        self.recorder = recorder

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


def test_insert_all_builds_geometry_clause_when_present():
    conn = FakeConnection()
    _patch_commit_rollback(conn)
    layers = {"infor_gener": [{"une_code_ident": "UE1", "geometry": "POINT(1 2)"}]}
    insert_all(layers, conn)
    sql, params = conn.executed[0]
    assert "ST_GeomFromText" in sql
    assert "POINT(1 2)" in params
