Este directorio contiene varias subcarpetas donde puedes colocar clips de
audio en formato `.mp3`, `.wav` u `.ogg`.  Cada carpeta corresponde a un
momento concreto del juego en el que se reproducirá un sonido al azar.

## Carpetas y cuándo se reproducen los sonidos

- **awake/** – clips que se reproducen cada 3–5 minutos mientras
  Mini‑Diego está despierto, simulando que "habla" o emite sonidos al azar.
- **eat/** – efectos de sonido al alimentar a la mascota.
- **shower/** – sonidos al duchar a la mascota.
- **sleep/** – se reproduce un clip al poner a Mini‑Diego a dormir.
- **sleep_ambient/** – sonidos ambientales que se reproducen en bucle mientras
  la mascota duerme (por ejemplo, ruido de lluvia o música relajante).
- **minigame_win/** – se reproduce un sonido al ganar un minijuego.
- **minigame_loss/** – se reproduce un sonido al perder un minijuego.
- **death/** – sonidos que se reproducen al morir Mini‑Diego.
- **game_complete/** – clips que suenan cuando el juego se completa y la
  cuenta atrás llega a cero.
- **qwer_q/**, **qwer_w/**, **qwer_e/** y **qwer_r/** – sonidos asociados a
  las teclas del antiguo minijuego QWER Hero (ya no se usa por defecto, pero
  puedes mantenerlos por si lo reactivas).

Para añadir tus propios sonidos, coloca los archivos en la carpeta
correspondiente.  Si una carpeta está vacía o la biblioteca de audio
necesaria no está instalada, se omitirá el sonido y el juego continuará
normalmente.
