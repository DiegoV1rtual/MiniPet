"""
CatchGame - A simple object catching game for MiniPet.

In this minigame the player controls a paddle at the bottom of the screen
and must catch falling objects by moving left and right with the arrow
keys. Each object caught awards a point while each object missed
subtracts from the available lives. After a fixed number of objects
spawned the game ends and the player wins if enough objects were caught.

The UI uses a canvas where objects (represented as circles) fall from
the top. The paddle is a rectangle that the user can move. If Pillow
and a background image are available the game displays that image under
the gameplay elements.
"""

import tkinter as tk
import random
import os

try:
    # Import ImageEnhance to adjust brightness of the background.
    from PIL import Image, ImageTk, ImageEnhance  # type: ignore
    HAS_PIL = True
except Exception:
    HAS_PIL = False


class CatchGame:
    """A catching game where the player moves a paddle to catch falling objects."""

    def __init__(self, parent_window: tk.Tk, callback) -> None:
        self.callback = callback
        self.game_closed = False
        # Configuration
        self.total_objects = 15
        self.required_catches = 8
        self.caught = 0
        self.missed = 0
        self.objects = []  # list of dicts with id and other data
        self.game_running = False

        # Create toplevel window
        self.window = tk.Toplevel()
        self.window.title("")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#1a1a1a")

        # Determine size and center position
        self.width, self.height = 600, 500
        self.canvas = tk.Canvas(self.window, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.window.update_idletasks()
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        x = (screen_w - self.width) // 2
        y = (screen_h - self.height) // 2
        self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")

        # Enable dragging
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag)

        # Background image: pick a random 'fran' image and darken it slightly to reduce contrast.
        self.bg_photo = None
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

        # Paddle
        self.paddle_width = 120
        self.paddle_height = 20
        self.paddle_x = (self.width - self.paddle_width) // 2
        self.paddle_y = self.height - 60
        self.paddle_id = None

        # Movimiento continuo: registrar teclas presionadas
        self.left_pressed = False
        self.right_pressed = False
        # Bindings para presionar y soltar flechas
        self.window.bind("<KeyPress-Left>", lambda e: self._on_key_press(-1))
        self.window.bind("<KeyRelease-Left>", lambda e: self._on_key_release(-1))
        self.window.bind("<KeyPress-Right>", lambda e: self._on_key_press(1))
        self.window.bind("<KeyRelease-Right>", lambda e: self._on_key_release(1))

        # Tracking items drawn
        self.widgets = []
        self.spawned_objects = 0

        # Configuración para movimiento continuo del paddle
        self.move_speed = 10

    def _on_key_press(self, direction: int) -> None:
        """Marcamos las teclas presionadas para mover continuamente la barra."""
        if direction == -1:
            self.left_pressed = True
        elif direction == 1:
            self.right_pressed = True

    def _on_key_release(self, direction: int) -> None:
        """Al soltar la tecla dejamos de mover en esa dirección."""
        if direction == -1:
            self.left_pressed = False
        elif direction == 1:
            self.right_pressed = False

    def _update_paddle_position(self) -> None:
        """Actualiza la posición del paddle de forma suave mientras se mantengan las teclas."""
        if self.game_running:
            if self.left_pressed and not self.right_pressed:
                self._move_paddle(-self.move_speed)
            if self.right_pressed and not self.left_pressed:
                self._move_paddle(self.move_speed)
            # Llamar de nuevo después de un pequeño intervalo
            self.window.after(30, self._update_paddle_position)

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
        # Draw background
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        self.widgets.append(self.canvas.create_text(
            cx, cy - 100,
            text="ATRAPA LOS OBJETOS",
            font=("Arial", 28, "bold"),
            fill="white"
        ))
        inst_text = (
            "Mueve la barra con las flechas izquierda y derecha.\n"
            "Mantén presionada la flecha para moverte de forma continua.\n"
            f"Debes atrapar al menos {self.required_catches} de {self.total_objects} objetos para ganar."
        )
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text=inst_text,
            font=("Arial", 13),
            fill="yellow",
            justify="center"
        ))
        # Botón gris para iniciar
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
        self.caught = 0
        self.missed = 0
        self.spawned_objects = 0
        self.game_running = True
        # Clear canvas
        self._clear_canvas()
        # Draw background if available
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        # Draw paddle
        self._draw_paddle()
        # Start spawning objects
        self.window.after(500, self._spawn_object)
        # Start moving objects
        self._update_objects()
        # Iniciar movimiento continuo del paddle
        self._update_paddle_position()

    def _draw_paddle(self) -> None:
        # Remove existing paddle
        if self.paddle_id is not None:
            try:
                self.canvas.delete(self.paddle_id)
            except Exception:
                pass
        self.paddle_id = self.canvas.create_rectangle(
            self.paddle_x, self.paddle_y,
            self.paddle_x + self.paddle_width, self.paddle_y + self.paddle_height,
            fill="#2196F3", outline="white", width=2
        )

    def _move_paddle(self, dx: int) -> None:
        # Move paddle within bounds
        new_x = self.paddle_x + dx
        new_x = max(0, min(new_x, self.width - self.paddle_width))
        self.paddle_x = new_x
        self._draw_paddle()

    def _spawn_object(self) -> None:
        if not self.game_running or self.spawned_objects >= self.total_objects:
            return
        # Los objetos siempre son buenos.  Se eliminan por completo las
        # "calaveras" o elementos negativos para evitar problemas de
        # renderizado y confusión.  Todos los objetos otorgarán puntos al
        # atraparlos y nunca terminarán la partida de forma inmediata al ser
        # capturados.
        is_bad = False
        radius = 15
        x = random.randint(radius, self.width - radius)
        y = 0 - radius  # inicia fuera de la pantalla
        # Dibujar objeto bueno (círculo amarillo)
        obj_id = self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill="#FFEB3B", outline="white", width=2
        )
        self.objects.append({
            "id": obj_id,
            "x": x,
            "y": y,
            "radius": radius,
            "is_bad": is_bad
        })
        self.spawned_objects += 1
        # Spawn next object after random interval between 600-1000ms
        self.window.after(random.randint(600, 1000), self._spawn_object)

    def _update_objects(self) -> None:
        if not self.game_running:
            return
        objects_to_remove = []
        for obj in self.objects:
            # Mover objeto hacia abajo
            obj["y"] += 5
            self.canvas.move(obj["id"], 0, 5)
            # Comprobar colisión con la barra
            if obj["y"] + obj["radius"] >= self.paddle_y:
                # Comprobar solapamiento horizontal
                if (self.paddle_x - obj["radius"] <= obj["x"] <= self.paddle_x + self.paddle_width + obj["radius"]):
                    # Si el objeto es malo (calavera), derrota inmediata
                    if obj.get("is_bad"):
                        self._game_over(False)
                        return
                    else:
                        # Atrapado
                        self.caught += 1
                        objects_to_remove.append(obj)
                        continue
            # Comprobar si salió de la pantalla (perdido)
            if obj["y"] - obj["radius"] > self.height:
                self.missed += 1
                objects_to_remove.append(obj)
        # Remove caught/missed objects
        for obj in objects_to_remove:
            try:
                self.canvas.delete(obj["id"])
            except Exception:
                pass
            if obj in self.objects:
                self.objects.remove(obj)
        # Update score display
        self._update_score_text()
        # Check end condition
        if self.spawned_objects >= self.total_objects and not self.objects:
            self._game_over()
            return
        # Continue updating
        self.window.after(30, self._update_objects)

    def _update_score_text(self) -> None:
        # Remove previous score text(s) if any
        # We'll identify by tag
        self.canvas.delete("score_text")
        score = f"Atrapados: {self.caught}  Perdidos: {self.missed}"
        self.canvas.create_text(
            10, 10,
            text=score,
            anchor="nw",
            font=("Arial", 14, "bold"),
            fill="white",
            tag="score_text"
        )

    def _game_over(self) -> None:
        self.game_running = False
        won = self.caught >= self.required_catches
        # Clear canvas
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
            text=f"Atrapados: {self.caught}/{self.total_objects}",
            font=("Arial", 16),
            fill="white"
        ))
        # Botón gris en la pantalla de resultado
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
        # Remove all items on canvas and internal lists
        for obj in self.objects:
            try:
                self.canvas.delete(obj["id"])
            except Exception:
                pass
        self.objects.clear()
        try:
            self.canvas.delete("all")
        except Exception:
            pass
        self.widgets.clear()