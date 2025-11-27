# Configuración del juego Mini-Diego

# Intervalos de tiempo (en segundos)
# Ajustes de tiempo para la versión de 24 horas.
# Los minijuegos aparecen cada 15 minutos independientemente de otras condiciones.
EVENT_INTERVAL_MIN = 900
EVENT_INTERVAL_MAX = 900
POPUP_RESPONSE_TIMEOUT = 60
MINIGAME_ANSWER_TIMEOUT = 6

# Admin
ADMIN_CODE = "admin123"

# Desgaste de estadísticas
# Incrementamos el desgaste de estadísticas para que el juego de 24h siga siendo desafiante.
# Multiplicamos los valores originales por ~7 (168h/24h) para mantener la dificultad.
HUNGER_DECAY_PER_HOUR = 35
SLEEP_DECAY_PER_HOUR = 105
HYGIENE_DECAY_PER_2HOURS = 70
SLEEP_DECAY_REDUCTION = 0.80

# Sistema de sueño por MINUTO
SLEEP_GAIN_PER_MINUTE = 1.43  # 100% en 7 horas (420 minutos) = ~1.43% por minuto
SLEEP_OPTIMAL_HOURS = 7        # Después de 7 horas empieza a ganar puntos

# Límites
HUNGER_DEATH_MIN = 0
HUNGER_DEATH_MAX = 90
SLEEP_MIN_HOURS = 7
HAPPINESS_PENALTY_OVERSLEEP = 10
HAPPINESS_PENALTY_SKIP_GAME = 25

# Acciones
FEED_INCREASE = 10
SHOWER_INCREASE = 40
SLEEP_RESTORE = 100

# Protección sueño
SLEEP_PROTECTION = True

# Configuración de ventana
ALWAYS_ON_TOP = True
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Movimiento
PET_MOVE_STEPS = 60
PET_MOVE_DELAY = 0.02
PET_MOVE_MIN_INTERVAL = 8
PET_MOVE_MAX_INTERVAL = 20

# Pausa
# La funcionalidad de pausa se ha eliminado en la versión de 24 horas.  El
# siguiente valor ya no se utiliza, pero se deja definido a cero por
# compatibilidad con código antiguo.
PAUSE_TIME_LIMIT = 0

# Colores del panel (ALEGRES)
PANEL_COLORS = {
    'hambre': '#FF6B6B',      # Rojo brillante
    'sueno': '#4ECDC4',       # Cian alegre
    'higiene': '#95E1D3',     # Verde agua
    'felicidad': '#FFE66D'    # Amarillo brillante
}

# Mensajes de muerte
DEATH_MESSAGES = [
    "Realmente dejaste morir a Mini-Diego de hambre. Que clase de padre eres.",
    "Mini-Diego murio por tu negligencia. No merecías ser su cuidador.",
    "Fallaste en lo mas basico: mantenerlo vivo. Patético.",
    "Mini-Diego sufrio hasta su ultimo momento. Esto es culpa tuya.",
    "No pudiste cuidar de una simple mascota virtual. Decepcionante.",
    "Mini-Diego confiaba en ti y lo abandonaste. Debería darte vergüenza.",
    "Tu irresponsabilidad mató a Mini-Diego. Reflexiona sobre eso.",
    "No merecías la confianza de Mini-Diego. Lo dejaste morir solo.",
    "Mini-Diego paso sus ultimas horas esperando tu ayuda. Nunca llegó.",
    "Eres la razon por la que Mini-Diego ya no existe. Buen trabajo.",
    "Mini-Diego merecía alguien mejor. Tu no estuviste a la altura.",
    "Fallaste como cuidador. Mini-Diego pago el precio de tu incompetencia.",
    "No supiste valorar a Mini-Diego hasta que fue demasiado tarde.",
    "Mini-Diego te necesitaba y tu simplemente no estuviste ahí."
]
