# plot.py
from __future__ import annotations

from dataclasses import dataclass
import itertools
from typing import Any

import matplotlib
from matplotlib.figure import Figure

from core.collatz_math import expected_benford, leading_digit_frequencies

# ------------------------ THEME ------------------------

@dataclass(frozen=True)
class PlotTheme:
    card_bg: str
    title: str
    ticks: str
    spine: str
    grid: str
    label: str
    bar: str
    benford: str


DEFAULT_THEME = PlotTheme(
    card_bg="#0b1220",
    title="#e2e8f0",
    ticks="#cbd5e1",
    spine="#334155",
    grid="#1f2a44",
    label="#f87171",
    bar="#60a5fa",
    benford="#f87171",
)


# ------------------------ INTERNAL STATE (PER-AXIS) ------------------------

_AX_ANN_KEY = "_collatz_annotations"
_AX_CYCLE_KEY = "_collatz_color_cycle"


def _ensure_ax_state(ax) -> None:
    if not hasattr(ax, _AX_ANN_KEY):
        setattr(ax, _AX_ANN_KEY, [])
    if not hasattr(ax, _AX_CYCLE_KEY):
        setattr(ax, _AX_CYCLE_KEY, itertools.cycle(matplotlib.cm.tab10.colors))


def _get_annotations(ax) -> list[Any]:
    _ensure_ax_state(ax)
    return getattr(ax, _AX_ANN_KEY)


def _get_color_cycle(ax):
    _ensure_ax_state(ax)
    return getattr(ax, _AX_CYCLE_KEY)


def _reset_color_cycle(ax) -> None:
    setattr(ax, _AX_CYCLE_KEY, itertools.cycle(matplotlib.cm.tab10.colors))


# ------------------------ STYLING HELPERS ------------------------

def apply_orbit_style(ax, *, title: str, theme: PlotTheme = DEFAULT_THEME) -> None:
    ax.set_facecolor(theme.card_bg)
    ax.set_title(title, color=theme.title, fontsize=12, pad=10)

    ax.tick_params(colors=theme.ticks)
    ax.xaxis.label.set_color(theme.ticks)
    ax.yaxis.label.set_color(theme.ticks)

    for spine in ax.spines.values():
        spine.set_color(theme.spine)
        spine.set_linewidth(1.0)

    ax.grid(True, color=theme.grid, linewidth=0.7, alpha=0.8)
    ax.set_yscale("log")
    ax.set_xticks([])


def apply_hist_style(ax, *, title: str, theme: PlotTheme = DEFAULT_THEME) -> None:
    ax.set_facecolor(theme.card_bg)
    ax.set_title(title, color=theme.title, fontsize=12, pad=10)

    ax.tick_params(colors=theme.ticks)
    ax.xaxis.label.set_color(theme.ticks)
    ax.yaxis.label.set_color(theme.ticks)

    for spine in ax.spines.values():
        spine.set_color(theme.spine)
        spine.set_linewidth(1.0)

    ax.grid(True, axis="y", color=theme.grid, linewidth=0.7, alpha=0.8)


def _style_legend(legend, theme: PlotTheme) -> None:
    if legend is None:
        return
    for text in legend.get_texts():
        text.set_color(theme.ticks)
    frame = legend.get_frame()
    frame.set_facecolor(theme.card_bg)
    frame.set_edgecolor(theme.spine)


# ------------------------ PUBLIC API ------------------------

