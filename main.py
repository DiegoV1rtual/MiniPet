import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import time
import threading
import os
import json
import math
from modules.config import *
from modules.roulette import Roulette
from minigames.math_quiz import MathQuiz
from minigames.memory_game import MemoryGame
from minigames.stroop_game import StroopGame
from minigames.snake_game import SnakeGame
from minigames.tetris_game import TetrisGame
# Nuevos minijuegos añadidos
# Se ha eliminado ReactionGame. Ahora se incluye un minijuego de pesca.
from minigames.typing_game import TypingGame
from minigames.catch_game import CatchGame
# Nuevos minijuegos solicitados
from minigames.lightning_dodge import LightningDodge
from minigames.disarm_bomb import DisarmBomb
from minigames.cross_road import CrossRoad
from minigames.express_race import ExpressRace
# El minijuego JumpClimb (Salta y sube) se ha eliminado a petición del usuario.
# from minigames.jump_climb import JumpClimb
# Nuevos minijuegos añadidos
# Importación de SpaceInvaderGame eliminada porque el juego
# no funciona correctamente y ha sido retirado del proyecto.
# from minigames.space_invader import SpaceInvaderGame
# Importamos solo los minijuegos permitidos.  Se eliminan AsteroidsGame, CasinoRouletteGame y PairsGame.
from minigames.blackjack_game import BlackjackGame

# Nota: El minijuego "Click Rapido" se ha eliminado a petición del usuario.
# Por lo tanto, no se importa ni se incluye en la lista de juegos disponibles.
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except:
    HAS_PIL = False
    print("Pillow no instalado - usando sprite simple")

