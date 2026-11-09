"""Оболонка вимірювань: медіани timeit, без порогів швидкості в тестах."""

from statistics import median
from timeit import repeat

from baseline import MutableSensor, add_reading_copy
from core import add_reading
from model import Reading, Sensor


def main() -> None:
    size, number, repeats = 1000, 100, 5
    immutable = Sensor(
        "T-01",
        "temperature",
        tuple(Reading(str(i), float(i)) for i in range(size)),
        frozenset({"indoor"}),
        {"unit": "C"},
    )
    mutable: MutableSensor = {
        "id": immutable.id,
        "kind": immutable.kind,
        "readings": [
            {"observed_at": r.observed_at, "value": r.value} for r in immutable.readings
        ],
        "labels": set(immutable.labels),
        "config": dict(immutable.config),
    }
    reading = Reading("new", 25.0)
    before = (
        median(
            repeat(
                lambda: add_reading_copy(
                    mutable, {"observed_at": "new", "value": 25.0}
                ),
                number=number,
                repeat=repeats,
            )
        )
        / number
    )
    after = (
        median(
            repeat(
                lambda: add_reading(immutable, reading),
                number=number,
                repeat=repeats,
            )
        )
        / number
    )
    print(f"Показів: {size}; повторів: {repeats}; операцій на повтор: {number}")
    print("Порівняння: нова незалежна версія, без зміни оригіналу")
    print(f"До: mutable + deepcopy + append: {before * 1e6:.2f} мкс/операцію")
    print(f"Після: frozen + tuple + replace: {after * 1e6:.2f} мкс/операцію")
    print(f"Відношення часу до/після: {before / after:.2f}")
    print("Це локальний вимір, а не гарантія швидкості для інших даних.")


if __name__ == "__main__":
    main()
