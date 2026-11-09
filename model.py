"""Незмінні сутності IoT-сенсорів, варіант 14."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from math import isfinite
from types import MappingProxyType

ConfigValue = str | int | float | bool


@dataclass(frozen=True, slots=True)
class Reading:
    observed_at: str
    value: float

    def __post_init__(self) -> None:
        if not isfinite(self.value):
            raise ValueError("Показ має бути скінченним числом")


@dataclass(frozen=True, slots=True)
class Sensor:
    id: str
    kind: str
    readings: tuple[Reading, ...] = ()
    labels: frozenset[str] = frozenset()
    config: Mapping[str, ConfigValue] = field(default_factory=dict, hash=False)

    def __post_init__(self) -> None:
        # Копіюємо джерело: proxy не відображатиме зовнішніх змін.
        config = dict(self.config)
        if any(
            not isinstance(key, str) or type(value) not in (str, int, float, bool)
            for key, value in config.items()
        ):
            raise TypeError("config допускає лише рядкові ключі та скалярні значення")
        if any(isinstance(v, float) and not isfinite(v) for v in config.values()):
            raise ValueError("Числові параметри config мають бути скінченними")
        object.__setattr__(self, "readings", tuple(self.readings))
        object.__setattr__(self, "labels", frozenset(self.labels))
        object.__setattr__(self, "config", MappingProxyType(config))
