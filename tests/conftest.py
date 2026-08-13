"""
Fixtures partagées par tous les tests du paquet validation_insertion.
"""

from __future__ import annotations

import geopandas as gpd
import pytest
from shapely.geometry import Point

from core.models import LayerSchema
from core.rule_base import RuleContext


@pytest.fixture
def make_context():
    """Fabrique un RuleContext minimal pour tester une règle isolément,
    sans passer par le moteur complet ni par une vraie base de données.

    Usage :
        ctx = make_context("detail_speci", {"dsp_no_speci": None}, layers={
            "infor_gener": [{"une_code_ident": "X", "mes_no_seq": 1, ...}],
        })
    """
    def _make(layer: str, row: dict, *, all_rows: list[dict] | None = None,
              layers: dict[str, list[dict]] | None = None,
              schemas: dict[str, LayerSchema] | None = None) -> RuleContext:
        all_rows = all_rows if all_rows is not None else [row]
        layers = dict(layers or {})
        layers.setdefault(layer, all_rows)
        return RuleContext(layer=layer, row=row, all_rows=all_rows, layers=layers,
                            schemas=schemas or {})
    return _make


@pytest.fixture
def sample_gpkg(tmp_path):
    """Construit un petit GeoPackage réel (2 couches) dans un dossier
    temporaire, pour tester gpkg_reader et engine sans dépendre d'un
    fichier fourni séparément."""
    path = tmp_path / "sample.gpkg"

    mesurage = gpd.GeoDataFrame(
        {"une_code_ident": ["UE001"], "mes_no_seq": [1], "mes_com": ["test"]},
        geometry=[None],
        crs="EPSG:32187",
    )
    mesurage.to_file(path, layer="mesurage", driver="GPKG")

    infor_gener = gpd.GeoDataFrame(
        {
            "une_code_ident": ["UE001"],
            "mes_no_seq": [1],
            "ing_nom_plan_eau": ["Lac Test"],
            "ing_no_plan_eau": ["12345"],
            "tpl_code": ["L"],
            "ing_latit_centr": [48.5],
            "ing_longi_centr": [-79.0],
            "ing_date_debut_inven": ["2024-06-01"],
            "ing_date_fin_inven": ["2024-09-01"],
        },
        geometry=[Point(300000, 5000000)],
        crs="EPSG:32187",
    )
    infor_gener.to_file(path, layer="infor_gener", driver="GPKG")

    return path
