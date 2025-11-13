"""
DisarmBomb - Juego de repetir secuencias para MiniPet.

En este minijuego aparece una secuencia de botones (flechas y letras).
El jugador debe repetir la secuencia correctamente antes de que acabe
un temporizador invisible. La secuencia aumenta de longitud cada ronda
de 3 hasta 6 pasos. Si completa correctamente las tres secuencias sin
errores, gana; de lo contrario, pierde al primer fallo.

El juego utiliza un fondo personalizable localizado en
``assets/custom/bomb_bg.png`` y muestra las secuencias como símbolos.
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


class DisarmBomb:
    """Juego de memoria de secuencias de botones."""

    def __init__(self, parent_window: tk.Tk, callback) -> None:
        self.callback = callback
        self.game_closed = False
        # Configuración de rondas y secuencias
        self.sequence_lengths = [3, 4, 6]
        self.current_round = 0
        self.sequence = []
        self.user_input = []
        self.showing_sequence = False
        self.input_allowed = False

        # Ventana
        self.window = tk.Toplevel()
        self.window.title("")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#1a1a1a")
        self.width, self.height = 600, 500
        self.canvas = tk.Canvas(self.window, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.window.update_idletasks()
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        x = (screen_w - self.width) // 2
        y = (screen_h - self.height) // 2
        self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")

        # Drag
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag)

        # Fondo
        self.bg_photo = None
        # Usar una imagen de fondo genérica 'fondo5.png'.
        bg_path = os.path.join("assets", "custom", "fondo5.png")
        if HAS_PIL and os.path.exists(bg_path):
            try:
                img = Image.open(bg_path)
                img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(img)
            except Exception:
                self.bg_photo = None

        # Conjunto de botones posibles
        self.available_buttons = ["Up", "Down", "Left", "Right", "A", "B"]
        self.symbol_map = {
            "Up": "↑",
            "Down": "↓",
            "Left": "←",
            "Right": "→",
            "A": "A",
            "B": "B"
        }

        # Widgets
        self.widgets = []
        # Bind global key press
        self.window.bind("<Key>", self._on_key_press)

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
        self._clear_canvas()
        cx, cy = self.width // 2, self.height // 2
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        self.widgets.append(self.canvas.create_text(
            cx, cy - 100,
            text="DESACTIVA LA BOMBA",
            font=("Arial", 28, "bold"),
            fill="white"
        ))
        inst_text = (
            "Memoriza la secuencia de botones y repítela correctamente antes de que acabe el tiempo.\n"
            "Las combinaciones pueden incluir las flechas ↑ ↓ ← → y las letras A y B del teclado.\n"
            "La secuencia se alarga cada ronda; fallar una vez implica perder."
        )
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text=inst_text,
            font=("Arial", 13),
            fill="yellow",
            justify="center"
        ))
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
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._start_round())
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._start_round())

    def _start_round(self) -> None:
        self.current_round = 0
        self._next_round()

    def _next_round(self) -> None:
        if self.current_round >= len(self.sequence_lengths):
            self._game_over(True)
            return
        # Preparar nueva secuencia
        self.sequence = [random.choice(self.available_buttons) for _ in range(self.sequence_lengths[self.current_round])]
        self.user_input = []
        self.current_round += 1
        self.showing_sequence = True
        self.input_allowed = False
        self._display_sequence()

    def _display_sequence(self) -> None:
        self._clear_canvas()
        # Fondo
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        cx = self.width // 2
        # Mostrar ronda
        self.widgets.append(self.canvas.create_text(
            cx, 40,
            text=f"Ronda {self.current_round}/{len(self.sequence_lengths)}",
            font=("Arial", 16, "bold"),
            fill="white"
        ))
        # Mostrar secuencia como símbolos centrados
        symbols = [self.symbol_map[b] for b in self.sequence]
        seq_text = " ".join(symbols)
        self.widgets.append(self.canvas.create_text(
            cx, self.height // 2,
            text=seq_text,
            font=("Arial", 32, "bold"),
            fill="#FFEB3B"
        ))
        # Mostrar instrucciones para no interactuar
        self.widgets.append(self.canvas.create_text(
            cx, self.height - 60,
            text="Memoriza la secuencia...",
            font=("Arial", 14),
            fill="#CCCCCC"
        ))
        # Ocultar secuencia después de 2 segundos y permitir entrada
        self.window.after(2000, self._start_input_phase)

    def _start_input_phase(self) -> None:
        self.showing_sequence = False
        self.input_allowed = True
        # Limpiar secuencia de la pantalla y mostrar indicación
        self._clear_canvas()
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        cx = self.width // 2
        self.widgets.append(self.canvas.create_text(
            cx, 40,
            text=f"Ronda {self.current_round}/{len(self.sequence_lengths)}",
            font=("Arial", 16, "bold"),
            fill="white"
        ))
        self.widgets.append(self.canvas.create_text(
            cx, self.height // 2,
            text="Introduce la secuencia",
            font=("Arial", 20, "bold"),
            fill="#FFEB3B"
        ))
        # Reset user input
        self.user_input = []

    def _on_key_press(self, event: tk.Event) -> None:
        if not self.input_allowed:
            return
        key = event.keysym
        # Convert to our representation
        if key in ["Up", "Down", "Left", "Right"]:
            self.user_input.append(key)
        elif key.lower() == 'a':
            self.user_input.append("A")
        elif key.lower() == 'b':
            self.user_input.append("B")
        else:
            # Ignore other keys
            return
        # Mostrar progreso del usuario
        self._update_user_input_display()
        # Comprobar si ha finalizado la secuencia
        if len(self.user_input) == len(self.sequence):
            self.input_allowed = False
            # Verificar
            if self.user_input == self.sequence:
                # Correcto - pasar a siguiente ronda tras breve pausa
                self.window.after(500, self._next_round)
            else:
                # Fallo
                self.window.after(500, lambda: self._game_over(False))

    def _update_user_input_display(self) -> None:
        # Eliminar texto anterior de entrada
        self.canvas.delete("input_text")
        cx = self.width // 2
        # Convertir a símbolos
        symbols = [self.symbol_map[b] for b in self.user_input]
        seq_text = " ".join(symbols)
        self.canvas.create_text(
            cx, self.height // 2 + 40,
            text=seq_text,
            font=("Arial", 24, "bold"),
            fill="#00FF00",
            tag="input_text"
        )

    def _game_over(self, won: bool) -> None:
        self.input_allowed = False
        self.showing_sequence = False
        self._clear_canvas()
        cx, cy = self.width // 2, self.height // 2
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
        msg = "Has desactivado la bomba" if won else "La bomba explotó"
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text=msg,
            font=("Arial", 16),
            fill="white"
        ))
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
                self.window.destroy()
            except Exception:
                pass
            try:
                self.callback('won' if won else 'lost')
            except Exception:
                pass

    def _clear_canvas(self) -> None:
        try:
            self.canvas.delete("all")
        except Exception:
            pass
        self.widgets.clear()