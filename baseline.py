"""Мутабельна модель «до» для чесного порівняння з immutable API."""

from copy import deepcopy
from typing import TypedDict

from model import ConfigValue


class MutableReading(TypedDict):
    observed_at: str
    value: float


class MutableSensor(TypedDict):
    id: str
    kind: str
    readings: list[MutableReading]
    labels: set[str]
    config: dict[str, ConfigValue]


def add_reading_copy(sensor: MutableSensor, reading: MutableReading) -> MutableSensor:
    """Захисна копія перед append зберігає початковий мутабельний стан."""
    copied = deepcopy(sensor)
    copied["readings"].append(deepcopy(reading))
    return copied
