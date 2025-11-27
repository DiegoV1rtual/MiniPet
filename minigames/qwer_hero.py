"""
QWERHeroGame - Mini‑juego de estilo Guitar Hero para Mini‑Pet.

En este juego, notas de cuatro columnas diferentes (asociadas a las teclas
Q, W, E y R) caen desde la parte superior de la pantalla hacia una línea de
golpeo situada cerca de la parte inferior.  El jugador debe pulsar la tecla
correspondiente cuando una nota llega a dicha línea.  El juego dura
aproximadamente un minuto; al finalizar, se calcula la precisión del
jugador.  Si la proporción de aciertos sobre el total de notas
alcanzadas supera el 70 %, el jugador gana el minijuego.

Características destacadas:

- Interfaz gráfica con `Canvas` de Tkinter.
- Cuatro columnas (Q/W/E/R) claramente delimitadas.
- Generación de una secuencia de notas con tiempos de aparición y columnas
  aleatorios.
- Actualización de las posiciones de las notas mediante ``after()`` para
  lograr animaciones fluidas.
- Detección de teclas en tiempo real para registrar aciertos o fallos.
- Finalización automática tras un minuto; se llama al ``callback`` del
  minijuego con ``'won'`` o ``'lost'`` según la precisión lograda.

Este minijuego está diseñado para ser sencillo y rápido, siguiendo la
estética y la mecánica de los otros juegos en el proyecto.
"""

import tkinter as tk
import random
import time
import os

# Importación opcional de playsound para reproducir sonidos de teclas.
try:
    from playsound import playsound  # type: ignore
except Exception:
    playsound = None

try:
    from PIL import Image, ImageTk, ImageEnhance  # type: ignore
    HAS_PIL = True
except Exception:
    HAS_PIL = False


