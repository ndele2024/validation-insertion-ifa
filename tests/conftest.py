"""
Fixtures partagées par tous les tests du paquet validation_insertion.

Le GeoPackage de test est construit avec `sqlite3` uniquement, comme
core/gpkg_reader.py qui le relit : un GeoPackage EST une base SQLite, donc
ni geopandas, ni fiona, ni GDAL ne sont nécessaires — ce qui garde la suite
de tests exécutable dans le même environnement "nu" que le conteneur
QFieldCloud visé par le programme.
"""

from __future__ import annotations

import sqlite3
import struct
from pathlib import Path
from typing import Any

import pytest

from core.models import LayerSchema
from core.rule_base import RuleContext

# Identifiant d'application d'un GeoPackage : les 4 octets ASCII "GPKG"
# (voir la spécification OGC GeoPackage, clause 1.1.1.1).
GPKG_APPLICATION_ID = int.from_bytes(b"GPKG", "big")
GPKG_USER_VERSION = 10200  # version 1.2 de la spécification
SRS_ID = 32187  # NAD83 / MTM zone 7 (Québec), le système du projet IPE


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


def point_gpkg_binary(x: float, y: float, srs_id: int = SRS_ID) -> bytes:
    """Encode un point au format GeoPackageBinary (spécification OGC, clause 2.1.3).

    Structure : en-tête "GP" + version + drapeaux + srs_id, puis la géométrie
    en WKB. Le lecteur ne décode jamais ces octets (il ignore les colonnes
    géométriques) ; on produit néanmoins un blob valide pour que le fichier de
    test soit un vrai GeoPackage et non une imitation approximative.
    """
    drapeaux = 0b0000_0001  # petit-boutiste, pas d'enveloppe
    entete = b"GP" + bytes([0, drapeaux]) + struct.pack("<i", srs_id)
    wkb_point = struct.pack("<BI2d", 1, 1, x, y)  # 1 = petit-boutiste, 1 = Point
    return entete + wkb_point


def _type_sqlite(valeur: Any) -> str:
    """Type de colonne SQLite déduit d'une valeur Python d'exemple."""
    if isinstance(valeur, bool):
        return "INTEGER"
    if isinstance(valeur, int):
        return "INTEGER"
    if isinstance(valeur, float):
        return "REAL"
    return "TEXT"


