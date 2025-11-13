# Mini-Diego - Tamagotchi Virtual

Mascota virtual que debes mantener viva durante 168 horas (7 días).

## Instalación

### Windows
```cmd
install.bat
python main.py
```

### Linux/Mac
```bash
chmod +x install.sh
./install.sh
python3 main.py
```

## Características

- **4 Estadísticas**: Hambre, Sueño, Higiene, Felicidad
- **Contador de 168h**: Sobrevive 7 días completos
- **Sistema de pausa**: 7 horas disponibles diarias
- **3 Minijuegos**: Quiz, Memoria, Stroop (todos centrados)
- **5 Formas de morir**: Cada una con sprite específico
- **Mascota flotante**: Se sobrepone a toda la pantalla

## Controles

- **Alimentar**: +10% hambre
- **Duchar**: +40% higiene
- **Dormir/Despertar**: Control total - duerme y despierta cuando quieras
  - Gana 1.43% sueño por minuto (100% en 7h)
  - Sin penalizaciones por dormir/despertar
- **Admin**: Código `admin123`

## Importante

- **NO hay guardado automático**: Si cierras el juego o la mascota muere, el tiempo vuelve a empezar
- **Dormir es libre**: Puedes poner a dormir y despertar a Mini-Diego cuando quieras
- Cada muerte reinicia el contador de 168 horas

## Objetivo

Mantén vivo a Mini-Diego durante 168 horas sin que ninguna stat llegue a 0% o hambre supere 90%.

## Sprites

Coloca sprites PNG (150x150px) en `assets/sprites/`:
- Estados: normal, hambriento, gordo, sucio, cansado, feliz, triste, etc.
- Muertes: muerte_hambre, muerte_obesidad, muerte_sueno, muerte_higiene, muerte_tristeza

Sin sprites, el juego usa cuadrados de colores automáticamente.
