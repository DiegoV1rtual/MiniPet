"""
AsteroidsGame - minijuego de esquivar asteroides para MiniPet.

El jugador controla una pequeña nave situada en la parte inferior de
la pantalla. Con las teclas de flecha izquierda y derecha debe mover
la nave para evitar ser golpeado por asteroides que caen desde la parte
superior. Los asteroides aparecen con tamaños y velocidades aleatorias.
Si un asteroide toca la nave, pierdes. Si sobrevives hasta que se
agote el tiempo de juego, ganas.

Se elige un fondo "fran" de forma aleatoria y se oscurece para que
resalten los elementos. Los textos de instrucciones usan Comic Sans
para tener apariencia manuscrita. Los botones son grises.
"""

import tkinter as tk
import random
import time
import os

try:
    from PIL import Image, ImageTk, ImageEnhance  # type: ignore
    HAS_PIL = True
except Exception:
    HAS_PIL = False


class AsteroidsGame:
    """Minijuego de esquivar asteroides."""

    def __init__(self, parent_window: tk.Tk, callback) -> None:
        self.callback = callback
        self.game_closed = False
        # Dimensiones de la ventana
        self.width = 600
        self.height = 500
        # Configuración temporal
        self.game_duration = 25  # duración del juego en segundos
        self.start_time = 0.0
        self.game_running = False
        # Nave
        self.player_width = 40
        self.player_height = 15
        self.player_x = self.width // 2
        self.player_y = self.height - 50
        # Asteroides
        self.asteroids = []  # cada elemento: dict con x,y,size,speed
        self.spawn_interval = 800  # ms
        # Ventana y canvas
        self.window = tk.Toplevel()
        self.window.title("")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#1a1a1a")
        self.canvas = tk.Canvas(self.window, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.window.update_idletasks()
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        x = (screen_w - self.width) // 2
        y = (screen_h - self.height) // 2
        self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")
        # Arrastre
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag)
        # Fondo
        self.bg_photo = None
        if HAS_PIL:
            bg_dir = os.path.join("assets", "custom")
            try:
                fran_files = [f for f in os.listdir(bg_dir)
                              if f.lower().startswith("fran") and f.lower().endswith((".png", ".gif"))]
            except Exception:
                fran_files = []
            if fran_files:
                chosen = random.choice(fran_files)
                path = os.path.join(bg_dir, chosen)
                try:
                    img = Image.open(path)
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
        # Widgets
        self.widgets = []
        # Controles
        self.window.bind("<Left>", lambda e: self._move_player(-20))
        self.window.bind("<Right>", lambda e: self._move_player(20))

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
            cx, cy - 120,
            text="EVITA LOS ASTEROIDES",
            font=("Comic Sans MS", 28, "bold"),
            fill="white"
        ))
        inst_text = (
            "Mueve la nave con ← y → para esquivar los asteroides.\n"
            "Sobrevive hasta que termine el tiempo para ganar."
        )
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text=inst_text,
            font=("Comic Sans MS", 13),
            fill="yellow",
            justify="center"
        ))
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 80, cx + 100, cy + 130,
            fill="#6e6e6e", outline="white", width=3
        )
        self.widgets.append(btn_rect)
        btn_text = self.canvas.create_text(
            cx, cy + 105,
            text="COMENZAR",
            font=("Comic Sans MS", 16, "bold"),
            fill="white"
        )
        self.widgets.append(btn_text)
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._start_game())
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._start_game())

    def _start_game(self) -> None:
        self._clear_canvas()
        self.game_running = True
        self.start_time = time.time()
        self.asteroids.clear()
        self._draw_scene()
        # Iniciar bucles de spawn y juego
        self._spawn_asteroid()
        self._game_loop()

    def _move_player(self, dx: int) -> None:
        if not self.game_running:
            return
        new_x = self.player_x + dx
        half = self.player_width // 2
        if new_x - half < 0:
            new_x = half
        if new_x + half > self.width:
            new_x = self.width - half
        self.player_x = new_x
        self._draw_scene()

    def _spawn_asteroid(self) -> None:
        if not self.game_running:
            return
        size = random.randint(20, 40)
        x = random.randint(0, self.width - size)
        speed = random.randint(3, 6)
        self.asteroids.append({"x": x, "y": -size, "size": size, "speed": speed})
        # Programar siguiente spawn
        self.window.after(self.spawn_interval, self._spawn_asteroid)

    def _update_asteroids(self) -> None:
        new_asteroids = []
        for asteroid in self.asteroids:
            asteroid["y"] += asteroid["speed"]
            # Verificar colisión con nave
            if self._check_collision(asteroid):
                self._game_over(False)
                return
            # Eliminar asteroides que salen de la pantalla
            if asteroid["y"] > self.height:
                continue
            new_asteroids.append(asteroid)
        self.asteroids = new_asteroids

    def _check_collision(self, asteroid) -> bool:
        ax = asteroid["x"]
        ay = asteroid["y"]
        size = asteroid["size"]
        # Nave representada como triángulo y rectángulo en draw_scene; aproximamos con rectángulo alrededor
        px_left = self.player_x - self.player_width // 2
        px_right = self.player_x + self.player_width // 2
        py_top = self.player_y - self.player_height
        py_bottom = self.player_y
        # Verificar intersección simple rect-rect
        if (ax + size > px_left and ax < px_right and
            ay + size > py_top and ay < py_bottom):
            return True
        return False

    def _game_loop(self) -> None:
        if not self.game_running or self.game_closed:
            return
        # Actualizar posiciones de asteroides
        self._update_asteroids()
        # Verificar tiempo
        elapsed = time.time() - self.start_time
        if elapsed >= self.game_duration:
            # Ganar si sobrevives todo el tiempo
            self._game_over(True)
            return
        # Dibujar escena
        self._draw_scene()
        # Programar siguiente actualización
        self.window.after(50, self._game_loop)

    def _draw_scene(self) -> None:
        self._clear_canvas()
        # Fondo
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        # Dibujar asteroides
        for ast in self.asteroids:
            oval = self.canvas.create_oval(
                ast["x"], ast["y"], ast["x"] + ast["size"], ast["y"] + ast["size"],
                fill="#795548", outline="white", width=1
            )
            self.widgets.append(oval)
        # Dibujar nave (triángulo)
        px = self.player_x
        py = self.player_y
        half = self.player_width // 2
        tri = self.canvas.create_polygon(
            px, py - self.player_height,
            px - half, py,
            px + half, py,
            fill="#2196F3", outline="white", width=2
        )
        self.widgets.append(tri)
        # Tiempo restante
        remaining = int(self.game_duration - (time.time() - self.start_time)) if self.game_running else 0
        self.widgets.append(self.canvas.create_text(
            10, 10,
            anchor="nw",
            text=f"Tiempo: {remaining:02d}s",
            font=("Comic Sans MS", 12, "bold"),
            fill="white"
        ))

    def _game_over(self, won: bool) -> None:
        if not self.game_running:
            return
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
            font=("Comic Sans MS", 36, "bold"),
            fill=result_color
        ))
        msg = "¡Has sobrevivido al campo de asteroides!" if won else "Un asteroide ha impactado contigo"
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text=msg,
            font=("Comic Sans MS", 16),
            fill="white"
        ))
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 60, cx + 100, cy + 110,
            fill="#6e6e6e", outline="white", width=3
        )
        self.widgets.append(btn_rect)
        btn_text = self.canvas.create_text(
            cx, cy + 85,
            text="CONTINUAR",
            font=("Comic Sans MS", 16, "bold"),
            fill="white"
        )
        self.widgets.append(btn_text)
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._close(won))
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._close(won))

    def _close(self, won: bool) -> None:
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