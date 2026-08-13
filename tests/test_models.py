from core.models import Severity, ValidationIssue, ValidationReport


def test_validation_issue_to_dict():
    issue = ValidationIssue(
        layer="detail_speci", severity=Severity.ERROR, code="X",
        message="msg", fields=["a"], record={"k": 1}, rule_name="r",
    )
    d = issue.to_dict()
    assert d == {
        "layer": "detail_speci", "severity": "error", "code": "X",
        "message": "msg", "fields": ["a"], "record": {"k": 1}, "rule_name": "r",
    }


def test_report_errors_warnings_split():
    report = ValidationReport(source="x.gpkg")
    report.issues.append(ValidationIssue(layer="a", severity=Severity.ERROR, code="E1", message="e"))
    report.issues.append(ValidationIssue(layer="a", severity=Severity.WARNING, code="W1", message="w"))

    assert len(report.errors) == 1
    assert len(report.warnings) == 1
    assert report.is_valid is False


def test_report_is_valid_with_only_warnings():
    report = ValidationReport(source="x.gpkg")
    report.issues.append(ValidationIssue(layer="a", severity=Severity.WARNING, code="W1", message="w"))
    assert report.is_valid is True


def test_report_to_dict_counts():
    report = ValidationReport(source="x.gpkg", layers_processed=["a"], record_counts={"a": 2})
    report.issues.append(ValidationIssue(layer="a", severity=Severity.ERROR, code="E1", message="e"))
    d = report.to_dict()
    assert d["error_count"] == 1
    assert d["warning_count"] == 0
    assert d["is_valid"] is False
    assert d["record_counts"] == {"a": 2}
