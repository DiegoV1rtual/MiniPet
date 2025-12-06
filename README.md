# Mini‑Diego – Tamagotchi virtual (versión 12 horas)

Esta carpeta contiene el código fuente y los recursos necesarios para
ejecutar **Mini‑Diego**, una mascota virtual inspirada en los
tamagotchis.  El objetivo del juego es cuidar de Mini‑Diego durante
12 horas reales sin que ninguna de sus estadísticas (hambre, sueño,
higiene y felicidad) llegue a cero ni que el hambre supere el 90 %.

## Ejecución

1. **Descarga y descomprime** este proyecto en una carpeta de tu ordenador.
2. Asegúrate de tener **Python 3.7 o superior** instalado.
3. En Windows, simplemente ejecuta el script **`ejecutame.bat`**
   haciendo doble clic; se encarga de instalar las dependencias básicas
   (Pillow y playsound) e inicia el juego sin abrir consola.
4. En Linux/Mac, puedes instalar las dependencias manualmente con:

   ```bash
   python3 -m pip install pillow playsound
   ```

   y luego lanzar el juego con:

   ```bash
   python3 main.py
   ```

El juego crea una ventana flotante con la mascota y otra ventana de
control donde podrás alimentar, duchar y hacer dormir a Mini‑Diego.
El **panel de administrador** se abre introduciendo la clave
`admin123` y permite forzar minijuegos, restaurar estadísticas,
manipular el temporizador e incluso forzar la victoria.

## Normas básicas

- **Alimentar** (+10 % de hambre) mantiene a Mini‑Diego satisfecho.
- **Dormir** (+6 % de sueño por minuto) recupera el sueño; no lo
  dejes dormido más de 6 horas seguidas o perderá felicidad.
- **Duchar** (+40 % de higiene) previene enfermedades.
- **Minijuegos**: acepta jugar para ganar felicidad; saltarlos penaliza
  la felicidad.
- Si cualquiera de las barras llega a 0 % o si el hambre supera 90 %,
  Mini‑Diego morirá y tendrás que empezar de nuevo.
- Al completar las 12 horas, se mostrará una pantalla de victoria con
  un mensaje especial y podrás cerrar el juego.

## Personalización de sprites

Puedes personalizar la apariencia de la mascota colocando imágenes o
GIFs en la carpeta `assets/sprites/`.  Utiliza como nombre de
archivo el estado correspondiente (por ejemplo, `feliz.png` o
`feliz.gif`).  Se admiten formatos `.png`, `.gif`, `.jpg` y `.jpeg`.
Para más detalles, consulta `assets/sprites/README.md`.

## Fondos de victoria

Para poner un fondo personalizado en la pantalla de felicitación,
coloca una imagen en la carpeta `assets/backgrounds/`.  El juego
tomará la primera imagen que encuentre (PNG, JPG o GIF) y la
redimensionará automáticamente al tamaño de la ventana de victoria.

Disfruta cuidando de Mini‑Diego y ¡buena suerte!