"""
JumpClimb - Minijuego de saltar y subir para MiniPet.

El jugador controla un personaje en la parte inferior de la pantalla y
debe saltar sobre plataformas que se desplazan lateralmente. Si el
jugador acierta 15 saltos consecutivos, gana. Si falla un salto,
pierde. Este minijuego simplifica la mecánica de "subir" haciendo que
las plataformas se encuentren a una altura fija y se muevan sólo en el
eje horizontal; el jugador debe alinear su personaje con la plataforma
y saltar cuando esté debajo de ella.

El fondo se puede personalizar con ``assets/custom/jump_bg.png``.
"""

import tkinter as tk
import random
import os

try:
    from PIL import Image, ImageTk  # type: ignore
    HAS_PIL = True
except Exception:
    HAS_PIL = False


class JumpClimb:
    """Juego de saltar sobre plataformas que se mueven de lado a lado."""

    def __init__(self, parent_window: tk.Tk, callback) -> None:
        self.callback = callback
        self.game_closed = False
        # Configuración
        self.target_jumps = 15
        self.success_count = 0
        self.game_running = False

        # Dimensiones
        self.width, self.height = 600, 500
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
        # Arrastrar
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag)

        # Fondo
        self.bg_photo = None
        # Usar una imagen de fondo genérica 'fondo9.png'.
        bg_path = os.path.join("assets", "custom", "fondo9.png")
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
        self.player_y = self.height - self.player_height - 20
        self.player_id = None
        # Movimiento
        self.player_step = 20
        self.window.bind("<Left>", lambda e: self._move_player(-self.player_step))
        self.window.bind("<Right>", lambda e: self._move_player(self.player_step))
        self.window.bind("<Up>", lambda e: self._jump())

        # Plataforma
        self.platform_y = self.height - 150  # altura fija
        self.platform_width = 120
        self.platform_height = 20
        self.platform_x = random.randint(0, self.width - self.platform_width)
        self.platform_speed = random.randint(3, 6)
        self.platform_dir = random.choice([-1, 1])
        self.platform_id = None

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
            text="SALTA Y SUBE",
            font=("Arial", 28, "bold"),
            fill="white"
        ))
        inst_text = (
            "Alinea al personaje con la plataforma en movimiento y pulsa ↑ para saltar.\n"
            f"Debes acertar {self.target_jumps} saltos consecutivos para ganar."
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
        self.success_count = 0
        self.game_running = True
        # Reset jugador
        self.player_x = (self.width - self.player_width) // 2
        self.player_y = self.height - self.player_height - 20
        # Reset plataforma
        self.platform_x = random.randint(0, self.width - self.platform_width)
        self.platform_speed = random.randint(3, 6)
        self.platform_dir = random.choice([-1, 1])
        # Dibujar
        self._clear_canvas()
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        self._draw_platform()
        self._draw_player()
        # Iniciar movimiento de plataforma
        self._update_platform()

    def _draw_player(self) -> None:
        if self.player_id is not None:
            try:
                self.canvas.delete(self.player_id)
            except Exception:
                pass
        self.player_id = self.canvas.create_rectangle(
            self.player_x, self.player_y,
            self.player_x + self.player_width, self.player_y + self.player_height,
            fill="#FFC107", outline="white", width=2
        )
        # Actualizar marcador
        self.canvas.delete("jump_text")
        self.canvas.create_text(
            10, 10,
            text=f"Saltos: {self.success_count}/{self.target_jumps}",
            anchor="nw",
            font=("Arial", 14, "bold"),
            fill="white",
            tag="jump_text"
        )

    def _draw_platform(self) -> None:
        if self.platform_id is not None:
            try:
                self.canvas.delete(self.platform_id)
            except Exception:
                pass
        self.platform_id = self.canvas.create_rectangle(
            self.platform_x, self.platform_y,
            self.platform_x + self.platform_width, self.platform_y + self.platform_height,
            fill="#3F51B5", outline="white", width=2
        )

    def _move_player(self, dx: int) -> None:
        if not self.game_running:
            return
        new_x = self.player_x + dx
        new_x = max(0, min(new_x, self.width - self.player_width))
        self.player_x = new_x
        self._draw_player()

    def _jump(self) -> None:
        if not self.game_running:
            return
        # Verificar si jugador está alineado horizontalmente con plataforma
        if (self.player_x + self.player_width > self.platform_x and
            self.player_x < self.platform_x + self.platform_width):
            # Acierta salto
            self.success_count += 1
            if self.success_count >= self.target_jumps:
                self._game_over(True)
                return
            # Reposicionar plataforma y seguir
            self.platform_x = random.randint(0, self.width - self.platform_width)
            self.platform_speed = random.randint(3, 6)
            self.platform_dir = random.choice([-1, 1])
            self._draw_platform()
            self._draw_player()
        else:
            # Fallo
            self._game_over(False)

    def _update_platform(self) -> None:
        if not self.game_running:
            return
        # Mover plataforma
        self.platform_x += self.platform_speed * self.platform_dir
        if self.platform_x < 0:
            self.platform_x = 0
            self.platform_dir *= -1
        elif self.platform_x + self.platform_width > self.width:
            self.platform_x = self.width - self.platform_width
            self.platform_dir *= -1
        self._draw_platform()
        # Continuar movimiento
        self.window.after(30, self._update_platform)

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
        msg = "¡Has subido todas las plataformas!" if won else "Has caído"
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
        # Eliminar elementos
        try:
            self.canvas.delete("all")
        except Exception:
            pass
        self.widgets.clear()