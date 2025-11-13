import tkinter as tk
import math
import random

class Roulette:
    def __init__(self, parent_window, sectors, callback, title="Ruleta"):
        """Ruleta con diseño renovado - Ventana flotante"""
        self.callback = callback
        self.sectors = sectors[:]
        self.n = len(self.sectors)
        self.title = title
        
        # Ventana flotante sin bordes
        self.window = tk.Toplevel()
        self.window.title("")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#1a1a1a")
        
        # Canvas
        width = 700
        height = 600
        self.canvas = tk.Canvas(self.window, bg="#1a1a1a", 
                               highlightthickness=0, width=width, height=height)
        self.canvas.pack(fill="both", expand=True)
        
        # Geometría centrada
        self.window.update_idletasks()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Arrastrable
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag)
        
        self.size = 350
        self.radius = 140
        self.angle = 0
        self.v = 0
        self.dec = 0
        self.spinning = False
        
        self.center_x = width // 2
        self.center_y = height // 2 - 20
        
        self.widgets = []
        self.draw_roulette(0)
    
    def _start_drag(self, event):
        self._drag_data = {"x": event.x, "y": event.y}
    
    def _drag(self, event):
        if hasattr(self, '_drag_data'):
            x = self.window.winfo_x() + event.x - self._drag_data["x"]
            y = self.window.winfo_y() + event.y - self._drag_data["y"]
            self.window.geometry(f"+{x}+{y}")
    
    def draw_roulette(self, rotation_angle):
        """Dibuja la ruleta con diseño mejorado"""
        # Limpiar widgets anteriores
        for widget_id in self.widgets:
            try:
                self.canvas.delete(widget_id)
            except:
                pass
        self.widgets.clear()
        
        # Título elegante
        title_id = self.canvas.create_text(
            self.center_x, 50,
            text=self.title, 
            font=("Arial", 26, "bold"),
            fill="white"
        )
        self.widgets.append(title_id)
        
        # Subtítulo
        if not self.spinning:
            subtitle_id = self.canvas.create_text(
                self.center_x, 85,
                text="Haz click en GIRAR para tu recompensa",
                font=("Arial", 11),
                fill="#aaa"
            )
            self.widgets.append(subtitle_id)
        
        cx = cy = self.center_x, self.center_y
        per_sector = 360.0 / self.n
        
        # Colores vibrantes
        colors = ["#FF6B6B", "#4ECDC4", "#FFE66D", "#A8E6CF", "#FF8B94", "#C7CEEA", "#95E1D3"]
        
        for i, (label, payload) in enumerate(self.sectors):
            start_angle = (i * per_sector - rotation_angle) % 360
            
            # Crear polígono del sector
            points = [self.center_x, self.center_y]
            for step in range(0, 37):
                angle_rad = math.radians(start_angle + step * (per_sector / 36))
                x = self.center_x + math.cos(angle_rad) * self.radius
                y = self.center_y + math.sin(angle_rad) * self.radius
                points.extend([x, y])
            
            color = colors[i % len(colors)]
            sector_id = self.canvas.create_polygon(
                points, fill=color, outline="white", width=3
            )
            self.widgets.append(sector_id)
            
            # Texto del sector
            mid_angle = math.radians(start_angle + per_sector / 2)
            text_distance = self.radius * 0.65
            tx = self.center_x + math.cos(mid_angle) * text_distance
            ty = self.center_y + math.sin(mid_angle) * text_distance
            
            text_id = self.canvas.create_text(
                tx, ty, text=label, 
                font=("Arial", 11, "bold"),
                fill="white", width=90, justify="center"
            )
            self.widgets.append(text_id)
        
        # Círculo central dorado
        circle_id = self.canvas.create_oval(
            self.center_x - 25, self.center_y - 25,
            self.center_x + 25, self.center_y + 25,
            fill="#FFD700", outline="white", width=3
        )
        self.widgets.append(circle_id)
        
        # Flecha indicador (más grande)
        arrow_points = [
            self.center_x - 18, self.center_y - self.radius - 25,
            self.center_x + 18, self.center_y - self.radius - 25,
            self.center_x, self.center_y - self.radius + 8
        ]
        arrow_id = self.canvas.create_polygon(
            arrow_points, fill="#FF0000", outline="white", width=3
        )
        self.widgets.append(arrow_id)
        
        # Botón girar (si no está girando)
        if not self.spinning:
            btn_rect = self.canvas.create_rectangle(
                self.center_x - 100, self.center_y + self.radius + 50,
                self.center_x + 100, self.center_y + self.radius + 110,
                fill="#4CAF50", outline="white", width=4
            )
            self.widgets.append(btn_rect)
            
            btn_text = self.canvas.create_text(
                self.center_x, self.center_y + self.radius + 80,
                text="GIRAR",
                font=("Arial", 20, "bold"),
                fill="white"
            )
            self.widgets.append(btn_text)
            
            # Bind click (solo en el botón, no en toda la ventana)
            self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self.start())
            self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self.start())
    
    def start(self):
        """Inicia el giro"""
        if self.spinning:
            return
        
        self.spinning = True
        self.v = random.uniform(22, 38)
        self.dec = random.uniform(0.16, 0.26)
        self._animate()
    
    def _animate(self):
        """Animación del giro"""
        if self.v > 0.1:
            self.angle += self.v
            self.v -= self.dec
            
            if self.v < 0:
                self.v = 0
            
            self.draw_roulette(self.angle)
            self.canvas.after(16, self._animate)
        else:
            # Giro terminado
            self.spinning = False
            idx = self._get_winning_sector()
            label, payload = self.sectors[idx]
            
            # Mostrar resultado antes de cerrar
            self._show_result(label)
            self.canvas.after(1500, lambda: self._finish(payload))
    
    def _show_result(self, label):
        """Muestra el resultado ganador"""
        result_bg = self.canvas.create_rectangle(
            self.center_x - 150, self.center_y - 60,
            self.center_x + 150, self.center_y + 60,
            fill="#1a1a1a", outline="white", width=3
        )
        self.widgets.append(result_bg)
        
        result_text = self.canvas.create_text(
            self.center_x, self.center_y - 20,
            text="RESULTADO:",
            font=("Arial", 14, "bold"),
            fill="#FFD700"
        )
        self.widgets.append(result_text)
        
        winner_text = self.canvas.create_text(
            self.center_x, self.center_y + 20,
            text=label,
            font=("Arial", 16, "bold"),
            fill="white",
            width=280,
            justify="center"
        )
        self.widgets.append(winner_text)
    
    def _get_winning_sector(self):
        """Determina el sector ganador"""
        normalized = self.angle % 360
        # La flecha de la ruleta está situada en la parte superior apuntando hacia abajo (270°).
        # Ajustamos el ángulo para que el cálculo del sector ganador coincida con la flecha.
        pointer_angle = (270 - normalized) % 360
        per_sector = 360.0 / self.n
        sector_index = int(pointer_angle / per_sector) % self.n
        return sector_index
    
    def _finish(self, payload):
        """Finaliza y limpia"""
        self.close()
        try:
            self.callback(payload)
        except:
            pass
    
    def close(self):
        """Cierra la ruleta"""
        try:
            self.window.destroy()
        except:
            pass
