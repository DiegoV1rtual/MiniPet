"""
TypingGame - A typing speed and accuracy game for MiniPet.

In this game the player is presented with a sequence of words and must
type each one correctly within a time limit. The game measures how many
words are typed correctly and awards a win if the player achieves at
least the configured number of successes. It offers instructions up
front and displays a summary when finished.

This minigame is designed to be straightforward and encourages quick
typing. A collection of words is embedded in the class but can be
extended or replaced as desired. If Pillow is installed and a suitable
background image exists in ``assets/minigames/typing_bg.png`` it will
display that image behind the content.
"""

import tkinter as tk
import random
import time
import os

try:
    from PIL import Image, ImageTk  # type: ignore
    HAS_PIL = True
except Exception:
    HAS_PIL = False


class TypingGame:
    """A simple typing game where the user must correctly type displayed words."""

    def __init__(self, parent_window: tk.Tk, callback) -> None:
        self.callback = callback
        self.game_closed = False
        # Configuration
        self.words = [
            "python", "mascota", "teclado", "pantalla", "comida",
            "felicidad", "higiene", "dormir", "hambriento", "juego",
            "ventana", "programacion", "minijuego", "sorpresa", "rapido"
        ]
        self.num_rounds = 5
        self.required_successes = 4
        self.current_round = 0
        self.successes = 0
        self.current_word = ""
        self.timeout_id = None

        # Create toplevel window
        self.window = tk.Toplevel()
        self.window.title("")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#1a1a1a")

        # Determine screen centre for initial placement
        w, h = 600, 500
        self.canvas = tk.Canvas(self.window, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.window.update_idletasks()
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        self.window.geometry(f"{w}x{h}+{x}+{y}")

        # Enable dragging
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag)

        # Attempt to load a background image
        self.bg_photo = None
        # Usar una imagen de fondo genérica 'fondo2.png'.
        bg_path = os.path.join("assets", "custom", "fondo2.png")
        if HAS_PIL and os.path.exists(bg_path):
            try:
                img = Image.open(bg_path)
                img = img.resize((w, h), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(img)
            except Exception:
                self.bg_photo = None

        # Tracking drawn items
        self.widgets = []
        self.entry_widget = None

    def _start_drag(self, event: tk.Event) -> None:
        self._drag_data = {"x": event.x, "y": event.y}

    def _drag(self, event: tk.Event) -> None:
        if hasattr(self, "_drag_data"):
            x = self.window.winfo_x() + event.x - self._drag_data["x"]
            y = self.window.winfo_y() + event.y - self._drag_data["y"]
            self.window.geometry(f"+{x}+{y}")

    def run(self) -> None:
        self.window.after(100, self._show_instructions)

    def _show_instructions(self) -> None:
        self._clear_widgets()
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        # Background
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        self.widgets.append(self.canvas.create_text(
            cx, cy - 100,
            text="JUEGO DE MECANOGRAFIA",
            font=("Arial", 28, "bold"),
            fill="white"
        ))
        inst_text = (
            "Escribe las palabras que aparecen en la pantalla.\n"
            f"Debes acertar al menos {self.required_successes} de {self.num_rounds} palabras para ganar."
        )
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text=inst_text,
            font=("Arial", 13),
            fill="yellow",
            justify="center"
        ))
        # Start button
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 80, cx + 100, cy + 130,
            fill="#4CAF50", outline="white", width=3
        )
        self.widgets.append(btn_rect)
        btn_text = self.canvas.create_text(
            cx, cy + 105,
            text="COMENZAR",
            font=("Arial", 16, "bold"),
            fill="white"
        )
        self.widgets.append(btn_text)
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._start_game())
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._start_game())

    def _start_game(self) -> None:
        self.current_round = 0
        self.successes = 0
        # Randomize order
        random.shuffle(self.words)
        self._next_round()

    def _on_keypress_check(self, entry: tk.Entry) -> None:
        """Comprueba en cada pulsación si el texto coincide con el prefijo de la palabra.
        Si el usuario escribe una letra incorrecta en cualquier momento,
        se declara pérdida inmediata del minijuego."""
        typed = entry.get().strip().lower()
        if not self.current_word.lower().startswith(typed):
            # Cancelar cualquier timeout pendiente
            if self.timeout_id is not None:
                try:
                    self.window.after_cancel(self.timeout_id)
                except Exception:
                    pass
                self.timeout_id = None
            # Mostrar derrota inmediata
            self._clear_widgets()
            w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
            cx, cy = w // 2, h // 2
            if self.bg_photo:
                bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
                self.widgets.append(bg_id)
            self.widgets.append(self.canvas.create_text(
                cx, cy - 60,
                text="Derrota",
                font=("Arial", 36, "bold"),
                fill="#f44336"
            ))
            self.widgets.append(self.canvas.create_text(
                cx, cy,
                text="Has escrito una letra incorrecta",
                font=("Arial", 16),
                fill="white"
            ))
            # Llamar callback tras una breve pausa y cerrar ventana
            def finish_fail() -> None:
                try:
                    self.window.destroy()
                except Exception:
                    pass
                if callable(self.callback):
                    try:
                        self.callback('lost')
                    except Exception:
                        pass
            self.window.after(1500, finish_fail)

    def _next_round(self) -> None:
        if self.current_round >= self.num_rounds:
            self._game_over()
            return
        self.current_round += 1
        self.current_word = self.words[self.current_round - 1]
        self.clicked = False
        self._clear_widgets()
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx = w // 2
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        self.widgets.append(self.canvas.create_text(
            cx, 40,
            text=f"Palabra {self.current_round}/{self.num_rounds}  -  Aciertos: {self.successes}",
            font=("Arial", 16, "bold"),
            fill="white"
        ))
        # Show the target word
        self.widgets.append(self.canvas.create_text(
            cx, h // 2 - 50,
            text=self.current_word.upper(),
            font=("Arial", 32, "bold"),
            fill="#FFEB3B"
        ))
        # Create entry widget
        entry = tk.Entry(self.window, font=("Arial", 18))
        entry.place(relx=0.5, rely=0.6, anchor="center", width=250)
        entry.focus_set()
        # Comprobar entrada al pulsar Enter
        entry.bind("<Return>", lambda e: self._check_input(entry))
        # Verificar cada pulsación de tecla para detectar errores inmediatamente
        entry.bind("<KeyRelease>", lambda e: self._on_keypress_check(entry))
        self.entry_widget = entry
        # Timeout for this word (6 seconds)
        # Cancel any previous timeout
        if self.timeout_id is not None:
            try:
                self.window.after_cancel(self.timeout_id)
            except Exception:
                pass
        self.timeout_id = self.window.after(6000, lambda: self._on_timeout(entry))

    def _check_input(self, entry: tk.Entry) -> None:
        # Prevent multiple submissions
        if self.timeout_id:
            try:
                self.window.after_cancel(self.timeout_id)
            except Exception:
                pass
            self.timeout_id = None
        user_input = entry.get().strip().lower()
        if user_input == self.current_word.lower():
            self.successes += 1
        self._proceed_after_input()

    def _on_timeout(self, entry: tk.Entry) -> None:
        # Called when the user fails to type within the time limit
        self.timeout_id = None
        self._proceed_after_input()

    def _proceed_after_input(self) -> None:
        # Remove entry widget
        if self.entry_widget:
            try:
                self.entry_widget.destroy()
            except Exception:
                pass
            self.entry_widget = None
        # Delay before next word
        self.window.after(300, self._next_round)

    def _game_over(self) -> None:
        # Cancel any pending timeout
        if self.timeout_id is not None:
            try:
                self.window.after_cancel(self.timeout_id)
            except Exception:
                pass
            self.timeout_id = None
        won = self.successes >= self.required_successes
        self._clear_widgets()
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        result_text = "VICTORIA" if won else "Derrota"
        result_color = "#4CAF50" if won else "#f44336"
        self.widgets.append(self.canvas.create_text(
            cx, cy - 60,
            text=result_text,
            font=("Arial", 36, "bold"),
            fill=result_color
        ))
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text=f"Aciertos: {self.successes}/{self.num_rounds}",
            font=("Arial", 16),
            fill="white"
        ))
        # Continue button
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 60, cx + 100, cy + 110,
            fill="#2196F3", outline="white", width=3
        )
        self.widgets.append(btn_rect)
        btn_text = self.canvas.create_text(
            cx, cy + 85,
            text="CONTINUAR",
            font=("Arial", 16, "bold"),
            fill="white"
        )
        self.widgets.append(btn_text)
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._close_result(won))
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._close_result(won))

    def _close_result(self, won: bool) -> None:
        if not self.game_closed:
            self.game_closed = True
            try:
                if self.entry_widget:
                    self.entry_widget.destroy()
            except Exception:
                pass
            try:
                self.window.destroy()
            except Exception:
                pass
            try:
                self.callback('won' if won else 'lost')
            except Exception:
                pass

    def _clear_widgets(self) -> None:
        for wid in self.widgets:
            try:
                self.canvas.delete(wid)
            except Exception:
                pass
        self.widgets.clear()