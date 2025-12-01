# Cómo utilizar los sprites de la mascota

Esta carpeta está destinada a contener las imágenes (sprites) que
representan la cara de Mini‑Diego en los distintos estados de ánimo
y condiciones (hambre, sueño, higiene, felicidad, etc.).  Por defecto,
si no se encuentra un archivo de imagen para un estado, el juego
dibuja un cuadrado de colores con texto.  Sin embargo, puedes
personalizar la apariencia de tu mascota colocando aquí tus propios
gráficos.

## Formato de las imágenes

- **Resolución recomendada:** 150×150 píxeles.  El juego reescalará
  las imágenes a 150 px cuadrados, pero partir de este tamaño evita
  deformaciones.
- **Formatos de archivo:** Se admiten `.png`, `.gif`, `.jpg` y `.jpeg`.
  - Para archivos GIF sólo se utiliza el primer fotograma (no hay
    animación).  Si deseas animaciones, será necesario extender el
    código.
- **Nombre del archivo:** debe coincidir exactamente con el nombre del
  estado para el que se mostrará.  Por ejemplo, para el estado
  "feliz" puedes utilizar `feliz.png` o `feliz.gif`.  Algunos
  ejemplos de nombres válidos:

  | Estado           | Nombre de archivo         |
  |------------------|----------------------------|
  | normal           | `normal.png`               |
  | hambriento       | `hambriento.png`           |
  | muy_hambriento   | `muy_hambriento.png`       |
  | gordo            | `gordo.png`                |
  | sucio            | `sucio.png`                |
  | muy_sucio        | `muy_sucio.png`            |
  | cansado          | `cansado.png`              |
  | agotado          | `agotado.png`              |
  | feliz            | `feliz.png`                |
  | muy_feliz        | `muy_feliz.png`            |
  | triste           | `triste.png`               |
  | muy_triste       | `muy_triste.png`           |
  | durmiendo        | `durmiendo.png`            |
  | enfermo          | `enfermo.png`              |
  | muriendo         | `muriendo.png`             |
  | muerte_obesidad  | `muerte_obesidad.png`      |
  | muerte_tristeza  | `muerte_tristeza.png`      |
  | muerte_sueno     | `muerte_sueno.png`         |
  | muerte_hambre    | `muerte_hambre.png`        |
  | muerte_higiene   | `muerte_higiene.png`       |

Si deseas añadir un nuevo estado, asegúrate de crear una imagen con
el nombre adecuado y modificar la función `_draw_simple_sprite` en
`main.py` para incluir ese estado en el diccionario `states_config`.

## Cómo agregar tus sprites

1. Prepara las imágenes en formato PNG con el tamaño recomendado.
2. Asigna a cada archivo el nombre de estado correspondiente (ver tabla anterior).
3. Copia o mueve los archivos a esta carpeta `assets/sprites`.
4. Ejecuta el juego (`python main.py`).  La mascota cargará los sprites
   personalizados cuando exista un archivo con el nombre del estado.

¡Listo!  Ahora Mini‑Diego mostrará tus sprites personalizados en los
momentos adecuados.