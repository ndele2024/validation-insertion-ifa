import json

from core.models import (
    LAYER_BASE_DE_DONNEES,
    Severity,
    ValidationIssue,
    ValidationReport,
)
from core.report import erreurs_base_de_donnees, report_summary, save_report


def test_save_report_writes_valid_json(tmp_path):
    report = ValidationReport(source="x.gpkg", layers_processed=["mesurage"], record_counts={"mesurage": 1})
    report.issues.append(ValidationIssue(layer="mesurage", severity=Severity.ERROR, code="E", message="m"))
    out = tmp_path / "report.json"

    save_report(report, out)

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["source"] == "x.gpkg"
    assert data["error_count"] == 1
    assert data["is_valid"] is False


def test_report_summary_valid_with_insertion():
    report = ValidationReport(source="x.gpkg", record_counts={"mesurage": 3})
    report.inserted = True
    summary = report_summary(report)
    assert "Validation réussie" in summary
    assert "insérées" in summary


def test_report_summary_invalid_lists_layers():
    report = ValidationReport(source="x.gpkg")
    report.issues.append(ValidationIssue(layer="detail_speci", severity=Severity.ERROR, code="E", message="m"))
    report.issues.append(ValidationIssue(layer="detail_speci", severity=Severity.ERROR, code="E2", message="m2"))
    summary = report_summary(report)
    assert "échouée" in summary
    assert "detail_speci : 2 erreur" in summary


# --------------------------------------------------------------------- erreurs de base de données
def _erreur_bd(code="DB_CONNEXION_IMPOSSIBLE", message="connexion refusée"):
    return ValidationIssue(layer=LAYER_BASE_DE_DONNEES, severity=Severity.ERROR,
                            code=code, message=message)


def test_erreurs_base_de_donnees_isole_les_anomalies_techniques():
    report = ValidationReport(source="x.gpkg")
    report.issues.append(ValidationIssue(layer="detail_speci", severity=Severity.ERROR,
                                          code="E", message="saisie"))
    report.issues.append(_erreur_bd())

    erreurs = erreurs_base_de_donnees(report)
    assert len(erreurs) == 1
    assert erreurs[0].code == "DB_CONNEXION_IMPOSSIBLE"


def test_report_summary_affiche_le_message_complet_des_erreurs_bd():
    """Contrairement aux erreurs de saisie (comptées par couche), les erreurs
    de base de données sont affichées en entier : c'est précisément ce qu'on
    cherche à lire sans ouvrir les journaux du conteneur."""
    report = ValidationReport(source="x.gpkg")
    report.issues.append(_erreur_bd(message="Connexion à PostgreSQL impossible (hôte db:5432)"))

    summary = report_summary(report)
    assert "Problème de base de données" in summary
    assert "DB_CONNEXION_IMPOSSIBLE" in summary
    assert "hôte db:5432" in summary
    assert "Aucune donnée insérée" in summary


def test_report_summary_separe_erreurs_bd_et_erreurs_de_saisie():
    report = ValidationReport(source="x.gpkg")
    report.issues.append(ValidationIssue(layer="detail_speci", severity=Severity.ERROR,
                                          code="E", message="saisie"))
    report.issues.append(_erreur_bd())

    summary = report_summary(report)
    assert "Problème de base de données" in summary
    assert "detail_speci : 1 erreur" in summary
    # Le décompte des erreurs de saisie ne doit pas englober l'erreur technique.
    assert "1 erreur(s). Aucune donnée insérée." in summary


def test_report_summary_sans_erreur_bd_inchange():
    """Un rapport sans problème technique garde exactement l'ancien format."""
    report = ValidationReport(source="x.gpkg")
    report.issues.append(ValidationIssue(layer="detail_speci", severity=Severity.ERROR,
                                          code="E", message="saisie"))
    summary = report_summary(report)
    assert "Problème de base de données" not in summary
    assert summary.startswith("✗ Validation échouée : 1 erreur(s).")
