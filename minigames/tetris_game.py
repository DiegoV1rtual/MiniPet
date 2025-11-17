import tkinter as tk
import random
import os

try:
    from PIL import Image, ImageTk, ImageEnhance  # type: ignore
    HAS_PIL = True
except Exception:
    HAS_PIL = False

class TetrisGame:
    """Tetris - Llega a 500 puntos para ganar"""
    def __init__(self, parent_window, callback):
        self.callback = callback
        self.game_closed = False
        
        # Configuración
        self.cell_size = 25
        self.grid_width = 10
        self.grid_height = 20
        self.score = 0
        # Puntaje objetivo: se gana al alcanzar 2000 puntos
        self.target_score = 2000
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.game_running = False
        
        # Grid de juego
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # Piezas de Tetris
        self.shapes = {
            'I': [[1,1,1,1]],
            'O': [[1,1],[1,1]],
            'T': [[0,1,0],[1,1,1]],
            'S': [[0,1,1],[1,1,0]],
            'Z': [[1,1,0],[0,1,1]],
            'J': [[1,0,0],[1,1,1]],
            'L': [[0,0,1],[1,1,1]]
        }
        
        self.colors = {
            'I': '#00FFFF',
            'O': '#FFFF00',
            'T': '#FF00FF',
            'S': '#00FF00',
            'Z': '#FF0000',
            'J': '#0000FF',
            'L': '#FFA500'
        }
        
        self.current_piece = None
        self.current_shape = None
        self.current_color = None
        self.current_x = 0
        self.current_y = 0
        
        # Ventana
        self.window = tk.Toplevel()
        self.window.title("")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#1a1a1a")
        
        canvas_width = self.grid_width * self.cell_size + 220
        canvas_height = self.grid_height * self.cell_size + 100
        
        self.canvas = tk.Canvas(self.window, bg="#1a1a1a",
                               highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
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
        self.window.bind("<Left>", lambda e: self._move(-1, 0))
        self.window.bind("<Right>", lambda e: self._move(1, 0))
        self.window.bind("<Down>", lambda e: self._move(0, 1))
        self.window.bind("<Up>", lambda e: self._rotate())
        self.window.bind("<space>", lambda e: self._hard_drop())
        
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
                    # redimensionar a tamaño del canvas
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
        self._clear_widgets()
        # Fondo en pantalla de instrucciones
        if getattr(self, 'bg_photo', None):
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        
        self.widgets.append(self.canvas.create_text(
            cx, cy - 100,
            text="TETRIS",
            font=("Arial", 28, "bold"),
            fill="white"))
        
        inst_text = """Llega a 2000 puntos para ganar

CONTROLES:
Flechas: Mover y rotar
Espacio: Caida rapida

PUNTUACION:
1 linea = 100 puntos
2 lineas = 300 puntos
3 lineas = 500 puntos
4 lineas = 800 puntos"""
        
        self.widgets.append(self.canvas.create_text(
            cx, cy + 20,
            text=inst_text,
            font=("Arial", 12),
            fill="yellow",
            justify="center"))
        
        # Botón gris
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 150, cx + 100, cy + 200,
            fill="#6e6e6e", outline="white", width=3)
        self.widgets.append(btn_rect)
        
        btn_text = self.canvas.create_text(
            cx, cy + 175,
            text="COMENZAR",
            font=("Arial", 16, "bold"),
            fill="white")
        self.widgets.append(btn_text)
        
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._start_game())
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._start_game())
    
    def _start_game(self):
        self._clear_widgets()
        self.game_running = True
        self._spawn_piece()
        self._game_loop()
    
    def _spawn_piece(self):
        shape_name = random.choice(list(self.shapes.keys()))
        self.current_shape = self.shapes[shape_name]
        self.current_color = self.colors[shape_name]
        self.current_x = self.grid_width // 2 - len(self.current_shape[0]) // 2
        self.current_y = 0
        
        if self._check_collision(self.current_x, self.current_y):
            self.game_over = True
            self._game_over_screen()
    
    def _check_collision(self, x, y):
        for row_idx, row in enumerate(self.current_shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    new_x = x + col_idx
                    new_y = y + row_idx
                    if (new_x < 0 or new_x >= self.grid_width or
                        new_y >= self.grid_height or
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return True
        return False
    
    def _move(self, dx, dy):
        if not self.game_running or self.game_over:
            return
        new_x = self.current_x + dx
        new_y = self.current_y + dy
        if not self._check_collision(new_x, new_y):
            self.current_x = new_x
            self.current_y = new_y
            self._draw_game()
    
    def _rotate(self):
        if not self.game_running or self.game_over:
            return
        rotated = list(zip(*self.current_shape[::-1]))
        old_shape = self.current_shape
        self.current_shape = [list(row) for row in rotated]
        if self._check_collision(self.current_x, self.current_y):
            self.current_shape = old_shape
        else:
            self._draw_game()
    
    def _hard_drop(self):
        if not self.game_running or self.game_over:
            return
        while not self._check_collision(self.current_x, self.current_y + 1):
            self.current_y += 1
        self._lock_piece()
    
    def _lock_piece(self):
        for row_idx, row in enumerate(self.current_shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    grid_y = self.current_y + row_idx
                    grid_x = self.current_x + col_idx
                    if grid_y >= 0:
                        self.grid[grid_y][grid_x] = self.current_color
        
        self._clear_lines()
        self._spawn_piece()
    
    def _clear_lines(self):
        lines_to_clear = []
        for y in range(self.grid_height):
            if all(self.grid[y]):
                lines_to_clear.append(y)
        
        if lines_to_clear:
            for y in lines_to_clear:
                del self.grid[y]
                self.grid.insert(0, [0 for _ in range(self.grid_width)])
            
            self.lines_cleared += len(lines_to_clear)
            points = [0, 100, 300, 500, 800]
            self.score += points[len(lines_to_clear)]
            
            if self.score >= self.target_score:
                self.game_over = True
                self.game_running = False
                self._game_over_screen()
    
    def _game_loop(self):
        if not self.game_running or self.game_over or self.game_closed:
            return
        
        if not self._check_collision(self.current_x, self.current_y + 1):
            self.current_y += 1
        else:
            self._lock_piece()
        
        self._draw_game()
        delay = max(200, 800 - self.level * 50)
        self.window.after(delay, self._game_loop)
    
    def _draw_game(self):
        self._clear_widgets()
        # Fondo durante el juego
        if getattr(self, 'bg_photo', None):
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        offset_x = 20
        offset_y = 80
        
        # Título y stats
        self.widgets.append(self.canvas.create_text(
            200, 30,
            text=f"TETRIS - Puntos: {self.score}/{self.target_score}",
            font=("Arial", 16, "bold"),
            fill="white"))
        
        self.widgets.append(self.canvas.create_text(
            200, 55,
            text=f"Lineas: {self.lines_cleared}",
            font=("Arial", 12),
            fill="#FFD700"))
        
        # Borde del grid
        self.widgets.append(self.canvas.create_rectangle(
            offset_x - 2, offset_y - 2,
            offset_x + self.grid_width * self.cell_size + 2,
            offset_y + self.grid_height * self.cell_size + 2,
            outline="white", width=3))
        
        # Dibujar grid
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x]:
                    px = offset_x + x * self.cell_size
                    py = offset_y + y * self.cell_size
                    self.widgets.append(self.canvas.create_rectangle(
                        px, py, px + self.cell_size, py + self.cell_size,
                        fill=self.grid[y][x], outline="black", width=1))
        
        # Dibujar pieza actual
        for row_idx, row in enumerate(self.current_shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    px = offset_x + (self.current_x + col_idx) * self.cell_size
                    py = offset_y + (self.current_y + row_idx) * self.cell_size
                    if py >= offset_y:
                        self.widgets.append(self.canvas.create_rectangle(
                            px, py, px + self.cell_size, py + self.cell_size,
                            fill=self.current_color, outline="white", width=2))
    
    def _game_over_screen(self):
        self._clear_widgets()
        # Fondo en pantalla final
        if getattr(self, 'bg_photo', None):
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        
        won = self.score >= self.target_score
        result_text = "VICTORIA" if won else "Derrota"
        result_color = "#4CAF50" if won else "#f44336"
        
        self.widgets.append(self.canvas.create_text(
            cx, cy - 80,
            text=result_text,
            font=("Arial", 36, "bold"),
            fill=result_color))
        
        self.widgets.append(self.canvas.create_text(
            cx, cy - 20,
            text=f"Puntuacion final: {self.score}",
            font=("Arial", 16),
            fill="white"))
        
        self.widgets.append(self.canvas.create_text(
            cx, cy + 10,
            text=f"Lineas completadas: {self.lines_cleared}",
            font=("Arial", 14),
            fill="#FFD700"))
        
        # Botón gris
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 70, cx + 100, cy + 120,
            fill="#6e6e6e", outline="white", width=3)
        self.widgets.append(btn_rect)
        
        btn_text = self.canvas.create_text(
            cx, cy + 95,
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
