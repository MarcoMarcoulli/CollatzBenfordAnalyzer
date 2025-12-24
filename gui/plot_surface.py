# gui/plot_surface.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any

import tkinter as tk
from ttkbootstrap.constants import BOTH

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


@dataclass(frozen=True)
class PlotTheme:
    """Visual theme for Matplotlib surfaces embedded in Tk."""
    card_bg: str
    plot_title: str
    plot_ticks: str
    plot_spine: str
    plot_grid: str


class PlotSurface:
    """
    Manages Matplotlib figures/canvases embedded into Tkinter frames.

    Responsibilities
    ----------------
    - Create and destroy Matplotlib figures and FigureCanvasTkAgg widgets
    - Apply consistent dark theme styling to axes
    - Expose axes for higher-level plotting functions (add_orbit, update_histogram, etc.)
    - Redraw canvases safely
    """

    def __init__(
        self,
        orbits_parent: tk.Frame,
        hist_parent: tk.Frame,
        theme: PlotTheme,
    ) -> None:
        self._orbits_parent = orbits_parent
        self._hist_parent = hist_parent
        self._theme = theme

        # Orbits figure/canvas
        self.fig_orbits: Optional[Figure] = None
        self.ax_orbits: Any = None
        self.canvas_orbits: Optional[FigureCanvasTkAgg] = None

        # Histogram figure/canvas
        self.fig_hist: Optional[Figure] = None
        self.ax_hist: Any = None
        self.canvas_hist: Optional[FigureCanvasTkAgg] = None

    # ------------------------ CREATE / ENSURE ------------------------

    def ensure_orbits(self, title: str = "Collatz Orbits (Log Scale)") -> None:
        """Ensure the orbits figure+canvas exists."""
        if self.fig_orbits is not None:
            return

        self.fig_orbits = Figure(figsize=(6, 3), dpi=100, facecolor=self._theme.card_bg)
        self.ax_orbits = self.fig_orbits.add_subplot(111)
        self._apply_axes_style(self.ax_orbits, title=title)
        self.canvas_orbits = self._create_canvas(self.fig_orbits, self._orbits_parent)

    def ensure_hist(self, title: str = "Leading Digit Distribution (Observed vs Benford)") -> None:
        """Ensure the histogram figure+canvas exists."""
        if self.fig_hist is not None:
            return

        self.fig_hist = Figure(figsize=(6, 3), dpi=100, facecolor=self._theme.card_bg)
        self.ax_hist = self.fig_hist.add_subplot(111)
        self._apply_axes_style(self.ax_hist, title=title)
        self.canvas_hist = self._create_canvas(self.fig_hist, self._hist_parent)

    def ensure_for_mode(self, mode: str) -> None:
        """
        Convenience helper:
        - SINGLE: only orbits
        - CUMULATIVE: orbits + histogram
        """
        self.ensure_orbits()
        if mode == "CUMULATIVE":
            self.ensure_hist()

    # ------------------------ STYLE ------------------------

    def _apply_axes_style(self, ax: Any, title: str) -> None:
        ax.set_facecolor(self._theme.card_bg)
        ax.set_title(title, color=self._theme.plot_title, fontsize=12, pad=10)

        ax.tick_params(colors=self._theme.plot_ticks)
        ax.xaxis.label.set_color(self._theme.plot_ticks)
        ax.yaxis.label.set_color(self._theme.plot_ticks)

        for spine in ax.spines.values():
            spine.set_color(self._theme.plot_spine)
            spine.set_linewidth(1.0)

        ax.grid(True, color=self._theme.plot_grid, linewidth=0.7, alpha=0.8)

    # ------------------------ CANVAS ------------------------

    def _create_canvas(self, fig: Figure, parent: tk.Frame) -> FigureCanvasTkAgg:
        canvas = FigureCanvasTkAgg(fig, master=parent)
        widget = canvas.get_tk_widget()
        widget.configure(bg=self._theme.card_bg, highlightthickness=0, bd=0)
        widget.pack(fill=BOTH, expand=True)
        return canvas

    def redraw(self) -> None:
        """Redraw existing canvases."""
        if self.canvas_orbits is not None:
            self.canvas_orbits.draw()
        if self.canvas_hist is not None:
            self.canvas_hist.draw()

    # ------------------------ DESTROY ------------------------

    def destroy(self) -> None:
        """Destroy all Matplotlib surfaces and reset to a clean state."""
        if self.canvas_orbits is not None:
            self.canvas_orbits.get_tk_widget().destroy()
            self.canvas_orbits = None
        if self.canvas_hist is not None:
            self.canvas_hist.get_tk_widget().destroy()
            self.canvas_hist = None

        self.fig_orbits = None
        self.ax_orbits = None
        self.fig_hist = None
        self.ax_hist = None
