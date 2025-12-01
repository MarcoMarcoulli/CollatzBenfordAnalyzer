import tkinter as tk
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from Math import collatz_orbit
from Plot import create_figure, add_orbit, reset_ax, update_histogram


class CollatzGui:
    def __init__(self, root):
        self.root = root
        self.root.title("Collatz Visualizer")
        self.root.geometry("1000x750")
        self.root.configure(bg="#f0f2f5")

        # Dati cumulativi delle orbite
        self.all_orbits = []

        # Oggetti matplotlib
        self.fig = None
        self.ax = None
        self.ax_hist = None
        self.canvas = None
        self.toolbar = None

        # Stato evoluzione automatica
        self.is_evolving = False
        self.current_n = 1
        self.max_n = 0

        self.build_ui()

    # ------------------------ GUI ------------------------

    def build_ui(self):

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TButton",
            font=("Segoe UI", 12),
            padding=6,
            background="#1e88e5",
            foreground="white",
            borderwidth=0,
            focusthickness=3,
            focuscolor="none"
        )

        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 12, "bold"),
            padding=6,
            foreground="white",
            background="#43a047",
        )
        style.map("Accent.TButton", background=[("active", "#2e7d32")])

        style.configure(
            "Stop.TButton",
            font=("Segoe UI", 12, "bold"),
            padding=6,
            foreground="white",
            background="#e53935",
        )
        style.map("Stop.TButton", background=[("active", "#b71c1c")])



        title = tk.Label(
            self.root,
            text="COLLATZ ORBITS VISUALIZER",
            font=("Segoe UI", 20, "bold"),
            bg="#f0f2f5",
            fg="#003366"
        )
        title.pack(pady=(5, 5))

        # Frame superiore: input singola orbita
        frame_top = tk.Frame(self.root, bg="#f0f2f5")
        frame_top.pack(pady=(0, 5))

        lbl = tk.Label(frame_top, text="Number:", bg="#f0f2f5",
                       font=("Segoe UI", 12))
        lbl.pack(side=tk.LEFT, padx=10)

        self.entry = ttk.Entry(frame_top, width=12, font=("Segoe UI", 12))
        self.entry.pack(side=tk.LEFT, padx=5)

        self.btn_add = ttk.Button(frame_top, text="Add orbit", style="Accent.TButton", command=self.add_orbit)

        self.btn_add.pack(side=tk.LEFT, padx=8)

        self.btn_reset = ttk.Button(
            frame_top,
            text="Reset",
            style="Accent.TButton",
            command=self.reset
        )
        self.btn_reset.pack(side=tk.LEFT, padx=8)

        # Frame secondario: evoluzione automatica da 1 a N
        frame_evo = tk.Frame(self.root, bg="#f0f2f5")
        frame_evo.pack(pady=(0, 5))

        lbl_max = tk.Label(
            frame_evo,
            text="Max N:",
            bg="#f0f2f5",
            font=("Segoe UI", 12)
        )
        lbl_max.pack(side=tk.LEFT, padx=10)

        self.entry_max_n = ttk.Entry(frame_evo, width=12, font=("Segoe UI", 12))
        self.entry_max_n.pack(side=tk.LEFT, padx=5)

        self.btn_start = ttk.Button(
            frame_evo,
            text="Start evolution",
            style="Accent.TButton",
            command=self.start_evolution
        )
        self.btn_start.pack(side=tk.LEFT, padx=8)

        self.btn_stop = ttk.Button(
            frame_evo,
            text="Stop",
            style="Stop.TButton",
            command=self.stop_evolution,
            state="disabled"
        )
        self.btn_stop.pack(side=tk.LEFT, padx=8)

    # ----------------------- ORBITA SINGOLA -----------------------

    def add_orbit(self):
        """Aggiunge una singola orbita, come prima."""
        raw = self.entry.get()
        try:
            n = int(raw)
            if n <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Insert a positive integer")
            return

        self.entry.delete(0, tk.END)

        orbit = collatz_orbit(n)
        steps = list(range(len(orbit)))
        self.all_orbits.append(orbit)

        if self.fig is None:
            self.fig, self.ax, self.ax_hist = create_figure()
            self.create_canvas()

        show = (len(self.all_orbits) <= 2 and len(orbit) <= 20)
        add_orbit(self.ax, steps, orbit, n, show_labels=show, show_legend=True)

        # Se abbiamo superato 2 orbite → cancella tutte le etichette
        if len(self.all_orbits) > 2:
            from Plot import clear_all_labels
            clear_all_labels()
            self.canvas.draw()

        update_histogram(self.ax_hist, self.all_orbits)

        self.canvas.draw()

    # ------------------------ EVOLUZIONE AUTOMATICA ------------------------

    def start_evolution(self):
        """Avvia l'evoluzione cumulativa da 1 a MaxN."""
        if self.is_evolving:
            return

        raw = self.entry_max_n.get()
        try:
            max_n = int(raw)
            if max_n <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Insert a positive integer for Max N")
            return

        self.max_n = max_n
        self.current_n = 1
        self.is_evolving = True

        # Se non c'è ancora il grafico, crealo
        if self.fig is None:
            self.fig, self.ax, self.ax_hist = create_figure()
            self.create_canvas()

        # Reset dati e assi per partire "pulito"
        self.all_orbits.clear()
        reset_ax(self.ax)
        update_histogram(self.ax_hist, self.all_orbits)
        self.canvas.draw()

        # Disabilita interazione manuale, abilita Stop
        self.btn_add.config(state="disabled")
        self.btn_reset.config(state="disabled")
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")

        # Avvia il primo passo
        self.evolve_step()

    def evolve_step(self):
        """Esegue un passo dell'evoluzione: aggiunge l'orbita di current_n."""
        if not self.is_evolving:
            return

        if self.current_n > self.max_n:
            # Evoluzione terminata
            self.is_evolving = False
            self.btn_add.config(state="normal")
            self.btn_reset.config(state="normal")
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")
            return

        # Calcola orbita di current_n
        orbit = collatz_orbit(self.current_n)
        steps = list(range(len(orbit)))
        self.all_orbits.append(orbit)

        # Aggiungi orbita al grafico superiore
        add_orbit(self.ax, steps, orbit, self.current_n, show_labels=False, show_legend=False)

        # Aggiorna istogramma cumulativo
        update_histogram(self.ax_hist, self.all_orbits)

        # Ridisegna
        if self.canvas is not None:
            self.canvas.draw()

        # Prossimo n
        self.current_n += 1

        # Pianifica il prossimo passo tra 1000 ms (1 secondo)
        self.root.after(300, self.evolve_step)

    def stop_evolution(self):
        """Ferma l'evoluzione automatica."""
        if not self.is_evolving:
            return

        self.is_evolving = False

        # Riabilita pulsanti manuali
        self.btn_add.config(state="normal")
        self.btn_reset.config(state="normal")
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")

    # ------------------------ CANVAS ------------------------

    def create_canvas(self):
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(
            fill=tk.BOTH, expand=True, padx=15, pady=(5, 2)
        )

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        self.toolbar.update()

    # ------------------------- RESET -------------------------

    def reset(self):
        """Reset manuale: cancella grafici e dati."""
        # Ferma eventuale evoluzione
        self.is_evolving = False

        self.all_orbits.clear()

        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None

        if self.toolbar is not None:
            self.toolbar.destroy()
            self.toolbar = None

        self.fig = None
        self.ax = None
        self.ax_hist = None

        # Ripristina stato pulsanti
        self.btn_add.config(state="normal")
        self.btn_reset.config(state="normal")
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