class QWERHeroGame:
    """Mini‑juego de caída de notas controlado con las teclas QWER."""

    def __init__(self, parent_window: tk.Tk, callback) -> None:
        self.callback = callback
        self.game_closed = False

        # Configuración
        # Hacemos la ventana más grande para que se vea mejor (800x600)
        self.width = 800
        self.height = 600
        # Duración total del juego en milisegundos (1 minuto)
        self.duration_ms = 60000
        # Tiempo que tarda una nota en recorrer de arriba abajo.  Con una
        # pantalla más alta, mantenemos una velocidad similar.
        self.note_speed_ms = 3000
        # Ventana de acierto más estrecha para mayor precisión
        self.hit_window_px = 30
        # Patrón de canción: secuencia repetitiva de notas QWER.  Se repite
        # suficientes veces para cubrir aproximadamente un minuto.  Cada
        # elemento de la lista representa la tecla que debe tocarse.
        self.pattern = ['q', 'w', 'e', 'r'] * 20  # 80 notas en total
        # Número total de notas generadas durante la partida
        self.total_notes = len(self.pattern)

        # Estado del juego
        self.notes: list[dict] = []  # Lista de diccionarios de notas
        self.start_time = 0.0  # Momento de inicio del juego (en ms)
        self.hits = 0
        self.misses = 0
        self.running = False

        # Crear ventana
        self.window = tk.Toplevel()
        self.window.title("")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#1a1a1a")
        self.canvas = tk.Canvas(self.window, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Centrar en la pantalla
        self.window.update_idletasks()
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        x = (screen_w - self.width) // 2
        y = (screen_h - self.height) // 2
        self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")

        # Permitir arrastrar
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag)

        # Fondo opcional
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
                    img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(0.7)
                    self.bg_photo = ImageTk.PhotoImage(img)
                except Exception:
                    self.bg_photo = None

        # Contenedores de widgets para limpiar fácilmente
        self.widgets = []
        # Identificador de texto de marcador (aciertos/misses) para actualizar dinámicamente
        self.score_id: int | None = None

        # Función local para reproducir sonidos de teclas.  Busca en la carpeta
        # ``assets/sounds/qwer_<tecla>`` archivos de audio y reproduce uno al
        # azar. Si no hay archivos o la biblioteca playsound no está
        # disponible, no hace nada.
        def _play_key_sound(key: str) -> None:
            folder = os.path.join('assets', 'sounds', f'qwer_{key}')
            try:
                files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(('.mp3', '.wav', '.ogg'))]
                if not files:
                    return
                file_path = random.choice(files)
                if playsound is not None:
                    try:
                        playsound(file_path)
                    except Exception:
                        pass
            except Exception:
                pass

        # Asignamos la función como atributo para usarla en otros métodos
        self.play_key_sound = _play_key_sound

    def _start_drag(self, event: tk.Event) -> None:
        self._drag_data = {"x": event.x, "y": event.y}

    def _drag(self, event: tk.Event) -> None:
        if hasattr(self, "_drag_data"):
            x = self.window.winfo_x() + event.x - self._drag_data["x"]
            y = self.window.winfo_y() + event.y - self._drag_data["y"]
            self.window.geometry(f"+{x}+{y}")

    def run(self) -> None:
        """Inicia el minijuego mostrando la pantalla de instrucciones."""
        self.window.after(100, self._show_instructions)

    def _show_instructions(self) -> None:
        """Muestra instrucciones y botón de inicio."""
        self._clear_widgets()
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        # Fondo
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        # Título
        self.widgets.append(self.canvas.create_text(
            cx, cy - 150,
            text="QWER HERO",
            font=("Comic Sans MS", 32, "bold"),
            fill="white"
        ))
        inst = (
            "Presiona las teclas Q, W, E y R cuando las notas\n"
            "lleguen a la línea de golpeo. Gana si tu precisión supera el 70 %\n"
            "tras 1 minuto de juego."
        )
        self.widgets.append(self.canvas.create_text(
            cx, cy - 40,
            text=inst,
            font=("Comic Sans MS", 14),
            fill="yellow",
            justify="center"
        ))
        # Botón empezar
        rect = self.canvas.create_rectangle(
            cx - 100, cy + 80, cx + 100, cy + 130,
            fill="#6e6e6e", outline="white", width=3
        )
        self.widgets.append(rect)
        text_id = self.canvas.create_text(
            cx, cy + 105,
            text="COMENZAR",
            font=("Comic Sans MS", 16, "bold"),
            fill="white"
        )
        self.widgets.append(text_id)
        self.canvas.tag_bind(rect, "<Button-1>", lambda e: self._start_game())
        self.canvas.tag_bind(text_id, "<Button-1>", lambda e: self._start_game())

    def _start_game(self) -> None:
        """Prepara la lista de notas y comienza la animación."""
        # Inicializar contadores
        self.hits = 0
        self.misses = 0
        self.running = True
        # Limpiar pantalla
        self._clear_widgets()
        # Dibujar columnas y línea de golpeo
        self._draw_columns()
        # Dibujar marcador inicial
        score_text = f"Aciertos: {self.hits}/{self.total_notes} (0%)"
        # Ubicamos el marcador en la parte superior de la pantalla
        self.score_id = self.canvas.create_text(
            self.width / 2, 20,
            text=score_text,
            font=("Comic Sans MS", 14, "bold"),
            fill="white"
        )
        self.widgets.append(self.score_id)
        # Generar notas
        self.notes = []
        for i, k in enumerate(self.pattern):
            spawn_time = int(i * (self.duration_ms / len(self.pattern)))
            column_map = {"q": 0, "w": 1, "e": 2, "r": 3}
            column = column_map.get(k, 0)
            self.notes.append({
                "spawn_time": spawn_time,
                "column": column,
                "id": None,
                "hit": False,
                "drawn": False,
                "key": k
            })
        # Registrar eventos de teclado
        self.window.bind("<Key>", self._on_key)
        # Establecer inicio
        self.start_time = time.time() * 1000.0
        # Comenzar bucle de actualización
        self._update()

    def _draw_columns(self) -> None:
        """Dibuja las cuatro columnas y la línea de golpeo."""
        w = self.width
        h = self.height
        col_width = w / 4
        # Etiquetas de teclas
        keys = ["Q", "W", "E", "R"]
        for i in range(4):
            x0 = i * col_width
            x1 = x0 + col_width
            # Delimitar columna con línea ligera
            self.widgets.append(self.canvas.create_rectangle(
                x0, 0, x1, h, outline="#444", width=1
            ))
            # Etiqueta de la tecla
            self.widgets.append(self.canvas.create_text(
                x0 + col_width / 2, h - 30,
                text=keys[i],
                font=("Comic Sans MS", 24, "bold"),
                fill="white"
            ))
        # Línea de golpeo
        self.hit_line_y = h - 80
        self.widgets.append(self.canvas.create_line(
            0, self.hit_line_y, w, self.hit_line_y,
            fill="#FFFFFF", width=2
        ))

    def _update(self) -> None:
        """Actualiza la posición de las notas y gestiona el final del juego."""
        if not self.running:
            return
        now = time.time() * 1000.0
        elapsed = now - self.start_time
        # Dibujar o actualizar notas
        for note in self.notes:
            # Crear nota si aún no se ha creado y es el momento
            if not note["drawn"] and elapsed >= note["spawn_time"]:
                col = note["column"]
                col_width = self.width / 4
                note_x0 = col * col_width + col_width * 0.25
                note_x1 = col * col_width + col_width * 0.75
                # Iniciar en y=0
                rect_id = self.canvas.create_rectangle(
                    note_x0, 0,
                    note_x1, 40,
                    fill="#FF5722", outline="white", width=2
                )
                note["id"] = rect_id
                note["drawn"] = True
            # Actualizar posición si ya está dibujada y no ha sido golpeada
            if note["drawn"] and not note["hit"]:
                progress = (elapsed - note["spawn_time"]) / self.note_speed_ms
                # Mover nota según el progreso
                if progress >= 1.0:
                    # Nota llegó al final sin ser golpeada
                    self.misses += 1
                    note["hit"] = True
                    # Eliminar del canvas
                    try:
                        self.canvas.delete(note["id"])
                    except Exception:
                        pass
                    # Actualizar marcador al contar un fallo
                    self._update_score()
                else:
                    y = progress * (self.hit_line_y - 40)
                    # Actualizar posición
                    try:
                        self.canvas.coords(note["id"],
                                           self.canvas.coords(note["id"])[0],
                                           y,
                                           self.canvas.coords(note["id"])[2],
                                           y + 40)
                    except Exception:
                        pass
        # Comprobar final del juego (una vez pasados todos los tiempos más la
        # duración de caída)
        if elapsed >= self.duration_ms + self.note_speed_ms:
            self.running = False
            # Retirar notas restantes del canvas
            for note in self.notes:
                if note["drawn"]:
                    try:
                        self.canvas.delete(note["id"])
                    except Exception:
                        pass
            # Calcular resultado
            total = self.hits + self.misses if (self.hits + self.misses) > 0 else 1
            accuracy = self.hits / total
            result = 'won' if accuracy >= 0.70 else 'lost'
            # Desvincular teclas
            self.window.unbind("<Key>")
            # Pequeña pausa antes de cerrar
            self.window.after(500, lambda: self._end_game(result))
            return
        # Continuar actualizando
        self.window.after(20, self._update)

    def _update_score(self) -> None:
        """Actualiza el marcador que muestra los aciertos, fallos y precisión."""
        if self.score_id is None:
            return
        total_attempts = self.hits + self.misses if (self.hits + self.misses) > 0 else 1
        accuracy = self.hits / total_attempts
        score_text = f"Aciertos: {self.hits}/{self.total_notes} ({accuracy*100:.0f}% )"
        try:
            self.canvas.itemconfigure(self.score_id, text=score_text)
        except Exception:
            pass

    def _on_key(self, event: tk.Event) -> None:
        """Gestiona las pulsaciones de teclas para detectar aciertos."""
        key = event.char.lower()
        key_map = {"q": 0, "w": 1, "e": 2, "r": 3}
        if key not in key_map:
            return
        col_idx = key_map[key]
        # Emitir sonido al pulsar la tecla asociada
        try:
            self.play_key_sound(key)
        except Exception:
            pass
        # Buscar notas activas en esa columna cerca de la línea de golpeo
        for note in self.notes:
            if note["drawn"] and not note["hit"] and note["column"] == col_idx:
                # Obtener coordenadas
                coords = self.canvas.coords(note["id"])
                # coords = [x0, y0, x1, y1]
                if not coords:
                    continue
                note_y_center = (coords[1] + coords[3]) / 2
                # Si está en la ventana de acierto
                if abs(note_y_center - self.hit_line_y) <= self.hit_window_px:
                    # Acertado
                    self.hits += 1
                    note["hit"] = True
                    try:
                        self.canvas.delete(note["id"])
                    except Exception:
                        pass
                    # Actualizar marcador tras un acierto
                    self._update_score()
                    return  # Evitar golpear varias notas a la vez
                else:
                    # Fuera de la ventana de acierto no se contabiliza
                    return

    def _end_game(self, result: str) -> None:
        """Cierra la ventana y llama al callback con el resultado."""
        if self.game_closed:
            return
        self.game_closed = True
        try:
            self.window.destroy()
        except Exception:
            pass
        # Notificar resultado al juego principal
        try:
            self.callback(result)
        except Exception:
            pass

    def _clear_widgets(self) -> None:
        """Elimina widgets dibujados en el canvas y la ventana."""
        for item in self.widgets:
            try:
                self.canvas.delete(item)
            except Exception:
                pass
        self.widgets.clear()
