"""
ExpressRace - Minijuego de carrera exprés para MiniPet.

El jugador debe pulsar repetidamente la barra espaciadora para hacer
avanzar su personaje a lo largo de una pista. Tiene 20 segundos para
llegar a la meta. Cada pulsación incrementa la posición del corredor;
si llega a la meta antes de que acabe el tiempo, gana; de lo contrario,
pierde.

Se utiliza un fondo personalizable en ``assets/custom/race_bg.png`` y
se muestra una barra de progreso en la parte inferior de la pantalla.
"""

import tkinter as tk
import time
import os
import random

try:
    # Import ImageEnhance to adjust background brightness.
    from PIL import Image, ImageTk, ImageEnhance  # type: ignore
    HAS_PIL = True
except Exception:
    HAS_PIL = False


class ExpressRace:
    """Minijuego donde se presiona espacio rápidamente para avanzar."""

    def __init__(self, parent_window: tk.Tk, callback) -> None:
        self.callback = callback
        self.game_closed = False
        # Configuración
        self.game_duration = 20  # segundos
        self.required_distance = 100  # unidades de barra
        self.progress = 0.0
        self.start_time = 0.0
        self.game_running = False

        # Ventana
        self.window = tk.Toplevel()
        self.window.title("")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#1a1a1a")
        self.width, self.height = 600, 400
        self.canvas = tk.Canvas(self.window, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.window.update_idletasks()
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        x = (screen_w - self.width) // 2
        y = (screen_h - self.height) // 2
        self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")
        # Arrastrar
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag)

        # Fondo
        self.bg_photo = None
        # Selecciona al azar una imagen 'fran' y oscurece ligeramente la imagen.
        if HAS_PIL:
            bg_dir = os.path.join("assets", "custom")
            try:
                fran_files = [f for f in os.listdir(bg_dir) if f.lower().startswith("fran") and f.lower().endswith((".png", ".gif"))]
            except Exception:
                fran_files = []
            if fran_files:
                chosen = random.choice(fran_files)
                image_path = os.path.join(bg_dir, chosen)
                try:
                    img = Image.open(image_path)
                    try:
                        img = img.convert("RGBA")
                    except Exception:
                        pass
                    img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(0.7)
                    self.bg_photo = ImageTk.PhotoImage(img)
                except Exception:
                    self.bg_photo = None

        # Barra de progreso (rectángulo)
        self.progress_bar_bg = None
        self.progress_bar_fg = None

        # Bind espacio
        self.window.bind("<space>", lambda e: self._on_space())

        # Widgets
        self.widgets = []

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
        # Título con fuente manuscrita para un toque más informal
        self.widgets.append(self.canvas.create_text(
            cx, cy - 80,
            text="CARRERA EXPRÉS",
            font=("Comic Sans MS", 28, "bold"),
            fill="white"
        ))
        inst_text = (
            "Pulsa repetidamente la barra espaciadora para avanzar.\n"
            "Tienes 20 segundos para llegar a la meta."
        )
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text=inst_text,
            font=("Comic Sans MS", 13),
            fill="yellow",
            justify="center"
        ))
        # Botón de inicio gris
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 70, cx + 100, cy + 120,
            fill="#6e6e6e", outline="white", width=3
        )
        self.widgets.append(btn_rect)
        btn_text = self.canvas.create_text(
            cx, cy + 95,
            text="COMENZAR",
            font=("Comic Sans MS", 16, "bold"),
            fill="white"
        )
        self.widgets.append(btn_text)
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._start_game())
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._start_game())

    def _start_game(self) -> None:
        self.progress = 0.0
        self.start_time = time.time()
        self.game_running = True
        self._clear_canvas()
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        # Dibujar barra de progreso de fondo
        bar_y = self.height - 70
        bar_height = 30
        self.progress_bar_bg = self.canvas.create_rectangle(
            100, bar_y, 500, bar_y + bar_height,
            fill="#555555", outline="white", width=2
        )
        self.progress_bar_fg = self.canvas.create_rectangle(
            100, bar_y, 100, bar_y + bar_height,
            fill="#00BCD4", outline="white", width=2
        )
        # Iniciar actualización de temporizador y progreso
        self._update_game()

    def _on_space(self) -> None:
        if not self.game_running:
            return
        # Cada pulsación avanza una cantidad
        self.progress += 2.0
        if self.progress > self.required_distance:
            self.progress = self.required_distance
        self._update_progress_bar()
        # Revisar victoria inmediata
        if self.progress >= self.required_distance:
            self._game_over(True)

    def _update_progress_bar(self) -> None:
        # Actualizar longitud de barra
        bar_start_x = 100
        bar_end_x = 500
        total_len = bar_end_x - bar_start_x
        current_len = (self.progress / self.required_distance) * total_len
        self.canvas.coords(self.progress_bar_fg, bar_start_x, self.height - 70, bar_start_x + current_len, self.height - 40)

    def _update_game(self) -> None:
        if not self.game_running:
            return
        elapsed = time.time() - self.start_time
        remaining = self.game_duration - elapsed
        # Actualizar temporizador
        self.canvas.delete("timer_text")
        if remaining < 0:
            remaining = 0
        seconds = int(remaining)
        self.canvas.create_text(
            10, 10,
            text=f"Tiempo: {seconds:02d}s",
            anchor="nw",
            font=("Comic Sans MS", 16, "bold"),
            fill="white",
            tag="timer_text"
        )
        # Comprobar fin del tiempo
        if remaining <= 0:
            # Verificar si llegó a meta
            self._game_over(self.progress >= self.required_distance)
            return
        # Continuar actualizando
        self.window.after(100, self._update_game)

    def _game_over(self, won: bool) -> None:
        self.game_running = False
        self._clear_canvas()
        cx, cy = self.width // 2, self.height // 2
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        result_text = "VICTORIA" if won else "Derrota"
        result_color = "#4CAF50" if won else "#f44336"
        self.widgets.append(self.canvas.create_text(
            cx, cy - 50,
            text=result_text,
            font=("Comic Sans MS", 36, "bold"),
            fill=result_color
        ))
        msg = "¡Has llegado a la meta!" if won else "No has llegado a tiempo"
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text=msg,
            font=("Comic Sans MS", 16),
            fill="white"
        ))
        # Botón de continuar gris
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 50, cx + 100, cy + 100,
            fill="#6e6e6e", outline="white", width=3
        )
        self.widgets.append(btn_rect)
        btn_text = self.canvas.create_text(
            cx, cy + 75,
            text="CONTINUAR",
            font=("Comic Sans MS", 16, "bold"),
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