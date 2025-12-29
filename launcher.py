"""
SARA - Launcher Rápido
======================
Este script muestra el splash inmediatamente y luego carga SARA.
"""

import sys
import os

# Agregar directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mostrar splash PRIMERO (antes de cualquier import pesado)
from splash_screen import crear_splash

splash = crear_splash()
splash.update_progress(10, "Iniciando SARA...", "Cargando módulos base...")

# Ahora sí, importar SARA
splash.update_progress(30, "Cargando interfaz...", "Esto puede tardar...")

from sara import SaraUltimateGUI

splash.update_progress(90, "Casi listo...", "Preparando ventana...")

# Cerrar splash y mostrar SARA
splash.close()

# Iniciar SARA
if __name__ == "__main__":
    app = SaraUltimateGUI()
    app.mainloop()