def creer_gpkg(chemin: str | Path, couches: dict[str, list[dict[str, Any]]],
                *, colonne_geometrie: str = "geom") -> Path:
    """Construit un GeoPackage minimal mais conforme, contenant `couches`.

    Args:
        chemin: fichier .gpkg à créer.
        couches: { nom_couche: [enregistrements] }. Chaque enregistrement est
            un dict { colonne: valeur } ; la clé `colonne_geometrie` est
            facultative et doit contenir un blob GeoPackageBinary (voir
            point_gpkg_binary) ou None.
        colonne_geometrie: nom de la colonne géométrique des couches.

    Returns:
        Le chemin du fichier créé.
    """
    chemin = Path(chemin)
    con = sqlite3.connect(str(chemin))
    cur = con.cursor()

    cur.execute(f"PRAGMA application_id = {GPKG_APPLICATION_ID}")
    cur.execute(f"PRAGMA user_version = {GPKG_USER_VERSION}")

    # Tables de métadonnées exigées par la spécification, et que
    # core/gpkg_reader.py interroge (gpkg_contents, gpkg_geometry_columns).
    cur.execute("""
        CREATE TABLE gpkg_spatial_ref_sys (
            srs_name TEXT NOT NULL, srs_id INTEGER PRIMARY KEY,
            organization TEXT NOT NULL, organization_coordsys_id INTEGER NOT NULL,
            definition TEXT NOT NULL, description TEXT
        )
    """)
    cur.executemany(
        "INSERT INTO gpkg_spatial_ref_sys VALUES (?, ?, ?, ?, ?, ?)",
        [
            ("Undefined cartesian SRS", -1, "NONE", -1, "undefined", None),
            ("Undefined geographic SRS", 0, "NONE", 0, "undefined", None),
            ("WGS 84 geodetic", 4326, "EPSG", 4326, "undefined", None),
            ("NAD83 / MTM zone 7", SRS_ID, "EPSG", SRS_ID, "undefined", None),
        ],
    )

    cur.execute("""
        CREATE TABLE gpkg_contents (
            table_name TEXT NOT NULL PRIMARY KEY, data_type TEXT NOT NULL,
            identifier TEXT UNIQUE, description TEXT DEFAULT '',
            last_change DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
            min_x DOUBLE, min_y DOUBLE, max_x DOUBLE, max_y DOUBLE,
            srs_id INTEGER REFERENCES gpkg_spatial_ref_sys(srs_id)
        )
    """)
    cur.execute("""
        CREATE TABLE gpkg_geometry_columns (
            table_name TEXT NOT NULL, column_name TEXT NOT NULL,
            geometry_type_name TEXT NOT NULL,
            srs_id INTEGER NOT NULL REFERENCES gpkg_spatial_ref_sys(srs_id),
            z TINYINT NOT NULL, m TINYINT NOT NULL,
            PRIMARY KEY (table_name, column_name)
        )
    """)

    for nom_couche, enregistrements in couches.items():
        if not enregistrements:
            raise ValueError(
                f"La couche « {nom_couche} » doit contenir au moins un enregistrement "
                "pour que ses colonnes puissent être déduites."
            )

        modele = enregistrements[0]
        colonnes_attributs = [c for c in modele if c != colonne_geometrie]
        definitions = ", ".join(
            f'"{col}" {_type_sqlite(modele[col])}' for col in colonnes_attributs
        )
        cur.execute(
            f'CREATE TABLE "{nom_couche}" ('
            f'fid INTEGER PRIMARY KEY AUTOINCREMENT, '
            f'"{colonne_geometrie}" BLOB, {definitions})'
        )

        colonnes_insertion = [colonne_geometrie, *colonnes_attributs]
        marqueurs = ", ".join("?" for _ in colonnes_insertion)
        noms = ", ".join(f'"{c}"' for c in colonnes_insertion)
        cur.executemany(
            f'INSERT INTO "{nom_couche}" ({noms}) VALUES ({marqueurs})',
            [tuple(e.get(c) for c in colonnes_insertion) for e in enregistrements],
        )

        cur.execute(
            "INSERT INTO gpkg_contents (table_name, data_type, identifier, srs_id) "
            "VALUES (?, 'features', ?, ?)",
            (nom_couche, nom_couche, SRS_ID),
        )
        cur.execute(
            "INSERT INTO gpkg_geometry_columns VALUES (?, ?, 'POINT', ?, 0, 0)",
            (nom_couche, colonne_geometrie, SRS_ID),
        )

    con.commit()
    con.close()
    return chemin


@pytest.fixture
def sample_gpkg(tmp_path):
    """Construit un petit GeoPackage réel (2 couches) dans un dossier
    temporaire, pour tester gpkg_reader et engine sans dépendre d'un
    fichier fourni séparément.

    « mesurage » a une géométrie NULL et « infor_gener » une géométrie
    renseignée : les deux couches déclarent donc une colonne géométrique,
    ce qui permet de vérifier que le lecteur l'exclut dans les deux cas.
    """
    return creer_gpkg(tmp_path / "sample.gpkg", {
        "mesurage": [{
            "geom": None,
            "une_code_ident": "UE001",
            "mes_no_seq": 1,
            "mes_com": "test",
        }],
        "infor_gener": [{
            "geom": point_gpkg_binary(300000, 5000000),
            "une_code_ident": "UE001",
            "mes_no_seq": 1,
            "ing_nom_plan_eau": "Lac Test",
            "ing_no_plan_eau": "12345",
            "tpl_code": "L",
            "ing_latit_centr": 48.5,
            "ing_longi_centr": -79.0,
            "ing_date_debut_inven": "2024-06-01",
            "ing_date_fin_inven": "2024-09-01",
        }],
    })
