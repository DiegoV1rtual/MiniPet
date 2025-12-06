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
# Eliminamos la importación de QWERHeroGame (minijuego de guitarra).

# Importaciones para audio y enlaces externos
import webbrowser
import threading
import os
try:
    # playsound es una librería sencilla para reproducir clips de audio. Si no
    # está disponible, los sonidos simplemente no se reproducen.
    from playsound import playsound  # type: ignore
except Exception:
    playsound = None


# Utilidad de reproducción de audio.

# Implementación simple para reproducir sonido en varias plataformas sin abrir
# un reproductor gráfico.  Esta función intenta usar bibliotecas o
# utilidades del sistema para reproducir archivos de audio de forma
# asíncrona.  Es una alternativa a la librería ``playsound`` cuando esta no
# está disponible.
def simple_play_sound(file_path: str) -> None:
    import platform
    import subprocess
    import os
    system = platform.system()
    try:
        if system == 'Windows':
            # En Windows, usa winsound para WAV y la API MCI para otros
            ext = os.path.splitext(file_path)[1].lower()
            try:
                import winsound  # type: ignore
                if ext == '.wav':
                    winsound.PlaySound(file_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                    return
            except Exception:
                pass
            # Para otros formatos (MP3, OGG, etc.), utiliza mciSendString
            try:
                import ctypes
                from ctypes import wintypes  # type: ignore
                # Construir comando open.  Utiliza alias único para evitar
                # conflictos; se usa el nombre base del archivo como alias.
                alias = 'media'
                # Cerrar previamente cualquier alias con el mismo nombre
                try:
                    ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, None)
                except Exception:
                    pass
                cmd_open = f'open "{file_path}" alias {alias}'
                ctypes.windll.winmm.mciSendStringW(cmd_open, None, 0, None)
                # Reproducir desde el principio de forma asíncrona
                cmd_play = f'play {alias} from 0'
                ctypes.windll.winmm.mciSendStringW(cmd_play, None, 0, None)
                return
            except Exception:
                pass
        elif system == 'Darwin':
            # macOS incluye afplay para reproducir audio
            subprocess.Popen(['afplay', file_path])
            return
        else:
            # En sistemas Linux se puede utilizar aplay o paplay
            # Intentar con aplay primero
            try:
                subprocess.Popen(['aplay', file_path])
                return
            except FileNotFoundError:
                pass
            # Intentar con paplay si aplay no existe
            try:
                subprocess.Popen(['paplay', file_path])
                return
            except FileNotFoundError:
                pass
    except Exception:
        pass
    # Si todo falla, no hacemos nada.  El llamador puede intentar con
    # métodos alternativos o abrir el archivo en un reproductor.
    return
