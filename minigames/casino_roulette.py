"""
CasinoRouletteGame - Minijuego de ruleta de casino para MiniPet.

Este minijuego simula una mesa de ruleta clásica de 0 a 36. El jugador
dispone de fichas (chips) ficticias para apostar en números individuales.
Comienza con 100 fichas y su objetivo es alcanzar 500. Puede apostar
una cantidad de fichas a cualquier número de la mesa haciendo clic en
la casilla correspondiente; se le solicitará el importe mediante una
ventana emergente. Tras colocar las apuestas, debe pulsar GIRAR para
iniciar el giro. Si el número ganador coincide con alguna de sus
apuestas, recibirá 36 veces la cantidad apostada en esa casilla (la
apuesta se recupera junto al premio). Si desea abandonar antes de
alcanzar 500 fichas, puede pulsar RETIRARSE; se considerará victoria
solo si supera o iguala el objetivo.

Se utilizan fondos aleatorios a partir de imágenes con prefijo "fran"
de la carpeta ``assets/custom``. Todo el texto emplea la fuente
Comic Sans MS para mantener la coherencia estética.
"""

import tkinter as tk
from tkinter import simpledialog
import random
import os

try:
    from PIL import Image, ImageTk, ImageEnhance  # type: ignore
    HAS_PIL = True
except Exception:
    HAS_PIL = False


