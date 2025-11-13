"""
FishingGame - Un minijuego de pesca inspirado en Stardew Valley para MiniPet.

En este minijuego el jugador debe capturar 3 peces consecutivos utilizando
una mecánica de barra. Se muestra una barra vertical con un área verde que
representa la zona donde el pez debe permanecer. Un indicador del pez se
mueve de arriba abajo de forma aleatoria. El jugador debe mantener la
barra en la zona correcta pulsando y soltando la barra espaciadora.
Cada pez capturado incrementa la dificultad aumentando la velocidad del pez.

Controles:
  - Mantén presionada la barra espaciadora para subir la barra.
  - Suelta la barra espaciadora para que baje.
  - Mantén el indicador del pez dentro del área verde hasta que la barra de progreso
    llegue al 100 %.

Si el jugador atrapa 3 peces seguidos, gana; si falla uno, pierde. El juego
muestra una pantalla de resultado indicando la victoria o derrota y luego
invoca el callback proporcionado con "won" o "lost".

El fondo puede personalizarse colocando una imagen llamada ``fondo10.png`` en
``assets/custom``. Si la imagen no existe o Pillow no está disponible, el
fondo será un color sólido predeterminado.
"""

import tkinter as tk
import random
import os

try:
    from PIL import Image, ImageTk  # type: ignore
    HAS_PIL = True
except Exception:
    HAS_PIL = False


