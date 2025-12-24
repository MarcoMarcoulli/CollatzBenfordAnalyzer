# gui/app.py
import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as tb
from ttkbootstrap.constants import LEFT, BOTH, X, Y

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from collatz_math import collatz_orbit
from plot import add_orbit, reset_ax, update_histogram, reset_plot_state

from gui.theme import (
    # colors
    SIDEBAR_BG,
    SIDEBAR_TEXT,
    SIDEBAR_MUTED,
    CONTENT_BG,
    CARD_BG,
    CARD_SHADOW,
    ENTRY_TEXT,
    ENTRY_PLACEHOLDER,
    PLOT_TICKS,
    PLOT_TITLE,
    PLOT_SPINE,
    PLOT_GRID,
    BTN_TEXT,
    BTN_DISABLED_BG,
    BTN_PRIMARY_BG,
    BTN_PRIMARY_HOVER,
    BTN_SECONDARY_BG,
    BTN_SECONDARY_HOVER,
    BTN_SUCCESS_BG,
    BTN_SUCCESS_HOVER,
    BTN_DANGER_BG,
    BTN_DANGER_HOVER,
    # sizing
    WINDOW_GEOMETRY,
    WINDOW_MINSIZE,
    SIDEBAR_WIDTH,
    CONTENT_PADX,
    CONTENT_PADY,
    SIDEBAR_PADX,
    TITLE_PADY,
    SUBTITLE_PADY,
    CARD_RADIUS,
    CARD_PADDING,
    CARD_PACK_PADX,
    CARD_PACK_PADY_TOP,
    CARD_PACK_PADY_BOTTOM,
    BTN_RADIUS,
    BTN_HEIGHT,
    BTN_FONT,
    ENTRY_FONT,
    ENTRY_IPADY,
)

from gui.widgets import RoundedCard, RoundedButton


