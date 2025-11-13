"""
ReactionGame - A simple reflex based minigame for MiniPet.

In this minigame the player is presented with a series of rounds where
they must click a target as soon as it appears on the screen. The target
appears after a random delay to prevent the player from anticipating its
appearance. If the player reacts quickly enough a success is recorded.
After all rounds have completed the game reports whether the player
achieved the required number of successes to win.

This class follows the same structure as other minigames in the project:
it accepts a parent window and a callback. When the game finishes it
invokes the callback with either "won" or "lost" depending on the
player's performance.

The game uses Tkinter for the UI and supports dragging the window around
just like the other games. If Pillow is available and an appropriate
background image exists in the ``assets/minigames`` directory it will
display that image behind the game area. Otherwise it falls back to a
solid background colour.

"""

import tkinter as tk
import random
import time
import os

try:
    from PIL import Image, ImageTk  # type: ignore
    HAS_PIL = True
except Exception:
    HAS_PIL = False


class ReactionGame:
    """A reaction time minigame where the player must click as soon as a target appears."""

    def __init__(self, parent_window: tk.Tk, callback) -> None:
        self.callback = callback
        self.game_closed = False
        # Configuration
        self.num_rounds = 5
        self.required_successes = 3
        self.current_round = 0
        self.successes = 0
        self.target_id = None
        self.clicked = False
        self.start_time = 0.0

        # Create toplevel window
        self.window = tk.Toplevel()
        self.window.title("")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#1a1a1a")

        # Determine screen centre for initial placement
        w, h = 600, 500
        self.canvas = tk.Canvas(self.window, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.window.update_idletasks()
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        self.window.geometry(f"{w}x{h}+{x}+{y}")

        # Support dragging the window
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag)

        # Attempt to load a background image
        self.bg_photo = None
        # Usar una imagen de fondo genérica 'fondo1.png' en la carpeta assets/custom.
        # Esto permite al usuario reemplazar fácilmente la imagen sin modificar el código.
        bg_path = os.path.join("assets", "custom", "fondo1.png")
        if HAS_PIL and os.path.exists(bg_path):
            try:
                img = Image.open(bg_path)
                img = img.resize((w, h), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(img)
            except Exception:
                self.bg_photo = None

        # Keep track of widgets drawn on the canvas for easy removal
        self.widgets = []

    def _start_drag(self, event: tk.Event) -> None:
        """Begin dragging the window."""
        self._drag_data = {"x": event.x, "y": event.y}

    def _drag(self, event: tk.Event) -> None:
        """Drag the window to a new location."""
        if hasattr(self, "_drag_data"):
            x = self.window.winfo_x() + event.x - self._drag_data["x"]
            y = self.window.winfo_y() + event.y - self._drag_data["y"]
            self.window.geometry(f"+{x}+{y}")

    def run(self) -> None:
        """Begin the game by showing instructions."""
        # Delay to ensure the canvas is rendered before adding text
        self.window.after(100, self._show_instructions)

    def _show_instructions(self) -> None:
        """Display initial instructions and a start button."""
        self._clear_widgets()
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2

        # Draw background if available
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)

        self.widgets.append(self.canvas.create_text(
            cx, cy - 100,
            text="JUEGO DE REACCION",
            font=("Arial", 28, "bold"),
            fill="white"
        ))

        inst_text = (
            "Haz click en el circulo tan pronto como aparezca.\n"
            f"Completa {self.num_rounds} rondas y consigue al menos {self.required_successes} aciertos para ganar."
        )
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text=inst_text,
            font=("Arial", 13),
            fill="yellow",
            justify="center"
        ))

        # Start button
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 80, cx + 100, cy + 130,
            fill="#4CAF50", outline="white", width=3
        )
        self.widgets.append(btn_rect)
        btn_text = self.canvas.create_text(
            cx, cy + 105,
            text="COMENZAR",
            font=("Arial", 16, "bold"),
            fill="white"
        )
        self.widgets.append(btn_text)

        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._start_game())
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._start_game())

    def _start_game(self) -> None:
        """Reset counters and begin the first round."""
        self.current_round = 0
        self.successes = 0
        self._next_round()

    def _next_round(self) -> None:
        """Set up the next reaction round or finish the game if done."""
        if self.current_round >= self.num_rounds:
            self._game_over()
            return
        self.current_round += 1
        self.clicked = False
        # Clear previous target and texts
        self._clear_widgets()
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx = w // 2
        # Draw background if available
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        # Show round counter
        self.widgets.append(self.canvas.create_text(
            cx, 40,
            text=f"Ronda {self.current_round}/{self.num_rounds}  -  Aciertos: {self.successes}",
            font=("Arial", 16, "bold"),
            fill="white"
        ))
        # Wait a random amount of time before showing target
        delay = random.randint(1000, 3000)
        self.window.after(delay, self._show_target)

    def _show_target(self) -> None:
        """Display the clickable target on the canvas and start the timer."""
        if self.clicked:
            return
        # Random position for the target
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        size = 60
        x = random.randint(100, w - 100 - size)
        y = random.randint(150, h - 150 - size)
        # Draw a red circle
        self.target_id = self.canvas.create_oval(
            x, y, x + size, y + size,
            fill="#FF6B6B", outline="white", width=3
        )
        self.widgets.append(self.target_id)
        # Record start time
        self.start_time = time.time()
        # Bind click event
        self.canvas.tag_bind(self.target_id, "<Button-1>", self._on_click)
        # Set a timeout for the round (1.5 seconds)
        self.window.after(1500, self._check_timeout)

    def _on_click(self, event: tk.Event) -> None:
        """Handle a click on the target; record success if within time."""
        if self.clicked:
            return
        self.clicked = True
        reaction_time = time.time() - self.start_time
        # Consider anything within 1.5 seconds a success (we already timed out at 1.5s)
        self.successes += 1
        # Provide quick feedback by changing colour
        try:
            self.canvas.itemconfig(self.target_id, fill="#4CAF50")
        except Exception:
            pass
        # Proceed to next round after short delay
        self.window.after(400, self._next_round)

    def _check_timeout(self) -> None:
        """Called after the round timeout to proceed if not clicked."""
        if not self.clicked:
            # Indicate miss by changing colour
            if self.target_id:
                try:
                    self.canvas.itemconfig(self.target_id, fill="#9E9E9E")
                except Exception:
                    pass
            # Short delay then next round
            self.window.after(500, self._next_round)

    def _game_over(self) -> None:
        """Display the result screen and invoke the callback."""
        won = self.successes >= self.required_successes
        self._clear_widgets()
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        if self.bg_photo:
            bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.widgets.append(bg_id)
        result_text = "VICTORIA" if won else "Derrota"
        result_color = "#4CAF50" if won else "#f44336"
        self.widgets.append(self.canvas.create_text(
            cx, cy - 60,
            text=result_text,
            font=("Arial", 36, "bold"),
            fill=result_color
        ))
        self.widgets.append(self.canvas.create_text(
            cx, cy,
            text=f"Aciertos: {self.successes}/{self.num_rounds}",
            font=("Arial", 16),
            fill="white"
        ))
        # Continue button
        btn_rect = self.canvas.create_rectangle(
            cx - 100, cy + 60, cx + 100, cy + 110,
            fill="#2196F3", outline="white", width=3
        )
        self.widgets.append(btn_rect)
        btn_text = self.canvas.create_text(
            cx, cy + 85,
            text="CONTINUAR",
            font=("Arial", 16, "bold"),
            fill="white"
        )
        self.widgets.append(btn_text)
        self.canvas.tag_bind(btn_rect, "<Button-1>", lambda e: self._close_result(won))
        self.canvas.tag_bind(btn_text, "<Button-1>", lambda e: self._close_result(won))

    def _close_result(self, won: bool) -> None:
        """Close the game window and report the result via callback."""
        if not self.game_closed:
            self.game_closed = True
            try:
                self.window.destroy()
            except Exception:
                pass
            try:
                self.callback('won' if won else 'lost')
            except Exception:
                pass

    def _clear_widgets(self) -> None:
        """Remove all drawn items from the canvas."""
        for wid in self.widgets:
            try:
                self.canvas.delete(wid)
            except Exception:
                pass
        self.widgets.clear()