class CasinoRouletteGame:
    """Minijuego de ruleta de casino con apuestas a números."""

    def __init__(self, parent_window: tk.Tk, callback) -> None:
        self.callback = callback
        self.game_closed = False
        # Dimensiones
        self.width = 700
        self.height = 600
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
        # Variables de juego
        self.chips = 100
        self.target = 500
        self.bets = {}  # número -> cantidad apostada
        self.number_cells = {}  # rect_id -> número
        self.overlay_tokens = {}  # número -> id de gráfico de ficha
        # Colores de números (ruleta europea):
        self.red_numbers = {1, 3, 5, 7, 9, 12, 14, 16, 18,
                            19, 21, 23, 25, 27, 30, 32, 34, 36}
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
        # Fondo
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        # Título
        self.widgets.append(self.canvas.create_text(
            cx, 80,
            text="RULETA DE CASINO",
            font=("Comic Sans MS", 32, "bold"),
            fill="white"
        ))
        inst = (
            "Empiezas con 100 fichas. Haz clic en los números de la mesa para apostar.\n"
            "Cuando termines de apostar, pulsa GIRAR.\n"
            "Cada acierto paga 36× la apuesta. Llega a 500 fichas para ganar.\n"
            "Si te retiras antes de alcanzar 500 fichas, pierdes."
        )
        self.widgets.append(self.canvas.create_text(
            cx, 170,
            text=inst,
            font=("Comic Sans MS", 14),
            fill="yellow",
            justify="center",
            width=self.width - 80
        ))
        # Botón comenzar
        btn_rect = self.canvas.create_rectangle(
            cx - 110, cy + 100, cx + 110, cy + 150,
            fill="#6e6e6e", outline="white", width=3
        )
        self.widgets.append(btn_rect)
        btn_text = self.canvas.create_text(
            cx, cy + 125,
            text="COMENZAR",
            font=("Comic Sans MS", 18, "bold"),
            fill="white"
        )
        self.widgets.append(btn_text)
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._start_game())
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._start_game())

    def _start_game(self) -> None:
        # Reiniciar estado
        self.chips = 100
        self.bets.clear()
        self._draw_board()

    def _draw_board(self) -> None:
        """Dibuja la mesa de la ruleta y controles de juego."""
        self._clear_canvas()
        cx = self.width // 2
        # Fondo
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        # Mostrar fichas disponibles
        self.widgets.append(self.canvas.create_text(
            20, 20,
            anchor="nw",
            text=f"Fichas: {self.chips}",
            font=("Comic Sans MS", 16, "bold"),
            fill="white"
        ))
        # Dibujar celda para 0 (verde) encima del resto
        board_x = 90
        board_y = 80
        cell_w = 80
        cell_h = 40
        # 0 ocupa tres columnas
        rect = self.canvas.create_rectangle(
            board_x, board_y,
            board_x + cell_w * 3, board_y + cell_h,
            fill="#008000", outline="white", width=3
        )
        self.widgets.append(rect)
        zero_id = self.canvas.create_text(
            board_x + 1.5 * cell_w, board_y + cell_h / 2,
            text="0",
            font=("Comic Sans MS", 16, "bold"),
            fill="white"
        )
        self.widgets.append(zero_id)
        self.number_cells[rect] = 0
        # Filas de números 1-36
        self.number_cells.clear()
        # reiniciar overlay tokens
        self.overlay_tokens.clear()
        start_y = board_y + cell_h
        number = 1
        for row in range(12):
            for col in range(3):
                num = number
                x1 = board_x + col * cell_w
                y1 = start_y + row * cell_h
                x2 = x1 + cell_w
                y2 = y1 + cell_h
                color = "#E53935" if num in self.red_numbers else "#212121"
                rect_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color, outline="white", width=2
                )
                self.widgets.append(rect_id)
                txt_id = self.canvas.create_text(
                    x1 + cell_w / 2, y1 + cell_h / 2,
                    text=str(num),
                    font=("Comic Sans MS", 16, "bold"),
                    fill="white"
                )
                self.widgets.append(txt_id)
                self.number_cells[rect_id] = num
                # Vincular click para apostar
                self.canvas.tag_bind(rect_id, "<Button-1>", lambda e, n=num: self._place_bet(n))
                number += 1
        # Botón girar
        spin_rect = self.canvas.create_rectangle(
            cx - 120, self.height - 120, cx - 10, self.height - 70,
            fill="#6e6e6e", outline="white", width=3
        )
        self.widgets.append(spin_rect)
        spin_text = self.canvas.create_text(
            (cx - 120 + cx - 10) / 2, self.height - 95,
            text="GIRAR",
            font=("Comic Sans MS", 18, "bold"),
            fill="white"
        )
        self.widgets.append(spin_text)
        self.canvas.tag_bind(spin_rect, "<Button-1>", lambda e: self._spin())
        self.canvas.tag_bind(spin_text, "<Button-1>", lambda e: self._spin())
        # Botón retirarse
        retire_rect = self.canvas.create_rectangle(
            cx + 10, self.height - 120, cx + 120, self.height - 70,
            fill="#6e6e6e", outline="white", width=3
        )
        self.widgets.append(retire_rect)
        retire_text = self.canvas.create_text(
            (cx + 10 + cx + 120) / 2, self.height - 95,
            text="RETIRARSE",
            font=("Comic Sans MS", 18, "bold"),
            fill="white"
        )
        self.widgets.append(retire_text)
        self.canvas.tag_bind(retire_rect, "<Button-1>", lambda e: self._retire())
        self.canvas.tag_bind(retire_text, "<Button-1>", lambda e: self._retire())
        # Mostrar apuestas actuales sobre la mesa
        for num, bet in self.bets.items():
            self._draw_token_on_number(num, bet)

    def _draw_token_on_number(self, num: int, bet: int) -> None:
        """Dibuja una ficha pequeña en la casilla del número con la cantidad apostada."""
        # Encontrar celda del número
        board_x = 90
        board_y = 80
        cell_w = 80
        cell_h = 40
        if num == 0:
            x = board_x + (cell_w * 3) / 2
            y = board_y + cell_h / 2
        else:
            row = (num - 1) // 3
            col = (num - 1) % 3
            x = board_x + col * cell_w + cell_w / 2
            y = board_y + cell_h + row * cell_h + cell_h / 2
        # Dibujar círculo y texto
        token = self.canvas.create_oval(
            x - 12, y - 12, x + 12, y + 12,
            fill="#FFD700", outline="white", width=2
        )
        text_id = self.canvas.create_text(
            x, y,
            text=str(bet),
            font=("Comic Sans MS", 10, "bold"),
            fill="black"
        )
        # Guardar para futura limpieza
        self.overlay_tokens[num] = (token, text_id)

    def _place_bet(self, num: int) -> None:
        """Solicita al usuario una apuesta para el número seleccionado."""
        if self.chips <= 0:
            return
        # Preguntar por la apuesta
        try:
            bet = simpledialog.askinteger(
                "Apuesta",
                f"Cantidad a apostar en el {num}?\nFichas disponibles: {self.chips}",
                minvalue=1,
                maxvalue=self.chips,
                parent=self.window
            )
        except Exception:
            bet = None
        if bet is None:
            return
        # Añadir apuesta
        self.bets[num] = self.bets.get(num, 0) + bet
        self.chips -= bet
        # Redibujar mesa para mostrar ficha y fichas restantes
        self._draw_board()

    def _spin(self) -> None:
        """Ejecuta la ruleta, determina el número ganador y actualiza fichas."""
        if not self.bets:
            return  # no hay apuestas
        # Mostrar mensaje de giro
        self._clear_canvas()
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        cx, cy = self.width // 2, self.height // 2
        self.widgets.append(self.canvas.create_text(
            cx, cy - 30,
            text="Girando...",
            font=("Comic Sans MS", 28, "bold"),
            fill="white"
        ))
        self.widgets.append(self.canvas.create_text(
            cx, cy + 10,
            text="Suerte en la tirada",
            font=("Comic Sans MS", 16),
            fill="yellow"
        ))
        # Tras una pausa mostrar resultado
        self.window.after(2000, self._determine_spin_result)

    def _determine_spin_result(self) -> None:
        outcome = random.randint(0, 36)
        # Calcular ganancia
        payout = 0
        for num, bet in self.bets.items():
            if num == outcome:
                payout += bet * 36
        # Actualizar fichas
        self.chips += payout
        # Reset apuestas
        self.bets.clear()
        # Mostrar resultado
        self._clear_canvas()
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        cx, cy = self.width // 2, self.height // 2
        msg = f"Ha salido el {outcome}"
        self.widgets.append(self.canvas.create_text(
            cx, cy - 60,
            text=msg,
            font=("Comic Sans MS", 26, "bold"),
            fill="white"
        ))
        if payout > 0:
            gain_msg = f"¡Ganaste {payout} fichas!"
            color = "#4CAF50"
        else:
            gain_msg = "No acertaste ninguna apuesta"
            color = "#f44336"
        self.widgets.append(self.canvas.create_text(
            cx, cy - 20,
            text=gain_msg,
            font=("Comic Sans MS", 18, "bold"),
            fill=color
        ))
        self.widgets.append(self.canvas.create_text(
            cx, cy + 20,
            text=f"Fichas actuales: {self.chips}",
            font=("Comic Sans MS", 16),
            fill="yellow"
        ))
        # Botón siguiente
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 60, cx + 100, cy + 110,
            fill="#6e6e6e", outline="white", width=3
        )
        self.widgets.append(btn_rect)
        btn_text = self.canvas.create_text(
            cx, cy + 85,
            text="SIGUIENTE",
            font=("Comic Sans MS", 18, "bold"),
            fill="white"
        )
        self.widgets.append(btn_text)
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._after_result())
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._after_result())

    def _after_result(self) -> None:
        # Comprobar fin y redibujar tablero
        self._check_end()
        self._draw_board()

    def _retire(self) -> None:
        """El jugador decide retirarse. Verifica si alcanzó el objetivo."""
        # Finaliza el juego inmediatamente
        if self.chips >= self.target:
            self._game_over(True)
        else:
            self._game_over(False)

    def _check_end(self) -> None:
        """Comprueba si el juego debería terminar por objetivo alcanzado o fichas agotadas."""
        if self.chips >= self.target:
            self._game_over(True)
        elif self.chips <= 0:
            self._game_over(False)

    def _game_over(self, won: bool) -> None:
        if self.game_closed:
            return
        self.game_closed = True
        self._clear_canvas()
        cx, cy = self.width // 2, self.height // 2
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        result_text = "VICTORIA" if won else "Derrota"
        color = "#4CAF50" if won else "#f44336"
        self.widgets.append(self.canvas.create_text(
            cx, cy - 60,
            text=result_text,
            font=("Comic Sans MS", 36, "bold"),
            fill=color
        ))
        msg = "¡Has alcanzado las 500 fichas!" if won else "No alcanzaste el objetivo."
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text=msg,
            font=("Comic Sans MS", 18),
            fill="white"
        ))
        btn_rect = self.canvas.create_rectangle(
            cx - 110, cy + 60, cx + 110, cy + 110,
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
        # Asignar callback al cerrar
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