import cli


def test_cli_returns_2_when_gpkg_missing(tmp_path):
    code = cli.main([str(tmp_path / "absent.gpkg")])
    assert code == 2


def test_cli_returns_2_on_db_connection_failure(monkeypatch, sample_gpkg):
    def fail_connect(dsn):
        raise RuntimeError("connexion refusée (simulée)")

    monkeypatch.setattr(cli.psycopg2, "connect", fail_connect)
    code = cli.main([str(sample_gpkg)])
    assert code == 2
