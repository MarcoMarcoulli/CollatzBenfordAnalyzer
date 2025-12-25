# gui/controller.py
from __future__ import annotations

from tkinter import messagebox

import ttkbootstrap as tb

from plotting.plot import reset_plot_state

from gui.layout import configure_root, build_layout, apply_plot_layout_for_mode, UiRefs
from gui.plot_surface import PlotSurface, PlotTheme
from gui.state import Mode, EvolutionState
from gui.theme import CARD_BG, PLOT_TITLE, PLOT_TICKS, PLOT_SPINE, PLOT_GRID, BTN_PAUSE_BG, BTN_PAUSE_HOVER, BTN_RESUME_BG, BTN_RESUME_HOVER
from gui import actions


class CollatzGui:
    """
    App controller: owns state and orchestrates UI + plotting.
    """

    def __init__(self, root: tb.Window) -> None:
        self.root = root
        configure_root(self.root)

        # state
        self.mode: Mode = Mode.IDLE
        self.evo = EvolutionState()
        self.all_orbits: list[list[int]] = []

        # build UI
        self.ui: UiRefs = build_layout(
            self.root,
            callbacks={
                "run_single": lambda: actions.run_single(self),
                "start_cumulative": lambda: actions.start_cumulative(self),
                "run_tree": self.run_tree,
                "stop_evolution": self.toggle_pause,  # <-- changed
                "reset": self.reset,
                "on_enter": self.on_enter_pressed,
            },
        )

        # plots
        self.plots = PlotSurface(
            orbits_parent=self.ui.orbits_card.inner,
            hist_parent=self.ui.hist_card.inner,
            theme=PlotTheme(
                card_bg=CARD_BG,
                plot_title=PLOT_TITLE,
                plot_ticks=PLOT_TICKS,
                plot_spine=PLOT_SPINE,
                plot_grid=PLOT_GRID,
            ),
        )

        self.set_mode(Mode.IDLE)

    # ------------------------ MODE ------------------------

    def set_mode(self, mode: Mode) -> None:
        self.mode = mode

        if mode == Mode.IDLE:
            self.ui.mode_label.config(text="Insert a positive integer:")

            self.ui.entry_main.delete(0, "end")   
            self.ui.entry_main.focus_set() 

            # show actions
            self.ui.btn_single.pack(fill="x", pady=(0, 10))
            self.ui.btn_cumulative.pack(fill="x", pady=(0, 10))
            self.ui.btn_tree.pack(fill="x")

            # hide pause/reset
            self.ui.btn_stop.pack_forget()
            self.ui.btn_reset.pack_forget()

            apply_plot_layout_for_mode(self.ui, mode)
            return

        if mode == Mode.SINGLE:
            self.ui.mode_label.config(text="Mode: Single Orbit")
            self.ui.btn_stop.pack_forget()

        elif mode == Mode.CUMULATIVE:
            self.ui.mode_label.config(text="Mode: Benford Analysis")

            self.ui.btn_stop.set_text("PAUSE")
            self.ui.btn_stop.pack(fill="x", pady=(0, 10))
            self.ui.btn_stop.set_background(
                bg=BTN_PAUSE_BG,
                bg_hover=BTN_PAUSE_HOVER,
            )
            self.ui.btn_stop.configure_state("disabled")

        elif mode == Mode.TREE:
            self.ui.mode_label.config(text="Mode: Collatz inverse Tree")
            self.ui.btn_stop.pack_forget()

        # hide actions
        self.ui.btn_single.pack_forget()
        self.ui.btn_cumulative.pack_forget()
        self.ui.btn_tree.pack_forget()

        # show reset
        self.ui.btn_reset.pack(fill="x")

        apply_plot_layout_for_mode(self.ui, mode)

    def on_enter_pressed(self) -> None:
        if self.mode in (Mode.IDLE, Mode.SINGLE):
            actions.run_single(self)
        elif self.mode == Mode.CUMULATIVE:
            actions.start_cumulative(self)
        elif self.mode == Mode.TREE:
            self.run_tree()

    # ------------------------ TREE (TODO) ------------------------

    def run_tree(self) -> None:
        if self.mode == Mode.IDLE:
            self.set_mode(Mode.TREE)
        messagebox.showinfo("Info", "Collatz Tree: not implemented yet.")

    # ------------------------ EVOLUTION CONTROL ------------------------

    def toggle_pause(self) -> None:
        if not self.evo.is_evolving:
            return

        self.evo.is_paused = not self.evo.is_paused

        if self.evo.is_paused:
            self.ui.btn_stop.set_text("RESUME")
            self.ui.btn_stop.set_background(
                bg=BTN_RESUME_BG,
                bg_hover=BTN_RESUME_HOVER,
            )
        else:
            self.ui.btn_stop.set_text("PAUSE")
            self.ui.btn_stop.set_background(
                bg=BTN_PAUSE_BG,
                bg_hover=BTN_PAUSE_HOVER,
            )
            actions.evolve_step(self)  

    # ------------------------ RESET ------------------------

    def reset(self) -> None:
        self.evo.is_evolving = False
        self.evo.is_paused = False
        self.evo.current_n = 1
        self.evo.max_n = 0
        self.all_orbits.clear()

        self.set_mode(Mode.IDLE)

        reset_plot_state()
        self.plots.destroy()
