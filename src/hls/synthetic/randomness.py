"""Explicit injectable randomness sources."""

from __future__ import annotations

from dataclasses import dataclass, field
import random


@dataclass
class SeededRandomSource:
    seed: int
    _generator: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._generator = random.Random(self.seed)

    def random(self) -> float:
        return self._generator.random()
