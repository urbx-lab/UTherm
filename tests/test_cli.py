"""Exercise the public CLI without running the numerical pipeline."""
import sys

import pytest

from utherm import cli


def test_cli_preserves_api_defaults_and_forwards_paths(monkeypatch, tmp_path):
    met = tmp_path / "met.txt"
    met.write_text("synthetic meteorology")
    calls = []
    monkeypatch.setattr(cli, "thermal_comfort", lambda **kwargs: calls.append(kwargs))
    monkeypatch.setattr(sys, "argv", [
        "utherm", "--base_path", str(tmp_path), "--date", "2023-07-15",
        "--own_metfile", str(met), "--trees", "CDSM.tif",
    ])
    cli.main()
    assert len(calls) == 1
    assert calls[0]["save_tmrt"] is True
    assert calls[0]["trees_filename"] == "CDSM.tif"
    assert calls[0]["own_met_file"] == str(met)
    assert calls[0]["selected_date_str"] == "2023-07-15"


def test_cli_missing_weather_stops_before_simulation(monkeypatch, tmp_path):
    def unexpected_run(**kwargs):
        pytest.fail("simulation started with a missing weather file")
    monkeypatch.setattr(cli, "thermal_comfort", unexpected_run)
    monkeypatch.setattr(sys, "argv", [
        "utherm", "--base_path", str(tmp_path), "--date", "2023-07-15",
        "--own_metfile", str(tmp_path / "missing.txt"),
    ])
    with pytest.raises(SystemExit) as error:
        cli.main()
    assert error.value.code == 2
