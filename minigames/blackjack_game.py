"""
BlackjackGame - Minijuego de blackjack (veintiuno) para MiniPet.

El objetivo es vencer al crupier (IA) en una serie de manos de
blackjack. El jugador y el crupier reciben cartas de una baraja
estándar. El jugador puede pedir cartas ("PEDIR") o plantarse
("PLANTARME"). El crupier pedirá cartas hasta alcanzar 17 puntos.
Si el jugador supera 21 puntos, pierde automáticamente. Si el
crupier supera 21 o el jugador tiene un valor de mano superior,
gana la mano.

El juego continúa hasta que el jugador gane 3 manos o pierda 3
manos, lo que ocurra primero. Las instrucciones y botones usan
Comic Sans y se integran con el resto del proyecto.
"""

import tkinter as tk
import random
import os

try:
    from PIL import Image, ImageTk, ImageEnhance  # type: ignore
    HAS_PIL = True
except Exception:
    HAS_PIL = False


class BlackjackGame:
    """Minijuego de blackjack contra la IA."""

    def __init__(self, parent_window: tk.Tk, callback) -> None:
        self.callback = callback
        self.game_closed = False
        # Dimensiones
        self.width = 650
        self.height = 550
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
        self.deck = []
        self.player_hand = []
        self.dealer_hand = []
        self.rounds_won = 0
        self.rounds_lost = 0
        self.current_round = 0
        self.max_rounds = 5
        # Widgets guardados para borrar
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
            cx, cy - 140,
            text="BLACKJACK",
            font=("Comic Sans MS", 32, "bold"),
            fill="white"
        ))
        inst_text = (
            "Gana 3 de 5 manos contra el crupier.\n"
            "Pide cartas con PEDIR o planta tu mano con PLANTARME.\n"
            "Si superas 21 puntos pierdes la mano."
        )
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text=inst_text,
            font=("Comic Sans MS", 14),
            fill="yellow",
            justify="center"
        ))
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 100, cx + 100, cy + 150,
            fill="#6e6e6e", outline="white", width=3
        )
        self.widgets.append(btn_rect)
        btn_text = self.canvas.create_text(
            cx, cy + 125,
            text="COMENZAR",
            font=("Comic Sans MS", 16, "bold"),
            fill="white"
        )
        self.widgets.append(btn_text)
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._start_game())
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._start_game())

    def _start_game(self) -> None:
        self.rounds_won = 0
        self.rounds_lost = 0
        self.current_round = 0
        self._start_round()

    def _start_round(self) -> None:
        # Comprobar condición final
        if self.rounds_won >= 3 or self.rounds_lost >= 3 or self.current_round >= self.max_rounds:
            # Juego terminado
            won = self.rounds_won > self.rounds_lost
            self._game_over(won)
            return
        # Reiniciar manos y baraja
        self.current_round += 1
        self.deck = self._create_deck()
        random.shuffle(self.deck)
        self.player_hand = []
        self.dealer_hand = []
        # Repartir dos cartas a cada uno
        self.player_hand.append(self.deck.pop())
        self.dealer_hand.append(self.deck.pop())
        self.player_hand.append(self.deck.pop())
        self.dealer_hand.append(self.deck.pop())
        # Mostrar ronda
        self._draw_table(player_turn=True)

    @staticmethod
    def _create_deck():
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        suits = ['♠', '♥', '♦', '♣']
        return [(r, s) for r in ranks for s in suits]

    @staticmethod
    def _hand_value(hand):
        """Calcula el valor de una mano según las reglas de blackjack."""
        value = 0
        aces = 0
        for rank, _ in hand:
            if rank in ['J', 'Q', 'K']:
                value += 10
            elif rank == 'A':
                value += 11
                aces += 1
            else:
                value += int(rank)
        # Ajustar ases
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def _draw_table(self, player_turn: bool) -> None:
        # Limpia y dibuja el fondo y manos
        self._clear_canvas()
        cx = self.width // 2
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        # Títulos de ronda
        self.widgets.append(self.canvas.create_text(
            cx, 20,
            text=f"Mano {self.current_round}/{self.max_rounds} - Tus victorias: {self.rounds_won}  Derrotas: {self.rounds_lost}",
            font=("Comic Sans MS", 12, "bold"),
            fill="white"
        ))
        # Dibujar manos
        # Dealer
        self.widgets.append(self.canvas.create_text(
            100, 60,
            text="Crupier:",
            font=("Comic Sans MS", 14, "bold"),
            fill="white",
            anchor="nw"
        ))
        dx = 0
        for idx, card in enumerate(self.dealer_hand):
            card_text = f"{card[0]}{card[1]}" if (not player_turn or idx != 0) else "??"
            rect = self.canvas.create_rectangle(
                100 + dx, 90, 100 + dx + 50, 130,
                fill="#4E342E", outline="white"
            )
            self.widgets.append(rect)
            txt = self.canvas.create_text(
                100 + dx + 25, 110,
                text=card_text,
                font=("Comic Sans MS", 16, "bold"),
                fill="white"
            )
            self.widgets.append(txt)
            dx += 60
        # Player
        self.widgets.append(self.canvas.create_text(
            100, 180,
            text="Jugador:",
            font=("Comic Sans MS", 14, "bold"),
            fill="white",
            anchor="nw"
        ))
        dx = 0
        for card in self.player_hand:
            rect = self.canvas.create_rectangle(
                100 + dx, 210, 100 + dx + 50, 250,
                fill="#1E88E5", outline="white"
            )
            self.widgets.append(rect)
            txt = self.canvas.create_text(
                100 + dx + 25, 230,
                text=f"{card[0]}{card[1]}",
                font=("Comic Sans MS", 16, "bold"),
                fill="white"
            )
            self.widgets.append(txt)
            dx += 60
        # Mostrar valores de manos si no es turno del jugador
        if not player_turn:
            dealer_value = self._hand_value(self.dealer_hand)
            player_value = self._hand_value(self.player_hand)
            self.widgets.append(self.canvas.create_text(
                100, 140,
                text=f"Puntos crupier: {dealer_value}",
                font=("Comic Sans MS", 14),
                fill="yellow",
                anchor="nw"
            ))
            self.widgets.append(self.canvas.create_text(
                100, 270,
                text=f"Tus puntos: {player_value}",
                font=("Comic Sans MS", 14),
                fill="yellow",
                anchor="nw"
            ))
        else:
            # Solo mostrar tus puntos durante tu turno
            player_value = self._hand_value(self.player_hand)
            self.widgets.append(self.canvas.create_text(
                100, 270,
                text=f"Tus puntos: {player_value}",
                font=("Comic Sans MS", 14),
                fill="yellow",
                anchor="nw"
            ))
        # Botones según el turno
        if player_turn:
            # Botones PEDIR y PLANTARME
            # Botones PEDIR y PLANTARME con mayor ancho para que quepan los textos.
            # Se calcula un ancho amplio (160 px) y se distribuye de forma simétrica
            # alrededor del centro de la pantalla.  Esto evita que la palabra
            # "PLANTARME" se corte visualmente.
            button_width = 160
            # Botón PEDIR
            pedir_rect = self.canvas.create_rectangle(
                cx - button_width - 10, self.height - 100,
                cx - 10, self.height - 60,
                fill="#6e6e6e", outline="white", width=3
            )
            self.widgets.append(pedir_rect)
            pedir_text = self.canvas.create_text(
                cx - button_width // 2 - 10, self.height - 80,
                text="PEDIR",
                font=("Comic Sans MS", 16, "bold"),
                fill="white"
            )
            self.widgets.append(pedir_text)
            # Botón PLANTARME
            plantar_rect = self.canvas.create_rectangle(
                cx + 10, self.height - 100,
                cx + button_width + 10, self.height - 60,
                fill="#6e6e6e", outline="white", width=3
            )
            self.widgets.append(plantar_rect)
            plantar_text = self.canvas.create_text(
                cx + button_width // 2 + 10, self.height - 80,
                text="PLANTARME",
                font=("Comic Sans MS", 16, "bold"),
                fill="white"
            )
            self.widgets.append(plantar_text)
            # Enlaces
            self.canvas.tag_bind(pedir_rect, "<Button-1>", lambda e: self._player_hit())
            self.canvas.tag_bind(pedir_text, "<Button-1>", lambda e: self._player_hit())
            self.canvas.tag_bind(plantar_rect, "<Button-1>", lambda e: self._player_stand())
            self.canvas.tag_bind(plantar_text, "<Button-1>", lambda e: self._player_stand())
        else:
            # Botón para siguiente ronda
            btn_rect = self.canvas.create_rectangle(
                cx - 100, self.height - 100, cx + 100, self.height - 60,
                fill="#6e6e6e", outline="white", width=3
            )
            self.widgets.append(btn_rect)
            text = "SIGUIENTE" if (self.rounds_won < 3 and self.rounds_lost < 3 and self.current_round < self.max_rounds) else "FINALIZAR"
            btn_text = self.canvas.create_text(
                cx, self.height - 80,
                text=text,
                font=("Comic Sans MS", 16, "bold"),
                fill="white"
            )
            self.widgets.append(btn_text)
            self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._start_round())
            self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._start_round())

    def _player_hit(self) -> None:
        # Añadir carta a jugador
        self.player_hand.append(self.deck.pop())
        # Si se pasa de 21 pierde
        if self._hand_value(self.player_hand) > 21:
            self.rounds_lost += 1
            self._draw_table(player_turn=False)
        else:
            # Continuar turno del jugador
            self._draw_table(player_turn=True)

    def _player_stand(self) -> None:
        """El jugador se planta. El crupier revelará sus cartas lentamente."""
        # Iniciar turno del crupier con animación lenta
        self._dealer_turn()

    def _dealer_turn(self) -> None:
        """Añade cartas al crupier una a una con pequeñas pausas para crear tensión."""
        # Si el crupier necesita otra carta, tomarla y volver tras una pausa
        if self._hand_value(self.dealer_hand) < 17:
            if self.deck:
                self.dealer_hand.append(self.deck.pop())
            # Dibujar mesa actual mostrando cartas del crupier
            self._draw_table(player_turn=False)
            # Esperar 600 ms antes de tomar otra carta
            self.window.after(600, self._dealer_turn)
            return
        # Cuando el crupier se planta, determinar el resultado tras una breve pausa
        self.window.after(500, self._determine_round_result)

    def _determine_round_result(self) -> None:
        """Calcula quién gana la ronda y actualiza contadores."""
        player_score = self._hand_value(self.player_hand)
        dealer_score = self._hand_value(self.dealer_hand)
        if dealer_score > 21 or player_score > dealer_score:
            self.rounds_won += 1
        elif player_score < dealer_score:
            self.rounds_lost += 1
        else:
            self.rounds_lost += 1  # empate cuenta como derrota
        # Redibujar mesa con resultado final
        self._draw_table(player_turn=False)

    def _game_over(self, won: bool) -> None:
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
        msg = "Has ganado al crupier" if won else "El crupier ha ganado"
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