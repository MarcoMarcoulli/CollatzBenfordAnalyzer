# gui/actions.py
from __future__ import annotations

from typing import TYPE_CHECKING

from tkinter import messagebox

from core.collatz_math import collatz_orbit
from plotting.plot import add_orbit, reset_ax, update_histogram

from gui.state import Mode
from gui.validators import parse_positive_int

if TYPE_CHECKING:
    from gui.controller import CollatzGui


def run_single(controller: "CollatzGui") -> None:
    if controller.mode == Mode.IDLE:
        controller.set_mode(Mode.SINGLE)

    n = parse_positive_int(controller.ui.entry_main.get())
    if n is None:
        messagebox.showerror("Error", "Insert a positive integer N")
        return

    controller.plots.ensure_for_mode("SINGLE")

    orbit = collatz_orbit(n)
    steps = list(range(len(orbit)))

    controller.all_orbits.clear()
    reset_ax(controller.plots.ax_orbits)
    controller.all_orbits.append(orbit)

    show_labels = (len(controller.all_orbits) <= 2 and len(orbit) <= 20)
    add_orbit(controller.plots.ax_orbits, steps, orbit, n, show_labels=show_labels, show_legend=True)

    controller.plots.redraw()


def start_cumulative(controller: "CollatzGui") -> None:
    if controller.evo.is_evolving:
        return

    if controller.mode != Mode.CUMULATIVE:
        controller.set_mode(Mode.CUMULATIVE)

    max_n = parse_positive_int(controller.ui.entry_main.get())
    if max_n is None:
        messagebox.showerror("Error", "Insert a positive integer for Max N")
        return

    controller.evo.max_n = max_n
    controller.evo.current_n = 1
    controller.evo.is_evolving = True
    controller.evo.is_paused = False

    controller.plots.ensure_for_mode("CUMULATIVE")

    controller.all_orbits.clear()
    reset_ax(controller.plots.ax_orbits)
    update_histogram(controller.plots.ax_hist, controller.all_orbits)
    controller.plots.redraw()

    controller.ui.btn_stop.set_text("PAUSE")
    controller.ui.btn_stop.configure_state("normal")
    evolve_step(controller)


def evolve_step(controller: "CollatzGui") -> None:
    if not controller.evo.is_evolving:
        return
    
    if controller.evo.is_paused:
        return

    if controller.evo.current_n > controller.evo.max_n:
        controller.evo.is_evolving = False
        controller.ui.btn_stop.configure_state("disabled")
        return

    orbit = collatz_orbit(controller.evo.current_n)
    steps = list(range(len(orbit)))
    controller.all_orbits.append(orbit)

    add_orbit(controller.plots.ax_orbits, steps, orbit, controller.evo.current_n, show_labels=False, show_legend=False)
    update_histogram(controller.plots.ax_hist, controller.all_orbits)
    controller.plots.redraw()

    controller.evo.current_n += 1
    controller.root.after(controller.evo.delay_ms, lambda: evolve_step(controller))
