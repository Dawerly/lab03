"""Демонстраційна I/O-оболонка для варіанта 14."""

from core import (
    add_label,
    add_reading,
    average_reading,
    calibrate,
    rank_sensors,
    update_config,
)
from model import Reading, Sensor


def main() -> None:
    original = Sensor(
        id="T-01",
        kind="temperature",
        readings=(Reading("09:00", 20.0), Reading("10:00", 22.0)),
        labels=frozenset({"indoor"}),
        config={"unit": "C", "interval": 60},
    )
    updated = update_config(
        add_label(add_reading(original, Reading("11:00", 24.0)), "verified"),
        {"interval": 30},
    )
    calibrated = calibrate(updated, factor=1.0, offset=0.5)
    print("=== IOT-СЕНСОРИ | ВАРІАНТ 14 ===")
    for title, sensor in [
        ("Оригінал", original),
        ("Нова версія", updated),
        ("Калібрування", calibrated),
    ]:
        print(
            f"{title}: показів={len(sensor.readings)}, середнє={average_reading(sensor):.2f}"
        )
    print(f"Мітки оригіналу: {', '.join(sorted(original.labels))}")
    print(f"Нові мітки: {', '.join(sorted(updated.labels))}")
    print(f"Інтервал: {original.config['interval']} -> {updated.config['interval']}")
    print(f"Новий об'єкт: {original is not updated}")
    print(
        f"Sensor як ключ dict: {{original: 'saved'}} -> { {original: 'saved'}[original] }"
    )
    try:
        updated.config["interval"] = 1  # type: ignore[index]
    except TypeError:
        print("config: зміну заблоковано (TypeError)")
    top = rank_sensors(
        (original, Sensor("T-02", "temperature", (Reading("10:00", 23.0),))),
        kind="temperature",
        min_readings=1,
        top_n=2,
    )
    print("Рейтинг сенсорів:", ", ".join(s.id for s in top))


if __name__ == "__main__":
    main()
