# gui/state.py
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class Mode(Enum):
    IDLE = auto()
    SINGLE = auto()
    CUMULATIVE = auto()
    TREE = auto()


@dataclass
class EvolutionState:
    is_evolving: bool = False
    is_paused: bool = False
    current_n: int = 1
    max_n: int = 0
    delay_ms: int = 250
