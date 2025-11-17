import tkinter as tk
import random
import json
import os

try:
    # Cargar Pillow para fondos aleatorios y ajuste de brillo
    from PIL import Image, ImageTk, ImageEnhance  # type: ignore
    HAS_PIL = True
except Exception:
    HAS_PIL = False

class MathQuiz:
    """Quiz Matemtico - Versin mejorada"""
    def __init__(self, parent_window, callback):
        self.callback = callback
        self.questions = self.load_questions()
        self.selected = random.sample(self.questions, min(10, len(self.questions)))
        self.current_index = 0
        self.correct_count = 0
        self.game_closed = False
        self.answer_given = False
        
        # Ventana flotante sin bordes
        self.window = tk.Toplevel()
        self.window.title("")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#1a1a1a")
        
        # Canvas
        self.canvas = tk.Canvas(self.window, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Geometra
        w, h = 700, 500
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

        # Fondo aleatorio: selecciona una imagen que comience por "fran" y oscurece
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
                    img = Image.open(path)
                    try:
                        img = img.convert("RGBA")
                    except Exception:
                        pass
                    img = img.resize((700, 500), Image.Resampling.LANCZOS)
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
    
    def load_questions(self):
        """Carga preguntas del JSON"""
        try:
            base_path = os.path.dirname(os.path.dirname(__file__))
            json_path = os.path.join(base_path, "data", "math_questions.json")
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return [
                {"question": "5 + 3 = ?", "options": ["7", "8", "9", "6"], "answer": "8"},
                {"question": "10 - 4 = ?", "options": ["5", "6", "7", "8"], "answer": "6"},
                {"question": "3 * 4 = ?", "options": ["10", "11", "12", "13"], "answer": "12"},
            ]
    
    def run(self):
        """Inicia el juego con instrucciones"""
        self.window.after(100, self._show_instructions)
    
    def _show_instructions(self):
        """Pantalla de instrucciones mejorada"""
        self._clear_widgets()
        
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        
        # Dibujar fondo si está disponible
        if getattr(self, 'bg_photo', None):
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)

        # Título
        self.widgets.append(self.canvas.create_text(
            cx, cy - 160,
            text="QUIZ MATEMATICO",
            font=("Arial", 28, "bold"),
            fill="white"))
        
        # Instrucciones centradas
        inst_text = """10 preguntas matematicas
6 segundos por pregunta
Necesitas 5 correctas para ganar"""
        
        self.widgets.append(self.canvas.create_text(
            cx, cy - 30,
            text=inst_text,
            font=("Arial", 13),
            fill="yellow",
            justify="center"))
        
        # Botn comenzar
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 120, cx + 100, cy + 170,
            fill="#6e6e6e", outline="white", width=3)
        self.widgets.append(btn_rect)
        
        btn_text = self.canvas.create_text(
            cx, cy + 145,
            text="COMENZAR",
            font=("Arial", 16, "bold"),
            fill="white")
        self.widgets.append(btn_text)
        
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._show_next_question())
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._show_next_question())
    
    def _show_next_question(self):
        """Muestra la siguiente pregunta con diseo mejorado"""
        if self.game_closed or self.current_index >= len(self.selected):
            self._finish_game()
            return
        
        self._clear_widgets()
        # Dibujar fondo
        if getattr(self, 'bg_photo', None):
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        self.answer_given = False
        
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        
        question_data = self.selected[self.current_index]
        
        # Contador de preguntas
        counter_text = f"Pregunta {self.current_index + 1} de {len(self.selected)}"
        self.widgets.append(self.canvas.create_text(
            cx, 40,
            text=counter_text,
            font=("Arial", 16, "bold"),
            fill="white"))
        
        # Timer visual
        self.timer_label = self.canvas.create_text(
            cx, 80,
            text=" 6s",
            font=("Arial", 18, "bold"),
            fill="#FFD700")
        self.widgets.append(self.timer_label)
        
        # Pregunta grande y destacada
        self.widgets.append(self.canvas.create_text(
            cx, cy - 80,
            text=question_data["question"],
            font=("Arial", 42, "bold"),
            fill="#2196F3"))
        
        # Opciones en grid 2x2
        options = question_data["options"]
        positions = [
            (cx - 140, cy + 50),
            (cx + 140, cy + 50),
            (cx - 140, cy + 140),
            (cx + 140, cy + 140)
        ]
        
        colors = ["#FF6B6B", "#4ECDC4", "#FFE66D", "#A8E6CF"]
        
        for i, (opt, pos) in enumerate(zip(options, positions)):
            is_correct = (opt == question_data["answer"])
            
            btn_rect = self.canvas.create_rectangle(
                pos[0] - 100, pos[1] - 35,
                pos[0] + 100, pos[1] + 35,
                fill=colors[i],
                outline="white", width=3)
            self.widgets.append(btn_rect)
            
            btn_text = self.canvas.create_text(
                pos[0], pos[1],
                text=opt,
                font=("Arial", 22, "bold"),
                fill="white")
            self.widgets.append(btn_text)
            
            self.canvas.tag_bind(btn_rect, "<Button-1>",
                               lambda e, correct=is_correct: self._check_answer(correct))
            self.canvas.tag_bind(btn_text, "<Button-1>",
                               lambda e, correct=is_correct: self._check_answer(correct))
        
        # Iniciar timer
        self._start_timer(6.0)
    
    def _start_timer(self, time_left):
        """Timer con iconos visuales"""
        if self.game_closed or self.answer_given:
            return
        
        if time_left <= 0:
            self.answer_given = True
            self.current_index += 1
            self.canvas.after(500, self._show_next_question)
            return
        
        try:
            if time_left > 3:
                icon = ""
                color = "#FFD700"
            elif time_left > 1:
                icon = ""
                color = "#FF9800"
            else:
                icon = ""
                color = "#FF0000"
            
            self.canvas.itemconfig(self.timer_label, 
                                 text=f"{icon} {int(time_left)}s",
                                 fill=color)
        except:
            pass
        
        self.canvas.after(100, lambda: self._start_timer(time_left - 0.1))
    
    def _check_answer(self, is_correct):
        """Verifica respuesta"""
        if self.answer_given:
            return
        
        self.answer_given = True
        
        if is_correct:
            self.correct_count += 1
        
        self.current_index += 1
        self.canvas.after(200, self._show_next_question)
    
    def _finish_game(self):
        """Pantalla de resultados mejorada"""
        if self.game_closed:
            return
        
        self._clear_widgets()
        # Dibujar fondo en la pantalla final si está disponible
        if getattr(self, 'bg_photo', None):
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        
        won = self.correct_count >= 5
        
        # Emoji segn resultado
        emoji = "" if won else ""
        result_text = "VICTORIA!" if won else "Derrota"
        result_color = "#4CAF50" if won else "#f44336"
        
        # Resultado con emoji
        self.widgets.append(self.canvas.create_text(
            cx, cy - 100,
            text=f"{emoji} {result_text} {emoji}",
            font=("Arial", 36, "bold"),
            fill=result_color))
        
        # Estadsticas
        percentage = int((self.correct_count / len(self.selected)) * 100)
        stats_text = f"Aciertos: {self.correct_count} / {len(self.selected)}\n({percentage}%)"
        
        self.widgets.append(self.canvas.create_text(
            cx, cy - 10,
            text=stats_text,
            font=("Arial", 18),
            fill="white",
            justify="center"))
        
        # Mensaje motivacional
        if won:
            msg = "Excelente trabajo"
        elif self.correct_count >= 3:
            msg = "Casi lo logras"
        else:
            msg = "Sigue practicando"
        
        self.widgets.append(self.canvas.create_text(
            cx, cy + 40,
            text=msg,
            font=("Arial", 14),
            fill="#FFD700"))
        
        # Botón continuar gris
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 100, cx + 100, cy + 150,
            fill="#6e6e6e", outline="white", width=3)
        self.widgets.append(btn_rect)
        
        btn_text = self.canvas.create_text(
            cx, cy + 125,
            text="CONTINUAR",
            font=("Arial", 16, "bold"),
            fill="white")
        self.widgets.append(btn_text)
        
        self.canvas.tag_bind(btn_rect, "<Button-1>",
                           lambda e: self._close_result(won))
        self.canvas.tag_bind(btn_text, "<Button-1>",
                           lambda e: self._close_result(won))
    
    def _close_result(self, won):
        """Cierra resultado"""
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
        for widget_id in self.widgets:
            try:
                self.canvas.delete(widget_id)
            except:
                pass
        self.widgets.clear()
    
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
