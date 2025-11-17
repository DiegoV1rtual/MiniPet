"""
LightningDodge - Juego de esquivar rayos para MiniPet.

El jugador controla un personaje que se desplaza horizontalmente por la
parte inferior de la pantalla. Desde la parte superior caen rayos de
forma aleatoria. Si el jugador es alcanzado por un rayo, pierde. Si
consigue sobrevivir durante 20 segundos esquivando todos los rayos,
gana.

El juego muestra un temporizador de cuenta atrás y utiliza un fondo
personalizable almacenado en ``assets/custom/lightning_bg.png`` si está
disponible. Los rayos se representan como rectángulos verticales o, si
existe la imagen ``assets/custom/lightning.png``, como sprites.

"""

import tkinter as tk
import random
import time
import os

try:
    # Import ImageEnhance to allow dimming of randomly selected backgrounds.
    from PIL import Image, ImageTk, ImageEnhance  # type: ignore
    HAS_PIL = True
except Exception:
    HAS_PIL = False


class LightningDodge:
    """Minijuego para esquivar rayos durante un periodo de tiempo."""

    def __init__(self, parent_window: tk.Tk, callback) -> None:
        self.callback = callback
        self.game_closed = False
        # Configuración
        self.game_duration = 20  # segundos
        self.player_speed = 20
        self.bolt_spawn_interval = (500, 800)  # milisegundos
        self.bolt_speed_range = (5, 9)
        self.bolt_size = (20, 60)
        self.active_bolts = []  # cada elemento: {id, x, y, speed, width, height}
        self.game_running = False
        self.start_time = 0.0

        # Crear ventana flotante
        self.window = tk.Toplevel()
        self.window.title("")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#1a1a1a")

        # Dimensiones
        self.width, self.height = 600, 500
        self.canvas = tk.Canvas(self.window, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.window.update_idletasks()
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        x = (screen_w - self.width) // 2
        y = (screen_h - self.height) // 2
        self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")

        # Permitir arrastrar
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag)

        # Imagen de fondo
        self.bg_photo = None
        # Seleccionar aleatoriamente una imagen 'fran' y oscurecerla ligeramente.
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
                    # Convertir a RGBA para soportar GIFs (primer fotograma)
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

        # Sprite de rayo (opcional)
        self.bolt_photo = None
        bolt_path = os.path.join("assets", "custom", "lightning.png")
        if HAS_PIL and os.path.exists(bolt_path):
            try:
                bolt_img = Image.open(bolt_path)
                try:
                    bolt_img = bolt_img.convert("RGBA")
                except Exception:
                    pass
                bolt_img = bolt_img.resize((self.bolt_size[0], self.bolt_size[1]), Image.Resampling.LANCZOS)
                self.bolt_photo = ImageTk.PhotoImage(bolt_img)
            except Exception:
                self.bolt_photo = None

        # Jugador
        self.player_width = 80
        self.player_height = 30
        self.player_x = (self.width - self.player_width) // 2
        self.player_y = self.height - 60
        self.player_id = None

        # Configuración para movimiento continuo del jugador
        self.left_pressed = False
        self.right_pressed = False
        # Bindings de movimiento continuo: presionar y soltar
        self.window.bind("<KeyPress-Left>", lambda e: self._on_key_press(-1))
        self.window.bind("<KeyRelease-Left>", lambda e: self._on_key_release(-1))
        self.window.bind("<KeyPress-Right>", lambda e: self._on_key_press(1))
        self.window.bind("<KeyRelease-Right>", lambda e: self._on_key_release(1))

        # Elementos dibujados
        self.widgets = []

    def _on_key_press(self, direction: int) -> None:
        """Establece la dirección de movimiento continuo cuando se presiona una tecla."""
        if direction == -1:
            self.left_pressed = True
        elif direction == 1:
            self.right_pressed = True

    def _on_key_release(self, direction: int) -> None:
        """Detiene el movimiento continuo cuando se suelta la tecla."""
        if direction == -1:
            self.left_pressed = False
        elif direction == 1:
            self.right_pressed = False

    def _update_player_position(self) -> None:
        """Actualiza la posición del jugador de manera suave mientras se mantenga presionada la tecla."""
        if self.game_running:
            if self.left_pressed and not self.right_pressed:
                self._move_player(-self.player_speed)
            if self.right_pressed and not self.left_pressed:
                self._move_player(self.player_speed)
            self.window.after(30, self._update_player_position)

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
            text="EVITA LOS RAYOS",
            font=("Arial", 28, "bold"),
            fill="white"
        ))
        inst_text = (
            "Esquiva los rayos moviendo al personaje con las flechas izquierda/derecha.\n"
            "Puedes mantener presionada la flecha para moverte suavemente.\n"
            "Sobrevive 20 segundos para ganar."
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
        self.active_bolts = []
        self.start_time = time.time()
        self.game_running = True
        self._clear_canvas()
        # Dibujar fondo
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        # Dibujar jugador
        self._draw_player()
        # Iniciar timers
        self._update_game()
        self._spawn_bolt()
        # Iniciar actualización continua de la posición del jugador
        self._update_player_position()

    def _draw_player(self) -> None:
        if self.player_id is not None:
            try:
                self.canvas.delete(self.player_id)
            except Exception:
                pass
        self.player_id = self.canvas.create_rectangle(
            self.player_x, self.player_y,
            self.player_x + self.player_width, self.player_y + self.player_height,
            fill="#2196F3", outline="white", width=2
        )

    def _move_player(self, dx: int) -> None:
        if not self.game_running:
            return
        new_x = self.player_x + dx
        new_x = max(0, min(new_x, self.width - self.player_width))
        self.player_x = new_x
        self._draw_player()

    def _spawn_bolt(self) -> None:
        if not self.game_running:
            return
        # Crear un nuevo rayo
        w, h = self.bolt_size
        x = random.randint(0, self.width - w)
        y = -h  # Empieza fuera de la pantalla
        speed = random.randint(self.bolt_speed_range[0], self.bolt_speed_range[1])
        if self.bolt_photo:
            bolt_id = self.canvas.create_image(x, y, anchor="nw", image=self.bolt_photo)
            width = w
            height = h
        else:
            bolt_id = self.canvas.create_rectangle(
                x, y, x + w, y + h,
                fill="#FFEB3B", outline="white", width=2
            )
            width = w
            height = h
        self.active_bolts.append({
            "id": bolt_id,
            "x": x,
            "y": y,
            "speed": speed,
            "width": width,
            "height": height
        })
        # Programar siguiente aparición
        next_spawn = random.randint(self.bolt_spawn_interval[0], self.bolt_spawn_interval[1])
        self.window.after(next_spawn, self._spawn_bolt)

    def _update_game(self) -> None:
        if not self.game_running:
            return
        now = time.time()
        elapsed = now - self.start_time
        remaining = self.game_duration - elapsed
        # Actualizar temporizador en la pantalla (arriba a la izquierda)
        self.canvas.delete("timer_text")
        if remaining < 0:
            remaining = 0
        seconds = int(remaining)
        self.canvas.create_text(
            10, 10,
            text=f"Tiempo restante: {seconds:02d}s",
            anchor="nw",
            font=("Arial", 14, "bold"),
            fill="white",
            tag="timer_text"
        )
        # Mover rayos
        bolts_to_remove = []
        for bolt in self.active_bolts:
            bolt["y"] += bolt["speed"]
            self.canvas.move(bolt["id"], 0, bolt["speed"])
            # Colisión con jugador
            if (bolt["y"] + bolt["height"] >= self.player_y and
                bolt["y"] <= self.player_y + self.player_height and
                bolt["x"] + bolt["width"] >= self.player_x and
                bolt["x"] <= self.player_x + self.player_width):
                # Golpeado
                self._game_over(False)
                return
            # Salir de pantalla
            if bolt["y"] > self.height:
                bolts_to_remove.append(bolt)
        for bolt in bolts_to_remove:
            try:
                self.canvas.delete(bolt["id"])
            except Exception:
                pass
            if bolt in self.active_bolts:
                self.active_bolts.remove(bolt)
        # Comprobar victoria
        if remaining <= 0:
            self._game_over(True)
            return
        # Continuar bucle
        self.window.after(30, self._update_game)

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
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text="Has sobrevivido a la tormenta" if won else "Un rayo te alcanzó",
            font=("Arial", 16),
            fill="white"
        ))
        # Botón continuar
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
        for bolt in self.active_bolts:
            try:
                self.canvas.delete(bolt["id"])
            except Exception:
                pass
        self.active_bolts.clear()
        try:
            self.canvas.delete("all")
        except Exception:
            pass
        self.widgets.clear()