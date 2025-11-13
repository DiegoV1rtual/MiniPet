"""
CrossRoad - Juego de cruzar la carretera para MiniPet.

El jugador controla un avatar que debe cruzar una carretera con varios
carriles en los que circulan coches a distintas velocidades. El
objetivo es alcanzar la zona superior de la pantalla sin ser atropellado.
Debe lograrlo tres veces para ganar. Si un coche choca con el jugador
en cualquier intento, pierde.

Se utiliza un fondo personalizable ``assets/custom/cross_bg.png`` si
está disponible. Los coches son simples rectángulos con colores vivos.
"""

import tkinter as tk
import random
import os

try:
    from PIL import Image, ImageTk  # type: ignore
    HAS_PIL = True
except Exception:
    HAS_PIL = False


class CrossRoad:
    """Minijuego de cruzar una carretera esquivando coches."""

    def __init__(self, parent_window: tk.Tk, callback) -> None:
        self.callback = callback
        self.game_closed = False
        # Configuración
        self.required_crosses = 3
        self.crosses = 0
        self.game_running = False
        # Dimensiones
        self.width, self.height = 600, 500
        # Carriles y coches
        self.lanes = []
        self.cars = []  # lista de coches activos

        # Ventana
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

        # Arrastrar ventana
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag)

        # Fondo
        self.bg_photo = None
        # Usar una imagen de fondo genérica 'fondo6.png'.
        bg_path = os.path.join("assets", "custom", "fondo6.png")
        if HAS_PIL and os.path.exists(bg_path):
            try:
                img = Image.open(bg_path)
                img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(img)
            except Exception:
                self.bg_photo = None

        # Jugador
        self.player_width = 30
        self.player_height = 30
        self.player_x = (self.width - self.player_width) // 2
        self.start_y = self.height - self.player_height - 10
        self.player_y = self.start_y
        self.player_id = None
        # Movimiento del jugador
        self.step_x = 20
        self.step_y = 40
        self.window.bind("<Left>", lambda e: self._move_player(-self.step_x, 0))
        self.window.bind("<Right>", lambda e: self._move_player(self.step_x, 0))
        self.window.bind("<Up>", lambda e: self._move_player(0, -self.step_y))
        self.window.bind("<Down>", lambda e: self._move_player(0, self.step_y))

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
            text="CRUZA LA CALLE",
            font=("Arial", 28, "bold"),
            fill="white"
        ))
        inst_text = (
            "Guía al personaje con las flechas: arriba para avanzar, abajo para retroceder y \n"
            "izquierda/derecha para esquivar.\n"
            "Debes cruzar la carretera 3 veces sin chocar con los coches para ganar."
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
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._start_game())
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._start_game())

    def _start_game(self) -> None:
        self.crosses = 0
        self.game_running = True
        self.cars = []
        # Configurar carriles
        lane_count = 4
        lane_height = (self.height - 100) // lane_count
        self.lanes = []
        base_y = 60
        for i in range(lane_count):
            y = base_y + i * lane_height + lane_height // 2
            speed = random.randint(4, 8)
            direction = 1 if i % 2 == 0 else -1
            self.lanes.append({"y": y, "speed": speed, "direction": direction})
        # Limpiar y dibujar fondo
        self._clear_canvas()
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        # Colocar jugador en posición inicial
        self.player_x = (self.width - self.player_width) // 2
        self.player_y = self.start_y
        self._draw_player()
        # Arrancar bucles
        self._spawn_car()
        self._update_cars()

    def _draw_player(self) -> None:
        if self.player_id is not None:
            try:
                self.canvas.delete(self.player_id)
            except Exception:
                pass
        self.player_id = self.canvas.create_rectangle(
            self.player_x, self.player_y,
            self.player_x + self.player_width, self.player_y + self.player_height,
            fill="#8BC34A", outline="white", width=2
        )

    def _move_player(self, dx: int, dy: int) -> None:
        if not self.game_running:
            return
        new_x = self.player_x + dx
        new_y = self.player_y + dy
        if new_x < 0 or new_x + self.player_width > self.width:
            new_x = self.player_x
        if new_y < 0 or new_y + self.player_height > self.height:
            new_y = self.player_y
        self.player_x = new_x
        self.player_y = new_y
        self._draw_player()
        # Comprobar si llegó al otro lado
        if self.player_y <= 20:
            self.crosses += 1
            if self.crosses >= self.required_crosses:
                self._game_over(True)
                return
            # Reset a posición inicial
            self.player_x = (self.width - self.player_width) // 2
            self.player_y = self.start_y
            self._draw_player()

    def _spawn_car(self) -> None:
        if not self.game_running:
            return
        for lane in self.lanes:
            if random.random() < 0.5:
                car_width = random.randint(60, 100)
                car_height = 30
                if lane["direction"] == 1:
                    x = -car_width
                else:
                    x = self.width
                color = random.choice(["#FF5722", "#3F51B5", "#009688", "#E91E63"])
                car_id = self.canvas.create_rectangle(
                    x, lane["y"] - car_height//2,
                    x + car_width, lane["y"] + car_height//2,
                    fill=color, outline="white", width=2
                )
                self.cars.append({
                    "id": car_id,
                    "x": x,
                    "y": lane["y"],
                    "width": car_width,
                    "height": car_height,
                    "speed": lane["speed"],
                    "direction": lane["direction"]
                })
        # Programar siguiente coche
        self.window.after(800, self._spawn_car)

    def _update_cars(self) -> None:
        if not self.game_running:
            return
        cars_to_remove = []
        for car in self.cars:
            car["x"] += car["speed"] * car["direction"]
            self.canvas.move(car["id"], car["speed"] * car["direction"], 0)
            # Colisión con jugador
            if (self.player_y + self.player_height > car["y"] - car["height"] / 2 and
                self.player_y < car["y"] + car["height"] / 2 and
                self.player_x + self.player_width > car["x"] and
                self.player_x < car["x"] + car["width"]):
                self._game_over(False)
                return
            # Eliminación cuando sale de la pantalla
            if car["direction"] == 1 and car["x"] > self.width:
                cars_to_remove.append(car)
            elif car["direction"] == -1 and car["x"] + car["width"] < 0:
                cars_to_remove.append(car)
        for car in cars_to_remove:
            try:
                self.canvas.delete(car["id"])
            except Exception:
                pass
            if car in self.cars:
                self.cars.remove(car)
        # Actualizar etiqueta de cruzados
        self.canvas.delete("cross_text")
        self.canvas.create_text(
            10, 10,
            text=f"Cruces: {self.crosses}/{self.required_crosses}",
            anchor="nw",
            font=("Arial", 14, "bold"),
            fill="white",
            tag="cross_text"
        )
        self.window.after(30, self._update_cars)

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
        msg = "¡Has cruzado todas las calles!" if won else "Has sido atropellado"
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text=msg,
            font=("Arial", 16),
            fill="white"
        ))
        # Botón continuar
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
        # Eliminar coches
        for car in self.cars:
            try:
                self.canvas.delete(car["id"])
            except Exception:
                pass
        self.cars.clear()
        try:
            self.canvas.delete("all")
        except Exception:
            pass
        self.widgets.clear()