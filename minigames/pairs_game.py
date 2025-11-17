"""
PairsGame - Minijuego de buscar parejas para MiniPet.

Este juego presenta una cuadrícula de cartas boca abajo con iconos
repetidos por parejas. El objetivo es encontrar todas las parejas
de iconos antes de que se agote el tiempo. Cada vez que el jugador
selecciona dos cartas que coinciden, estas permanecen volteadas. Si
no coinciden, se vuelven a girar después de un breve intervalo.
El fondo se elige al azar entre las imágenes "fran" de la carpeta
``assets/custom`` y se oscurece ligeramente. Todos los textos usan
Comic Sans MS para mantener la coherencia estética.
"""

import tkinter as tk
import random
import os

try:
    from PIL import Image, ImageTk, ImageEnhance  # type: ignore
    HAS_PIL = True
except Exception:
    HAS_PIL = False


class PairsGame:
    """Minijuego de memorizar parejas de iconos."""

    def __init__(self, parent_window: tk.Tk, callback) -> None:
        self.callback = callback
        self.game_closed = False
        # Dimensiones
        self.width = 600
        self.height = 520
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
        # Variables del juego
        self.icons = ['😀', '🐶', '🍎', '⚽', '🚗', '🎵', '🌟', '🍕']
        # Duplicar y barajar
        self.deck = []
        self.cards_state = []  # 'hidden', 'revealed', 'matched'
        self.first_selection = None
        self.start_time = 0.0
        self.time_limit = 60  # segundos
        self.timer_job = None
        # Widgets para limpiar
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
            cx, cy - 120,
            text="BUSCA LAS PAREJAS",
            font=("Comic Sans MS", 28, "bold"),
            fill="white"
        ))
        inst = (
            "Encuentra todas las parejas de iconos antes de que se acabe el tiempo.\n"
            "Haz clic en dos cartas para girarlas. Si son iguales, se quedarán descubiertas."
        )
        self.widgets.append(self.canvas.create_text(
            cx, cy - 40,
            text=inst,
            font=("Comic Sans MS", 14),
            fill="yellow",
            justify="center",
            width=self.width - 80
        ))
        # Botón comenzar
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 60, cx + 100, cy + 110,
            fill="#6e6e6e", outline="white", width=3
        )
        self.widgets.append(btn_rect)
        btn_text = self.canvas.create_text(
            cx, cy + 85,
            text="COMENZAR",
            font=("Comic Sans MS", 18, "bold"),
            fill="white"
        )
        self.widgets.append(btn_text)
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._start_game())
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._start_game())

    def _start_game(self) -> None:
        # Preparar baraja
        deck = self.icons * 2
        random.shuffle(deck)
        self.deck = deck
        self.cards_state = ['hidden'] * len(deck)
        self.first_selection = None
        self.start_time = time.time()
        # Dibujar tablero
        self._draw_board()
        # Iniciar temporizador
        self._update_timer()

    def _draw_board(self) -> None:
        self._clear_canvas()
        # Fondo
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        # Mostrar temporizador
        elapsed = time.time() - self.start_time
        remaining = max(0, int(self.time_limit - elapsed)) if self.start_time else self.time_limit
        self.widgets.append(self.canvas.create_text(
            20, 20,
            anchor="nw",
            text=f"Tiempo: {remaining:02d}s",
            font=("Comic Sans MS", 16, "bold"),
            fill="white"
        ))
        # Dimensiones de cartas y posiciones
        rows = 4
        cols = 4
        card_w = 80
        card_h = 80
        spacing_x = (self.width - cols * card_w) // (cols + 1)
        spacing_y = (self.height - 150 - rows * card_h) // (rows + 1)
        y0 = 100
        idx = 0
        for r in range(rows):
            x = spacing_x
            y = y0 + spacing_y + r * (card_h + spacing_y)
            for c in range(cols):
                # Dibujar carta según estado
                state = self.cards_state[idx]
                rect = self.canvas.create_rectangle(
                    x, y, x + card_w, y + card_h,
                    fill="#455A64" if state == 'hidden' else "#FFF59D", outline="white", width=2
                )
                self.widgets.append(rect)
                # Mostrar icono si revelada o emparejada
                if state in ('revealed', 'matched'):
                    icon = self.deck[idx]
                    self.widgets.append(self.canvas.create_text(
                        x + card_w/2, y + card_h/2,
                        text=icon,
                        font=("Comic Sans MS", 32),
                        fill="#000000"
                    ))
                # Asociar eventos solo a cartas ocultas
                if state == 'hidden':
                    self.canvas.tag_bind(rect, "<Button-1>", lambda e, i=idx: self._reveal_card(i))
                idx += 1
                x += card_w + spacing_x

    def _reveal_card(self, index: int) -> None:
        # Ignorar si ya está revelada o emparejada
        if self.cards_state[index] != 'hidden':
            return
        # Revelar la carta
        self.cards_state[index] = 'revealed'
        self._draw_board()
        if self.first_selection is None:
            self.first_selection = index
            return
        # Segunda selección
        second = index
        first = self.first_selection
        self.first_selection = None
        # Comprobar coincidencia
        if self.deck[first] == self.deck[second]:
            # Marcar ambas como emparejadas
            self.cards_state[first] = 'matched'
            self.cards_state[second] = 'matched'
            # Comprobar victoria
            if all(state == 'matched' for state in self.cards_state):
                # Ganaste
                self._game_over(True)
        else:
            # No coinciden: ocultar después de medio segundo
            def hide_again():
                if not self.game_closed:
                    self.cards_state[first] = 'hidden'
                    self.cards_state[second] = 'hidden'
                    self._draw_board()
            self.window.after(600, hide_again)

    def _update_timer(self) -> None:
        if self.game_closed:
            return
        if not self.start_time:
            return
        elapsed = time.time() - self.start_time
        remaining = self.time_limit - elapsed
        if remaining <= 0:
            # Tiempo agotado
            self._game_over(False)
            return
        # Continuar actualizando cada 1 segundo
        self.timer_job = self.window.after(500, self._update_timer)
        # Redibujar tablero para actualizar temporizador
        self._draw_board()

    def _game_over(self, won: bool) -> None:
        if self.game_closed:
            return
        self.game_closed = True
        # Cancelar temporizador
        if self.timer_job:
            try:
                self.window.after_cancel(self.timer_job)
            except Exception:
                pass
            self.timer_job = None
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
        msg = "¡Has encontrado todas las parejas!" if won else "Se ha agotado el tiempo."
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text=msg,
            font=("Comic Sans MS", 18),
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
            font=("Comic Sans MS", 18, "bold"),
            fill="white"
        )
        self.widgets.append(btn_text)
        # Asignar callback
        def close():
            try:
                self.window.destroy()
            except Exception:
                pass
            try:
                self.callback('won' if won else 'lost')
            except Exception:
                pass
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: close())
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: close())

    def _clear_canvas(self) -> None:
        try:
            self.canvas.delete("all")
        except Exception:
            pass
        self.widgets.clear()