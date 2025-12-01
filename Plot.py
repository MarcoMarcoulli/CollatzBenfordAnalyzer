from matplotlib.figure import Figure
import matplotlib
import itertools

from Math import expected_benford, leading_digit_frequencies

annotations = []

# ciclo di colori: ciclico, così non si esaurisce mai
color_cycle = itertools.cycle(matplotlib.cm.tab10.colors)


def create_figure():
    # figura con 2 subplot affiancati verticalmente
    fig = Figure(figsize=(7, 8), dpi=100)

    # 2 righe, 1 colonna: ax (orbite), ax_hist (istogramma)
    ax = fig.add_subplot(2, 1, 1)
    ax_hist = fig.add_subplot(2, 1, 2)

    # Pan/Zoom solo sul grafico superiore
    ax.set_navigate(True)
    ax_hist.set_navigate(False)

    # --- Setup asse principale ---
    ax.set_title("Collatz orbits (log scale)",
                 fontsize=14, fontweight="bold", color="#004080")
    ax.set_xlabel("Step")
    ax.set_ylabel("Value (log scale)")
    ax.set_yscale("log")
    ax.grid(True, which="both", linestyle="--", alpha=0.5)

    # --- Setup istogramma ---
    ax_hist.set_title("Leading digit frequency")
    ax_hist.set_xlabel("Leading digit")
    ax_hist.set_ylabel("Relative frequency")
    ax_hist.grid(axis="y", linestyle="--", alpha=0.5)

    fig.subplots_adjust(
        top=0.95,
        bottom=0.08,
        hspace=0.35   # distanza verticale tra grafici
    )

    return fig, ax, ax_hist


def add_orbit(ax, steps, orbit, n, show_labels=True, show_legend=True):
    """Add a new orbit to the graph."""

    color = next(color_cycle)

    ax.plot(
        steps,
        orbit,
        marker="o",
        linewidth=2,
        label=f"n = {n}",
        color=color
    )

    # Mostra il valore numerico vicino a ciascun punto
    if show_labels:
        for x, y in zip(steps, orbit):
            ann = ax.annotate(
                str(y),
                (x, y),
                textcoords="offset points",
                xytext=(0, 5),     # sposta il testo un po' sopra il punto
                ha="center",
                fontsize=10,
                color="#d30c0c"
            )
            annotations.append(ann)

    ax.set_xticks([])

    if show_legend:
        ax.legend()


def clear_all_labels():
    for ann in annotations:
        ann.remove()
    annotations.clear()


def reset_ax(ax):
    """Reset the axis to initial appearance."""
    ax.clear()

    ax.set_title("Collatz orbits (log scale)",
                 fontsize=14, fontweight="bold", color="#004080")
    ax.set_xlabel("Step")
    ax.set_ylabel("Value (log scale)")
    ax.set_yscale("log")
    ax.grid(True, which="both", linestyle="--", alpha=0.5)


def update_histogram(ax_hist, all_orbits):
    """Update histogram with cumulative leading-digit frequencies."""
    flattened = [x for orbit in all_orbits for x in orbit]

    ax_hist.clear()

    if not flattened:
        ax_hist.set_title("Leading digit frequency")
        ax_hist.set_xlabel("Leading digit")
        ax_hist.set_ylabel("Relative frequency")
        ax_hist.grid(axis="y", linestyle="--", alpha=0.5)
        return

    # Frequenze relative delle prime cifre (1..9)
    counts = leading_digit_frequencies(flattened)
    digits = list(range(1, 10))

    # Istogramma relativo osservato
    ax_hist.bar(
        digits,
        counts,
        color="#6699cc",
        alpha=0.8,
        label="Observed (relative)"
    )

    # Benford è già relativa
    exp_digits, exp_probs = expected_benford()
    exp_counts = exp_probs

    # Spezzata Benford
    ax_hist.plot(
        exp_digits,
        exp_counts,
        "-o",
        color="red",
        linewidth=2,
        markersize=6,
        label="Benford expected"
    )

    ax_hist.set_xticks(digits)
    ax_hist.set_xlabel("Leading digit")
    ax_hist.set_ylabel("Relative frequency")
    ax_hist.set_title("Leading digit distribution (observed vs Benford)")
    ax_hist.grid(axis="y", linestyle="--", alpha=0.5)
    ax_hist.legend()
