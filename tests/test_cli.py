import json

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


def test_cli_ecrit_un_rapport_si_connexion_impossible(monkeypatch, sample_gpkg, tmp_path):
    """L'échec de connexion est l'erreur de base de données la plus
    fréquente : elle doit produire un rapport JSON, sans quoi l'incident
    n'est visible que dans les journaux du conteneur."""
    def fail_connect(dsn):
        raise RuntimeError("could not connect to server: Connection refused")

    monkeypatch.setattr(cli.psycopg2, "connect", fail_connect)
    rapport = tmp_path / "rapport.json"

    code = cli.main([str(sample_gpkg), "--report", str(rapport)])

    assert code == 2
    assert rapport.exists(), "un rapport doit être écrit même sans connexion"

    charge = json.loads(rapport.read_text(encoding="utf-8"))
    assert charge["is_valid"] is False
    assert charge["inserted"] is False

    anomalie = next(i for i in charge["issues"] if i["code"] == "DB_CONNEXION_IMPOSSIBLE")
    assert anomalie["layer"] == "(base de données)"
    assert "Connection refused" in anomalie["message"]


def test_cli_rapport_connexion_mentionne_la_cible(monkeypatch, sample_gpkg, tmp_path):
    """Le message nomme l'hôte et la base visés : sans cela, impossible de
    distinguer une mauvaise configuration d'une base réellement arrêtée."""
    monkeypatch.setattr(cli.psycopg2, "connect",
                         lambda dsn: (_ for _ in ()).throw(RuntimeError("timeout")))
    monkeypatch.setattr(cli.config, "PG_HOST", "serveur-test")
    monkeypatch.setattr(cli.config, "PG_DB", "base-test")
    rapport = tmp_path / "rapport.json"

    cli.main([str(sample_gpkg), "--report", str(rapport)])

    message = json.loads(rapport.read_text(encoding="utf-8"))["issues"][0]["message"]
    assert "serveur-test" in message
    assert "base-test" in message
