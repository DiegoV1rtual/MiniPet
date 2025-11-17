"""
BalloonPop - Juego de reventar globos para MiniPet.

Globos de distintos colores flotan por la pantalla desde la parte
inferior hacia arriba. El jugador debe hacer clic únicamente en los
globos rojos, evitando los demás colores. Si revienta 20 globos rojos
sin haber tocado más de 3 globos incorrectos, gana. Si toca más de 3
globos incorrectos, pierde.

El fondo se puede personalizar mediante ``assets/custom/balloon_bg.png``.
"""

import tkinter as tk
import random
import os

try:
    # Import ImageEnhance to tweak brightness of chosen backgrounds.
    from PIL import Image, ImageTk, ImageEnhance  # type: ignore
    HAS_PIL = True
except Exception:
    HAS_PIL = False


class BalloonPop:
    """Minijuego de reventar globos rojos evitando otros colores."""

    def __init__(self, parent_window: tk.Tk, callback) -> None:
        self.callback = callback
        self.game_closed = False
        # Configuración
        self.target_reds = 20
        self.max_wrong = 3
        self.red_popped = 0
        self.wrong_popped = 0
        self.active_balloons = []
        self.game_running = False

        # Ventana
        self.window = tk.Toplevel()
        self.window.title("")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#1a1a1a")
        # Aumenta el tamaño de la ventana para un juego más exigente
        self.width, self.height = 800, 600
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
        # Selecciona aleatoriamente una imagen de 'fran' y oscurece ligeramente la imagen.
        if HAS_PIL:
            bg_dir = os.path.join("assets", "custom")
            try:
                fran_files = [f for f in os.listdir(bg_dir) if f.lower().startswith("fran") and f.lower().endswith(".png")]
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

        # Colores de globos (indicamos rojos y otros colores)
        self.colors = ["red", "blue", "green", "yellow", "purple", "orange"]

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
        self.widgets.append(self.canvas.create_text(
            cx, cy - 100,
            text="REVIENTA GLOBOS",
            font=("Arial", 28, "bold"),
            fill="white"
        ))
        inst_text = (
            "Haz clic solo en los globos ROJOS.\n"
            f"Debes reventar {self.target_reds} globos rojos sin fallar más de {self.max_wrong} veces."
        )
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text=inst_text,
            font=("Arial", 13),
            fill="yellow",
            justify="center"
        ))
        # Botón gris en lugar de verde
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 80, cx + 100, cy + 130,
            fill="#6e6e6e", outline="white", width=3
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
        self.red_popped = 0
        self.wrong_popped = 0
        self.active_balloons = []
        self.game_running = True
        self._clear_canvas()
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        # Empezar generación y movimiento
        self._spawn_balloon()
        self._update_balloons()

    def _spawn_balloon(self) -> None:
        if not self.game_running:
            return
        # Generar entre dos y tres globos cada vez para incrementar la dificultad
        for _ in range(random.randint(2, 3)):
            radius = random.randint(15, 25)
            x = random.randint(radius, self.width - radius)
            y = self.height + radius  # empieza fuera de la parte visible
            color = random.choice(self.colors)
            balloon_id = self.canvas.create_oval(
                x - radius, y - radius, x + radius, y + radius,
                fill=color, outline="white", width=2
            )
            self.canvas.tag_bind(balloon_id, "<Button-1>", lambda e, bid=balloon_id, col=color: self._on_balloon_click(bid, col))
            self.active_balloons.append({
                "id": balloon_id,
                "x": x,
                "y": y,
                "radius": radius,
                "color": color,
                # Mayor velocidad para que sea más difícil
                "speed": random.randint(4, 7)
            })
        # Programar siguiente aparición más frecuente
        self.window.after(600, self._spawn_balloon)

    def _on_balloon_click(self, balloon_id: int, color: str) -> None:
        if not self.game_running:
            return
        # Encontrar y eliminar el globo
        to_remove = None
        for b in self.active_balloons:
            if b["id"] == balloon_id:
                to_remove = b
                break
        if to_remove:
            # Evaluar color
            if to_remove["color"] == "red":
                self.red_popped += 1
            else:
                self.wrong_popped += 1
            try:
                self.canvas.delete(to_remove["id"])
            except Exception:
                pass
            self.active_balloons.remove(to_remove)
        # Comprobar condiciones
        if self.red_popped >= self.target_reds and self.wrong_popped <= self.max_wrong:
            self._game_over(True)
        elif self.wrong_popped > self.max_wrong:
            self._game_over(False)

    def _update_balloons(self) -> None:
        if not self.game_running:
            return
        to_remove = []
        for b in self.active_balloons:
            b["y"] -= b["speed"]
            self.canvas.move(b["id"], 0, -b["speed"])
            if b["y"] + b["radius"] < 0:
                to_remove.append(b)
        for b in to_remove:
            try:
                self.canvas.delete(b["id"])
            except Exception:
                pass
            if b in self.active_balloons:
                self.active_balloons.remove(b)
        # Actualizar texto de contador
        self.canvas.delete("score_text")
        self.canvas.create_text(
            10, 10,
            text=f"Rojos: {self.red_popped}/{self.target_reds}  Fallos: {self.wrong_popped}/{self.max_wrong}",
            anchor="nw",
            font=("Arial", 14, "bold"),
            fill="white",
            tag="score_text"
        )
        # Seguir actualizando
        self.window.after(30, self._update_balloons)

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
            cx, cy - 60,
            text=result_text,
            font=("Arial", 36, "bold"),
            fill=result_color
        ))
        msg = "¡Has reventado todos los globos rojos!" if won else "Has fallado demasiados globos"
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text=msg,
            font=("Arial", 16),
            fill="white"
        ))
        # Botón gris en pantalla final
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 60, cx + 100, cy + 110,
            fill="#6e6e6e", outline="white", width=3
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
        for b in self.active_balloons:
            try:
                self.canvas.delete(b["id"])
            except Exception:
                pass
        self.active_balloons.clear()
        try:
            self.canvas.delete("all")
        except Exception:
            pass
        self.widgets.clear()