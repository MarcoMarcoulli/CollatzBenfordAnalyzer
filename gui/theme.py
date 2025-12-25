# gui/theme.py
"""
Centralized UI theme constants for the Collatz GUI.

Keep all palette + sizing knobs here so you can tweak the look
without touching layout logic.
"""

# ------------------------ COLORS ------------------------

# Sidebar
SIDEBAR_BG = "#dee1e7"
SIDEBAR_TEXT = "#020202"
SIDEBAR_MUTED = "#a9b4c6"

# Main content area
CONTENT_BG = "#ffffff"

# Cards (plots)
CARD_BG = "#465e8f"
CARD_SHADOW = "#2a3245"

# Plot styling (dark)
PLOT_TICKS = "#cbd5e1"
PLOT_TITLE = "#e2e8f0"
PLOT_SPINE = "#334155"
PLOT_GRID = "#1f2a44"

# Buttons
BTN_TEXT = "#ffffff"
BTN_RESET_BG = "#475569"
BTN_RESET_HOVER = "#323C4A"
BTN_DISABLED_TEXT = "#e2e8f0"

BTN_SELECTION_BG = "#2563eb"
BTN_SELECTION_HOVER = "#163c90"

BTN_RESUME_BG = "#22c55e"
BTN_RESUME_HOVER = "#16a34a"

BTN_PAUSE_BG = "#ef4444"
BTN_PAUSE_HOVER = "#dc2626"


# ------------------------ SIZING / SPACING ------------------------

# Window
WINDOW_GEOMETRY = "1200x720"
WINDOW_MINSIZE = (1050, 650)

# Sidebar
SIDEBAR_WIDTH = 360

# Common paddings
CONTENT_PADX = 18
CONTENT_PADY = 18

SIDEBAR_PADX = 22
TITLE_PADY = (18, 8)

SECTION_GAP = 18

# Cards
CARD_RADIUS = 22
CARD_PADDING = 18
CARD_PACK_PADX = 10
CARD_PACK_PADY_TOP = (10, 12)
CARD_PACK_PADY_BOTTOM = (0, 10)

# Buttons
BTN_RADIUS = 14
BTN_HEIGHT = 40
BTN_FONT = ("Segoe UI", 15, "bold")

# Entry
ENTRY_FONT = ("Segoe UI", 12)
ENTRY_IPADY = 6
