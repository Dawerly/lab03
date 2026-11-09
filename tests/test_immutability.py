from collections.abc import Mapping
from dataclasses import FrozenInstanceError, replace
from types import MappingProxyType
from typing import cast

import pytest

from core import (
    add_label,
    add_reading,
    average_reading,
    calibrate,
    rank_sensors,
    update_config,
)
from model import ConfigValue, Reading, Sensor


@pytest.fixture
def sensor() -> Sensor:
    return Sensor(
        "T-01",
        "temperature",
        (Reading("09:00", 20.0), Reading("10:00", 22.0)),
        frozenset({"indoor"}),
        {"unit": "C", "interval": 60},
    )


def test_add_reading_is_pure(sensor: Sensor) -> None:
    original_values = tuple(r.value for r in sensor.readings)
    reading = Reading("11:00", 24.0)
    result = add_reading(sensor, reading)
    assert result is not sensor
    assert tuple(r.value for r in sensor.readings) == original_values
    assert result.readings == sensor.readings + (reading,)
    assert average_reading(result) == 22
    assert add_reading(sensor, reading) == result


def test_add_label_is_pure(sensor: Sensor) -> None:
    result = add_label(sensor, "verified")
    assert result is not sensor
    assert sensor.labels == frozenset({"indoor"})
    assert result.labels == frozenset({"indoor", "verified"})
    assert add_label(result, "verified") == result


def test_config_update_is_pure(sensor: Sensor) -> None:
    updates: dict[str, ConfigValue] = {"interval": 30, "enabled": True}
    result = update_config(sensor, updates)
    updates["interval"] = 999
    assert sensor.config["interval"] == 60
    assert result.config["interval"] == 30
    assert result.config["unit"] == "C"
    assert result.config["enabled"] is True


def test_source_config_is_copied() -> None:
    source: dict[str, ConfigValue] = {"unit": "C"}
    sensor = Sensor("T-01", "temperature", config=source)
    source["unit"] = "changed"
    assert isinstance(sensor.config, MappingProxyType)
    assert sensor.config["unit"] == "C"


def test_read_only_config(sensor: Sensor) -> None:
    with pytest.raises(TypeError):
        sensor.config["unit"] = "F"  # type: ignore[index]


def test_frozen_entities(sensor: Sensor) -> None:
    with pytest.raises(FrozenInstanceError):
        sensor.id = "changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        sensor.readings[0].value = 99  # type: ignore[misc]
    assert not hasattr(sensor, "__dict__")


def test_hashability_and_equality(sensor: Sensor) -> None:
    equal = replace(sensor, config=dict(sensor.config))
    changed = add_reading(sensor, Reading("11:00", 24))
    assert sensor == equal and hash(sensor) == hash(equal)
    assert {sensor: "saved"}[equal] == "saved"
    assert len({sensor, equal, changed}) == 2
    # config враховано в рівності, але виключено з hash.
    different = update_config(sensor, {"unit": "F"})
    assert different != sensor
    assert hash(different) == hash(sensor)
    assert len({sensor, different}) == 2
    assert len({Reading("09:00", 20), Reading("09:00", 20)}) == 1


def test_calibration_returns_new_readings(sensor: Sensor) -> None:
    result = calibrate(sensor, factor=2, offset=1)
    assert [r.value for r in result.readings] == [41, 45]
    assert [r.value for r in sensor.readings] == [20, 22]
    assert result.readings[0] is not sensor.readings[0]
    assert result.readings[0].observed_at == "09:00"


def test_rank_and_tie_breaker(sensor: Sensor) -> None:
    tied = replace(sensor, id="T-00")
    other_kind = replace(sensor, id="H-01", kind="humidity")
    assert rank_sensors(
        [sensor, tied, other_kind],
        kind="temperature",
        min_readings=2,
        top_n=1,
    ) == (tied,)
    assert sensor.id == "T-01"


def test_empty_cases() -> None:
    empty = Sensor("T-01", "temperature")
    assert average_reading(empty) == 0
    assert rank_sensors([empty], kind="temperature", min_readings=1, top_n=3) == ()
    assert rank_sensors([empty], kind="temperature", min_readings=0, top_n=0) == ()


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_non_finite_reading(value: float) -> None:
    with pytest.raises(ValueError):
        Reading("09:00", value)


def test_invalid_config_and_parameters(sensor: Sensor) -> None:
    bad = cast(Mapping[str, ConfigValue], {"nested": [1, 2]})
    with pytest.raises(TypeError):
        Sensor("T-01", "temperature", config=bad)
    with pytest.raises(ValueError):
        calibrate(sensor, factor=float("nan"), offset=0)
    with pytest.raises(ValueError):
        rank_sensors([sensor], kind="temperature", min_readings=1, top_n=-1)
