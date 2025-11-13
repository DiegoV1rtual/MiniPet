#!/bin/bash
# Ejecuta Mini-Diego sin terminal
nohup python3 main.py > /dev/null 2>&1 &
echo "Mini-Diego ejecutándose en background (PID: $!)"
