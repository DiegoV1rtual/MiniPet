import tkinter as tk
import random
import time

class ClickRapido:
    """Click Rapido - Acierta 8 de 10 botones"""
    def __init__(self, parent_window, callback):
        self.callback = callback
        self.game_closed = False
        self.rounds = 10
        self.current_round = 0
        self.aciertos = 0
        self.game_running = False
        
        self.window = tk.Toplevel()
        self.window.title("")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#1a1a1a")
        
        w, h = 600, 500
        self.canvas = tk.Canvas(self.window, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.window.update_idletasks()
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        self.window.geometry(f"{w}x{h}+{x}+{y}")
        
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
        self._clear_widgets()
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        
        self.widgets.append(self.canvas.create_text(
            cx, cy - 100,
            text="CLICK RAPIDO",
            font=("Arial", 28, "bold"),
            fill="white"))
        
        inst_text = """Haz click en el boton antes de 2 segundos
10 rondas - Necesitas 8 aciertos para ganar"""
        
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text=inst_text,
            font=("Arial", 13),
            fill="yellow",
            justify="center"))
        
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 80, cx + 100, cy + 130,
            fill="#4CAF50", outline="white", width=3)
        self.widgets.append(btn_rect)
        
        btn_text = self.canvas.create_text(
            cx, cy + 105,
            text="COMENZAR",
            font=("Arial", 16, "bold"),
            fill="white")
        self.widgets.append(btn_text)
        
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._next_round())
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._next_round())
    
    def _next_round(self):
        if self.current_round >= self.rounds:
            self._game_over()
            return
        
        self._clear_widgets()
        self.game_running = True
        self.clicked = False
        
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        
        self.widgets.append(self.canvas.create_text(
            w // 2, 40,
            text=f"Ronda {self.current_round + 1}/10 - Aciertos: {self.aciertos}",
            font=("Arial", 16, "bold"),
            fill="white"))
        
        # Botón en posición aleatoria
        btn_w, btn_h = 120, 60
        btn_x = random.randint(100, w - 100 - btn_w)
        btn_y = random.randint(100, h - 100 - btn_h)
        
        btn_rect = self.canvas.create_rectangle(
            btn_x, btn_y, btn_x + btn_w, btn_y + btn_h,
            fill="#FF6B6B", outline="white", width=3)
        self.widgets.append(btn_rect)
        
        btn_text = self.canvas.create_text(
            btn_x + btn_w // 2, btn_y + btn_h // 2,
            text="CLICK!",
            font=("Arial", 18, "bold"),
            fill="white")
        self.widgets.append(btn_text)
        
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._on_click())
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._on_click())
        
        self.timeout_time = time.time() + 2.0
        self._check_timeout()
    
    def _on_click(self):
        if not self.game_running or self.clicked:
            return
        self.clicked = True
        self.aciertos += 1
        self.current_round += 1
        self.window.after(300, self._next_round)
    
    def _check_timeout(self):
        if not self.game_running or self.clicked:
            return
        
        if time.time() >= self.timeout_time:
            self.current_round += 1
            self.window.after(500, self._next_round)
        else:
            self.window.after(50, self._check_timeout)
    
    def _game_over(self):
        self.game_running = False
        self._clear_widgets()
        
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        
        won = self.aciertos >= 8
        result_text = "VICTORIA" if won else "Derrota"
        result_color = "#4CAF50" if won else "#f44336"
        
        self.widgets.append(self.canvas.create_text(
            cx, cy - 60,
            text=result_text,
            font=("Arial", 36, "bold"),
            fill=result_color))
        
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text=f"Aciertos: {self.aciertos}/10",
            font=("Arial", 16),
            fill="white"))
        
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 60, cx + 100, cy + 110,
            fill="#2196F3", outline="white", width=3)
        self.widgets.append(btn_rect)
        
        btn_text = self.canvas.create_text(
            cx, cy + 85,
            text="CONTINUAR",
            font=("Arial", 16, "bold"),
            fill="white")
        self.widgets.append(btn_text)
        
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._close_result(won))
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._close_result(won))
    
    def _close_result(self, won):
        if not self.game_closed:
            self.game_closed = True
            try:
                self.window.destroy()
            except:
                pass
            try:
                self.callback('won' if won else 'lost')
            except:
                pass
    
    def _clear_widgets(self):
        for wid in self.widgets:
            try:
                self.canvas.delete(wid)
            except:
                pass
        self.widgets.clear()
    
    def force_close(self):
        if not self.game_closed:
            self.game_closed = True
            self.game_running = False
            try:
                self.window.destroy()
            except:
                pass
            try:
                self.callback('closed')
            except:
                pass
