import tkinter as tk
import random

class PescaLoca:
    """Pesca Loca - Captura 3 peces consecutivos"""
    def __init__(self, parent_window, callback):
        self.callback = callback
        self.game_closed = False
        self.peces_capturados = 0
        self.peces_objetivo = 3
        self.pescando = False
        self.progreso = 0
        self.fish_pos = 50
        self.fish_speed = 2
        self.fish_direction = 1
        self.bar_pos = 50
        
        # Ventana
        self.window = tk.Toplevel()
        self.window.title("")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#1a1a1a")
        
        w, h = 400, 600
        self.canvas = tk.Canvas(self.window, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.window.update_idletasks()
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        self.window.geometry(f"{w}x{h}+{x}+{y}")
        
        # Arrastrable
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag)
        
        # Control con barra espaciadora
        self.window.bind("<space>", self._hold_bar)
        self.window.bind("<KeyRelease-space>", self._release_bar)
        
        self.window.focus_force()
        self.widgets = []
        self.holding = False
    
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
            cx, cy - 150,
            text="PESCA LOCA",
            font=("Arial", 28, "bold"),
            fill="white"))
        
        inst_text = """Captura 3 peces consecutivos

COMO JUGAR:
Manten ESPACIO presionado para subir la barra
Suelta para bajar
Manten al pez en el area verde

Si fallas uno, pierdes"""
        
        self.widgets.append(self.canvas.create_text(
            cx, cy - 30,
            text=inst_text,
            font=("Arial", 12),
            fill="yellow",
            justify="center"))
        
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 100, cx + 100, cy + 150,
            fill="#4CAF50", outline="white", width=3)
        self.widgets.append(btn_rect)
        
        btn_text = self.canvas.create_text(
            cx, cy + 125,
            text="COMENZAR",
            font=("Arial", 16, "bold"),
            fill="white")
        self.widgets.append(btn_text)
        
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._start_fishing())
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._start_fishing())
    
    def _start_fishing(self):
        self.pescando = True
        self.progreso = 0
        self.fish_pos = 50
        self.bar_pos = 50
        self.fish_speed = 2 + (self.peces_capturados * 0.5)  # Mas rapido cada vez
        self._fishing_loop()
    
    def _hold_bar(self, event):
        self.holding = True
    
    def _release_bar(self, event):
        self.holding = False
    
    def _fishing_loop(self):
        if not self.pescando or self.game_closed:
            return
        
        # Mover barra
        if self.holding:
            self.bar_pos = max(0, self.bar_pos - 3)
        else:
            self.bar_pos = min(100, self.bar_pos + 2)
        
        # Mover pez
        self.fish_pos += self.fish_speed * self.fish_direction
        if self.fish_pos <= 0 or self.fish_pos >= 100:
            self.fish_direction *= -1
        
        # Verificar si pez esta en area verde (barra)
        bar_top = self.bar_pos
        bar_bottom = self.bar_pos + 20
        
        if bar_top <= self.fish_pos <= bar_bottom:
            self.progreso += 2
            if self.progreso >= 100:
                # Pez capturado
                self.peces_capturados += 1
                self.pescando = False
                if self.peces_capturados >= self.peces_objetivo:
                    self._game_over(True)
                else:
                    self.window.after(500, self._start_fishing)
                return
        else:
            self.progreso = max(0, self.progreso - 1)
        
        self._draw_fishing()
        self.window.after(30, self._fishing_loop)
    
    def _draw_fishing(self):
        self._clear_widgets()
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx = w // 2
        
        # Titulo y contador
        self.widgets.append(self.canvas.create_text(
            cx, 40,
            text=f"PESCA LOCA - Peces: {self.peces_capturados}/3",
            font=("Arial", 18, "bold"),
            fill="white"))
        
        # Barra de progreso
        prog_y = 80
        prog_width = 300
        prog_x = cx - prog_width // 2
        
        self.widgets.append(self.canvas.create_rectangle(
            prog_x, prog_y, prog_x + prog_width, prog_y + 30,
            fill="#333", outline="white", width=2))
        
        self.widgets.append(self.canvas.create_rectangle(
            prog_x, prog_y, prog_x + (prog_width * self.progreso // 100), prog_y + 30,
            fill="#4CAF50", outline=""))
        
        self.widgets.append(self.canvas.create_text(
            cx, prog_y + 15,
            text=f"Progreso: {self.progreso}%",
            font=("Arial", 12, "bold"),
            fill="white"))
        
        # Area de pesca
        fishing_top = 150
        fishing_height = 350
        fishing_width = 80
        fishing_x = cx - fishing_width // 2
        
        # Fondo
        self.widgets.append(self.canvas.create_rectangle(
            fishing_x, fishing_top, fishing_x + fishing_width, fishing_top + fishing_height,
            fill="#1E3A5F", outline="white", width=3))
        
        # Barra verde (area de captura)
        bar_y = fishing_top + (fishing_height * self.bar_pos // 100)
        bar_height = fishing_height * 20 // 100
        
        self.widgets.append(self.canvas.create_rectangle(
            fishing_x, bar_y, fishing_x + fishing_width, bar_y + bar_height,
            fill="#4CAF50", outline="white", width=2))
        
        # Pez
        fish_y = fishing_top + (fishing_height * self.fish_pos // 100)
        self.widgets.append(self.canvas.create_oval(
            fishing_x + 20, fish_y - 10, fishing_x + 60, fish_y + 10,
            fill="#FF6B6B", outline="white", width=2))
        
        # Instruccion
        self.widgets.append(self.canvas.create_text(
            cx, fishing_top + fishing_height + 30,
            text="Manten ESPACIO para subir la barra",
            font=("Arial", 11),
            fill="#FFD700"))
    
    def _game_over(self, won):
        self.pescando = False
        self._clear_widgets()
        
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        
        result_text = "VICTORIA" if won else "Derrota"
        result_color = "#4CAF50" if won else "#f44336"
        
        self.widgets.append(self.canvas.create_text(
            cx, cy - 80,
            text=result_text,
            font=("Arial", 36, "bold"),
            fill=result_color))
        
        self.widgets.append(self.canvas.create_text(
            cx, cy - 20,
            text=f"Peces capturados: {self.peces_capturados}/3",
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
            self.pescando = False
            try:
                self.window.destroy()
            except:
                pass
            try:
                self.callback('closed')
            except:
                pass
