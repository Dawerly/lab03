"""Парні навантажувальні тести, час порівнюється через --durations=5."""

from baseline import MutableSensor, add_reading_copy
from core import add_reading
from model import Reading, Sensor


def test_before_mutable_defensive_copy() -> None:
    sensor: MutableSensor = {
        "id": "T-01",
        "kind": "temperature",
        "readings": [{"observed_at": str(i), "value": float(i)} for i in range(1000)],
        "labels": {"indoor"},
        "config": {"unit": "C"},
    }
    for _ in range(40):
        result = add_reading_copy(sensor, {"observed_at": "new", "value": 25.0})
        assert len(result["readings"]) == 1001
        assert result["readings"][-1]["value"] == 25.0
    assert len(sensor["readings"]) == 1000


def test_after_immutable_shared_readings() -> None:
    sensor = Sensor(
        "T-01",
        "temperature",
        tuple(Reading(str(i), float(i)) for i in range(1000)),
        frozenset({"indoor"}),
        {"unit": "C"},
    )
    for _ in range(40):
        result = add_reading(sensor, Reading("new", 25.0))
        assert len(result.readings) == 1001
        assert result.readings[-1].value == 25.0
        assert result.readings[0] is sensor.readings[0]
    assert len(sensor.readings) == 1000
