import tkinter as tk
import random
import os

try:
    from PIL import Image, ImageTk, ImageEnhance  # type: ignore
    HAS_PIL = True
except Exception:
    HAS_PIL = False

class SnakeGame:
    """Juego de Snake - Come 15 frutas para ganar"""
    def __init__(self, parent_window, callback):
        self.callback = callback
        self.game_closed = False
        
        # Configuración del juego
        self.cell_size = 20
        self.grid_width = 25
        self.grid_height = 20
        self.snake = [(12, 10), (11, 10), (10, 10)]  # Posición inicial
        self.direction = (1, 0)  # Derecha
        self.next_direction = (1, 0)
        self.fruit = None
        self.score = 0
        self.target_score = 15  # Ganar con 15 frutas
        self.game_over = False
        self.game_running = False
        
        # Ventana flotante
        self.window = tk.Toplevel()
        self.window.title("")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#1a1a1a")
        
        # Canvas
        canvas_width = self.grid_width * self.cell_size + 40
        canvas_height = self.grid_height * self.cell_size + 140
        
        self.canvas = tk.Canvas(self.window, bg="#1a1a1a", 
                               highlightthickness=0,
                               width=canvas_width, height=canvas_height)
        self.canvas.pack(fill="both", expand=True)
        
        # Centrar
        self.window.update_idletasks()
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        x = (screen_w - canvas_width) // 2
        y = (screen_h - canvas_height) // 2
        self.window.geometry(f"{canvas_width}x{canvas_height}+{x}+{y}")
        
        # Arrastrable
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag)
        
        # Controles
        self.window.bind("<Up>", lambda e: self._change_direction((0, -1)))
        self.window.bind("<Down>", lambda e: self._change_direction((0, 1)))
        self.window.bind("<Left>", lambda e: self._change_direction((-1, 0)))
        self.window.bind("<Right>", lambda e: self._change_direction((1, 0)))
        self.window.bind("<w>", lambda e: self._change_direction((0, -1)))
        self.window.bind("<s>", lambda e: self._change_direction((0, 1)))
        self.window.bind("<a>", lambda e: self._change_direction((-1, 0)))
        self.window.bind("<d>", lambda e: self._change_direction((1, 0)))
        
        self.window.focus_force()
        self.widgets = []

        # Fondo aleatorio
        self.bg_photo = None
        if HAS_PIL:
            bg_dir = os.path.join("assets", "custom")
            try:
                fran_files = [f for f in os.listdir(bg_dir) if f.lower().startswith("fran") and f.lower().endswith((".png", ".gif"))]
            except Exception:
                fran_files = []
            if fran_files:
                chosen = random.choice(fran_files)
                path = os.path.join(bg_dir, chosen)
                try:
                    # redimensionar fondo a tamaño del canvas
                    img = Image.open(path)
                    try:
                        img = img.convert("RGBA")
                    except Exception:
                        pass
                    img = img.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(0.7)
                    self.bg_photo = ImageTk.PhotoImage(img)
                except Exception:
                    self.bg_photo = None
    
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
        """Instrucciones cortas"""
        self._clear_widgets()
        # Fondo para instrucciones
        if getattr(self, 'bg_photo', None):
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        
        # Título
        self.widgets.append(self.canvas.create_text(
            cx, cy - 120,
            text="SNAKE",
            font=("Arial", 28, "bold"),
            fill="white"))
        
        # Instrucciones
        inst_text = """Come 15 frutas para ganar
No choques con las paredes ni contigo mismo

CONTROLES:
Flechas o WASD para moverte"""
        
        self.widgets.append(self.canvas.create_text(
            cx, cy - 20,
            text=inst_text,
            font=("Arial", 13),
            fill="yellow",
            justify="center"))
        
        # Botón comenzar gris
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 80, cx + 100, cy + 130,
            fill="#6e6e6e", outline="white", width=3)
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
        """Inicia el juego"""
        self._clear_widgets()
        self.game_running = True
        self._spawn_fruit()
        self._draw_game()
        self._game_loop()
    
    def _spawn_fruit(self):
        """Genera fruta en posición aleatoria"""
        while True:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in self.snake:
                self.fruit = (x, y)
                break
    
    def _change_direction(self, new_direction):
        """Cambia dirección (no permite 180 grados)"""
        if not self.game_running or self.game_over:
            return
        
        # No permitir dirección opuesta
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.next_direction = new_direction
    
    def _game_loop(self):
        """Loop principal del juego"""
        if not self.game_running or self.game_over or self.game_closed:
            return
        
        self.direction = self.next_direction
        
        # Nueva posición de la cabeza
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        # Verificar colisiones
        if (new_head[0] < 0 or new_head[0] >= self.grid_width or
            new_head[1] < 0 or new_head[1] >= self.grid_height or
            new_head in self.snake):
            self._game_over_screen(False)
            return
        
        # Mover serpiente
        self.snake.insert(0, new_head)
        
        # Verificar si comió fruta
        if new_head == self.fruit:
            self.score += 1
            if self.score >= self.target_score:
                self._game_over_screen(True)
                return
            self._spawn_fruit()
        else:
            self.snake.pop()
        
        self._draw_game()
        self.window.after(120, self._game_loop)
    
    def _draw_game(self):
        """Dibuja el estado del juego"""
        self._clear_widgets()
        # Dibujar fondo si está disponible
        if getattr(self, 'bg_photo', None):
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        offset_x = (w - self.grid_width * self.cell_size) // 2
        offset_y = 100
        
        # Título y puntuación
        self.widgets.append(self.canvas.create_text(
            w // 2, 40,
            text=f"SNAKE - Frutas: {self.score}/{self.target_score}",
            font=("Arial", 18, "bold"),
            fill="white"))
        
        # Borde del área de juego
        self.widgets.append(self.canvas.create_rectangle(
            offset_x - 2, offset_y - 2,
            offset_x + self.grid_width * self.cell_size + 2,
            offset_y + self.grid_height * self.cell_size + 2,
            outline="white", width=3))
        
        # Dibujar serpiente
        for i, (x, y) in enumerate(self.snake):
            px = offset_x + x * self.cell_size
            py = offset_y + y * self.cell_size
            
            color = "#4CAF50" if i == 0 else "#66BB6A"  # Cabeza más oscura
            
            self.widgets.append(self.canvas.create_rectangle(
                px, py, px + self.cell_size, py + self.cell_size,
                fill=color, outline="white", width=1))
        
        # Dibujar fruta
        if self.fruit:
            fx = offset_x + self.fruit[0] * self.cell_size
            fy = offset_y + self.fruit[1] * self.cell_size
            
            self.widgets.append(self.canvas.create_oval(
                fx + 2, fy + 2,
                fx + self.cell_size - 2, fy + self.cell_size - 2,
                fill="#FF0000", outline="white", width=2))
    
    def _game_over_screen(self, won):
        """Pantalla de fin de juego"""
        self.game_over = True
        self.game_running = False
        self._clear_widgets()
        # Fondo en pantalla final
        if getattr(self, 'bg_photo', None):
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        
        result_text = "VICTORIA" if won else "Derrota"
        result_color = "#4CAF50" if won else "#f44336"
        
        self.widgets.append(self.canvas.create_text(
            cx, cy - 80,
            text=result_text,
            font=("Arial", 36, "bold"),
            fill=result_color))
        
        stats = f"Frutas comidas: {self.score}/{self.target_score}"
        self.widgets.append(self.canvas.create_text(
            cx, cy - 20,
            text=stats,
            font=("Arial", 16),
            fill="white"))
        
        msg = "Objetivo completado" if won else "Intentalo de nuevo"
        self.widgets.append(self.canvas.create_text(
            cx, cy + 20,
            text=msg,
            font=("Arial", 14),
            fill="#FFD700"))
        
        # Botón continuar gris
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 80, cx + 100, cy + 130,
            fill="#6e6e6e", outline="white", width=3)
        self.widgets.append(btn_rect)
        
        btn_text = self.canvas.create_text(
            cx, cy + 105,
            text="CONTINUAR",
            font=("Arial", 16, "bold"),
            fill="white")
        self.widgets.append(btn_text)
        
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._close_result(won))
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._close_result(won))
    
    def _close_result(self, won):
        """Cierra el juego"""
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
        """Limpia widgets"""
        for wid in self.widgets:
            try:
                self.canvas.delete(wid)
            except:
                pass
        self.widgets.clear()
    
    def force_close(self):
        """Cierre forzado"""
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