class PetOverlay:
    """MASCOTA FLOTANTE que se sobrepone a TODO el sistema"""
    def __init__(self, parent_app):
        self.app = parent_app
        self.window = tk.Toplevel()
        self.window.title("")
        
        # CRÍTICO: Ventana transparente y SIEMPRE SOBRE TODO
        self.window.attributes("-topmost", True)
        self.window.attributes("-transparentcolor", "black")
        self.window.overrideredirect(True)
        
        # Obtener tamaño de pantalla
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Tamaño del sprite
        self.size = 150
        
        # Posición inicial (centro de pantalla)
        x = screen_width // 2 - self.size // 2
        y = screen_height // 2 - self.size // 2
        self.window.geometry(f"{self.size}x{self.size}+{x}+{y}")
        
        # Canvas transparente
        self.canvas = tk.Canvas(self.window, bg="black", 
                               highlightthickness=0, width=self.size, height=self.size)
        self.canvas.pack()
        
        # Cargar sprite
        self.load_sprite()
        
        # Hacer arrastrable
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag)
        
        self.screen_width = screen_width
        self.screen_height = screen_height
    
    def load_sprite(self, state="normal"):
        """Carga sprite según el estado emocional"""
        self.canvas.delete("all")
        
        sprite_path = os.path.join("assets", "sprites", f"{state}.png")
        
        if HAS_PIL and os.path.exists(sprite_path):
            try:
                img = Image.open(sprite_path)
                img = img.resize((self.size, self.size), Image.Resampling.LANCZOS)
                self.sprite_img = ImageTk.PhotoImage(img)
                self.sprite_id = self.canvas.create_image(
                    self.size//2, self.size//2, image=self.sprite_img
                )
                return
            except Exception as e:
                print(f"Error cargando {sprite_path}: {e}")
        
        self._draw_simple_sprite(state)
    
    def _draw_simple_sprite(self, state):
        """Dibuja sprite simple según el estado - SIN EMOTICONOS"""
        center = self.size // 2
        
        states_config = {
            "normal": {"color": "#4CAF50", "text": "NORMAL", "text_color": "white"},
            "hambriento": {"color": "#FF6B6B", "text": "HAMBRE", "text_color": "white"},
            "muy_hambriento": {"color": "#D32F2F", "text": "MUERO\nHAMBRE", "text_color": "white"},
            "gordo": {"color": "#FF9800", "text": "GORDO", "text_color": "white"},
            "sucio": {"color": "#8B4513", "text": "SUCIO", "text_color": "white"},
            "muy_sucio": {"color": "#5D4037", "text": "MUY\nSUCIO", "text_color": "white"},
            "cansado": {"color": "#9E9E9E", "text": "CANSADO", "text_color": "white"},
            "agotado": {"color": "#616161", "text": "AGOTADO", "text_color": "white"},
            "feliz": {"color": "#FFD700", "text": "FELIZ", "text_color": "black"},
            "muy_feliz": {"color": "#FFC107", "text": "SUPER\nFELIZ", "text_color": "black"},
            "triste": {"color": "#2196F3", "text": "TRISTE", "text_color": "white"},
            "muy_triste": {"color": "#1565C0", "text": "MUY\nTRISTE", "text_color": "white"},
            "durmiendo": {"color": "#7E57C2", "text": "Zzz...", "text_color": "white"},
            "enfermo": {"color": "#66BB6A", "text": "ENFERMO", "text_color": "white"},
            "muriendo": {"color": "#424242", "text": "MURIENDO", "text_color": "white"},
            # NUEVOS SPRITES DE MUERTE
            "muerte_obesidad": {"color": "#FF6600", "text": "OBESO\nMUERTE", "text_color": "white"},
            "muerte_tristeza": {"color": "#000080", "text": "SUICIDIO\nTRISTEZA", "text_color": "white"},
            "muerte_sueno": {"color": "#404040", "text": "MUERTE\nAGOTAMIENTO", "text_color": "white"},
            "muerte_hambre": {"color": "#8B0000", "text": "MUERTE\nHAMBRE", "text_color": "white"},
            "muerte_higiene": {"color": "#3D2817", "text": "MUERTE\nENFERMEDAD", "text_color": "white"}
        }
        
        config = states_config.get(state, states_config["normal"])
        
        self.canvas.create_rectangle(
            10, 10, self.size-10, self.size-10,
            fill=config["color"], outline="white", width=4
        )
        
        self.canvas.create_text(
            center, center,
            text=config["text"],
            font=("Arial", 14, "bold"),
            fill=config["text_color"],
            justify="center"
        )
    
    def update_state(self, state):
        """Actualiza el sprite según el estado"""
        self.load_sprite(state)
    
    def _start_drag(self, event):
        self._drag_data = {"x": event.x, "y": event.y}
    
    def _drag(self, event):
        """Arrastra la mascota"""
        if hasattr(self, '_drag_data'):
            x = self.window.winfo_x() + event.x - self._drag_data["x"]
            y = self.window.winfo_y() + event.y - self._drag_data["y"]
            self.window.geometry(f"{self.size}x{self.size}+{x}+{y}")
    
    def move_to(self, x, y):
        """Mueve la mascota a posición específica"""
        x = max(0, min(x, self.screen_width - self.size))
        y = max(0, min(y, self.screen_height - self.size))
        self.window.geometry(f"{self.size}x{self.size}+{x}+{y}")
    
    def get_position(self):
        """Obtiene posición actual"""
        return self.window.winfo_x(), self.window.winfo_y()
    
    def smooth_move(self):
        """Mueve la mascota SUAVEMENTE a posición aleatoria"""
        target_x = random.randint(0, self.screen_width - self.size)
        target_y = random.randint(0, self.screen_height - self.size)
        self._animate_move_to(target_x, target_y)
    
    def _animate_move_to(self, target_x, target_y):
        """Anima el movimiento SUAVEMENTE usando interpolación"""
        current_x = self.window.winfo_x()
        current_y = self.window.winfo_y()
        
        steps = PET_MOVE_STEPS
        
        def ease_in_out(t):
            """Función de suavizado (ease-in-out)"""
            return t * t * (3.0 - 2.0 * t)
        
        for i in range(steps + 1):
            t = i / steps
            eased_t = ease_in_out(t)
            
            new_x = current_x + (target_x - current_x) * eased_t
            new_y = current_y + (target_y - current_y) * eased_t
            
            self.window.geometry(f"{self.size}x{self.size}+{int(new_x)}+{int(new_y)}")
            self.window.update()
            time.sleep(PET_MOVE_DELAY)