class FishingGame:
    """Un juego de pesca donde hay que atrapar tres peces consecutivos."""

    def __init__(self, parent_window: tk.Tk, callback) -> None:
        self.callback = callback
        self.game_closed = False
        # Estado del juego
        self.fish_caught = 0
        self.fish_target = 3
        self.fishing = False
        self.progress = 0  # porcentaje de captura del pez actual
        self.fish_pos = 50  # posición del pez (0-100)
        self.fish_speed = 2  # velocidad base del pez
        self.fish_direction = 1
        self.bar_pos = 50  # posición de la barra verde (0-100)

        # Ventana
        self.window = tk.Toplevel()
        self.window.title("")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#1a1a1a")

        # Dimensiones
        self.width, self.height = 400, 600
        self.canvas = tk.Canvas(self.window, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Centrar ventana
        self.window.update_idletasks()
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        x = (screen_w - self.width) // 2
        y = (screen_h - self.height) // 2
        self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")

        # Permitir arrastrar
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag)

        # Control con barra espaciadora
        self.window.bind("<space>", self._hold_bar)
        self.window.bind("<KeyRelease-space>", self._release_bar)

        # Forzar foco para recibir eventos de teclado
        self.window.focus_force()

        # Imagen de fondo
        self.bg_photo = None
        bg_path = os.path.join("assets", "custom", "fondo10.png")
        if HAS_PIL and os.path.exists(bg_path):
            try:
                img = Image.open(bg_path)
                img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(img)
            except Exception:
                self.bg_photo = None

        # Widgets dibujados
        self.widgets = []
        # Estado de la barra (manteniendo espacio)
        self.holding = False

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
        """Muestra la pantalla de instrucciones con controles y objetivo."""
        self._clear_widgets()
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        # Fondo
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        # Título
        self.widgets.append(self.canvas.create_text(
            cx, cy - 200,
            text="JUEGO DE PESCA",
            font=("Arial", 28, "bold"),
            fill="white"
        ))
        # Instrucciones
        inst_text = (
            "Atrapa 3 peces consecutivos\n\n"
            "CÓMO JUGAR:\n"
            "- Mantén pulsada la barra espaciadora para subir la barra verde.\n"
            "- Suelta la barra espaciadora para que la barra baje.\n"
            "- Mantén el pez en el área verde hasta llenar la barra de progreso.\n"
            "Si fallas un pez, pierdes."
        )
        self.widgets.append(self.canvas.create_text(
            cx, cy - 40,
            text=inst_text,
            font=("Arial", 12),
            fill="yellow",
            justify="center"
        ))
        # Botón comenzar
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
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._start_fishing())
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._start_fishing())

    def _start_fishing(self) -> None:
        """Inicializa variables para una ronda de pesca y comienza el bucle."""
        self.fishing = True
        self.progress = 0
        self.fish_pos = 50
        self.bar_pos = 50
        # Aumentar velocidad del pez según peces ya capturados
        self.fish_speed = 2 + (self.fish_caught * 0.5)
        self._fishing_loop()

    def _hold_bar(self, event: tk.Event) -> None:
        self.holding = True

    def _release_bar(self, event: tk.Event) -> None:
        self.holding = False

    def _fishing_loop(self) -> None:
        """Bucle principal que actualiza barra, pez y progreso."""
        if not self.fishing or self.game_closed:
            return
        # Mover barra: subir si se sostiene espacio, bajar si no
        if self.holding:
            self.bar_pos = max(0, self.bar_pos - 3)
        else:
            self.bar_pos = min(100, self.bar_pos + 2)
        # Mover pez
        self.fish_pos += self.fish_speed * self.fish_direction
        if self.fish_pos <= 0 or self.fish_pos >= 100:
            self.fish_direction *= -1
        # Comprobar si pez está en el área verde
        bar_top = self.bar_pos
        bar_bottom = self.bar_pos + 20
        if bar_top <= self.fish_pos <= bar_bottom:
            # Progreso aumenta mientras el pez está en el área
            self.progress += 2
            if self.progress >= 100:
                # Pez capturado
                self.fish_caught += 1
                self.fishing = False
                if self.fish_caught >= self.fish_target:
                    # Ganar minijuego
                    self._game_over(True)
                else:
                    # Mostrar breve pausa y comenzar el siguiente pez
                    self.window.after(500, self._start_fishing)
                return
        else:
            # Retroceso del progreso si el pez sale del área
            self.progress = max(0, self.progress - 1)
        # Dibujar interfaz
        self._draw_fishing()
        # Continuar bucle tras pequeño intervalo
        self.window.after(30, self._fishing_loop)

    def _draw_fishing(self) -> None:
        """Dibuja los elementos del juego durante la pesca."""
        self._clear_widgets()
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx = w // 2
        # Fondo
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        # Título y contador de peces
        self.widgets.append(self.canvas.create_text(
            cx, 40,
            text=f"PESCA - Peces: {self.fish_caught}/{self.fish_target}",
            font=("Arial", 18, "bold"),
            fill="white"
        ))
        # Barra de progreso horizontal
        prog_y = 80
        prog_width = 300
        prog_x = cx - prog_width // 2
        # Marco
        self.widgets.append(self.canvas.create_rectangle(
            prog_x, prog_y, prog_x + prog_width, prog_y + 30,
            fill="#333", outline="white", width=2
        ))
        # Progreso verde
        self.widgets.append(self.canvas.create_rectangle(
            prog_x, prog_y, prog_x + (prog_width * self.progress // 100), prog_y + 30,
            fill="#4CAF50", outline=""
        ))
        # Porcentaje de progreso
        self.widgets.append(self.canvas.create_text(
            cx, prog_y + 15,
            text=f"Progreso: {self.progress}%",
            font=("Arial", 12, "bold"),
            fill="white"
        ))
        # Área de pesca vertical
        fishing_top = 150
        fishing_height = 350
        fishing_width = 80
        fishing_x = cx - fishing_width // 2
        # Fondo del área
        self.widgets.append(self.canvas.create_rectangle(
            fishing_x, fishing_top, fishing_x + fishing_width, fishing_top + fishing_height,
            fill="#1E3A5F", outline="white", width=3
        ))
        # Barra verde (área de captura) con altura relativa al total
        bar_y = fishing_top + (fishing_height * self.bar_pos // 100)
        bar_height = fishing_height * 20 // 100
        self.widgets.append(self.canvas.create_rectangle(
            fishing_x, bar_y, fishing_x + fishing_width, bar_y + bar_height,
            fill="#4CAF50", outline="white", width=2
        ))
        # Indicador del pez (círculo rojo)
        fish_y = fishing_top + (fishing_height * self.fish_pos // 100)
        fish_radius = 8
        self.widgets.append(self.canvas.create_oval(
            fishing_x + fishing_width // 2 - fish_radius,
            fish_y - fish_radius,
            fishing_x + fishing_width // 2 + fish_radius,
            fish_y + fish_radius,
            fill="#FF6B6B", outline="white", width=2
        ))

    def _game_over(self, won: bool) -> None:
        """Muestra el resultado y llama al callback."""
        self.fishing = False
        self._clear_widgets()
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        # Mensaje de resultado
        result_text = "VICTORIA" if won else "Derrota"
        result_color = "#4CAF50" if won else "#f44336"
        self.widgets.append(self.canvas.create_text(
            cx, cy - 80,
            text=result_text,
            font=("Arial", 36, "bold"),
            fill=result_color
        ))
        msg = "¡Has atrapado todos los peces!" if won else "Fallaste en la pesca"
        self.widgets.append(self.canvas.create_text(
            cx, cy - 30,
            text=msg,
            font=("Arial", 16),
            fill="white"
        ))
        # Botón continuar
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 40, cx + 100, cy + 90,
            fill="#2196F3", outline="white", width=3
        )
        self.widgets.append(btn_rect)
        btn_text = self.canvas.create_text(
            cx, cy + 65,
            text="CONTINUAR",
            font=("Arial", 16, "bold"),
            fill="white"
        )
        self.widgets.append(btn_text)
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._close_result(won))
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._close_result(won))

    def _close_result(self, won: bool) -> None:
        """Cierra el minijuego y notifica al juego principal."""
        try:
            self.window.destroy()
        except Exception:
            pass
        # Llamar callback con 'won' o 'lost'
        if callable(self.callback):
            try:
                self.callback('won' if won else 'lost')
            except Exception:
                pass

    def _clear_widgets(self) -> None:
        """Elimina todos los elementos creados en el canvas"""
        for wid in self.widgets:
            try:
                self.canvas.delete(wid)
            except Exception:
                pass
        self.widgets.clear()