class CollatzGui:
    """
    GUI controller for the Collatz visualizer.

    Responsibilities
    ----------------
    - Build and style the layout (left sidebar + right plot area)
    - Validate user inputs and coordinate state transitions
    - Embed and manage Matplotlib canvases inside Tkinter
    - Orchestrate computations (Math) and rendering (Plot)
    """

    def __init__(self, root: tb.Window) -> None:
        self.root = root
        self.root.title("Collatz Visualizer")

        try:
            self.root.state("zoomed")
        except tk.TclError:
            self.root.attributes("-zoomed", True)

        self.root.geometry(WINDOW_GEOMETRY)
        self.root.minsize(*WINDOW_MINSIZE)

        # Cumulative orbit data used to update the histogram across all plotted sequences.
        self.all_orbits: list[list[int]] = []

        # Matplotlib objects (two independent figures for the two cards).
        self.fig_orbits: Figure | None = None
        self.ax_orbits = None
        self.canvas_orbits: FigureCanvasTkAgg | None = None

        self.fig_hist: Figure | None = None
        self.ax_hist = None
        self.canvas_hist: FigureCanvasTkAgg | None = None

        # Automatic evolution state.
        self.is_evolving = False
        self.current_n = 1
        self.max_n = 0
        self.evolution_delay_ms = 250

        self._configure_root()
        self._build_layout()

    # ------------------------ ROOT ------------------------

    def _configure_root(self) -> None:
        self.root.configure(bg=CONTENT_BG)

    # ------------------------ LAYOUT ------------------------

    def _build_layout(self) -> None:
        main = tk.Frame(self.root, bg=CONTENT_BG)
        main.pack(fill=BOTH, expand=True)

        # Sidebar (fixed width)
        self.sidebar = tk.Frame(main, bg=SIDEBAR_BG, width=SIDEBAR_WIDTH)
        self.sidebar.pack(side=LEFT, fill=Y)
        self.sidebar.pack_propagate(False)

        # Content
        self.content = tk.Frame(main, bg=CONTENT_BG)
        self.content.pack(side=LEFT, fill=BOTH, expand=True, padx=CONTENT_PADX, pady=CONTENT_PADY)

        self._build_sidebar()
        self._build_plot_area()

    def _build_sidebar(self) -> None:
        title = tk.Label(
            self.sidebar,
            text="COLLATZ ANALYZER",
            bg=SIDEBAR_BG,
            fg=SIDEBAR_TEXT,
            font=("Segoe UI", 20, "bold"),
        )
        title.pack(anchor="w", padx=SIDEBAR_PADX, pady=TITLE_PADY)

        subtitle = tk.Label(
            self.sidebar,
            text="Plot a single orbit, evolve 1..N cumulatively,\nor explore the Collatz tree.",
            bg=SIDEBAR_BG,
            fg=SIDEBAR_MUTED,
            font=("Segoe UI", 10),
            justify="left",
        )
        subtitle.pack(anchor="w", padx=SIDEBAR_PADX, pady=SUBTITLE_PADY)

        self._build_sidebar_controls()

        tk.Frame(self.sidebar, bg=SIDEBAR_BG).pack(fill=BOTH, expand=True)

    def _build_sidebar_controls(self) -> None:
        self.mode_label = tk.Label(
            self.sidebar,
            text="Choose a mode:",
            bg=SIDEBAR_BG,
            fg=SIDEBAR_TEXT,
            font=("Segoe UI", 12, "bold"),
        )
        self.mode_label.pack(anchor="w", padx=SIDEBAR_PADX, pady=(8, 8))

        self.help_label = tk.Label(
            self.sidebar,
            text="Enter a value and pick an action.",
            bg=SIDEBAR_BG,
            fg=SIDEBAR_MUTED,
            font=("Segoe UI", 10),
            justify="left",
            wraplength=SIDEBAR_WIDTH - 2 * SIDEBAR_PADX,
        )
        self.help_label.pack(anchor="w", padx=SIDEBAR_PADX, pady=(0, 10))

        body = tk.Frame(self.sidebar, bg=SIDEBAR_BG)
        body.pack(fill=X, padx=SIDEBAR_PADX)

        self.entry_main = tb.Entry(body, bootstyle="light", font=ENTRY_FONT)
        self.entry_main.pack(fill=X, pady=(0, 14), ipady=ENTRY_IPADY)
        self.entry_main.focus_set()

        # Actions (stacked)
        self.btn_single = RoundedButton(
            body,
            text="SINGLE ORBIT",
            command=self.run_single,
            bg=BTN_PRIMARY_BG,
            fg=BTN_TEXT,
            bg_hover=BTN_PRIMARY_HOVER,
            bg_disabled=BTN_DISABLED_BG,
            radius=BTN_RADIUS,
            font=BTN_FONT,
            height=BTN_HEIGHT,
        )
        self.btn_single.pack(fill=X, pady=(0, 10))

        self.btn_cumulative = RoundedButton(
            body,
            text="BENFORD ANALYSIS",
            command=self.start_cumulative,
            bg=BTN_SUCCESS_BG,
            fg=BTN_TEXT,
            bg_hover=BTN_SUCCESS_HOVER,
            bg_disabled=BTN_DISABLED_BG,
            radius=BTN_RADIUS,
            font=BTN_FONT,
            height=BTN_HEIGHT,
        )
        self.btn_cumulative.pack(fill=X, pady=(0, 10))

        self.btn_tree = RoundedButton(
            body,
            text="COLLATZ TREE",
            command=self.run_tree,
            bg=BTN_SECONDARY_BG,
            fg=BTN_TEXT,
            bg_hover=BTN_SECONDARY_HOVER,
            bg_disabled=BTN_DISABLED_BG,
            radius=BTN_RADIUS,
            font=BTN_FONT,
            height=BTN_HEIGHT,
        )
        self.btn_tree.pack(fill=X)

        # Stop + Reset (hidden initially)
        tk.Frame(body, bg=SIDEBAR_BG, height=14).pack(fill=X)

        self.btn_stop = RoundedButton(
            body,
            text="STOP",
            command=self.stop_evolution,
            bg=BTN_DANGER_BG,
            fg=BTN_TEXT,
            bg_hover=BTN_DANGER_HOVER,
            bg_disabled=BTN_DISABLED_BG,
            radius=BTN_RADIUS,
            font=BTN_FONT,
            height=BTN_HEIGHT,
        )

        self.btn_reset = RoundedButton(
            body,
            text="RESET",
            command=self.reset,
            bg=BTN_SECONDARY_BG,
            fg=BTN_TEXT,
            bg_hover=BTN_SECONDARY_HOVER,
            bg_disabled=BTN_DISABLED_BG,
            radius=BTN_RADIUS,
            font=BTN_FONT,
            height=BTN_HEIGHT,
        )

        # Enter triggers action depending on mode
        self.entry_main.bind("<Return>", lambda _e: self._on_enter_pressed())
        self.entry_main.focus_set()

        self._set_mode("IDLE")
    
    def _set_mode(self, mode: str) -> None:
        self.mode = mode

        # show/hide action buttons
        is_idle = (mode == "IDLE")
        is_cumulative = (mode == "CUMULATIVE")

        if is_idle:
            self.mode_label.config(text="Choose a mode:")
            self.help_label.config(text="Enter a value and pick an action.")

            # show actions
            self.btn_single.pack_configure()
            self.btn_cumulative.pack_configure()
            self.btn_tree.pack_configure()

            # hide stop/reset
            self.btn_stop.pack_forget()
            self.btn_reset.pack_forget()
            return

        # Non-idle modes
        if mode == "SINGLE":
            self.mode_label.config(text="Mode: Single Orbit")
            self.help_label.config(text="Enter N and press Enter (or Reset to change mode).")
            self.btn_stop.pack_forget()

        elif mode == "CUMULATIVE":
            self.mode_label.config(text="Mode: Cumulative Orbits (1..MaxN)")
            self.help_label.config(text="Enter Max N and start. Stop is available during evolution.")

            # show stop
            self.btn_stop.pack(fill=X, pady=(0, 10))
            self.btn_stop.configure_state("disabled")

        elif mode == "TREE":
            self.mode_label.config(text="Mode: Collatz Tree")
            self.help_label.config(text="Enter a parameter (e.g., depth) and run. (TODO)")
            self.btn_stop.pack_forget()

        # hide actions
        self.btn_single.pack_forget()
        self.btn_cumulative.pack_forget()
        self.btn_tree.pack_forget()

        # show reset
        self.btn_reset.pack(fill=X)


    def _on_enter_pressed(self) -> None:
        if self.mode == "IDLE":
            # sensible default: single orbit
            self.run_single()
        elif self.mode == "SINGLE":
            self.run_single()
        elif self.mode == "CUMULATIVE":
            self.start_cumulative()
        elif self.mode == "TREE":
            self.run_tree()

    def _build_plot_area(self) -> None:
        self.plot_container = tk.Frame(self.content, bg=CONTENT_BG)
        self.plot_container.pack(fill=BOTH, expand=True)

        # Card 1 (orbits)
        self.orbits_card = RoundedCard(
            self.plot_container,
            card_bg=CARD_BG,
            shadow_bg=CARD_SHADOW,
            radius=CARD_RADIUS,
            padding=CARD_PADDING,
        )
        self.orbits_card.pack(fill=BOTH, expand=True, padx=CARD_PACK_PADX, pady=CARD_PACK_PADY_TOP)

        # Card 2 (histogram)
        self.hist_card = RoundedCard(
            self.plot_container,
            card_bg=CARD_BG,
            shadow_bg=CARD_SHADOW,
            radius=CARD_RADIUS,
            padding=CARD_PADDING,
        )
        self.hist_card.pack(fill=BOTH, expand=True, padx=CARD_PACK_PADX, pady=CARD_PACK_PADY_BOTTOM)

    # ------------------------ INPUT VALIDATION ------------------------

    @staticmethod
    def _parse_positive_int(raw: str) -> int | None:
        try:
            n = int(raw.strip())
            return n if n > 0 else None
        except (ValueError, AttributeError):
            return None


    # ------------------------ MANUAL ORBIT ------------------------

    def run_single(self) -> None:
        if self.mode == "IDLE":
            self._set_mode("SINGLE")

        n = self._parse_positive_int(self.entry_main.get())
        if n is None:
            messagebox.showerror("Error", "Insert a positive integer N")
            return

        orbit = collatz_orbit(n)
        steps = list(range(len(orbit)))

        if self.ax_orbits is None or self.ax_hist is None:
            self._ensure_plot_surface()

        self.all_orbits.clear()
        reset_ax(self.ax_orbits)

        self.all_orbits.append(orbit)

        show_labels = (len(self.all_orbits) <= 2 and len(orbit) <= 20)
        add_orbit(self.ax_orbits, steps, orbit, n, show_labels=show_labels, show_legend=True)

        update_histogram(self.ax_hist, self.all_orbits)
        self._redraw()

    # ------------------------ AUTOMATIC EVOLUTION ------------------------

    def start_cumulative(self) -> None:
        if self.is_evolving:
            return

        if self.mode == "IDLE":
            self._set_mode("CUMULATIVE")
        elif self.mode != "CUMULATIVE":
            self._set_mode("CUMULATIVE")

        max_n = self._parse_positive_int(self.entry_main.get())
        if max_n is None:
            max_n = self._parse_positive_int(self.entry_main.get())
        if max_n is None:
            messagebox.showerror("Error", "Insert a positive integer for Max N")
            return

        self.max_n = max_n
        self.current_n = 1
        self.is_evolving = True

        if self.fig_orbits is None:
            self._ensure_plot_surface()

        self.all_orbits.clear()
        reset_ax(self.ax_orbits)
        update_histogram(self.ax_hist, self.all_orbits)
        self._redraw()

        # enable Stop while running
        self.btn_stop.configure_state("normal")

        self._evolve_step()
    
    def run_tree(self) -> None:
        if self.mode == "IDLE":
            self._set_mode("TREE")
        messagebox.showinfo("Info", "Collatz Tree: not implemented yet.")

    def _evolve_step(self) -> None:
        if not self.is_evolving:
            return

        if self.current_n > self.max_n:
            self.is_evolving = False
            self.btn_stop.configure_state("disabled")
            return

        orbit = collatz_orbit(self.current_n)
        steps = list(range(len(orbit)))
        self.all_orbits.append(orbit)

        add_orbit(self.ax_orbits, steps, orbit, self.current_n, show_labels=False, show_legend=False)
        update_histogram(self.ax_hist, self.all_orbits)
        self._redraw()

        self.current_n += 1
        self.root.after(self.evolution_delay_ms, self._evolve_step)

    def stop_evolution(self) -> None:
        if not self.is_evolving:
            return
        self.is_evolving = False
        self.btn_stop.configure_state("disabled")

    # ------------------------ PLOT SURFACE ------------------------

    def _apply_dark_axes_style(self, ax, title: str) -> None:
        ax.set_facecolor(CARD_BG)
        ax.set_title(title, color=PLOT_TITLE, fontsize=12, pad=10)

        ax.tick_params(colors=PLOT_TICKS)
        ax.xaxis.label.set_color(PLOT_TICKS)
        ax.yaxis.label.set_color(PLOT_TICKS)

        for spine in ax.spines.values():
            spine.set_color(PLOT_SPINE)
            spine.set_linewidth(1.0)

        ax.grid(True, color=PLOT_GRID, linewidth=0.7, alpha=0.8)

    def _ensure_plot_surface(self) -> None:
        if self.fig_orbits is not None and self.fig_hist is not None:
            return

        # Orbits
        self.fig_orbits = Figure(figsize=(6, 3), dpi=100, facecolor=CARD_BG)
        self.ax_orbits = self.fig_orbits.add_subplot(111)
        self._apply_dark_axes_style(self.ax_orbits, "Collatz Orbits (Log Scale)")

        # Histogram
        self.fig_hist = Figure(figsize=(6, 3), dpi=100, facecolor=CARD_BG)
        self.ax_hist = self.fig_hist.add_subplot(111)
        self._apply_dark_axes_style(self.ax_hist, "Leading Digit Distribution (Observed vs Benford)")

        self._create_canvas_orbits()
        self._create_canvas_hist()

    def _create_canvas_orbits(self) -> None:
        self.canvas_orbits = FigureCanvasTkAgg(self.fig_orbits, master=self.orbits_card.inner)
        widget = self.canvas_orbits.get_tk_widget()
        widget.configure(bg=CARD_BG, highlightthickness=0, bd=0)
        widget.pack(fill=BOTH, expand=True)

    def _create_canvas_hist(self) -> None:
        self.canvas_hist = FigureCanvasTkAgg(self.fig_hist, master=self.hist_card.inner)
        widget = self.canvas_hist.get_tk_widget()
        widget.configure(bg=CARD_BG, highlightthickness=0, bd=0)
        widget.pack(fill=BOTH, expand=True)

    def _redraw(self) -> None:
        if self.canvas_orbits is not None:
            self.canvas_orbits.draw()
        if self.canvas_hist is not None:
            self.canvas_hist.draw()

    # ------------------------ RESET ------------------------

    def reset(self) -> None:
        self.is_evolving = False
        self.current_n = 1
        self.max_n = 0
        self.all_orbits.clear()
        self._set_mode("IDLE")

        reset_plot_state()
        self._destroy_plot_surface()

    def _destroy_plot_surface(self) -> None:
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
