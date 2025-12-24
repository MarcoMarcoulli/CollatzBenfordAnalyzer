# gui/widgets.py
import tkinter as tk

def _rounded_rect_points(x1: int, y1: int, x2: int, y2: int, r: int) -> list[int]:
    """
    Return a list of points suitable for a smooth polygon approximating
    a rounded rectangle in a Tk Canvas.
    """
    r = max(0, min(r, (x2 - x1) // 2, (y2 - y1) // 2))
    return [
        x1 + r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1,
    ]


class RoundedCard(tk.Frame):
    """
    Rounded "card" with shadow, implemented with a Canvas background,
    plus an inner frame where you pack normal widgets.

    Usage:
        card = RoundedCard(parent, card_bg="#0b1220", shadow_bg="#0a0f1c")
        card.pack(...)
        # Put content inside:
        some_widget = tk.Label(card.inner, ...)
        some_widget.pack(...)
    """

    def __init__(
        self,
        master,
        card_bg: str,
        shadow_bg: str,
        radius: int = 18,
        shadow_offset: tuple[int, int] = (6, 8),
        padding: int = 18,
        **kwargs,
    ):
        super().__init__(master, bg=master["bg"], **kwargs)

        self.card_bg = card_bg
        self.shadow_bg = shadow_bg
        self.radius = radius
        self.shadow_dx, self.shadow_dy = shadow_offset
        self.padding = padding

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=self["bg"])
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.inner = tk.Frame(self.canvas, bg=self.card_bg)
        self._inner_window = self.canvas.create_window(0, 0, anchor="nw", window=self.inner)

        self.canvas.bind("<Configure>", self._redraw)

    def _draw_round(self, x1: int, y1: int, x2: int, y2: int, r: int, fill: str, tag: str) -> None:
        pts = _rounded_rect_points(x1, y1, x2, y2, r)
        self.canvas.create_polygon(
            pts,
            smooth=True,
            splinesteps=12,
            fill=fill,
            outline="",
            tags=tag,
        )

    def _redraw(self, _evt=None) -> None:
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 2 or h <= 2:
            return

        self.canvas.delete("card")

        pad_outer = 10

        # Shadow
        self._draw_round(
            pad_outer + self.shadow_dx,
            pad_outer + self.shadow_dy,
            w - pad_outer + self.shadow_dx,
            h - pad_outer + self.shadow_dy,
            self.radius,
            self.shadow_bg,
            "card",
        )

        # Main card
        self._draw_round(
            pad_outer,
            pad_outer,
            w - pad_outer,
            h - pad_outer,
            self.radius,
            self.card_bg,
            "card",
        )

        # Inner content placement
        ix = pad_outer + self.padding
        iy = pad_outer + self.padding
        iw = max(0, w - 2 * pad_outer - 2 * self.padding)
        ih = max(0, h - 2 * pad_outer - 2 * self.padding)

        self.canvas.coords(self._inner_window, ix, iy)
        self.canvas.itemconfigure(self._inner_window, width=iw, height=ih)


class RoundedButton(tk.Canvas):
    """
    A rounded button drawn on Canvas (true rounded corners).
    It calls `command` on click and supports a simple disabled state.

    Notes:
    - This is intentionally a Canvas widget so it looks the same on all platforms.
    - Use `configure_state("disabled")` or `configure_state("normal")`.
    """

    def __init__(
        self,
        master,
        text: str,
        command,
        bg: str,
        fg: str = "white",
        bg_hover: str | None = None,
        bg_disabled: str = "#475569",
        radius: int = 14,
        font=("Segoe UI", 10, "bold"),
        height: int = 40,
        cursor: str = "hand2",
        **kwargs,
    ):
        super().__init__(
            master,
            highlightthickness=0,
            bd=0,
            bg=master["bg"],
            height=height,
            cursor=cursor,
            **kwargs,
        )

        self._text = text
        self._command = command
        self._bg = bg
        self._bg_hover = bg_hover or bg
        self._bg_disabled = bg_disabled
        self._fg = fg
        self._radius = radius
        self._font = font
        self._state = "normal"

        self._is_hover = False

        self.bind("<Configure>", self._redraw)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

        self._redraw()

    def configure_state(self, state: str) -> None:
        if state not in ("normal", "disabled"):
            raise ValueError("state must be 'normal' or 'disabled'")
        self._state = state
        self._redraw()

    def _current_bg(self) -> str:
        if self._state == "disabled":
            return self._bg_disabled
        return self._bg_hover if self._is_hover else self._bg

    def _on_enter(self, _e) -> None:
        if self._state != "disabled":
            self._is_hover = True
            self._redraw()

    def _on_leave(self, _e) -> None:
        self._is_hover = False
        self._redraw()

    def _on_click(self, _e) -> None:
        if self._state == "disabled":
            return
        if callable(self._command):
            self._command()

    def _redraw(self, _evt=None) -> None:
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 2 or h <= 2:
            return

        self.delete("btn")

        pad = 2
        pts = _rounded_rect_points(pad, pad, w - pad, h - pad, self._radius)

        self.create_polygon(
            pts,
            smooth=True,
            splinesteps=12,
            fill=self._current_bg(),
            outline="",
            tags="btn",
        )

        self.create_text(
            w // 2,
            h // 2,
            text=self._text,
            fill=self._fg if self._state != "disabled" else "#e2e8f0",
            font=self._font,
            tags="btn",
        )
        
    def set_text(self, text: str) -> None:
        self._text = text
        self._redraw()
