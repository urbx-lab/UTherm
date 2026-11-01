"""Exercise the public CLI without running the numerical pipeline."""

import sys

import pytest

from utherm import cli


def test_cli_preserves_api_defaults_and_forwards_paths(monkeypatch, tmp_path):
    met = tmp_path / "met.txt"
    met.write_text("synthetic meteorology")
    calls = []
    monkeypatch.setattr(cli, "thermal_comfort", lambda **kwargs: calls.append(kwargs))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "utherm",
            "--base_path",
            str(tmp_path),
            "--date",
            "2023-07-15",
            "--own_metfile",
            str(met),
            "--trees",
            "CDSM.tif",
        ],
    )
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
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "utherm",
            "--base_path",
            str(tmp_path),
            "--date",
            "2023-07-15",
            "--own_metfile",
            str(tmp_path / "missing.txt"),
        ],
    )
    with pytest.raises(SystemExit) as error:
        cli.main()
    assert error.value.code == 2


def test_cli_reports_invalid_model_settings_without_traceback(monkeypatch, tmp_path, capsys):
    met = tmp_path / "met.txt"
    met.write_text("synthetic meteorology")

    def invalid_run(**kwargs):
        raise ValueError("tile_size must be a positive integer")

    monkeypatch.setattr(cli, "thermal_comfort", invalid_run)
    with pytest.raises(SystemExit) as error:
        cli.main(["--base_path", str(tmp_path), "--date", "2023-07-15", "--own_metfile", str(met)])
    assert error.value.code == 2
    stderr = capsys.readouterr().err
    assert "tile_size must be a positive integer" in stderr
    assert "Traceback" not in stderr


def test_doctor_dispatch_propagates_failure_without_needing_scene_arguments(monkeypatch):
    from utherm import doctor

    monkeypatch.setattr(doctor, "main", lambda argv: 1 if argv == ["--require-cuda"] else 0)
    assert cli.main(["doctor", "--require-cuda"]) == 1


def test_cli_exposes_moisture_controls_and_rejects_unknown_weather_sources():
    parser = cli.build_parser()
    options = parser.parse_args(
        [
            "--base_path",
            ".",
            "--date",
            "2023-07-15",
            "--ground_wetness",
            "0.4",
            "--canopy_gmax_fraction",
            "0.7",
        ]
    )
    assert options.ground_wetness == 0.4
    assert options.canopy_gmax_fraction == 0.7
    with pytest.raises(SystemExit):
        parser.parse_args(["--base_path", ".", "--date", "2023-07-15", "--data_source_type", "unknown"])
