"""Diagnostics must fail clearly for missing libraries and unavailable CUDA."""

import json

from utherm import doctor


def test_missing_binary_dependency_is_reported(monkeypatch):
    monkeypatch.setattr(doctor, "REQUIRED_MODULES", {"GDAL": "osgeo.gdal"})

    def broken_import(name):
        raise OSError("native GDAL library could not be loaded")

    monkeypatch.setattr(doctor, "import_module", broken_import)
    report = doctor.collect_diagnostics()
    assert not report["ok"]
    assert "native GDAL" in report["errors"]["GDAL"]


def test_cuda_requirement_cannot_silently_pass_on_cpu(monkeypatch, capsys):
    monkeypatch.setattr(doctor, "REQUIRED_MODULES", {})
    assert doctor.main(["--json", "--require-cuda"]) == 1
    report = json.loads(capsys.readouterr().out)
    assert not report["ok"]
    assert "cuda" in report["errors"]


def test_ready_installation_has_machine_readable_success(monkeypatch, capsys):
    monkeypatch.setattr(doctor, "REQUIRED_MODULES", {})
    assert doctor.main(["--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["ok"]
    assert report["python"]


def test_real_installation_loads_compiled_geospatial_stack():
    report = doctor.collect_diagnostics()
    assert report["ok"], report["errors"]
    assert report["packages"]["GDAL"]
    assert report["packages"]["rasterio"]
    assert report["packages"]["torch"]
