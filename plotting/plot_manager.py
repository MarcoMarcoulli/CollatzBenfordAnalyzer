# plot_manager.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, Any

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from plotting.plot import (
    PlotTheme as PlotPyTheme,
    DEFAULT_THEME,
    add_orbit as plot_add_orbit,
    create_figure,
    reset_ax,
    update_histogram,
    reset_plot_state,
)


@dataclass(frozen=True)
class PlotTheme:
    """
    Theme aligned with the GUI palette, then mapped to plot.py PlotTheme.
    """
    card_bg: str
    title: str
    ticks: str
    spine: str
    grid: str
    label: str
    bar: str
    benford: str


class PlotManager:
    """
    Matplotlib/Tkinter integration layer.
    """

    def __init__(self, theme: PlotTheme) -> None:
        self._theme = theme
        self._plot_theme: PlotPyTheme = PlotPyTheme(
            card_bg=theme.card_bg,
            title=theme.title,
            ticks=theme.ticks,
            spine=theme.spine,
            grid=theme.grid,
            label=theme.label,
            bar=theme.bar,
            benford=theme.benford,
        )

        self._fig: Any = None
        self._ax: Any = None
        self._ax_hist: Any = None

        self._canvas: Optional[FigureCanvasTkAgg] = None
        self._toolbar: Optional[NavigationToolbar2Tk] = None
        self._parent = None

    @property
    def is_created(self) -> bool:
        return self._fig is not None and self._ax is not None and self._ax_hist is not None

    # ------------------------ LIFECYCLE ------------------------

    def ensure_created(self, parent) -> None:
        if self.is_created:
            return

        self._parent = parent
        self._fig, self._ax, self._ax_hist = create_figure(theme=self._plot_theme)
        self._create_canvas()

    def destroy(self) -> None:
        # reset per-axis state (labels + color cycle)
        if self._ax is not None:
            reset_plot_state(self._ax)

        if self._canvas is not None:
            self._canvas.get_tk_widget().destroy()
            self._canvas = None

        if self._toolbar is not None:
            self._toolbar.destroy()
            self._toolbar = None

        self._fig = None
        self._ax = None
        self._ax_hist = None
        self._parent = None

    # ------------------------ CANVAS ------------------------

    def _create_canvas(self) -> None:
        if self._parent is None:
            raise RuntimeError("PlotManager requires a Tkinter parent before creating a canvas.")

        self._canvas = FigureCanvasTkAgg(self._fig, master=self._parent)
        widget = self._canvas.get_tk_widget()
        widget.configure(bg=self._plot_theme.card_bg, highlightthickness=0, bd=0)
        widget.pack(fill="both", expand=True, padx=14, pady=(14, 8))

        self._toolbar = NavigationToolbar2Tk(self._canvas, self._parent)
        self._toolbar.update()

    def redraw(self) -> None:
        if self._canvas is not None:
            self._canvas.draw()

    # ------------------------ HIGH-LEVEL PLOTTING ------------------------

    def reset_axes(self) -> None:
        self._require_created()
        reset_ax(self._ax, theme=self._plot_theme)

    def clear_histogram(self) -> None:
        self._require_created()
        update_histogram(self._ax_hist, [], theme=self._plot_theme)

    def plot_orbit(
        self,
        n: int,
        orbit: Sequence[int],
        *,
        show_labels: bool,
        show_legend: bool,
    ) -> None:
        self._require_created()
        steps = list(range(len(orbit)))
        plot_add_orbit(
            self._ax,
            steps,
            orbit,
            n,
            show_labels=show_labels,
            show_legend=show_legend,
            theme=self._plot_theme,
        )

    def update_histogram(self, all_orbits: Sequence[Sequence[int]]) -> None:
        self._require_created()
        update_histogram(self._ax_hist, all_orbits, theme=self._plot_theme)

    # ------------------------ UTILITIES ------------------------

    def _require_created(self) -> None:
        if not self.is_created:
            raise RuntimeError("Plot surface not created. Call ensure_created(parent) first.")
