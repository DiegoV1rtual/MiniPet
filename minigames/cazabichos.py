import tkinter as tk
import random
import time

class Cazabichos:
    """Cazabichos - Acierta 15 bichos en 30 segundos"""
    def __init__(self, parent_window, callback):
        self.callback = callback
        self.game_closed = False
        self.aciertos = 0
        self.objetivo = 15
        self.tiempo_limite = 30
        self.game_running = False
        self.start_time = None
        
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
        
        self.window.focus_force()
        self.widgets = []
        self.current_bug = None
    
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
            text="CAZABICHOS",
            font=("Arial", 28, "bold"),
            fill="white"))
        
        inst_text = """Haz click en 15 bichos antes de 30 segundos
Los bichos aparecen y desaparecen rapido
Apunta bien"""
        
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
        
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._start_game())
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._start_game())
    
    def _start_game(self):
        self.game_running = True
        self.start_time = time.time()
        self._spawn_bug()
        self._game_loop()
    
    def _spawn_bug(self):
        if not self.game_running:
            return
        
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        bug_x = random.randint(80, w - 80)
        bug_y = random.randint(120, h - 80)
        
        # Dibujar bicho
        bug = self.canvas.create_oval(
            bug_x - 20, bug_y - 20, bug_x + 20, bug_y + 20,
            fill="#FF0000", outline="white", width=2)
        
        self.current_bug = bug
        self.canvas.tag_bind(bug, "<Button-1>", lambda e: self._hit_bug())
        
        # Desaparece despues de 0.8 segundos
        self.window.after(800, self._remove_bug)
    
    def _hit_bug(self):
        if self.current_bug and self.game_running:
            self.aciertos += 1
            try:
                self.canvas.delete(self.current_bug)
            except:
                pass
            self.current_bug = None
            if self.aciertos >= self.objetivo:
                self.game_running = False
                self._game_over(True)
            else:
                self._spawn_bug()
    
    def _remove_bug(self):
        if self.current_bug and self.game_running:
            try:
                self.canvas.delete(self.current_bug)
            except:
                pass
            self.current_bug = None
            self._spawn_bug()
    
    def _game_loop(self):
        if not self.game_running or self.game_closed:
            return
        
        elapsed = time.time() - self.start_time
        remaining = self.tiempo_limite - elapsed
        
        if remaining <= 0:
            self.game_running = False
            self._game_over(self.aciertos >= self.objetivo)
            return
        
        self._draw_ui(int(remaining))
        self.window.after(100, self._game_loop)
    
    def _draw_ui(self, remaining):
        # Actualizar solo el texto superior
        for wid in self.widgets:
            try:
                self.canvas.delete(wid)
            except:
                pass
        self.widgets.clear()
        
        w = self.canvas.winfo_width()
        self.widgets.append(self.canvas.create_text(
            w // 2, 40,
            text=f"CAZABICHOS - Aciertos: {self.aciertos}/{self.objetivo}",
            font=("Arial", 16, "bold"),
            fill="white"))
        
        self.widgets.append(self.canvas.create_text(
            w // 2, 70,
            text=f"Tiempo: {remaining}s",
            font=("Arial", 14),
            fill="#FFD700" if remaining > 10 else "#FF0000"))
    
    def _game_over(self, won):
        self._clear_widgets()
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        
        result_text = "VICTORIA" if won else "Derrota"
        result_color = "#4CAF50" if won else "#f44336"
        
        self.widgets.append(self.canvas.create_text(
            cx, cy - 60,
            text=result_text,
            font=("Arial", 36, "bold"),
            fill=result_color))
        
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text=f"Bichos cazados: {self.aciertos}/{self.objetivo}",
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
        if self.current_bug:
            try:
                self.canvas.delete(self.current_bug)
            except:
                pass
    
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
