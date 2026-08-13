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


def test_read_layer_geometry_as_wkt(sample_gpkg):
    records = read_layer(sample_gpkg, "infor_gener")
    assert records[0]["geometry"].startswith("POINT")


def test_read_layer_null_geometry_is_none(sample_gpkg):
    records = read_layer(sample_gpkg, "mesurage")
    assert records[0]["geometry"] is None


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
