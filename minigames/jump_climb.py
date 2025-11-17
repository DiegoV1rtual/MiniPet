"""
JumpClimb - Versión renovada estilo Doodle Jump para MiniPet.

Este minijuego reemplaza la antigua mecánica de "salta y sube" por un
juego vertical inspirado en Doodle Jump. El objetivo es saltar de
plataforma en plataforma mientras la pantalla se desplaza hacia abajo.
Cada vez que el jugador rebota en una plataforma se incrementa un
contador de saltos; al alcanzar un número objetivo de saltos el
jugador gana. Si cae por debajo de la pantalla, pierde.

El fondo se elige aleatoriamente entre las imágenes cuyo nombre
empieza por "fran" en la carpeta ``assets/custom`` y se oscurece
ligeramente para que el contraste con los elementos de juego sea
menor. Todos los botones usan un tono gris sólido para una estética
uniforme.
"""

import tkinter as tk
import random
import os

try:
    # Pillow es opcional. Si está disponible, lo usamos para cargar
    # las imágenes de fondo y ajustar su brillo.
    from PIL import Image, ImageTk, ImageEnhance  # type: ignore
    HAS_PIL = True
except Exception:
    HAS_PIL = False


class JumpClimb:
    """Juego estilo Doodle Jump.

    El jugador controla un rectángulo que rebota sobre plataformas
    horizontales. Cuando el personaje asciende por encima de la mitad
    de la pantalla, las plataformas se desplazan hacia abajo para dar
    la impresión de que el jugador sube. El objetivo es lograr un
    número determinado de rebotes en plataformas; si el jugador cae
    por debajo de la pantalla, pierde.
    """

    def __init__(self, parent_window: tk.Tk, callback) -> None:
        self.callback = callback
        self.game_closed = False
        # Configuración
        self.target_jumps = 20  # número de rebotes necesarios para ganar
        self.success_count = 0
        self.game_running = False

        # Dimensiones de la ventana y área de juego
        self.width = 400
        self.height = 600

        # Crear la ventana toplevel sin bordes
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

        # Hacer la ventana arrastrable
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

        # Jugador (rectángulo)
        self.player_width = 30
        self.player_height = 30
        self.player_x = self.width // 2
        self.player_y = self.height - 60
        self.vy = 0.0
        self.gravity = 0.5
        self.jump_velocity = -12.0
        self.player_id = None

        # Control de movimiento horizontal
        self.move_left = False
        self.move_right = False
        self.move_speed = 5
        self.window.bind("<KeyPress-Left>", lambda e: self._on_key_press(-1))
        self.window.bind("<KeyRelease-Left>", lambda e: self._on_key_release(-1))
        self.window.bind("<KeyPress-Right>", lambda e: self._on_key_press(1))
        self.window.bind("<KeyRelease-Right>", lambda e: self._on_key_release(1))

        # Plataformas: lista de dicts con x, y, w, h, id
        self.platforms = []
        self.platform_width = 80
        self.platform_height = 20
        self.platform_count = 10

        # Widgets dibujados (para limpieza)
        self.widgets = []

    # Métodos de arrastre de la ventana
    def _start_drag(self, event: tk.Event) -> None:
        self._drag_data = {"x": event.x, "y": event.y}

    def _drag(self, event: tk.Event) -> None:
        if hasattr(self, "_drag_data"):
            x = self.window.winfo_x() + event.x - self._drag_data["x"]
            y = self.window.winfo_y() + event.y - self._drag_data["y"]
            self.window.geometry(f"+{x}+{y}")

    # Métodos de teclado para movimiento horizontal
    def _on_key_press(self, direction: int) -> None:
        if direction == -1:
            self.move_left = True
        elif direction == 1:
            self.move_right = True

    def _on_key_release(self, direction: int) -> None:
        if direction == -1:
            self.move_left = False
        elif direction == 1:
            self.move_right = False

    def run(self) -> None:
        """Mostrar la pantalla de instrucciones y esperar al jugador."""
        self.window.after(100, self._show_instructions)

    def _show_instructions(self) -> None:
        """Pantalla de instrucciones con botón de inicio."""
        self._clear_canvas()
        cx, cy = self.width // 2, self.height // 2
        # Dibujar fondo
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        # Título
        self.widgets.append(self.canvas.create_text(
            cx, cy - 150,
            text="SALTA Y SUBE",
            font=("Arial", 28, "bold"),
            fill="white"
        ))
        # Instrucciones
        inst = (
            f"Salta de plataforma en plataforma y evita caer.\n"
            f"Llega a {self.target_jumps} rebotes para ganar.\n"
            "Usa las flechas izquierda/derecha para moverte."
        )
        self.widgets.append(self.canvas.create_text(
            cx, cy - 60,
            text=inst,
            font=("Arial", 13),
            fill="yellow",
            justify="center"
        ))
        # Botón comenzar
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 40, cx + 100, cy + 90,
            fill="#6e6e6e", outline="white", width=3
        )
        self.widgets.append(btn_rect)
        btn_text = self.canvas.create_text(
            cx, cy + 65,
            text="COMENZAR",
            font=("Arial", 16, "bold"),
            fill="white"
        )
        self.widgets.append(btn_text)
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._start_game())
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._start_game())

    def _start_game(self) -> None:
        """Inicializa los parámetros del juego y comienza el bucle principal."""
        self.success_count = 0
        self.game_running = True
        # Restablecer jugador
        self.player_x = self.width // 2
        self.player_y = self.height - 60
        self.vy = 0.0
        # Generar plataformas iniciales
        self.platforms.clear()
        spacing = self.height // self.platform_count
        for i in range(self.platform_count):
            py = self.height - i * spacing
            px = random.randint(0, self.width - self.platform_width)
            self.platforms.append({"x": px, "y": py})
        # Dibujar pantalla inicial
        self._clear_canvas()
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        # Dibujar plataformas y jugador
        self._draw_platforms()
        self._draw_player()
        # Iniciar actualizaciones
        self._update_game()

    def _draw_player(self) -> None:
        """Dibuja el jugador en la posición actual."""
        if self.player_id is not None:
            try:
                self.canvas.delete(self.player_id)
            except Exception:
                pass
        self.player_id = self.canvas.create_rectangle(
            self.player_x - self.player_width // 2, self.player_y - self.player_height // 2,
            self.player_x + self.player_width // 2, self.player_y + self.player_height // 2,
            fill="#FFC107", outline="white", width=2
        )
        # Mostrar contador de saltos
        self.canvas.delete("jump_text")
        self.canvas.create_text(
            10, 10,
            text=f"Rebotes: {self.success_count}/{self.target_jumps}",
            anchor="nw",
            font=("Arial", 14, "bold"),
            fill="white",
            tag="jump_text"
        )

    def _draw_platforms(self) -> None:
        """Dibuja todas las plataformas."""
        # Eliminar plataformas existentes
        self.canvas.delete("platform")
        for plat in self.platforms:
            self.canvas.create_rectangle(
                plat["x"], plat["y"],
                plat["x"] + self.platform_width, plat["y"] + self.platform_height,
                fill="#6e6e6e", outline="white", width=2,
                tags="platform"
            )

    def _update_game(self) -> None:
        """Actualiza la lógica del juego en cada fotograma."""
        if not self.game_running or self.game_closed:
            return
        # Actualizar velocidad vertical
        self.vy += self.gravity
        # Actualizar posición horizontal según teclas
        if self.move_left and not self.move_right:
            self.player_x -= self.move_speed
        if self.move_right and not self.move_left:
            self.player_x += self.move_speed
        # Limitar movimiento horizontal y efecto de wrap-around
        if self.player_x < -self.player_width // 2:
            self.player_x = self.width + self.player_width // 2
        elif self.player_x > self.width + self.player_width // 2:
            self.player_x = -self.player_width // 2
        # Actualizar posición vertical
        self.player_y += self.vy
        # Colisiones con plataformas (solo cuando cae)
        if self.vy > 0:
            for plat in self.platforms:
                # Coordenadas de la plataforma
                px1 = plat["x"]
                px2 = plat["x"] + self.platform_width
                py = plat["y"]
                # Comprobar colisión: el jugador debe estar sobre la plataforma
                if (self.player_x + self.player_width // 2 >= px1 and
                    self.player_x - self.player_width // 2 <= px2 and
                    self.player_y + self.player_height // 2 >= py and
                    self.player_y + self.player_height // 2 - self.vy < py):
                    # Rebote
                    self.player_y = py - self.player_height // 2
                    self.vy = self.jump_velocity
                    self.success_count += 1
                    break
        # Scroll: si el jugador sube más arriba de la mitad
        if self.player_y < self.height // 2:
            shift = (self.height // 2) - self.player_y
            self.player_y = self.height // 2
            # Desplazar todas las plataformas hacia abajo
            for plat in self.platforms:
                plat["y"] += shift
            # Generar nuevas plataformas si es necesario
            while self.platforms and self.platforms[0]["y"] > self.height:
                # Eliminar plataformas que salen por la parte inferior
                self.platforms.pop(0)
            # Añadir nuevas plataformas en la parte superior
            while len(self.platforms) < self.platform_count:
                # Tomar la y mínima de las actuales
                min_y = min(p["y"] for p in self.platforms) if self.platforms else self.height
                new_y = min_y - random.randint(70, 100)
                new_x = random.randint(0, self.width - self.platform_width)
                self.platforms.append({"x": new_x, "y": new_y})
            # Ordenar plataformas por y ascendente
            self.platforms.sort(key=lambda p: p["y"])
        # Comprobar derrota
        if self.player_y - self.player_height // 2 > self.height:
            self._game_over(False)
            return
        # Comprobar victoria
        if self.success_count >= self.target_jumps:
            self._game_over(True)
            return
        # Redibujar
        self._clear_canvas(background=False)
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        self._draw_platforms()
        self._draw_player()
        # Próxima actualización
        self.window.after(20, self._update_game)

    def _game_over(self, won: bool) -> None:
        """Muestra la pantalla final y llama al callback."""
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
        msg = "¡Has alcanzado la meta de rebotes!" if won else "Has caído fuera de la pantalla"
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text=msg,
            font=("Arial", 16),
            fill="white"
        ))
        # Botón continuar
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
        """Cierra la ventana y notifica el resultado."""
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

    def _clear_canvas(self, background: bool = True) -> None:
        """Limpia el canvas y la lista de widgets. Si background es False,
        conserva el fondo actual (se redibuja después)."""
        try:
            if background:
                self.canvas.delete("all")
            else:
                # Eliminamos todos los objetos salvo el fondo; lo identificamos
                # borrando por tags específicos.
                self.canvas.delete("platform")
                if self.player_id:
                    try:
                        self.canvas.delete(self.player_id)
                    except Exception:
                        pass
                self.canvas.delete("jump_text")
        except Exception:
            pass
        # Reiniciar lista de widgets
        self.widgets.clear()