# gui/layout.py
from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass

import ttkbootstrap as tb
from ttkbootstrap.constants import LEFT, BOTH, X, Y

from gui.theme import (
    SIDEBAR_BG,
    SIDEBAR_TEXT,
    CONTENT_BG,
    CARD_BG,
    CARD_SHADOW,
    WINDOW_GEOMETRY,
    WINDOW_MINSIZE,
    SIDEBAR_WIDTH,
    CONTENT_PADX,
    CONTENT_PADY,
    SIDEBAR_PADX,
    TITLE_PADY,
    CARD_RADIUS,
    CARD_PADDING,
    CARD_PACK_PADX,
    CARD_PACK_PADY_TOP,
    CARD_PACK_PADY_BOTTOM,
    BTN_TEXT,
    BTN_RESET_BG,
    BTN_RESET_HOVER,
    BTN_SELECTION_BG,
    BTN_SELECTION_HOVER,
    BTN_PAUSE_BG,
    BTN_PAUSE_HOVER,
    BTN_RADIUS,
    BTN_HEIGHT,
    BTN_FONT,
    ENTRY_FONT,
    ENTRY_IPADY,
)
from gui.widgets import RoundedCard, RoundedButton
from gui.state import Mode


@dataclass
class UiRefs:
    # root sections
    sidebar: tk.Frame
    content: tk.Frame

    # plot cards
    plot_container: tk.Frame
    orbits_card: RoundedCard
    hist_card: RoundedCard

    # sidebar widgets
    mode_label: tk.Label
    entry_main: tb.Entry

    btn_single: RoundedButton
    btn_cumulative: RoundedButton
    btn_tree: RoundedButton
    btn_stop: RoundedButton
    btn_reset: RoundedButton


def configure_root(root: tb.Window) -> None:
    root.title("COLLATZ ANALYZER")

    try:
        root.state("zoomed")
    except tk.TclError:
        root.attributes("-zoomed", True)

    root.geometry(WINDOW_GEOMETRY)
    root.minsize(*WINDOW_MINSIZE)
    root.configure(bg=CONTENT_BG)


