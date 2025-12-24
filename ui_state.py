# ui_state.py
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class UiState:
    """
    UI state container for the Collatz visualizer.

    Responsibilities
    ----------------
    - Track evolution lifecycle (idle vs running)
    - Track current iteration bounds (current n and max n)
    - Provide minimal, deterministic state transitions for evolution
    """

    is_evolving: bool = False
    current_n: int = 1
    max_n: int = 0

    def start_evolution(self, max_n: int) -> None:
        """
        Initialize the evolution state and transition to the running mode.

        Parameters
        ----------
        max_n:
            Inclusive upper bound for the evolution run. Must be a positive integer.
        """
        if max_n <= 0:
            raise ValueError("max_n must be a positive integer.")

        self.is_evolving = True
        self.current_n = 1
        self.max_n = max_n

    def stop_evolution(self) -> None:
        """Transition the evolution state to idle mode."""
        self.is_evolving = False

    def is_completed(self) -> bool:
        """Return True if the evolution run has reached its terminal condition."""
        return self.max_n > 0 and self.current_n > self.max_n

    def next_n(self) -> int:
        """
        Return the current n value and advance the internal counter.

        Raises
        ------
        RuntimeError
            If called while the evolution is not running.
        """
        if not self.is_evolving:
            raise RuntimeError("next_n() called while evolution is not running.")

        n = self.current_n
        self.current_n += 1
        return n

    def reset(self) -> None:
        """Reset the state to the initial idle configuration."""
        self.is_evolving = False
        self.current_n = 1
        self.max_n = 0
