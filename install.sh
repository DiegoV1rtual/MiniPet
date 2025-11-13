#!/bin/bash
# Instalación rápida de Mini-Diego

echo "=========================================="
echo "   Mini-Diego - Instalación"
echo "=========================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "X Python3 no encontrado"
    echo "Por favor instala Python 3.7+"
    exit 1
fi

echo "+ Python encontrado: $(python3 --version)"
echo ""

# Instalar Pillow
echo "Instalando dependencias..."
pip3 install pillow

if [ $? -eq 0 ]; then
    echo "+ Pillow instalado"
else
    echo "Intentando con --user..."
    pip3 install --user pillow
fi

echo ""
echo "=========================================="
echo "   + Instalación completada"
echo "=========================================="
echo ""
echo "Para ejecutar:"
echo "  python3 main.py"
echo ""
echo "IMPORTANTE:"
echo "  - La ventana estará SIEMPRE VISIBLE"
echo "  - NO se puede cerrar con X"
echo "  - Usa Panel Admin (admin123) - Salir"
echo ""
echo "Sistema de pausa:"
echo "  - Disponible: 7h/día"
echo "  - PAUSA el contador de 168h"
echo ""