def build_layout(root: tb.Window, callbacks: dict[str, callable]) -> UiRefs:
    """
    Builds the full UI and returns references to widgets.
    callbacks keys expected:
      - run_single, start_cumulative, run_tree, stop_evolution, reset, on_enter
    """
    main = tk.Frame(root, bg=CONTENT_BG)
    main.pack(fill=BOTH, expand=True)

    sidebar = tk.Frame(main, bg=SIDEBAR_BG, width=SIDEBAR_WIDTH)
    sidebar.pack(side=LEFT, fill=Y)
    sidebar.pack_propagate(False)

    content = tk.Frame(main, bg=CONTENT_BG)
    content.pack(side=LEFT, fill=BOTH, expand=True, padx=CONTENT_PADX, pady=CONTENT_PADY)

    # ---- controls
    mode_label = tk.Label(
        sidebar,
        text="Insert a positive integer:",
        bg=SIDEBAR_BG,
        fg=SIDEBAR_TEXT,
        font=("Segoe UI", 12, "bold"),
    )
    mode_label.pack(anchor="w", padx=SIDEBAR_PADX, pady=(8, 8))

    body = tk.Frame(sidebar, bg=SIDEBAR_BG)
    body.pack(fill=X, padx=SIDEBAR_PADX)

    entry_main = tb.Entry(body, bootstyle="light", font=ENTRY_FONT)
    entry_main.pack(fill=X, pady=(0, 14), ipady=ENTRY_IPADY)
    entry_main.focus_set()
    entry_main.bind("<Return>", lambda _e: callbacks["on_enter"]())

    btn_single = RoundedButton(
        body,
        text="SINGLE ORBIT",
        command=callbacks["run_single"],
        bg=BTN_SELECTION_BG,
        fg=BTN_TEXT,
        bg_hover=BTN_SELECTION_HOVER,
        bg_disabled=BTN_RESET_BG,
        radius=BTN_RADIUS,
        font=BTN_FONT,
        height=BTN_HEIGHT,
    )
    btn_single.pack(fill=X, pady=(0, 10))

    btn_cumulative = RoundedButton(
        body,
        text="BENFORD ANALYSIS",
        command=callbacks["start_cumulative"],
        bg=BTN_SELECTION_BG,
        fg=BTN_TEXT,
        bg_hover=BTN_SELECTION_HOVER,
        bg_disabled=BTN_RESET_BG,
        radius=BTN_RADIUS,
        font=BTN_FONT,
        height=BTN_HEIGHT,
    )
    btn_cumulative.pack(fill=X, pady=(0, 10))

    btn_tree = RoundedButton(
        body,
        text="COLLATZ INVERSE TREE",
        command=callbacks["run_tree"],
        bg=BTN_SELECTION_BG,
        fg=BTN_TEXT,
        bg_hover=BTN_SELECTION_HOVER,
        bg_disabled=BTN_RESET_BG,
        radius=BTN_RADIUS,
        font=BTN_FONT,
        height=BTN_HEIGHT,
    )
    btn_tree.pack(fill=X)

    tk.Frame(body, bg=SIDEBAR_BG, height=14).pack(fill=X)

    btn_stop = RoundedButton(
        body,
        text="PAUSE",
        command=callbacks["stop_evolution"],
        bg=BTN_PAUSE_BG,
        fg=BTN_TEXT,
        bg_hover=BTN_PAUSE_HOVER,
        bg_disabled=BTN_RESET_BG,
        radius=BTN_RADIUS,
        font=BTN_FONT,
        height=BTN_HEIGHT,
    )

    btn_reset = RoundedButton(
        body,
        text="RESET",
        command=callbacks["reset"],
        bg=BTN_RESET_BG,
        fg=BTN_TEXT,
        bg_hover=BTN_RESET_HOVER,
        bg_disabled=BTN_RESET_BG,
        radius=BTN_RADIUS,
        font=BTN_FONT,
        height=BTN_HEIGHT,
    )

    tk.Frame(sidebar, bg=SIDEBAR_BG).pack(fill=BOTH, expand=True)

    # ---- plot area
    plot_container = tk.Frame(content, bg=CONTENT_BG)
    plot_container.pack(fill=BOTH, expand=True)

    orbits_card = RoundedCard(
        plot_container,
        card_bg=CARD_BG,
        shadow_bg=CARD_SHADOW,
        radius=CARD_RADIUS,
        padding=CARD_PADDING,
    )
    orbits_card.pack(fill=BOTH, expand=True, padx=CARD_PACK_PADX, pady=CARD_PACK_PADY_TOP)

    hist_card = RoundedCard(
        plot_container,
        card_bg=CARD_BG,
        shadow_bg=CARD_SHADOW,
        radius=CARD_RADIUS,
        padding=CARD_PADDING,
    )
    hist_card.pack(fill=BOTH, expand=True, padx=CARD_PACK_PADX, pady=CARD_PACK_PADY_BOTTOM)

    return UiRefs(
        sidebar=sidebar,
        content=content,
        plot_container=plot_container,
        orbits_card=orbits_card,
        hist_card=hist_card,
        mode_label=mode_label,
        entry_main=entry_main,
        btn_single=btn_single,
        btn_cumulative=btn_cumulative,
        btn_tree=btn_tree,
        btn_stop=btn_stop,
        btn_reset=btn_reset,
    )


def apply_plot_layout_for_mode(ui: UiRefs, mode: Mode) -> None:
    """
    SINGLE/TREE: hide histogram, let orbits card fill space.
    CUMULATIVE: show both cards.
    IDLE: show both cards (ok) or same as SINGLE; choose what you prefer.
    """
    from gui.theme import CARD_PACK_PADX, CARD_PACK_PADY_TOP, CARD_PACK_PADY_BOTTOM

    if mode in (Mode.SINGLE, Mode.TREE):
        ui.hist_card.pack_forget()
        ui.orbits_card.pack_forget()
        ui.orbits_card.pack(fill=BOTH, expand=True, padx=CARD_PACK_PADX, pady=CARD_PACK_PADY_TOP)
        return

    if mode == Mode.CUMULATIVE:
        ui.orbits_card.pack_forget()
        ui.hist_card.pack_forget()

        ui.orbits_card.pack(fill=BOTH, expand=True, padx=CARD_PACK_PADX, pady=CARD_PACK_PADY_TOP)
        ui.hist_card.pack(fill=BOTH, expand=True, padx=CARD_PACK_PADX, pady=CARD_PACK_PADY_BOTTOM)
        return

    # IDLE: default = show both
    ui.orbits_card.pack_forget()
    ui.hist_card.pack_forget()
