"""
🎨 SARA - Splash Screen de Carga
=================================

Pantalla de carga visual que muestra el progreso de inicialización.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time

class SaraSplashScreen:
    """Splash screen con barra de progreso para inicialización de SARA."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SARA - Inicializando")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        
        # Centrar ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (300 // 2)
        self.root.geometry(f"500x300+{x}+{y}")
        
        # Sin bordes de ventana
        self.root.overrideredirect(True)
        
        # Fondo oscuro
        self.root.configure(bg='#1a1a2e')
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(expand=True, fill='both', padx=30, pady=30)
        
        # Logo/Título
        title = tk.Label(
            main_frame,
            text="🤖 SARA 2.0",
            font=('Segoe UI', 32, 'bold'),
            fg='#00d9ff',
            bg='#1a1a2e'
        )
        title.pack(pady=(0, 10))
        
        # Subtítulo
        subtitle = tk.Label(
            main_frame,
            text="Sistema Avanzado de Respuesta Automática",
            font=('Segoe UI', 10),
            fg='#a0a0a0',
            bg='#1a1a2e'
        )
        subtitle.pack(pady=(0, 30))
        
        # Label de estado
        self.status_label = tk.Label(
            main_frame,
            text="Iniciando...",
            font=('Segoe UI', 11),
            fg='#ffffff',
            bg='#1a1a2e'
        )
        self.status_label.pack(pady=(0, 15))
        
        # Barra de progreso
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor='#2d2d44',
            background='#00d9ff',
            bordercolor='#1a1a2e',
            lightcolor='#00d9ff',
            darkcolor='#00d9ff'
        )
        
        self.progress = ttk.Progressbar(
            main_frame,
            style="Custom.Horizontal.TProgressbar",
            length=400,
            mode='determinate'
        )
        self.progress.pack(pady=(0, 10))
        
        # Label de detalle
        self.detail_label = tk.Label(
            main_frame,
            text="",
            font=('Segoe UI', 9),
            fg='#808080',
            bg='#1a1a2e'
        )
        self.detail_label.pack()
        
        # Versión
        version_label = tk.Label(
            main_frame,
            text="v2.0 - NLU Híbrido",
            font=('Segoe UI', 8),
            fg='#505050',
            bg='#1a1a2e'
        )
        version_label.pack(side='bottom')
        
        self.is_closed = False
    
    def update_progress(self, value, status, detail=""):
        """
        Actualiza la barra de progreso y los textos.
        
        Args:
            value: Valor de 0-100
            status: Texto principal de estado
            detail: Texto de detalle (opcional)
        """
        if not self.is_closed:
            self.progress['value'] = value
            self.status_label.config(text=status)
            self.detail_label.config(text=detail)
            self.root.update()
    
    def show(self):
        """Muestra el splash screen (no bloqueante)."""
        self.root.update()
    
    def close(self):
        """Cierra el splash screen."""
        if not self.is_closed:
            self.is_closed = True
            self.root.destroy()


# Función de utilidad para usar en brain.py
def crear_splash():
    """Crea y retorna una instancia del splash screen."""
    splash = SaraSplashScreen()
    splash.show()
    return splash


if __name__ == "__main__":
    # Test
    splash = crear_splash()
    
    # Simular carga
    steps = [
        (20, "Cargando configuración...", "config.json"),
        (40, "Descargando modelo NLU...", "all-MiniLM-L6-v2 (90MB)"),
        (60, "Generando embeddings...", "1000+ ejemplos de entrenamiento"),
        (80, "Inicializando módulos...", "Voice, DevOps, Health, Games..."),
        (100, "¡Listo!", "SARA está lista para usar")
    ]
    
    for value, status, detail in steps:
        splash.update_progress(value, status, detail)
        time.sleep(1)
    
    time.sleep(1)
    splash.close()
