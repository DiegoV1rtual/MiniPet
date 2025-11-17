"""
SpaceInvaderGame - minijuego estilo Space Invaders para MiniPet.

El jugador controla una nave situada en la parte inferior de la pantalla.
Puede moverse a izquierda y derecha con las flechas y disparar con la
barra espaciadora. Un grupo de alienígenas se desplaza lateralmente y
desciende de forma gradual. Debes derribar a todos los alienígenas
antes de que alguno alcance la parte inferior o antes de que termine
el tiempo. Si destruyes todos los aliens, ganas; si algún alien
alcanza tu zona o se agota el tiempo, pierdes.

El fondo se elige al azar de las imágenes "fran" en ``assets/custom``
y se oscurece ligeramente. Las instrucciones están escritas con un
estilo informal (Comic Sans) y los botones son grises para integrarse
con el resto del proyecto.
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


class SpaceInvaderGame:
    """Minijuego similar a Space Invaders."""

    def __init__(self, parent_window: tk.Tk, callback) -> None:
        self.callback = callback
        self.game_closed = False
        # Configuración de juego
        self.width = 600
        self.height = 500
        self.game_duration = 30  # segundos para completar
        self.start_time = 0.0
        self.game_running = False
        # Nave del jugador
        self.player_width = 40
        self.player_height = 15
        self.player_x = self.width // 2
        self.player_y = self.height - 50
        # Balas
        self.bullet = None
        self.bullet_speed = 10
        # Aliens
        self.aliens = []  # lista de dicts con x,y
        self.alien_rows = 3
        self.alien_cols = 6
        self.alien_width = 40
        self.alien_height = 20
        self.alien_speed_x = 5
        self.alien_direction = 1  # 1 derecha, -1 izquierda
        # Puntuación
        self.score = 0
        # Ventana
        self.window = tk.Toplevel()
        self.window.title("")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#1a1a1a")
        # Canvas
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
        if HAS_PIL:
            bg_dir = os.path.join("assets", "custom")
            try:
                fran_files = [f for f in os.listdir(bg_dir)
                              if f.lower().startswith("fran") and f.lower().endswith((".png", ".gif"))]
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
        # Widgets
        self.widgets = []
        # Bind para controles
        self.window.bind("<Left>", lambda e: self._move_player(-15))
        self.window.bind("<Right>", lambda e: self._move_player(15))
        self.window.bind("<space>", lambda e: self._shoot())

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
        # Título e instrucciones
        self.widgets.append(self.canvas.create_text(
            cx, cy - 120,
            text="SPACE INVADERS",
            font=("Comic Sans MS", 28, "bold"),
            fill="white"
        ))
        inst_text = (
            "Mueve la nave con ← y → y dispara con ESPACIO.\n"
            "Derriba a todos los alienígenas antes de que bajen o se acabe el tiempo."
        )
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text=inst_text,
            font=("Comic Sans MS", 13),
            fill="yellow",
            justify="center"
        ))
        # Botón de inicio
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
        self.score = 0
        # Inicializar aliens
        self.aliens.clear()
        start_x = (self.width - (self.alien_cols * self.alien_width + (self.alien_cols - 1) * 20)) // 2
        for row in range(self.alien_rows):
            for col in range(self.alien_cols):
                x = start_x + col * (self.alien_width + 20)
                y = 80 + row * (self.alien_height + 20)
                self.aliens.append({"x": x, "y": y, "alive": True})
        # Reset bullet
        self.bullet = None
        # Dibujar escena inicial y lanzar bucle
        self._draw_scene()
        self._game_loop()

    def _move_player(self, dx: int) -> None:
        if not self.game_running:
            return
        new_x = self.player_x + dx
        # Restringir a límites
        half = self.player_width // 2
        if new_x - half < 0:
            new_x = half
        if new_x + half > self.width:
            new_x = self.width - half
        self.player_x = new_x
        self._draw_scene()

    def _shoot(self) -> None:
        if not self.game_running:
            return
        # Solo una bala activa a la vez
        if self.bullet is None:
            self.bullet = {"x": self.player_x, "y": self.player_y - self.player_height//2}

    def _update_bullet(self) -> None:
        if self.bullet is not None:
            self.bullet["y"] -= self.bullet_speed
            # Verificar colisión con aliens
            hit_index = None
            for idx, alien in enumerate(self.aliens):
                if not alien["alive"]:
                    continue
                ax = alien["x"]
                ay = alien["y"]
                aw = self.alien_width
                ah = self.alien_height
                bx = self.bullet["x"]
                by = self.bullet["y"]
                if (ax <= bx <= ax + aw) and (ay <= by <= ay + ah):
                    hit_index = idx
                    break
            if hit_index is not None:
                # Eliminar alien y bala
                self.aliens[hit_index]["alive"] = False
                self.bullet = None
                self.score += 1
                return
            # Si la bala sale de la pantalla, eliminarla
            if self.bullet["y"] < 0:
                self.bullet = None

    def _move_aliens(self) -> None:
        # Mover aliens horizontales; si chocan con el borde, cambiar dirección y bajar
        change_direction = False
        for alien in self.aliens:
            if not alien["alive"]:
                continue
            new_x = alien["x"] + self.alien_speed_x * self.alien_direction
            # Revisar colisiones con bordes
            if new_x < 0 or new_x + self.alien_width > self.width:
                change_direction = True
                break
        if change_direction:
            self.alien_direction *= -1
            # Bajar todos los aliens
            for alien in self.aliens:
                alien["y"] += 20
        else:
            # Mover normal
            for alien in self.aliens:
                alien["x"] += self.alien_speed_x * self.alien_direction

    def _check_game_conditions(self) -> None:
        # Verificar victoria: todos los aliens destruidos
        if all(not alien["alive"] for alien in self.aliens):
            self._game_over(True)
            return
        # Verificar derrota: un alien llega al nivel del jugador
        for alien in self.aliens:
            if alien["alive"] and alien["y"] + self.alien_height >= self.player_y - self.player_height:
                self._game_over(False)
                return
        # Verificar tiempo
        elapsed = time.time() - self.start_time
        if elapsed >= self.game_duration:
            # Si quedan aliens vivos, pierdes, de lo contrario ganas
            all_dead = all(not a["alive"] for a in self.aliens)
            self._game_over(all_dead)

    def _game_loop(self) -> None:
        if not self.game_running or self.game_closed:
            return
        # Actualizar elementos
        self._move_aliens()
        self._update_bullet()
        self._check_game_conditions()
        self._draw_scene()
        # Programar siguiente iteración
        self.window.after(50, self._game_loop)

    def _draw_scene(self) -> None:
        # Limpiar canvas
        self._clear_canvas()
        # Dibujar fondo
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        # Dibujar aliens
        for alien in self.aliens:
            if alien["alive"]:
                rect = self.canvas.create_rectangle(
                    alien["x"], alien["y"],
                    alien["x"] + self.alien_width,
                    alien["y"] + self.alien_height,
                    fill="#FF5722", outline="white", width=2
                )
                self.widgets.append(rect)
        # Dibujar bala
        if self.bullet is not None:
            bx = self.bullet["x"]
            by = self.bullet["y"]
            b_rect = self.canvas.create_rectangle(
                bx - 2, by - 10, bx + 2, by,
                fill="#FFFFFF", outline="white"
            )
            self.widgets.append(b_rect)
        # Dibujar jugador
        px = self.player_x
        py = self.player_y
        half = self.player_width // 2
        player_rect = self.canvas.create_polygon(
            px, py - self.player_height,
            px - half, py,
            px + half, py,
            fill="#2196F3", outline="white", width=2
        )
        self.widgets.append(player_rect)
        # Puntuación y tiempo
        elapsed = int(self.game_duration - (time.time() - self.start_time)) if self.game_running else 0
        self.widgets.append(self.canvas.create_text(
            10, 10,
            anchor="nw",
            text=f"Puntuación: {self.score}    Tiempo: {elapsed:02d}s",
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
        msg = "¡Has destruido a los invasores!" if won else "Los alienígenas te han vencido"
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text=msg,
            font=("Comic Sans MS", 16),
            fill="white"
        ))
        # Botón de continuar
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