# Busca archivos con extensión .mp3, .wav u .ogg en la carpeta indicada y
# reproduce uno al azar en un hilo aparte. Si no hay archivos o no está
# disponible la biblioteca playsound, la función no hace nada.
def play_random_sound(folder: str) -> None:
    """
    Reproduce un sonido aleatorio de una carpeta.  Se buscan archivos con
    extensiones .mp3, .wav u .ogg.  Si la biblioteca playsound está
    disponible, se utiliza para reproducir el sonido en un hilo
    independiente.  En caso contrario, se intenta abrir el archivo
    con el reproductor predeterminado del sistema operativo.
    """
    try:
        # Determinar carpeta absoluta relativa a este archivo, si es relativa
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_folder = folder if os.path.isabs(folder) else os.path.join(base_dir, folder)
        files = [f for f in os.listdir(full_folder) if f.lower().endswith((".mp3", ".wav", ".ogg"))]
        if not files:
            return
        file_path = os.path.join(full_folder, random.choice(files))
        def _play() -> None:
            # Usar playsound si está disponible
            # 1) Usar playsound si está disponible
            if playsound is not None:
                try:
                    playsound(file_path)
                    return
                except Exception:
                    pass
            # 2) Usar nuestra implementación simple basada en utilidades del sistema
            try:
                simple_play_sound(file_path)
                return
            except Exception:
                pass
            # 3) Abrir el archivo con el reproductor predeterminado (sólo si las
            # opciones anteriores fallan).  Esto puede abrir una ventana del
            # navegador, pero sirve como último recurso.
            try:
                import subprocess
                import sys
                if sys.platform.startswith('win'):
                    os.startfile(file_path)  # type: ignore[attr-defined]
                elif sys.platform == 'darwin':
                    subprocess.Popen(['open', file_path])
                else:
                    subprocess.Popen(['xdg-open', file_path])
                return
            except Exception:
                pass
            # 4) Último recurso: abrir en navegador
            try:
                import webbrowser
                webbrowser.open('file://' + file_path)
            except Exception:
                pass
        threading.Thread(target=_play, daemon=True).start()
    except Exception:
        pass

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

        # Atributos para animaciones GIF
        self.gif_frames: list[ImageTk.PhotoImage] | None = None  # tipo: ignore
        self.gif_index: int = 0
        self.gif_animation_id: str | None = None
        
        # Cargar sprite
        self.load_sprite()
        
        # Hacer arrastrable
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag)
        
        self.screen_width = screen_width
        self.screen_height = screen_height
    
    def load_sprite(self, state="normal"):
        """
        Carga un sprite según el estado emocional.

        Se admite tanto PNG como GIF, e incluso JPEG.  El método
        busca primero un archivo con el nombre de estado y extensión
        `.png`, luego `.gif`, `.jpg` o `.jpeg`.  Si encuentra uno,
        intenta cargarlo con PIL (si está disponible) y redimensionarlo
        al tamaño del sprite.  Si no existe ninguna imagen o se
        produce un error al cargarla, se dibuja un sprite simple de
        colores.

        Para garantizar que los sprites se encuentren correctamente
        independientemente del directorio de trabajo actual, se
        construye la ruta a partir del directorio en el que se
        encuentra este archivo (``main.py``).
        """
        self.canvas.delete("all")
        # Construir lista de extensiones en orden de preferencia
        exts = [".png", ".gif", ".jpg", ".jpeg"]
        sprite_path = None
        # Ruta base relativa a la ubicación de este archivo
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        except Exception:
            base_dir = os.getcwd()
        sprites_dir = os.path.join(base_dir, "assets", "sprites")
        for ext in exts:
            path = os.path.join(sprites_dir, f"{state}{ext}")
            if os.path.exists(path):
                sprite_path = path
                break
        if sprite_path:
            # Cancelar cualquier animación en curso
            if self.gif_animation_id:
                try:
                    self.canvas.after_cancel(self.gif_animation_id)
                except Exception:
                    pass
                self.gif_animation_id = None
            # Si es un GIF y PIL está disponible, intenta animar
            if sprite_path.lower().endswith('.gif') and HAS_PIL:
                if self._start_gif_animation(sprite_path):
                    return
            # Si no es GIF o la animación falló, cargar imagen estática
            if HAS_PIL:
                try:
                    img = Image.open(sprite_path)
                    # usar sólo primer frame
                    try:
                        img.seek(0)
                    except Exception:
                        pass
                    img = img.resize((self.size, self.size), Image.Resampling.LANCZOS)
                    self.sprite_img = ImageTk.PhotoImage(img)
                    self.sprite_id = self.canvas.create_image(
                        self.size//2, self.size//2, image=self.sprite_img
                    )
                    return
                except Exception as e:
                    print(f"Error cargando {sprite_path}: {e}")
            else:
                # Intentar cargar con Tkinter directamente si PIL no está disponible
                try:
                    photo = tk.PhotoImage(file=sprite_path)
                    self.sprite_img = photo
                    self.sprite_id = self.canvas.create_image(
                        self.size//2, self.size//2, image=self.sprite_img
                    )
                    return
                except Exception:
                    pass
        # Si no se cargó ninguna imagen, dibujar sprite básico
        self._draw_simple_sprite(state)

    def _start_gif_animation(self, sprite_path: str) -> bool:
        """
        Carga un archivo GIF y reproduce su animación en bucle.
        Devuelve ``True`` si la animación se pudo iniciar y ``False`` en caso contrario.
        """
        try:
            from PIL import Image, ImageTk, ImageSequence
            img = Image.open(sprite_path)
            frames: list[ImageTk.PhotoImage] = []
            for frame in ImageSequence.Iterator(img):
                f = frame.copy()
                # Asegurarse de que la imagen tiene modo RGBA para soportar transparencias
                try:
                    f = f.convert('RGBA')
                except Exception:
                    pass
                f = f.resize((self.size, self.size), Image.Resampling.LANCZOS)
                frames.append(ImageTk.PhotoImage(f))
            if not frames:
                return False
            self.gif_frames = frames
            self.gif_index = 0
            # Función interna de animación
            def animate():
                if self.gif_frames is None:
                    return
                self.canvas.delete("all")
                frame = self.gif_frames[self.gif_index]
                self.canvas.create_image(self.size//2, self.size//2, image=frame)
                self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
                self.gif_animation_id = self.canvas.after(100, animate)
            animate()
            return True
        except Exception as e:
            print(f"Error animando GIF {sprite_path}: {e}")
            return False
    
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
        """
        Mueve la mascota suavemente por la pantalla. Se asegura de que la
        mascota permanezca siempre visible sobre todas las ventanas y, de
        vez en cuando, realiza un pequeño viaje fuera de la pantalla y
        vuelve a entrar desde un borde aleatorio para dar la sensación de
        que desaparece y reaparece. Este comportamiento se activa de forma
        aleatoria para no resultar predecible.
        """
        # Asegurar que la ventana esté siempre en primer plano.
        try:
            self.window.lift()
            # Reaplicar la propiedad -topmost por si algún gestor de ventanas la
            # desactiva temporalmente.
            self.window.attributes("-topmost", True)
        except Exception:
            pass

        # Con una probabilidad muy baja (5 %) la mascota abandona brevemente un
        # borde de la pantalla y reaparece desde otro lado.  La mayor parte
        # del tiempo simplemente se moverá a una posición aleatoria dentro de
        # la pantalla para permanecer visible durante más tiempo.
        if random.random() < 0.05:
            # Elegir borde de salida y entrada
            side = random.choice(["left", "right", "top", "bottom"])
            # Posición actual
            current_x = self.window.winfo_x()
            current_y = self.window.winfo_y()
            # Elegir una coordenada aleatoria en el eje perpendicular
            if side == "left":
                # Salir por la izquierda y entrar por la derecha
                off_x = -self.size
                off_y = random.randint(0, self.screen_height - self.size)
                self._animate_move_to(off_x, off_y)
                # Reentrar desde la derecha
                in_x = self.screen_width
                in_y = random.randint(0, self.screen_height - self.size)
                self._animate_move_to(in_x, in_y)
            elif side == "right":
                off_x = self.screen_width
                off_y = random.randint(0, self.screen_height - self.size)
                self._animate_move_to(off_x, off_y)
                in_x = -self.size
                in_y = random.randint(0, self.screen_height - self.size)
                self._animate_move_to(in_x, in_y)
            elif side == "top":
                off_x = random.randint(0, self.screen_width - self.size)
                off_y = -self.size
                self._animate_move_to(off_x, off_y)
                in_x = random.randint(0, self.screen_width - self.size)
                in_y = self.screen_height
                self._animate_move_to(in_x, in_y)
            else:  # bottom
                off_x = random.randint(0, self.screen_width - self.size)
                off_y = self.screen_height
                self._animate_move_to(off_x, off_y)
                in_x = random.randint(0, self.screen_width - self.size)
                in_y = -self.size
                self._animate_move_to(in_x, in_y)
        else:
            # Mover a una posición aleatoria dentro de la pantalla
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
        # Ajustamos el tamaño por defecto del panel de control.  Volvemos a
        # un tamaño más compacto, ya que el usuario prefiere la distribución
        # vertical original de las estadísticas.
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
        
        # Contador de 12 horas.  Adaptamos la duración del juego a medio día, de modo
        # que Mini‑Diego pueda ser cuidado en sesiones más cortas.  La hora
        # inicial y el tiempo total se utilizan para calcular el tiempo
        # restante en ``_countdown_loop``.
        self.game_start_time = time.time()
        self.total_time = 12 * 3600
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

        # Iniciar hilo para reproducir sonidos aleatorios mientras la mascota está
        # despierta.  Este hilo se mantiene en espera y reproduce un sonido de
        # la carpeta "awake" en intervalos aleatorios cuando la mascota no
        # duerme.  Si no hay archivos en la carpeta, la función no hace nada.
        threading.Thread(target=self._awake_audio_loop, daemon=True).start()

        # Manejadores de audio de sueño
        self._sleep_ambient_thread = None
        self._sleep_ambient_stop = None
    
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

        # Ajustamos la etiqueta del contador para reflejar las 12 horas de juego.  El
        # formato mantiene tres dígitos para las horas por coherencia con la
        # versión anterior.
        self.time_label = tk.Label(
            self.time_frame,
            text="Tiempo: 012:00:00",
            font=("Arial", 12, "bold"),
            bg="#1a1a1a",
            fg="#00FF00"
        )
        self.time_label.pack(side="left", padx=10, pady=5)

        # El modo pausa ha sido eliminado para que el juego se juegue de una sola vez.
        
        # Contenedor para las estadísticas.  Utilizamos un layout horizontal para
        # mostrar todas las estadísticas en una sola fila.  Cada columna
        # contiene el botón (o etiqueta) y la barra de progreso debajo.
        stats_container = tk.Frame(self.root, bg="#2d2d2d")
        # Para la distribución vertical de antes, empaquetamos el contenedor
        # directamente sin expandir, manteniendo las filas una debajo de otra.
        stats_container.pack(fill="x", padx=10, pady=5)

        # Crear estadísticas con botones NEGROS.  Volvemos al método
        # _create_stat_row que organiza cada estadística en una fila.
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

    def _create_stat_column(self, parent: tk.Frame, stat_name: str, btn_text: str, color: str, command) -> None:
        """
        Crea una columna en el panel de estadísticas.  Cada columna contiene
        un botón o etiqueta en la parte superior y una barra de progreso
        vertical debajo.  Esto permite colocar varias estadísticas una al
        lado de la otra en el panel principal, ofreciendo un diseño más
        horizontal en comparación con la distribución por filas.  El
        parámetro ``command`` es la función que se invocará cuando el
        usuario haga clic en el botón (por ejemplo, alimentar, dormir o
        duchar).  Si ``command`` es ``None`` se muestra una etiqueta en
        lugar de un botón.
        """
        # Contenedor para la columna
        col_frame = tk.Frame(parent, bg="#2d2d2d")
        col_frame.pack(side="left", fill="both", expand=True, padx=4, pady=2)

        # Botón o etiqueta NEGRO en la parte superior
        if command:
            btn = tk.Button(col_frame, text=btn_text,
                             command=command,
                             font=("Arial", 10, "bold"), bg="#000000", fg="white",
                             relief="raised", cursor="hand2", pady=4)
            # Hacemos el botón lo suficientemente ancho para que el texto quepa
            btn.pack(fill="x", padx=2, pady=(0, 6))

            # Referencia al botón de sueño para cambiar su texto/color al dormir
            if stat_name == "sueno":
                self.sleep_button = btn
        else:
            lbl = tk.Label(col_frame, text=btn_text,
                            font=("Arial", 10, "bold"), bg="#000000", fg="white",
                            anchor="center", relief="raised", bd=2, pady=4)
            lbl.pack(fill="x", padx=2, pady=(0, 6))

        # Contenedor para las barras horizontales (dentro de un marco de borde)
        bars_container = tk.Frame(col_frame, bg="#1a1a1a", relief="sunken", bd=2)
        bars_container.pack(fill="both", expand=True, padx=2, pady=2)

        bars_frame = tk.Frame(bars_container, bg="#1a1a1a")
        bars_frame.pack(padx=3, pady=3)

        # Crear 10 barras tipo barra de progreso horizontal
        bars: list[tk.Label] = []
        for i in range(10):
            bar = tk.Label(bars_frame, text="█", font=("Arial", 12),
                            bg="#1a1a1a", fg="#333", padx=0)
            bar.pack(side="left", padx=1)
            bars.append(bar)

        # Almacenar barras para actualizar posteriormente
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
        Loop del contador.  En la versión de 12 horas no existe modo de pausa
        manual, por lo que el tiempo restante sólo se detiene cuando
        Mini‑Diego está durmiendo.
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

    def force_victory(self) -> None:
        """
        Forzar la victoria.  Permite al administrador finalizar la partida
        inmediatamente.  Esto invoca el mismo flujo que cuando se agota el
        tiempo sin penalizar al jugador.
        """
        # Llama al manejador de victoria
        self._game_won()

    def reduce_time(self, seconds: int) -> None:
        """
        Reduce el tiempo restante del juego.

        Disminuye ``total_time`` en la cantidad especificada (en segundos).
        Si el tiempo restante se agota, se invoca la victoria.  Tras
        ajustar el temporizador, se actualiza inmediatamente la etiqueta de
        tiempo.

        :param seconds: segundos a restar (p.ej., 3600 para una hora o 300 para cinco minutos)
        """
        # No modificar si ya hemos finalizado
        if not self.alive:
            return
        # Ajustar total_time pero no permitir valores negativos
        self.total_time = max(0, self.total_time - seconds)
        # Calcular tiempo restante tras el ajuste
        elapsed = time.time() - self.game_start_time
        remaining = self.total_time - elapsed
        if remaining <= 0:
            # Invocar victoria si ya no queda tiempo
            self._game_won()
            return
        # Actualizar etiqueta de tiempo inmediatamente
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        seconds_left = int(remaining % 60)
        time_str = f"Tiempo: {hours:03d}:{minutes:02d}:{seconds_left:02d}"
        try:
            self.time_label.config(text=time_str, fg="#00FF00")
        except Exception:
            pass

    def preview_state(self, state: str) -> None:
        """
        Muestra el sprite correspondiente al estado indicado.  Esta
        función se utiliza en el panel de administración para que el
        usuario pueda ver los sprites de todos los estados disponibles.
        :param state: nombre del estado (por ejemplo, 'feliz', 'sucio')
        """
        try:
            self.pet_overlay.update_state(state)
        except Exception:
            pass
    
    def _game_won(self):
        """
        Maneja la victoria del juego.  Cuando el contador de tiempo llega a
        cero y Mini‑Diego sigue con vida, se reproduce un sonido de
        finalización y se muestra un panel heroico felicitando al jugador.

        En lugar de salir inmediatamente, se crea una ventana modal que
        presenta un mensaje de victoria para "Fran Rebollo" junto con la
        clave especial proporcionada por el usuario.  Al cerrar este panel,
        el programa termina.
        """
        # Marcar que el juego se ha completado para detener bucles de desgaste
        self.alive = False
        # Reproducir sonido de juego completado, si se ha definido alguno
        try:
            play_random_sound(os.path.join("assets", "sounds", "game_complete"))
        except Exception:
            pass
        # Crear panel de victoria
        top = tk.Toplevel(self.root)
        top.title("¡Victoria!")
        # Tamaño amplio para enfatizar la victoria
        top.geometry("700x500")
        top.attributes("-topmost", True)
        # Fondo predeterminado
        top.configure(bg="#0D47A1")  # azul oscuro heroico
        # Evitar que el usuario cierre la ventana accidentalmente con la X
        top.protocol("WM_DELETE_WINDOW", lambda: None)

        # Intentar cargar una imagen de fondo desde la carpeta assets/backgrounds
        bg_loaded = False
        try:
            bg_dir = os.path.join("assets", "backgrounds")
            if os.path.isdir(bg_dir):
                # Buscar el primer archivo de imagen (png o jpg o gif) en la carpeta
                for fname in os.listdir(bg_dir):
                    if fname.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                        bg_path = os.path.join(bg_dir, fname)
                        if HAS_PIL:
                            try:
                                from PIL import Image, ImageTk
                                img = Image.open(bg_path)
                                # Redimensionar al tamaño de la ventana
                                img = img.resize((700, 500), Image.Resampling.LANCZOS)
                                top._bg_photo = ImageTk.PhotoImage(img)  # guardar referencia
                                bg_label = tk.Label(top, image=top._bg_photo)
                                bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                                bg_loaded = True
                                break
                            except Exception:
                                pass
                        else:
                            try:
                                photo = tk.PhotoImage(file=bg_path)
                                top._bg_photo = photo
                                bg_label = tk.Label(top, image=top._bg_photo)
                                bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                                bg_loaded = True
                                break
                            except Exception:
                                pass
        except Exception:
            pass

        # Usar un canvas para evitar fondos blancos.  Dibujamos textos
        # directamente sobre el canvas, de modo que el fondo (imagen o
        # color sólido) sea visible detrás de las letras.
        canvas = tk.Canvas(top, width=700, height=500, highlightthickness=0)
        canvas.place(x=0, y=0)
        # Dibujar fondo si se cargó
        if bg_loaded:
            try:
                canvas.create_image(0, 0, anchor="nw", image=top._bg_photo)
            except Exception:
                # Fallback: color sólido
                canvas.configure(bg="#0D47A1")
        else:
            canvas.configure(bg="#0D47A1")
        # Titular en color dorado
        canvas.create_text(350, 140, text="¡HAS COMPLETADO EL JUEGO!", fill="#FFD700",
                            font=("Comic Sans MS", 24, "bold"), anchor="center")
        # Mensaje personal en naranja
        canvas.create_text(350, 200,
                            text="Muchas gracias por ser mi amigo Fran, feliz cumpleaños, te quiero",
                            fill="#FFA500", font=("Comic Sans MS", 16, "bold"), anchor="center",
                            width=600)
        # Clave en azul
        canvas.create_text(350, 260, text="Clave: 65XYD-QR6L0-ETGG9", fill="#2196F3",
                            font=("Courier New", 20, "bold"), anchor="center")
        # Mensaje inferior animando a explorar
        canvas.create_text(350, 320,
                            text="¡Ya puedes explorar el proyecto y descubrir todos sus secretos!",
                            fill="#BBDEFB", font=("Arial", 14, "italic"), anchor="center",
                            width=650)
        # Botón para cerrar
        def close_game():
            try:
                top.destroy()
            except Exception:
                pass
            self.root.quit()
        close_btn = tk.Button(top, text="Cerrar", command=close_game,
                             font=("Arial", 14, "bold"), bg="#4CAF50", fg="white",
                             width=12, pady=6)
        # Posicionar botón en la parte inferior
        close_btn.place(relx=0.5, rely=0.88, anchor="center")
    
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
        """
        Actualiza la imagen de la mascota en pantalla.

        Cuando Mini‑Diego está dormida (``self.sleeping`` es ``True``),
        siempre se muestra el sprite de ``durmiendo`` sin importar el resto
        de estadísticas.  De lo contrario, se utiliza el estado emocional
        calculado en ``_get_emotional_state``.
        """
        # Si la mascota está dormida, forzar el estado a "durmiendo"
        if getattr(self, 'sleeping', False):
            state = "durmiendo"
        else:
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
                # Siempre mover la mascota si está viva, no duerme y no está en pausa. La frecuencia
                # de movimiento está controlada por PET_MOVE_MIN_INTERVAL y PET_MOVE_MAX_INTERVAL.
                if self.alive and not self.sleeping and not self.paused:
                    self.pet_overlay.smooth_move()
                # Esperar un intervalo aleatorio antes de moverse de nuevo
                time.sleep(random.randint(PET_MOVE_MIN_INTERVAL, PET_MOVE_MAX_INTERVAL))
            except Exception:
                # En caso de error inesperado, esperar unos segundos y continuar
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
                        # Ganar sueño según configuración (por minuto)
                        try:
                            self.change_stat('sueno', SLEEP_GAIN_PER_MINUTE)
                        except Exception:
                            # En caso de error, usar un valor predeterminado
                            self.change_stat('sueno', 1.5)
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

    def _awake_audio_loop(self):
        """Reproduce sonidos aleatorios mientras la mascota está despierta.

        Este hilo se ejecuta en segundo plano y espera un intervalo aleatorio
        de entre 3 y 5 minutos.  Si la mascota está viva y no está dormida,
        reproduce un clip de audio aleatorio de la carpeta ``assets/sounds/awake``.
        Si la biblioteca ``playsound`` no está disponible o no hay archivos de
        audio, la función no hace nada.  Durante el sueño o cuando está
        muerta, el hilo simplemente espera y vuelve a comprobar más tarde.
        """
        while True:
            try:
                # Generar un intervalo aleatorio en segundos (180, 240 o 300)
                delay = random.choice([180, 240, 300])
                time.sleep(delay)
                # Solo reproducir sonido si la mascota está viva y despierta
                if self.alive and not self.sleeping:
                    try:
                        folder = os.path.join("assets", "sounds", "awake")
                        play_random_sound(folder)
                    except Exception:
                        pass
            except Exception:
                # En caso de error inesperado, esperar un poco antes de reintentar
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

        # Jugar un minijuego cansa a Mini‑Diego: reduce el nivel de sueño
        # para reflejar el esfuerzo.  Si el nivel de sueño baja mucho, será
        # necesario dormir para recuperarse.
        try:
            # Restamos 15 puntos (15 %) de sueño por cada minijuego jugado
            self.change_stat('sueno', -15)
        except Exception:
            pass
        
        if result == 'won':
            self.change_stat('felicidad', 15)  # +15% felicidad por ganar
            # Sonido de victoria en minijuego
            try:
                play_random_sound(os.path.join("assets", "sounds", "minigame_win"))
            except Exception:
                pass
            self.open_good_roulette()
        elif result == 'lost':
            self.change_stat('felicidad', -10)
            # Sonido de derrota en minijuego
            try:
                play_random_sound(os.path.join("assets", "sounds", "minigame_loss"))
            except Exception:
                pass
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
        # Reproducir sonido de muerte si existe
        play_random_sound(os.path.join("assets", "sounds", "death"))
        messagebox.showerror("GAME OVER", f"Mini-Diego ha muerto.\n\nCausa: {cause}\n\n{message}")
        # Con una probabilidad del 10 %, abrir un vídeo en el navegador web como broma final
        try:
            if random.random() < 0.1:
                webbrowser.open("https://www.youtube.com/watch?v=lv9cLJ41Rzc")
        except Exception:
            pass
        self.root.quit()
    
    def feed_pet(self):
        """Alimentar"""
        if not self.alive or self.sleeping:
            return
        self.change_stat('hambre', FEED_INCREASE)
        # Reproducir sonido de comer
        play_random_sound(os.path.join("assets", "sounds", "eat"))
    
    def shower_pet(self):
        """Duchar"""
        if not self.alive or self.sleeping:
            return
        self.change_stat('higiene', SHOWER_INCREASE)
        # Opcional: reproducir un sonido al duchar si se agregan archivos en la carpeta correspondiente
        play_random_sound(os.path.join("assets", "sounds", "shower"))
    
    def toggle_sleep(self):
        """Dormir ON/OFF - Funciona cuando quieras"""
        if not self.alive:
            return
        
        if self.sleeping:
            # Despertar
            self.sleeping = False
            self.sleep_start_time = None
            self._update_sleep_button_color()
            # Detener sonidos ambientales de sueño al despertar
            self.stop_sleep_ambient_sound()
        else:
            # Dormir
            self.sleeping = True
            self.sleep_start_time = time.time()
            self._update_sleep_button_color()
            # Reproducir sonido de irse a dormir
            play_random_sound(os.path.join("assets", "sounds", "sleep"))
            # Iniciar sonidos ambientales en bucle mientras duerme
            self.start_sleep_ambient_sound()
        # Actualizar inmediatamente el sprite para reflejar el estado de sueño
        try:
            self._update_pet_sprite()
        except Exception:
            pass
    
    def open_admin(self):
        """Panel admin"""
        password = simpledialog.askstring("Admin", "Clave:", show="*")
        
        if password != ADMIN_CODE:
            messagebox.showerror("Error", "Clave incorrecta")
            return
        
        admin_win = tk.Toplevel(self.root)
        admin_win.title("Panel Admin")
        # Diseñamos una ventana más ancha que alta para disponer las opciones en
        # tres columnas horizontales.  Esta dimensión evita que el usuario
        # necesite estirar la ventana manualmente.
        admin_win.geometry("800x500")
        admin_win.attributes("-topmost", True)
        admin_win.configure(bg="#1a1a1a")

        # Título principal
        title_label = tk.Label(admin_win, text="ADMIN", font=("Comic Sans MS", 18, "bold"),
                               bg="#1a1a1a", fg="white")
        title_label.pack(pady=(10, 5))

        # Contenedor horizontal para las diferentes secciones del panel
        content_frame = tk.Frame(admin_win, bg="#1a1a1a")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ------------------------------------------------------------------
        # Columna de minijuegos
        minigame_col = tk.Frame(content_frame, bg="#1a1a1a")
        minigame_col.pack(side="left", fill="both", expand=True, padx=10)

        # Etiqueta sección
        tk.Label(minigame_col, text="Forzar minijuego:", font=("Comic Sans MS", 12, "bold"),
                 bg="#1a1a1a", fg="white").pack(pady=(0, 8))
        # Frame de botones de juegos
        game_frame = tk.Frame(minigame_col, bg="#1a1a1a")
        game_frame.pack(fill="both", expand=True)
        # Lista de minijuegos disponibles en el panel admin
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
            ("Blackjack", BlackjackGame)
        ]
        # Crear botón por cada juego
        for text, game_cls in admin_games:
            tk.Button(game_frame, text=text,
                     command=lambda cls=game_cls: self.launch_minigame(cls),
                     width=18, bg="#2196F3", fg="white", font=("Comic Sans MS", 10, "bold"),
                     wraplength=130, justify="center").pack(pady=2, fill="x")

        # Botón para forzar minijuego aleatorio
        tk.Button(minigame_col, text="FORZAR MINIJUEGO AHORA",
                 command=self.show_minigame_popup,
                 width=18, bg="#FF9800", fg="white", font=("Arial", 10, "bold"),
                 wraplength=130, justify="center").pack(pady=6, fill="x")

        # ------------------------------------------------------------------
        # Columna de acciones de control (restaurar, despertar, salir)
        control_col = tk.Frame(content_frame, bg="#1a1a1a")
        control_col.pack(side="left", fill="both", expand=True, padx=10)

        tk.Label(control_col, text="Acciones:", font=("Comic Sans MS", 12, "bold"),
                 bg="#1a1a1a", fg="white").pack(pady=(0, 8))
        # Restaurar estadísticas
        tk.Button(control_col, text="Restaurar 100%", command=self.restore_stats,
                 width=18, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(pady=4, fill="x")
        # Despertar mascota
        tk.Button(control_col, text="Despertar", command=lambda: setattr(self, 'sleeping', False),
                 width=18, bg="#FF9800", fg="white", font=("Arial", 10, "bold")).pack(pady=4, fill="x")
        # Botón para forzar la victoria inmediata
        tk.Button(control_col, text="Forzar Victoria", command=self.force_victory,
                 width=18, bg="#03A9F4", fg="white", font=("Arial", 10, "bold")).pack(pady=4, fill="x")
        # Botón para restar 1 hora (3600 segundos) al temporizador
        tk.Button(control_col, text="-1 hora", command=lambda: self.reduce_time(3600),
                 width=18, bg="#FF5722", fg="white", font=("Arial", 10, "bold")).pack(pady=4, fill="x")
        # Botón para restar 5 minutos (300 segundos) al temporizador
        tk.Button(control_col, text="-5 minutos", command=lambda: self.reduce_time(300),
                 width=18, bg="#FF7043", fg="white", font=("Arial", 10, "bold")).pack(pady=4, fill="x")
        # Salir del programa
        tk.Button(control_col, text="SALIR", command=self.root.quit,
                 width=18, bg="#f44336", fg="white", font=("Arial", 10, "bold")).pack(pady=4, fill="x")

        # ------------------------------------------------------------------
        # Columna de reproducción de sonidos
        sound_col = tk.Frame(content_frame, bg="#1a1a1a")
        sound_col.pack(side="left", fill="both", expand=True, padx=10)

        tk.Label(sound_col, text="Reproducir sonidos:", font=("Comic Sans MS", 12, "bold"),
                 bg="#1a1a1a", fg="white").pack(pady=(0, 8))

        sound_buttons = [
            ("Hablar despierto", "awake"),
            ("Comer", "eat"),
            ("Ducha", "shower"),
            ("Dormir", "sleep"),
            ("Ambiente sueño", "sleep_ambient"),
            ("Victoria minijuego", "minigame_win"),
            ("Derrota minijuego", "minigame_loss"),
            ("Muerte", "death")
        ]
        for text, folder in sound_buttons:
            tk.Button(sound_col, text=text,
                     command=lambda f=folder: play_random_sound(os.path.join("assets", "sounds", f)),
                     width=18, bg="#9C27B0", fg="white", font=("Arial", 10, "bold"),
                     wraplength=130, justify="center").pack(pady=2, fill="x")

        # ------------------------------------------------------------------
        # Columna para ver estados (sprites)
        state_col = tk.Frame(content_frame, bg="#1a1a1a")
        state_col.pack(side="left", fill="both", expand=True, padx=10)
        tk.Label(state_col, text="Ver estados:", font=("Comic Sans MS", 12, "bold"),
                 bg="#1a1a1a", fg="white").pack(pady=(0, 8))
        # Lista de todos los estados disponibles para previsualizar
        preview_states = [
            "normal", "hambriento", "muy_hambriento", "gordo", "sucio", "muy_sucio",
            "cansado", "agotado", "feliz", "muy_feliz", "triste", "muy_triste",
            "durmiendo", "enfermo", "muriendo", "muerte_obesidad", "muerte_tristeza",
            "muerte_sueno", "muerte_hambre", "muerte_higiene"
        ]
        for st in preview_states:
            tk.Button(state_col, text=st,
                     command=lambda s=st: self.preview_state(s),
                     width=18, bg="#607D8B", fg="white", font=("Arial", 9, "bold"),
                     wraplength=130, justify="center").pack(pady=1, fill="x")
    
    def restore_stats(self):
        """Restaurar stats"""
        self.hambre = 100
        self.sueno = 100
        self.higiene = 100
        self.felicidad = 100
        self.update_display()

    # ------------------------------------------------------------------
    # Reproducción de sonidos de sueño
    #
    # Estas funciones gestionan un hilo que reproduce de forma aleatoria
    # sonidos de ambiente mientras Mini‑Diego duerme. El hilo se detiene
    # automáticamente al despertar.
    def start_sleep_ambient_sound(self) -> None:
        """Comienza a reproducir sonidos ambientales mientras duerme."""
        # No iniciar de nuevo si ya hay un hilo activo
        if hasattr(self, '_sleep_ambient_thread') and self._sleep_ambient_thread:
            if self._sleep_ambient_thread.is_alive():
                return
        # Crear evento de parada
        self._sleep_ambient_stop = threading.Event()

        def loop() -> None:
            while not self._sleep_ambient_stop.is_set():
                play_random_sound(os.path.join("assets", "sounds", "sleep_ambient"))
                # Reproducir un sonido cada 2 minutos (120 segundos) para no
                # saturar al jugador y proporcionar un intervalo relajante.
                # Se puede ajustar este valor según la duración de las pistas.
                time.sleep(120)
        # Lanzar hilo en segundo plano
        self._sleep_ambient_thread = threading.Thread(target=loop, daemon=True)
        self._sleep_ambient_thread.start()

    def stop_sleep_ambient_sound(self) -> None:
        """Detiene la reproducción de sonidos ambientales de sueño."""
        if hasattr(self, '_sleep_ambient_stop') and self._sleep_ambient_stop:
            self._sleep_ambient_stop.set()
    

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
