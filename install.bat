@echo off
echo ==========================================
echo    Mini-Diego - Instalacion
echo ==========================================
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python no encontrado
    echo Por favor instala Python 3.7+
    pause
    exit /b 1
)

echo + Python encontrado
python --version
echo.

:: Instalar Pillow
echo Instalando dependencias...
pip install pillow

if errorlevel 1 (
    echo Intentando con --user...
    pip install --user pillow
)

echo.
echo ==========================================
echo    + Instalacion completada
echo ==========================================
echo.
echo Para ejecutar:
echo   python main.py
echo.
echo IMPORTANTE:
echo   - La ventana estara SIEMPRE VISIBLE
echo   - NO se puede cerrar con X
echo   - Usa Panel Admin (admin123) - Salir
echo.
echo Sistema de pausa:
echo   - Disponible: 7h/dia
echo   - PAUSA el contador de 168h
echo.
pause
