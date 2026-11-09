"""Чисті оновлення, обчислення та конвеєр незмінних сенсорів."""

from collections.abc import Mapping, Sequence
from dataclasses import replace
from math import isfinite

from model import ConfigValue, Reading, Sensor


def add_reading(sensor: Sensor, reading: Reading) -> Sensor:
    return replace(sensor, readings=sensor.readings + (reading,))


def add_label(sensor: Sensor, label: str) -> Sensor:
    return replace(sensor, labels=sensor.labels | frozenset({label}))


def update_config(sensor: Sensor, updates: Mapping[str, ConfigValue]) -> Sensor:
    return replace(sensor, config={**sensor.config, **updates})


def average_reading(sensor: Sensor) -> float:
    if not sensor.readings:
        return 0.0
    return sum(reading.value for reading in sensor.readings) / len(sensor.readings)


def calibrate(sensor: Sensor, *, factor: float, offset: float) -> Sensor:
    """Нова версія показів: value * factor + offset."""
    if not isfinite(factor) or not isfinite(offset):
        raise ValueError("Параметри калібрування мають бути скінченними")
    readings = tuple(
        Reading(r.observed_at, r.value * factor + offset) for r in sensor.readings
    )
    return replace(sensor, readings=readings)


def rank_sensors(
    sensors: Sequence[Sensor], *, kind: str, min_readings: int, top_n: int
) -> tuple[Sensor, ...]:
    """Конвеєр: один тип сенсорів → достатньо показів → середнє → Top-N."""
    if min_readings < 0 or top_n < 0:
        raise ValueError("min_readings і top_n мають бути невід'ємними")
    accepted = filter(
        lambda s: s.kind == kind and len(s.readings) >= min_readings, sensors
    )
    scored = map(lambda s: (s, average_reading(s)), accepted)
    ranked = sorted(scored, key=lambda pair: (-pair[1], pair[0].id))
    return tuple(sensor for sensor, _ in ranked[:top_n])