def create_figure(*, theme: PlotTheme = DEFAULT_THEME) -> tuple[Figure, Any, Any]:
    """
    Create a figure with:
      - top axis: Collatz orbits (log scale)
      - bottom axis: leading digit histogram (Benford comparison)
    """
    fig = Figure(figsize=(7, 8), dpi=100, facecolor=theme.card_bg)

    ax_orbits = fig.add_subplot(2, 1, 1)
    ax_hist = fig.add_subplot(2, 1, 2)

    ax_orbits.set_navigate(True)
    ax_hist.set_navigate(False)

    apply_orbit_style(ax_orbits, title="Collatz Orbits (Log Scale)", theme=theme)
    ax_orbits.set_xlabel("Step")
    ax_orbits.set_ylabel("Value (log scale)")

    apply_hist_style(ax_hist, title="Leading Digit Distribution (Observed vs Benford)", theme=theme)
    ax_hist.set_xlabel("Leading digit")
    ax_hist.set_ylabel("Relative frequency")

    fig.subplots_adjust(top=0.95, bottom=0.08, hspace=0.35)
    return fig, ax_orbits, ax_hist


def add_orbit(
    ax,
    steps,
    orbit,
    n: int,
    *,
    show_labels: bool = True,
    show_legend: bool = True,
    theme: PlotTheme = DEFAULT_THEME,
) -> None:
    """
    Plot one orbit on the orbit axis.
    Per-axis annotations are stored on the axis object.
    """
    _ensure_ax_state(ax)
    color = next(_get_color_cycle(ax))

    ax.plot(
        steps,
        orbit,
        marker="o",
        linewidth=2,
        label=f"n = {n}",
        color=color,
    )

    if show_labels:
        anns = _get_annotations(ax)
        for x, y in zip(steps, orbit):
            ann = ax.annotate(
                str(y),
                (x, y),
                textcoords="offset points",
                xytext=(0, 6),
                ha="center",
                fontsize=9,
                color=theme.label,
            )
            anns.append(ann)

    ax.set_xticks([])

    if show_legend:
        legend = ax.legend()
        _style_legend(legend, theme)


def clear_all_labels(ax) -> None:
    """
    Remove all stored annotations from the orbit axis.
    Safe to call multiple times.
    """
    if not hasattr(ax, _AX_ANN_KEY):
        return

    anns = getattr(ax, _AX_ANN_KEY)
    for ann in list(anns):
        try:
            ann.remove()
        except Exception:
            pass
    anns.clear()


def reset_plot_state(ax_orbits=None) -> None:
    """
    Reset plotting state. If you pass an orbit axis, it will:
      - clear stored labels on that axis
      - reset its color cycle

    If you don't pass an axis, nothing breaks, but you won't reset per-axis state.
    """
    if ax_orbits is None:
        return

    clear_all_labels(ax_orbits)
    _reset_color_cycle(ax_orbits)


def reset_ax(ax, *, theme: PlotTheme = DEFAULT_THEME) -> None:
    """
    Reset the orbit axis to initial look (dark theme + log scale).
    """
    ax.clear()
    _ensure_ax_state(ax)
    clear_all_labels(ax)
    _reset_color_cycle(ax)

    apply_orbit_style(ax, title="Collatz Orbits (Log Scale)", theme=theme)
    ax.set_xlabel("Step")
    ax.set_ylabel("Value (log scale)")


def update_histogram(ax_hist, all_orbits, *, theme: PlotTheme = DEFAULT_THEME) -> None:
    """
    Update the histogram axis based on the cumulative values of all plotted orbits.
    """
    flattened = [x for orbit in all_orbits for x in orbit]

    ax_hist.clear()
    apply_hist_style(ax_hist, title="Leading Digit Distribution (Observed vs Benford)", theme=theme)
    ax_hist.set_xlabel("Leading digit")
    ax_hist.set_ylabel("Relative frequency")

    if not flattened:
        return

    counts = leading_digit_frequencies(flattened)
    digits = list(range(1, 10))

    ax_hist.bar(
        digits,
        counts,
        color=theme.bar,
        alpha=0.85,
        label="Observed",
    )

    exp_digits, exp_probs = expected_benford()
    ax_hist.plot(
        exp_digits,
        exp_probs,
        "-o",
        color=theme.benford,
        linewidth=2,
        markersize=5,
        label="Benford",
    )

    ax_hist.set_xticks(digits)

    legend = ax_hist.legend()
    _style_legend(legend, theme)
