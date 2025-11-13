import tkinter as tk
import random

class MemoryGame:
    """Juego de Memoria (Simon Says) - Versin mejorada"""
    def __init__(self, parent_window, callback):
        self.callback = callback
        self.sequence = []
        self.player_sequence = []
        self.level = 1
        self.max_level = 10
        self.colors = ["ROJO", "AZUL", "VERDE", "AMARILLO"]
        self.color_hex = {
            "ROJO": "#f44336",
            "AZUL": "#2196F3",
            "VERDE": "#4CAF50",
            "AMARILLO": "#FFC107"
        }
        self.game_closed = False
        self.waiting_player = False
        self.button_rects = {}
        
        # Ventana flotante sin bordes
        self.window = tk.Toplevel()
        self.window.title("")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#1a1a1a")
        
        # Canvas
        self.canvas = tk.Canvas(self.window, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Geometra centrada
        w, h = 700, 550
        self.window.update_idletasks()
        
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        
        self.window.geometry(f"{w}x{h}+{x}+{y}")
        
        # Arrastrable
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag)
        
        self.widgets = []
    
    def _start_drag(self, event):
        self._drag_data = {"x": event.x, "y": event.y}
    
    def _drag(self, event):
        if hasattr(self, '_drag_data'):
            x = self.window.winfo_x() + event.x - self._drag_data["x"]
            y = self.window.winfo_y() + event.y - self._drag_data["y"]
            self.window.geometry(f"+{x}+{y}")
    
    def run(self):
        self.window.after(100, self._show_instructions)
    
    def _show_instructions(self):
        """Pantalla de instrucciones mejorada"""
        self._clear_widgets()
        
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        
        # Ttulo
        self.widgets.append(self.canvas.create_text(
            cx, cy - 180,
            text="JUEGO DE MEMORIA",
            font=("Arial", 28, "bold"),
            fill="white"))
        
        # Subttulo
        self.widgets.append(self.canvas.create_text(
            cx, cy - 130,
            text="(Simon Says)",
            font=("Arial", 16),
            fill="#FFD700"))
        
        # Instrucciones detalladas
        inst_text = """Memoriza la secuencia de colores
Repitela haciendo click
Llega al nivel 10 para ganar"""
        
        self.widgets.append(self.canvas.create_text(
            cx, cy - 10,
            text=inst_text,
            font=("Arial", 13),
            fill="yellow",
            justify="center"))
        
        # Vista previa de colores
        preview_colors = [
            (cx - 120, cy + 120, self.color_hex["ROJO"], "ROJO"),
            (cx - 40, cy + 120, self.color_hex["AZUL"], "AZUL"),
            (cx + 40, cy + 120, self.color_hex["VERDE"], "VERDE"),
            (cx + 120, cy + 120, self.color_hex["AMARILLO"], "AMAR.")
        ]
        
        for px, py, color, label in preview_colors:
            self.widgets.append(self.canvas.create_oval(
                px - 25, py - 25, px + 25, py + 25,
                fill=color, outline="white", width=2))
            self.widgets.append(self.canvas.create_text(
                px, py + 40,
                text=label,
                font=("Arial", 9),
                fill="white"))
        
        # Botn comenzar
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 190, cx + 100, cy + 240,
            fill="#4CAF50", outline="white", width=3)
        self.widgets.append(btn_rect)
        
        btn_text = self.canvas.create_text(
            cx, cy + 215,
            text="COMENZAR",
            font=("Arial", 16, "bold"),
            fill="white")
        self.widgets.append(btn_text)
        
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._next_level())
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._next_level())
    
    def _next_level(self):
        """Genera siguiente nivel"""
        if self.game_closed:
            return
        
        self.player_sequence = []
        self.sequence.append(random.choice(self.colors))
        self.waiting_player = False
        
        self._draw_game_screen()
        self.canvas.after(1000, lambda: self._show_sequence(0))
    
    def _draw_game_screen(self):
        """Pantalla de juego mejorada"""
        self._clear_widgets()
        
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        
        # Header con nivel
        self.widgets.append(self.canvas.create_text(
            cx, 50,
            text=f"NIVEL {self.level} / {self.max_level}",
            font=("Arial", 22, "bold"),
            fill="white"))
        
        # Barra de progreso
        bar_width = 400
        bar_x = cx - bar_width // 2
        progress = (self.level / self.max_level) * bar_width
        
        # Fondo barra
        self.widgets.append(self.canvas.create_rectangle(
            bar_x, 90, bar_x + bar_width, 110,
            fill="#333", outline="white", width=2))
        
        # Progreso
        self.widgets.append(self.canvas.create_rectangle(
            bar_x, 90, bar_x + progress, 110,
            fill="#4CAF50", outline=""))
        
        # Status con icono
        self.status_id = self.canvas.create_text(
            cx, 140,
            text=" Observa...",
            font=("Arial", 16, "bold"),
            fill="#FFD700")
        self.widgets.append(self.status_id)
        
        # Contador de secuencia
        self.sequence_counter = self.canvas.create_text(
            cx, 180,
            text=f"Longitud: {len(self.sequence)}",
            font=("Arial", 14),
            fill="#aaa")
        self.widgets.append(self.sequence_counter)
        
        # Botones grandes de colores
        positions = [
            (cx - 110, cy + 20, "ROJO"),
            (cx + 110, cy + 20, "AZUL"),
            (cx - 110, cy + 160, "VERDE"),
            (cx + 110, cy + 160, "AMARILLO")
        ]
        
        self.button_rects = {}
        
        for px, py, color in positions:
            # Botn circular grande
            radius = 65
            rect = self.canvas.create_oval(
                px - radius, py - radius,
                px + radius, py + radius,
                fill=self.color_hex[color],
                outline="white",
                width=4)
            self.widgets.append(rect)
            
            # Label del color
            text = self.canvas.create_text(
                px, py,
                text=color,
                font=("Arial", 16, "bold"),
                fill="white")
            self.widgets.append(text)
            
            self.button_rects[color] = (rect, text)
            
            self.canvas.tag_bind(rect, "<Button-1>",
                               lambda e, c=color: self._player_click(c))
            self.canvas.tag_bind(text, "<Button-1>",
                               lambda e, c=color: self._player_click(c))
    
    def _show_sequence(self, index):
        """Muestra la secuencia con efectos"""
        if self.game_closed or index >= len(self.sequence):
            if index >= len(self.sequence):
                try:
                    self.canvas.itemconfig(self.status_id,
                                         text=" Tu turno",
                                         fill="#4CAF50")
                except:
                    pass
                self.waiting_player = True
            return
        
        color = self.sequence[index]
        self._flash_button(color)
        self.canvas.after(700, lambda: self._show_sequence(index + 1))
    
    def _flash_button(self, color):
        """Efecto de parpadeo mejorado"""
        if self.game_closed or color not in self.button_rects:
            return
        
        rect, text = self.button_rects[color]
        original_color = self.color_hex[color]
        
        try:
            # Flash blanco
            self.canvas.itemconfig(rect, fill="white")
            self.canvas.itemconfig(text, fill=original_color)
            
            # Volver a color original
            self.canvas.after(250, lambda: self.canvas.itemconfig(rect, fill=original_color))
            self.canvas.after(250, lambda: self.canvas.itemconfig(text, fill="white"))
        except:
            pass
    
    def _player_click(self, color):
        """Maneja click del jugador"""
        if not self.waiting_player or self.game_closed:
            return
        
        self._flash_button(color)
        self.player_sequence.append(color)
        
        # Verificar si es correcto
        if self.player_sequence[-1] != self.sequence[len(self.player_sequence) - 1]:
            self._game_over(False)
            return
        
        # Complet la secuencia correctamente
        if len(self.player_sequence) == len(self.sequence):
            self.level += 1
            if self.level > self.max_level:
                self._game_over(True)
            else:
                self.waiting_player = False
                try:
                    self.canvas.itemconfig(self.status_id,
                                         text=" Correcto",
                                         fill="#4CAF50")
                except:
                    pass
                self.canvas.after(1500, self._next_level)
    
    def _game_over(self, won):
        """Pantalla final mejorada"""
        if self.game_closed:
            return
        
        self._clear_widgets()
        
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        
        # Resultado con emoji
        if won:
            emoji = ""
            result_text = "VICTORIA"
            result_color = "#4CAF50"
            msg = "Memoria perfecta\nCompletaste los 10 niveles"
        else:
            emoji = ""
            result_text = "Derrota"
            result_color = "#f44336"
            msg = f"Llegaste al nivel {self.level}\nSigue practicando tu memoria"
        
        self.widgets.append(self.canvas.create_text(
            cx, cy - 120,
            text=f"{emoji} {result_text} {emoji}",
            font=("Arial", 36, "bold"),
            fill=result_color))
        
        self.widgets.append(self.canvas.create_text(
            cx, cy - 40,
            text=msg,
            font=("Arial", 16),
            fill="white",
            justify="center"))
        
        # Estadsticas
        sequence_length = len(self.sequence) - 1 if not won else len(self.sequence)
        stats = f"Secuencia ms larga: {sequence_length} colores"
        
        self.widgets.append(self.canvas.create_text(
            cx, cy + 20,
            text=stats,
            font=("Arial", 14),
            fill="#FFD700"))
        
        # Botn continuar
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 80, cx + 100, cy + 130,
            fill="#2196F3", outline="white", width=3)
        self.widgets.append(btn_rect)
        
        btn_text = self.canvas.create_text(
            cx, cy + 105,
            text="CONTINUAR",
            font=("Arial", 16, "bold"),
            fill="white")
        self.widgets.append(btn_text)
        
        self.canvas.tag_bind(btn_rect, "<Button-1>",
                           lambda e: self._close_result(won))
        self.canvas.tag_bind(btn_text, "<Button-1>",
                           lambda e: self._close_result(won))
    
    def _close_result(self, won):
        """Cierra el juego"""
        if not self.game_closed:
            self.game_closed = True
            self._clear_widgets()
            try:
                self.window.destroy()
            except:
                pass
            try:
                self.callback('won' if won else 'lost')
            except:
                pass
    
    def _clear_widgets(self):
        """Limpia widgets"""
        for wid in self.widgets:
            try:
                self.canvas.delete(wid)
            except:
                pass
        self.widgets.clear()
        self.button_rects.clear()
    
    def force_close(self):
        """Cierre forzado"""
        if not self.game_closed:
            self.game_closed = True
            self._clear_widgets()
            try:
                self.window.destroy()
            except:
                pass
            try:
                self.callback('closed')
            except:
                pass
