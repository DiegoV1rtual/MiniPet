@echo off
REM ----------------------------------------------------------
REM  Ejecutable de Mini‑Diego (Windows)
REM  Este script intenta instalar las dependencias necesarias
REM  (Pillow y playsound) y luego inicia el juego sin abrir
REM  una ventana de consola.
REM ----------------------------------------------------------

echo ==========================================
echo    Preparando Mini‑Diego...
echo ==========================================

REM Intentar instalar dependencias de Python de forma silenciosa
for %%I in (pillow playsound) do (
    echo Instalando %%I...
    python -m pip install %%I --quiet
)

echo Dependencias instaladas.
echo Iniciando juego...

REM Ejecutar el juego con pythonw para ocultar consola
start "" pythonw main.py
