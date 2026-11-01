"""Physical invariants and directional transport for the air-temperature solver."""

import pytest
import torch

from utherm.energy_balance.advection_diffusion import AdvectionDiffusionAirTemp, wind_to_raster_velocity


@pytest.mark.parametrize("bearing,row,col", [(0, 2, 0), (90, 0, -2), (180, -2, 0), (270, 0, 2)])
def test_meteorological_bearings_follow_raster_axes(device, bearing, row, col):
    vr, vc = wind_to_raster_velocity(2, bearing, device, 3, 4)
    torch.testing.assert_close(vr, torch.full_like(vr, row), atol=1e-6, rtol=0)
    torch.testing.assert_close(vc, torch.full_like(vc, col), atol=1e-6, rtol=0)


def test_scalar_direction_preserves_spatial_wind_speed(device):
    speed = torch.tensor([[1.0, 2.0], [3.0, 4.0]], device=device)
    _, vc = wind_to_raster_velocity(speed, 270, device, 2, 2)
    torch.testing.assert_close(vc, speed)


def test_missing_bearing_and_speed_have_zero_velocity(device):
    speed = torch.tensor([[2.0, float("nan")]], device=device)
    bearing = torch.tensor([[float("nan"), 90.0]], device=device)
    vr, vc = wind_to_raster_velocity(speed, bearing, device, 1, 2)
    assert torch.count_nonzero(vr) == torch.count_nonzero(vc) == 0


@pytest.mark.parametrize(
    "name,value",
    [
        ("rows", 0),
        ("cols", True),
        ("dx", 0),
        ("dt", -1),
        ("eddy_diffusivity", -1),
        ("courant", float("nan")),
        ("max_substeps", 0),
    ],
)
def test_invalid_numerical_controls_fail_before_allocating(name, value, device):
    options = dict(rows=9, cols=9, dx=1.0, device=device)
    options[name] = value
    with pytest.raises(ValueError, match=name):
        AdvectionDiffusionAirTemp(**options)


def test_uniform_equilibrium_and_mask_are_preserved(device):
    model = AdvectionDiffusionAirTemp(9, 9, 1, device, dt=2)
    zeros = torch.zeros((9, 9), device=device)
    valid = torch.ones((9, 9), dtype=torch.bool, device=device)
    valid[4, 4] = False
    surface = torch.full_like(zeros, 300.0)
    surface[4, 4] = float("nan")
    out = model.step(300, zeros, zeros, surface, zeros, zeros, valid)
    assert torch.isnan(out[4, 4])
    torch.testing.assert_close(out[valid], torch.full_like(out[valid], 300.0))


def test_west_wind_transports_cool_air_east(device):
    model = AdvectionDiffusionAirTemp(9, 9, 1, device, dt=1, eddy_diffusivity=0)
    model.reset(300)
    model.T[4, 3] = 295
    zeros = torch.zeros_like(model.T)
    valid = torch.ones_like(zeros, dtype=torch.bool)
    vr, vc = wind_to_raster_velocity(1, 270, device, 9, 9)
    out = model.step(300, vr, vc, torch.full_like(zeros, 300), zeros, zeros, valid)
    assert out[4, 4].item() == pytest.approx(295, abs=1e-4)
    assert out[4, 3].item() == pytest.approx(300, abs=1e-4)


def test_diffusion_spreads_a_local_anomaly_without_overshoot(device):
    model = AdvectionDiffusionAirTemp(15, 15, 1, device, dt=1, eddy_diffusivity=1)
    field = torch.full((15, 15), 300.0, device=device)
    field[7, 7] = 310
    out = model._diffuse(field, 1.0)
    assert 300 < out[7, 7].item() < 310
    assert out[7, 8] > 300
    assert out.min() >= 299.9999
    assert out.max() <= 310


def test_surface_relaxation_is_bounded_and_retains_memory(device):
    model = AdvectionDiffusionAirTemp(9, 9, 1, device, dt=60, eddy_diffusivity=0)
    zeros = torch.zeros((9, 9), device=device)
    valid = torch.ones_like(zeros, dtype=torch.bool)
    first = model.step(300, zeros, zeros, zeros + 310, zeros + 10, zeros, valid)
    second = model.step(300, zeros, zeros, zeros + 310, zeros + 10, zeros, valid)
    assert 300 < first[4, 4] < second[4, 4] < 310
    assert torch.all(second[0] == 300)
    model.reset(300)
    torch.testing.assert_close(model.T, zeros + 300)