class MiniDiego:
    def __init__(self, root):
        self.root = root
        self.root.title("Cuidame Rebollo Rebollito !")
        self.root.geometry("450x400")
        self.root.configure(bg="#2d2d2d")
        
        if ALWAYS_ON_TOP:
            self.root.attributes("-topmost", True)
        
        # Sin cerrar con X
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Estados
        self.hambre = 50
        self.sueno = 50
        self.higiene = 50
        self.felicidad = 50
        self.alive = True
        self.paused = False
        self.sleeping = False
        self.sleep_start_time = None
        
        # Contador de 24 horas (1 día).  Adaptamos la duración del juego para que se pueda
        # completar en un día, en lugar de las 168 horas (7 días) originales.
        self.game_start_time = time.time()
        self.total_time = 24 * 3600
        self.pause_time_used = 0
        self.pause_start_time = None
        # Guardamos la fecha del último día en que se reseteó la pausa (YYYY-MM-DD)
        self.pause_reset_date = time.strftime("%Y-%m-%d")
        
        # Crear mascota flotante
        self.pet_overlay = PetOverlay(self)
        
        # Minigames
        self.current_game = None
        self.minigame_popup = None
        
        # Crear panel de control
        self.create_control_panel()
        
        # Iniciar threads
        threading.Thread(target=self._decay_loop, daemon=True).start()
        threading.Thread(target=self._pet_movement_loop, daemon=True).start()
        threading.Thread(target=self._minigame_event_loop, daemon=True).start()
        threading.Thread(target=self._sleep_monitor_loop, daemon=True).start()
    
    def create_control_panel(self):
        """Panel de control"""
        # Título
        title = tk.Label(self.root, text="Mini-Diego",
                        font=("Arial", 16, "bold"), bg="#2d2d2d", fg="white")
        title.pack(pady=10)
        
        # Contador de 24 horas
        # En esta versión de 24 horas el tiempo total se muestra como 024:00:00 al inicio.
        self.time_frame = tk.Frame(self.root, bg="#1a1a1a", relief="sunken", bd=2)
        self.time_frame.pack(fill="x", padx=10, pady=5)

        # Ajustamos la etiqueta del contador para reflejar las 24 horas de juego.
        self.time_label = tk.Label(
            self.time_frame,
            text="Tiempo: 024:00:00",
            font=("Arial", 12, "bold"),
            bg="#1a1a1a",
            fg="#00FF00"
        )
        self.time_label.pack(side="left", padx=10, pady=5)

        # El modo pausa ha sido eliminado para que el juego se juegue de una sola vez.
        
        # Frame para stats
        stats_container = tk.Frame(self.root, bg="#2d2d2d")
        stats_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Crear estadísticas con botones NEGROS
        self.stat_widgets = {}
        stats = [
            ("hambre", "Alimentar", "#FF6B6B", self.feed_pet),
            ("sueno", "Dormir", "#4ECDC4", self.toggle_sleep),
            ("higiene", "Duchar", "#95E1D3", self.shower_pet),
            ("felicidad", "Felicidad", "#FFE66D", None)
        ]
        
        for stat_name, btn_text, color, command in stats:
            self._create_stat_row(stats_container, stat_name, btn_text, color, command)
        
        # Separador
        sep = tk.Frame(self.root, height=2, bg="#555")
        sep.pack(fill="x", pady=8)
        
        # Botón admin
        admin_btn = tk.Button(self.root, text="Admin",
                             command=self.open_admin,
                             font=("Arial", 11, "bold"), bg="#000000", fg="white",
                             relief="raised", cursor="hand2", pady=6)
        admin_btn.pack(fill="x", padx=10, pady=5)
        
        # Iniciar thread del contador
        threading.Thread(target=self._countdown_loop, daemon=True).start()
        # Nota: No iniciamos _pause_info_loop porque la funcionalidad de pausa se ha eliminado.
    
    def _create_stat_row(self, parent, stat_name, btn_text, color, command):
        """Crea fila con botón NEGRO y barras"""
        row_frame = tk.Frame(parent, bg="#2d2d2d")
        row_frame.pack(fill="x", pady=5)
        
        # Botón o label NEGRO
        if command:
            btn = tk.Button(row_frame, text=btn_text,
                           command=command,
                           font=("Arial", 10, "bold"), bg="#000000", fg="white",
                           width=12, relief="raised", cursor="hand2", pady=3)
            btn.pack(side="left", padx=(0, 10))
            
            if stat_name == "sueno":
                self.sleep_button = btn
        else:
            lbl = tk.Label(row_frame, text=btn_text,
                          font=("Arial", 10, "bold"), bg="#000000", fg="white",
                          width=12, anchor="center", relief="raised", bd=2, pady=3)
            lbl.pack(side="left", padx=(0, 10))
        
        # Barras en cuadradito
        bars_container = tk.Frame(row_frame, bg="#1a1a1a", relief="sunken", bd=2)
        bars_container.pack(side="left", fill="x", expand=True)
        
        bars_frame = tk.Frame(bars_container, bg="#1a1a1a")
        bars_frame.pack(padx=3, pady=3)
        
        bars = []
        for i in range(10):
            bar = tk.Label(bars_frame, text="█", font=("Arial", 12),
                          bg="#1a1a1a", fg="#333", padx=0)
            bar.pack(side="left", padx=1)
            bars.append(bar)
        
        self.stat_widgets[stat_name] = {'bars': bars, 'color': color}
    
    def update_display(self):
        """Actualiza las barras"""
        stats = {
            'hambre': self.hambre,
            'sueno': self.sueno,
            'higiene': self.higiene,
            'felicidad': self.felicidad
        }
        
        for stat_name, value in stats.items():
            if stat_name in self.stat_widgets:
                bars_data = self.stat_widgets[stat_name]
                bars = bars_data['bars']
                color = bars_data['color']
                
                filled = int(value / 10)
                
                for i, bar in enumerate(bars):
                    if i < filled:
                        bar.config(fg=color, bg="#1a1a1a")
                    else:
                        bar.config(fg="#333", bg="#1a1a1a")
        
        self._update_pet_sprite()
        self._update_sleep_button_color()
    
    def _update_sleep_button_color(self):
        """Actualiza color del botón de dormir"""
        if hasattr(self, 'sleep_button'):
            if self.sleeping:
                self.sleep_button.config(bg="#9C27B0", text="Despertar", fg="white")
            else:
                self.sleep_button.config(bg="#000000", text="Dormir", fg="white")
    
    def toggle_pause(self):
        """Activa/desactiva pausa - El tiempo baja automáticamente"""
        if self.paused:
            # Reanudar
            if self.pause_start_time:
                elapsed_pause = time.time() - self.pause_start_time
                self.pause_time_used += elapsed_pause
                self.pause_start_time = None
            
            self.paused = False
            self.pause_button.config(text="PAUSAR (7h)", bg="#FFC107")
        else:
            # Verificar tiempo disponible
            remaining = PAUSE_TIME_LIMIT - self.pause_time_used
            if remaining <= 0:
                messagebox.showinfo("Pausa agotada", 
                    "Has usado todas las 7 horas de pausa de hoy.\n"
                    "Se resetea en 24 horas.")
                return
            
            # Pausar
            self.paused = True
            self.pause_start_time = time.time()
            self.pause_button.config(text="REANUDAR", bg="#4CAF50")
    
    def _pause_info_loop(self):
        """Actualiza crono de pausa - BAJA VISUALMENTE"""
        while True:
            try:
                if self.alive:
                    if self.paused and self.pause_start_time:
                        # PAUSADO: mostrar tiempo transcurrido desde que se inició la pausa
                        used = self.pause_time_used + (time.time() - self.pause_start_time)
                        # Si se ha agotado el tiempo total, reanudar automáticamente
                        if used >= PAUSE_TIME_LIMIT:
                            used = PAUSE_TIME_LIMIT
                            self.pause_time_used = PAUSE_TIME_LIMIT
                            self.pause_start_time = None
                            self.paused = False
                            self.pause_button.config(text="PAUSAR (agotado)", bg="#666666", state="disabled")
                            self.pause_time_label.config(
                                text="Pausa agotada - Se resetea en 24h",
                                fg="#FF0000"
                            )
                            time.sleep(1)
                            continue
                        # Calcular horas, minutos y segundos transcurridos (ir de 00:00:00 hasta 07:00:00)
                        hours = int(used // 3600)
                        minutes = int((used % 3600) // 60)
                        seconds = int(used % 60)
                        # Mostrar en verde porque la pausa está corriendo
                        self.pause_time_label.config(
                            text=f"Tiempo en pausa: {hours:02d}:{minutes:02d}:{seconds:02d}",
                            fg="#00FF00"
                        )
                    else:
                        # NO PAUSADO: Mostrar cuánto tiempo de pausa queda disponible
                        avail = PAUSE_TIME_LIMIT - self.pause_time_used
                        if avail < 0:
                            avail = 0
                        hours = int(avail // 3600)
                        minutes = int((avail % 3600) // 60)
                        seconds = int(avail % 60)
                        if avail > 0:
                            # La pausa está disponible pero no activa: mostrar en naranja
                            self.pause_time_label.config(
                                text=f"Pausa disponible: {hours:02d}:{minutes:02d}:{seconds:02d}",
                                fg="#FFC107"
                            )
                            self.pause_button.config(state="normal", bg="#FFC107")
                        else:
                            # Sin tiempo disponible
                            self.pause_time_label.config(
                                text="Pausa agotada - Se resetea en 24h",
                                fg="#FF0000"
                            )
                            self.pause_button.config(state="disabled", bg="#666666")
                
                time.sleep(1)
            except:
                time.sleep(1)
    
    def _countdown_loop(self):
        """
        Loop del contador.  En esta versión no existe un modo de pausa manual, por lo
        que el tiempo restante sólo se detiene cuando Mini‑Diego está durmiendo.
        """
        while True:
            try:
                if self.alive:
                    if not self.paused:
                        # Calcular tiempo transcurrido en un juego de 24 horas
                        elapsed = time.time() - self.game_start_time
                        remaining = self.total_time - elapsed
                        
                        if remaining <= 0:
                            self.root.after(0, self._game_won)
                            break
                        
                        hours = int(remaining // 3600)
                        minutes = int((remaining % 3600) // 60)
                        seconds = int(remaining % 60)
                        
                        # Formateamos con 3 dígitos para horas para mostrar 024:00:00 al inicio
                        time_str = f"Tiempo: {hours:03d}:{minutes:02d}:{seconds:02d}"
                        self.time_label.config(text=time_str, fg="#00FF00")
                    else:
                        # Si estuviera pausado (modo eliminado), simplemente mantén el color
                        # En esta versión no se utiliza self.paused, pero dejamos el código
                        # para compatibilidad.
                        self.time_label.config(fg="#FFC107")
                    
                    # En esta versión no reiniciamos la pausa diaria, ya que no hay pausa.
                
                time.sleep(1)
            except:
                time.sleep(1)
    
    def _game_won(self):
        """
        Victoria.  Se invoca cuando la cuenta atrás de 24 horas llega a cero y Mini‑Diego
        sigue con vida.
        """
        self.root.quit()
    
    def _get_emotional_state(self):
        """Determina estado emocional"""
        if self.sleeping:
            return "durmiendo"
        
        if self.hambre >= 90:
            return "gordo"
        elif self.hambre <= 10:
            return "muy_hambriento"
        elif self.hambre <= 30:
            return "hambriento"
        
        if self.higiene <= 10:
            return "muy_sucio"
        elif self.higiene <= 30:
            return "sucio"
        
        if self.sueno <= 10:
            return "agotado"
        elif self.sueno <= 30:
            return "cansado"
        
        if self.felicidad <= 10:
            return "muy_triste"
        elif self.felicidad <= 30:
            return "triste"
        elif self.felicidad >= 80:
            return "muy_feliz"
        elif self.felicidad >= 60:
            return "feliz"
        
        stats_bajas = sum([
            self.hambre < 40,
            self.sueno < 40,
            self.higiene < 40,
            self.felicidad < 40
        ])
        
        if stats_bajas >= 3:
            return "muriendo"
        elif stats_bajas >= 2:
            return "enfermo"
        
        return "normal"
    
    def _update_pet_sprite(self):
        """Actualiza sprite de mascota"""
        state = self._get_emotional_state()
        self.pet_overlay.update_state(state)
    
    def change_stat(self, stat_name, amount):
        """Cambia estadística"""
        if stat_name == 'hambre':
            self.hambre = max(0, min(100, self.hambre + amount))
        elif stat_name == 'sueno':
            self.sueno = max(0, min(100, self.sueno + amount))
        elif stat_name == 'higiene':
            self.higiene = max(0, min(100, self.higiene + amount))
        elif stat_name == 'felicidad':
            self.felicidad = max(0, min(100, self.felicidad + amount))
        
        self.update_display()
        self._check_death()
    
    def _decay_loop(self):
        """Desgaste de estadísticas - NO afecta si paused"""
        while True:
            try:
                if self.alive and not self.paused:
                    if self.sleeping:
                        time.sleep(3600)
                        self.change_stat('hambre', -HUNGER_DECAY_PER_HOUR * 0.2)
                        self.change_stat('higiene', -HYGIENE_DECAY_PER_2HOURS * 0.5 * 0.2)
                    else:
                        time.sleep(3600)
                        self.change_stat('hambre', -HUNGER_DECAY_PER_HOUR)
                        self.change_stat('sueno', -SLEEP_DECAY_PER_HOUR)
                        time.sleep(3600)
                        self.change_stat('higiene', -HYGIENE_DECAY_PER_2HOURS)
                else:
                    time.sleep(5)
            except:
                time.sleep(5)
    
    def _pet_movement_loop(self):
        """Mascota se mueve SUAVEMENTE"""
        while True:
            try:
                if self.alive and not self.sleeping and not self.paused and random.random() < 0.4:
                    self.pet_overlay.smooth_move()
                time.sleep(random.randint(PET_MOVE_MIN_INTERVAL, PET_MOVE_MAX_INTERVAL))
            except:
                time.sleep(5)
    
    def _sleep_monitor_loop(self):
        """Monitorea sueño - GANA POR MINUTO"""
        while True:
            try:
                if self.sleeping and self.sleep_start_time:
                    elapsed = time.time() - self.sleep_start_time
                    hours = elapsed / 3600
                    
                    # Ganar sueño CADA MINUTO
                    if self.sueno < 100:
                        self.change_stat('sueno', 1.43)
                    else:
                        # Si ya está al 100%, pierde felicidad lentamente
                        self.change_stat('felicidad', -0.5)  # -0.5% por minuto
                    
                    # Después de 7 horas, penalización por sobredescanso
                    if hours >= 7.0:
                        overtime_minutes = (hours - 7.0) * 60
                        if overtime_minutes >= 6:
                            penalty = int(overtime_minutes / 6)
                            self.change_stat('felicidad', -penalty)
                            self.sleep_start_time = time.time() - (7 * 3600)
                
                time.sleep(60)  # Verificar cada minuto
            except:
                time.sleep(60)
    
    def _minigame_event_loop(self):
        """
        Loop de minijuegos.

        Programa la aparición de un minijuego cada 15 minutos aproximadamente.  El
        intervalo entre eventos está configurado en `modules/config.py` a través de
        `EVENT_INTERVAL_MIN` y `EVENT_INTERVAL_MAX`, ambos establecidos en 900
        segundos (15 minutos).  Si Mini‑Diego está durmiendo, el contador de
        minijuegos se pausa automáticamente y se reanudará cuando despierte.
        """
        next_event = time.time() + random.randint(EVENT_INTERVAL_MIN, EVENT_INTERVAL_MAX)
        
        while True:
            try:
                if self.alive and not self.paused and not self.sleeping and not self.current_game:
                    now = time.time()
                    if now >= next_event:
                        self.root.after(0, self.show_minigame_popup)
                        next_event = now + random.randint(EVENT_INTERVAL_MIN, EVENT_INTERVAL_MAX)
                time.sleep(1)
            except:
                time.sleep(2)
    
    def show_minigame_popup(self):
        """Popup de minijuego - TIMEOUT 1 minuto = -25% felicidad"""
        if self.minigame_popup or self.current_game:
            return
        
        self.minigame_popup = tk.Toplevel(self.root)
        self.minigame_popup.title("Minijuego")
        self.minigame_popup.geometry("380x200+500+300")
        self.minigame_popup.attributes("-topmost", True)
        self.minigame_popup.resizable(False, False)
        self.minigame_popup.protocol("WM_DELETE_WINDOW", self._popup_closed)
        self.minigame_popup.configure(bg="#1a1a1a")
        
        response = {'value': None}
        
        tk.Label(self.minigame_popup,
                text="Mini-Diego quiere jugar",
                font=("Arial", 16, "bold"), bg="#1a1a1a",
                fg="#2196F3").pack(pady=20)
        
        tk.Label(self.minigame_popup,
                text="Aceptas?",
                font=("Arial", 13), bg="#1a1a1a",
                fg="white").pack(pady=10)
        
        def accept():
            response['value'] = True
            self.minigame_popup.destroy()
            self.minigame_popup = None
        
        def decline():
            response['value'] = False
            self.minigame_popup.destroy()
            self.minigame_popup = None
        
        btn_frame = tk.Frame(self.minigame_popup, bg="#1a1a1a")
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="Aceptar", command=accept,
                 font=("Arial", 12, "bold"), bg="#4CAF50", fg="white",
                 width=11, pady=6).pack(side="left", padx=10)
        
        tk.Button(btn_frame, text="Rechazar", command=decline,
                 font=("Arial", 12), bg="#f44336", fg="white",
                 width=11, pady=6).pack(side="right", padx=10)
        
        def wait_response():
            start = time.time()
            while time.time() - start < POPUP_RESPONSE_TIMEOUT and response['value'] is None:
                time.sleep(0.5)
            
            if response['value'] is None:
                try:
                    self.minigame_popup.destroy()
                    self.minigame_popup = None
                except:
                    pass
                self.change_stat('felicidad', -HAPPINESS_PENALTY_SKIP_GAME)
                return
            
            if response['value'] is False:
                self.change_stat('felicidad', -10)
                return
            
            self.change_stat('felicidad', 10)
            self.root.after(100, self.launch_minigame)
        
        threading.Thread(target=wait_response, daemon=True).start()
    
    def _popup_closed(self):
        """Cerró popup con X - PENALIZACIÓN"""
        try:
            self.minigame_popup.destroy()
            self.minigame_popup = None
        except:
            pass
        self.change_stat('felicidad', -HAPPINESS_PENALTY_SKIP_GAME)
    
    def launch_minigame(self, specific_game=None):
        """Lanza minijuego EN PRIMERA PANTALLA"""
        if self.current_game:
            return
        
        # Lista de minijuegos disponibles.  Añade nuevos juegos aquí para que
        # puedan ser seleccionados aleatoriamente cuando se inicie un minijuego.
        # Se ha eliminado ClickRapido de la lista.  La lista incluye tanto
        # los minijuegos clásicos (quiz, memoria, stroop, snake, tetris) como
        # los minijuegos de reacción, mecanografía, atrapar, evita rayos, desactiva
        # bomba, cruza la calle, revienta globos, carrera exprés y salta/sube.
        # Lista de minijuegos disponibles.  Se eliminan Asteroides, Ruleta Casino y Parejas
        games = [
            MathQuiz,
            MemoryGame,
            StroopGame,
            SnakeGame,
            TetrisGame,
            TypingGame,
            CatchGame,
            LightningDodge,
            DisarmBomb,
            CrossRoad,
            ExpressRace,
            # Se elimina SpaceInvaderGame ya que no funciona correctamente
            BlackjackGame,
            # JumpClimb se elimina de la lista de minijuegos disponibles
        ]
        # Si se especifica un juego concreto se usará, en caso contrario se
        # escogerá uno aleatorio de la lista anterior.
        game_class = specific_game if specific_game else random.choice(games)
        
        try:
            self.current_game = game_class(self.root, self._minigame_callback)
            self.current_game.run()
        except Exception as e:
            print(f"Error: {e}")
            self.current_game = None
    
    def _minigame_callback(self, result):
        """Callback de minijuego"""
        self.current_game = None
        
        if result == 'won':
            self.change_stat('felicidad', 15)  # +15% felicidad por ganar
            self.open_good_roulette()
        elif result == 'lost':
            self.change_stat('felicidad', -10)
            self.open_bad_roulette()
    
    def open_good_roulette(self):
        """Ruleta buena - PREMIOS JUSTOS"""
        sectors = [
            ("+15% felicidad", ('felicidad', 15)),
            ("+30% felicidad", ('felicidad', 30)),
            ("+20% hambre", ('hambre', 20)),
            ("+25% higiene", ('higiene', 25)),
            ("+20% sueno", ('sueno', 20)),
            ("+50% felicidad", ('felicidad', 50))
        ]
        Roulette(self.root, sectors, self._roulette_callback, "RULETA PREMIO")
    
    def open_bad_roulette(self):
        """Ruleta mala - CASTIGOS MEJORADOS"""
        sectors = [
            ("-15% felicidad", ('felicidad', -15)),
            ("-25% felicidad", ('felicidad', -25)),
            ("-20% hambre", ('hambre', -20)),
            ("-20% higiene", ('higiene', -20)),
            ("-20% sueno", ('sueno', -20)),
            ("-30% felicidad", ('felicidad', -30)),
            ("-10% todas las stats", ('all', -10))
        ]
        Roulette(self.root, sectors, self._roulette_callback, "RULETA CASTIGO")
    
    def _roulette_callback(self, payload):
        """Callback ruleta con ANIMACIÓN"""
        action, value = payload
        
        if action == 'all':
            # Aplicar a todas las stats
            self._animate_stat_change('hambre', value)
            self.canvas.after(300, lambda: self._animate_stat_change('sueno', value))
            self.canvas.after(600, lambda: self._animate_stat_change('higiene', value))
            self.canvas.after(900, lambda: self._animate_stat_change('felicidad', value))
        elif action in ['felicidad', 'hambre', 'higiene', 'sueno']:
            # ANIMAR stat antes de cambiar
            self._animate_stat_change(action, value)
        elif action == 'block':
            # BLOQUEO: Iluminar en ROJO
            self._animate_block(action)
        elif action == 'death':
            self.die("Ruleta de mala suerte")
    
    def _animate_stat_change(self, stat_name, value):
        """Anima cambio de stat - PARPADEO amarillo/blanco"""
        if stat_name not in self.stat_widgets:
            return
        
        bars = self.stat_widgets[stat_name]['bars']
        original_color = self.stat_widgets[stat_name]['color']
        
        # Parpadear 3 veces
        def flash(count):
            if count > 0:
                # Amarillo brillante
                for bar in bars:
                    try:
                        bar.config(fg="#FFFF00")
                    except:
                        pass
                
                self.root.after(200, lambda: restore(count))
            else:
                # Aplicar cambio final
                self.change_stat(stat_name, value)
        
        def restore(count):
            # Blanco brillante
            for bar in bars:
                try:
                    bar.config(fg="#FFFFFF")
                except:
                    pass
            self.root.after(200, lambda: flash(count - 1))
        
        flash(3)
    
    def _animate_block(self, stat_name):
        """Anima bloqueo - FONDO ROJO"""
        # Seleccionar stat aleatorio para bloquear
        import random
        stats_to_block = ['hambre', 'higiene', 'sueno']
        blocked = random.choice(stats_to_block)
        
        if blocked not in self.stat_widgets:
            return
        
        bars = self.stat_widgets[blocked]['bars']
        
        # Iluminar en ROJO por 3 segundos
        for bar in bars:
            try:
                bar.config(bg="#FF0000")
            except:
                pass
        
        # Restaurar después de 3 segundos
        self.root.after(3000, lambda: self._restore_bar_color(blocked))
    
    def _restore_bar_color(self, stat_name):
        """Restaura color normal de barras"""
        if stat_name not in self.stat_widgets:
            return
        
        bars = self.stat_widgets[stat_name]['bars']
        for bar in bars:
            try:
                bar.config(bg="#1a1a1a")
            except:
                pass
    
    def _check_death(self):
        if not self.alive:
            return
        
        # PROTECCIÓN: No morir hambre/higiene durmiendo
        if self.sleeping:
            if self.sueno <= 0:
                self.pet_overlay.update_state("muerte_sueno")
                self.die("Agotamiento")
            elif self.felicidad <= 0:
                self.pet_overlay.update_state("muerte_tristeza")
                self.die("Tristeza extrema")
            return
        
        """Verifica muerte con SPRITES ESPECÍFICOS"""
        
        # Verificar todas las muertes SI NO DUERME
        if self.hambre <= HUNGER_DEATH_MIN:
            self.pet_overlay.update_state("muerte_hambre")
            self.die("Hambre")
        elif self.hambre > HUNGER_DEATH_MAX:
            self.pet_overlay.update_state("muerte_obesidad")
            self.die("Obesidad")
        elif self.sueno <= 0:
            self.pet_overlay.update_state("muerte_sueno")
            self.die("Agotamiento")
        elif self.higiene <= 0:
            self.pet_overlay.update_state("muerte_higiene")
            self.die("Enfermedad por falta de higiene")
        elif self.felicidad <= 0:
            self.pet_overlay.update_state("muerte_tristeza")
            self.die("Tristeza extrema")
    
    def die(self, cause):
        """Muerte con MENSAJE ALEATORIO (14 mensajes)"""
        self.alive = False
        message = random.choice(DEATH_MESSAGES)
        messagebox.showerror("GAME OVER", f"Mini-Diego ha muerto.\n\nCausa: {cause}\n\n{message}")
        self.root.quit()
    
    def feed_pet(self):
        """Alimentar"""
        if not self.alive or self.sleeping:
            return
        self.change_stat('hambre', FEED_INCREASE)
    
    def shower_pet(self):
        """Duchar"""
        if not self.alive or self.sleeping:
            return
        self.change_stat('higiene', SHOWER_INCREASE)
    
    def toggle_sleep(self):
        """Dormir ON/OFF - Funciona cuando quieras"""
        if not self.alive:
            return
        
        if self.sleeping:
            # Despertar
            self.sleeping = False
            self.sleep_start_time = None
            self._update_sleep_button_color()
        else:
            # Dormir
            self.sleeping = True
            self.sleep_start_time = time.time()
            self._update_sleep_button_color()
    
    def open_admin(self):
        """Panel admin"""
        password = simpledialog.askstring("Admin", "Clave:", show="*")
        
        if password != ADMIN_CODE:
            messagebox.showerror("Error", "Clave incorrecta")
            return
        
        admin_win = tk.Toplevel(self.root)
        admin_win.title("Panel Admin")
        admin_win.geometry("320x500")
        admin_win.attributes("-topmost", True)
        admin_win.configure(bg="#1a1a1a")
        
        
        tk.Label(admin_win, text="ADMIN",
                font=("Comic Sans MS", 16, "bold"), bg="#1a1a1a", fg="white").pack(pady=15)

        tk.Label(admin_win, text="Forzar minijuego:",
                font=("Comic Sans MS", 12, "bold"), bg="#1a1a1a", fg="white").pack(pady=8)
        
        # Frame con scroll para los juegos
        game_frame = tk.Frame(admin_win, bg="#1a1a1a")
        game_frame.pack(pady=5)
        
        # Botones para forzar un minijuego específico.  Se incluyen todos los juegos
        # disponibles.  El botón invoca launch_minigame con la clase correspondiente.
        admin_games = [
            ("Quiz", MathQuiz),
            ("Memoria", MemoryGame),
            ("Stroop", StroopGame),
            ("Snake", SnakeGame),
            ("Tetris", TetrisGame),
            ("Mecanografía", TypingGame),
            ("Atrapar", CatchGame),
            ("Evita Rayos", LightningDodge),
            ("Desactiva Bomba", DisarmBomb),
            ("Cruza Calle", CrossRoad),
            ("Carrera Exprés", ExpressRace),
            # Nuevos minijuegos añadidos (eliminamos Asteroides, Ruleta Casino y Parejas)
            ("Blackjack", BlackjackGame)
        ]
        for text, game_cls in admin_games:
            tk.Button(game_frame, text=text, command=lambda cls=game_cls: self.launch_minigame(cls),
                     width=22, bg="#2196F3", fg="white", font=("Comic Sans MS", 10, "bold")).pack(pady=2)
        
        tk.Frame(admin_win, height=2, bg="#555").pack(fill="x", pady=5)
        
        tk.Button(admin_win, text="FORZAR MINIJUEGO AHORA", 
                 command=self.show_minigame_popup,
                 width=22, bg="#FF9800", fg="white", 
                 font=("Arial", 10, "bold")).pack(pady=8)
        
        tk.Frame(admin_win, height=2, bg="#555").pack(fill="x", pady=12)
        
        tk.Button(admin_win, text="Restaurar 100%", command=self.restore_stats, 
                 width=22, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(pady=6)
        tk.Button(admin_win, text="Despertar", command=lambda: setattr(self, 'sleeping', False), 
                 width=22, bg="#FF9800", fg="white", font=("Arial", 10)).pack(pady=6)
        tk.Button(admin_win, text="SALIR", command=self.root.quit, 
                 width=22, bg="#f44336", fg="white", font=("Arial", 10, "bold")).pack(pady=6)
    
    def restore_stats(self):
        """Restaurar stats"""
        self.hambre = 100
        self.sueno = 100
        self.higiene = 100
        self.felicidad = 100
        self.update_display()
    

def main():
    root = tk.Tk()
    app = MiniDiego(root)
    app.update_display()
    
    print("\n" + "="*60)
    print("Mini-Diego INICIADO")
    print("="*60)
    print("Panel de control: Visible")
    print("Mascota flotante: SOBRE TODA LA PANTALLA")
    print("Sprite: assets/sprites/")
    print("="*60 + "\n")
    
    root.mainloop()

# Ejecutar con: dar_a_luz.py
if __name__ == "__main__":
    main()
