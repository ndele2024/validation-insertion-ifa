from core.gpkg_reader import list_layers, read_gpkg, read_layer


def test_list_layers(sample_gpkg):
    layers = list_layers(sample_gpkg)
    assert set(layers) == {"mesurage", "infor_gener"}


def test_read_layer_returns_records(sample_gpkg):
    records = read_layer(sample_gpkg, "infor_gener")
    assert len(records) == 1
    assert records[0]["une_code_ident"] == "UE001"
    assert records[0]["mes_no_seq"] == 1
    assert records[0]["ing_nom_plan_eau"] == "Lac Test"


def test_read_layer_exclut_la_geometrie(sample_gpkg):
    """Le lecteur sqlite3 ignore volontairement les géométries binaires GPKG :
    les règles métier IPE sont purement attributaires (voir la docstring de
    core/gpkg_reader.py). La colonne géométrique est donc absente des
    enregistrements, alors que les attributs, eux, sont bien présents."""
    record = read_layer(sample_gpkg, "infor_gener")[0]
    assert "geom" not in record
    assert record["ing_nom_plan_eau"] == "Lac Test"


def test_read_layer_exclut_la_geometrie_meme_si_nulle(sample_gpkg):
    """La couche « mesurage » déclare une colonne géométrique dont la valeur
    est NULL : elle doit être exclue comme les autres."""
    record = read_layer(sample_gpkg, "mesurage")[0]
    assert "geom" not in record
    assert record["mes_com"] == "test"


def test_read_gpkg_all_layers_by_default(sample_gpkg):
    layers = read_gpkg(sample_gpkg)
    assert set(layers.keys()) == {"mesurage", "infor_gener"}
    assert len(layers["mesurage"]) == 1


def test_read_gpkg_filters_requested_layers(sample_gpkg):
    layers = read_gpkg(sample_gpkg, layers=["infor_gener"])
    assert set(layers.keys()) == {"infor_gener"}


def test_read_gpkg_missing_file_raises(tmp_path):
    import pytest
    with pytest.raises(FileNotFoundError):
        read_gpkg(tmp_path / "absent.gpkg")


# --------------------------------------------------------------------- conformité du fichier de test
def test_sample_gpkg_est_un_vrai_geopackage(sample_gpkg):
    """La fixture est construite en sqlite3 pur : on vérifie qu'elle produit
    un GeoPackage conforme (identifiant d'application « GPKG » et tables de
    métadonnées) et non une simple base SQLite qui y ressemble."""
    import sqlite3

    con = sqlite3.connect(str(sample_gpkg))
    try:
        application_id = con.execute("PRAGMA application_id").fetchone()[0]
        assert application_id.to_bytes(4, "big") == b"GPKG"

        tables = {r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'")}
        assert {"gpkg_contents", "gpkg_geometry_columns", "gpkg_spatial_ref_sys"} <= tables

        # La colonne géométrique est bien déclarée : sans cela, le test
        # « le lecteur exclut la géométrie » ne prouverait rien.
        declarees = dict(con.execute(
            "SELECT table_name, column_name FROM gpkg_geometry_columns"))
        assert declarees == {"mesurage": "geom", "infor_gener": "geom"}
    finally:
        con.close()


def test_sample_gpkg_geometrie_au_format_geopackage_binary(sample_gpkg):
    """Le blob écrit par la fixture respecte l'en-tête GeoPackageBinary."""
    import sqlite3

    con = sqlite3.connect(str(sample_gpkg))
    try:
        blob = con.execute("SELECT geom FROM infor_gener").fetchone()[0]
        assert blob[:2] == b"GP"
        assert con.execute("SELECT geom FROM mesurage").fetchone()[0] is None
    finally:
        con.close()
