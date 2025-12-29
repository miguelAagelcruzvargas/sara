"""
🎨 SARA - Splash Screen de Carga
=================================

Pantalla de carga visual que muestra el progreso de inicialización.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from pathlib import Path

class SaraSplashScreen:
    """Splash screen con barra de progreso para inicialización de SARA."""
    
    def __init__(self, is_first_time=False):
        self.root = tk.Tk()
        self.root.title("SARA - Inicializando")
        self.root.geometry("600x400" if is_first_time else "600x350")
        self.root.resizable(False, False)
        
        # Centrar ventana
        self.root.update_idletasks()
        width = 600
        height = 400 if is_first_time else 350
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Sin bordes de ventana
        self.root.overrideredirect(True)
        
        # Siempre al frente (para que no se oculte)
        self.root.attributes('-topmost', True)
        
        # Fondo con gradiente simulado (oscuro elegante)
        self.root.configure(bg='#0f0f23')
        
        # Frame principal con borde redondeado simulado
        main_frame = tk.Frame(self.root, bg='#0f0f23')
        main_frame.pack(expand=True, fill='both', padx=0, pady=0)
        
        # Frame interno con padding
        content_frame = tk.Frame(main_frame, bg='#0f0f23')
        content_frame.pack(expand=True, fill='both', padx=40, pady=40)
        
        # Logo/Título con mejor tipografía
        title = tk.Label(
            content_frame,
            text="S.A.R.A",
            font=('Segoe UI', 48, 'bold'),
            fg='#00d9ff',
            bg='#0f0f23'
        )
        title.pack(pady=(0, 5))
        
        # Subtítulo más elegante
        subtitle = tk.Label(
            content_frame,
            text="Sistema Avanzado de Respuesta Automática",
            font=('Segoe UI', 11),
            fg='#7c8db5',
            bg='#0f0f23'
        )
        subtitle.pack(pady=(0, 20))
        
        # Mensaje de bienvenida (solo primera vez) - Más compacto
        if is_first_time:
            welcome_frame = tk.Frame(content_frame, bg='#1a1f3a', relief='flat', bd=0)
            welcome_frame.pack(pady=(0, 25), fill='x', ipady=20)
            
            welcome_msg = tk.Label(
                welcome_frame,
                text="✨ ¡Bienvenido a tu asistente inteligente!\n\nPreparando todo para ti...",
                font=('Segoe UI', 12),
                fg='#ffffff',
                bg='#1a1f3a',
                justify='center'
            )
            welcome_msg.pack()
        
        # Label de estado - Más prominente
        self.status_label = tk.Label(
            content_frame,
            text="Iniciando...",
            font=('Segoe UI', 13, 'bold'),
            fg='#ffffff',
            bg='#0f0f23'
        )
        self.status_label.pack(pady=(0, 15))
        
        # Barra de progreso moderna
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Modern.Horizontal.TProgressbar",
            troughcolor='#1a1f3a',
            background='#00d9ff',
            bordercolor='#0f0f23',
            lightcolor='#00d9ff',
            darkcolor='#00b8d4',
            thickness=8
        )
        
        self.progress = ttk.Progressbar(
            content_frame,
            style="Modern.Horizontal.TProgressbar",
            length=500,
            mode='determinate'
        )
        self.progress.pack(pady=(0, 12))
        
        # Label de detalle - Más sutil
        self.detail_label = tk.Label(
            content_frame,
            text="",
            font=('Segoe UI', 10),
            fg='#5a6b8c',
            bg='#0f0f23'
        )
        self.detail_label.pack()
        
        # Versión - Más discreta
        version_label = tk.Label(
            content_frame,
            text="v2.0",
            font=('Segoe UI', 9),
            fg='#3a4b6c',
            bg='#0f0f23'
        )
        version_label.pack(side='bottom', pady=(20, 0))
        
        self.is_closed = False
        self.auto_close_scheduled = False
    
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
            
            # Auto-cerrar cuando llegue al 100%
            if value >= 100 and not self.auto_close_scheduled:
                self.auto_close_scheduled = True
                self.root.after(800, self.close)  # Cerrar después de 0.8 segundos
    
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
    # Detectar si es primera vez (si no existe el cache de embeddings)
    from pathlib import Path
    cache_file = Path(__file__).parent / ".sara_models" / "intent_embeddings.pkl"
    is_first_time = not cache_file.exists()
    
    splash = SaraSplashScreen(is_first_time=is_first_time)
    splash.show()
    return splash


if __name__ == "__main__":
    # Test - Mostrar splash y esperar a que lo cierres manualmente
    print("Mostrando splash screen de bienvenida (primera vez)...")
    print("Cierra la ventana manualmente para terminar el test.")
    
    splash = SaraSplashScreen(is_first_time=True)
    splash.show()
    
    # Simular carga
    steps = [
        (20, "Cargando configuración...", "config.json"),
        (40, "Descargando modelo NLU...", "all-MiniLM-L6-v2 (90MB)"),
        (60, "Generando embeddings...", "1000+ ejemplos de entrenamiento"),
        (80, "Inicializando módulos...", "Voice, DevOps, Health, Games..."),
        (100, "¡Listo!", "SARA está lista para usar")
    ]
    
    import threading
    def simulate_loading():
        for value, status, detail in steps:
            splash.update_progress(value, status, detail)
            time.sleep(1.5)
        # NO cerrar automáticamente, dejar que el usuario cierre manualmente
    
    # Ejecutar simulación en hilo separado
    threading.Thread(target=simulate_loading, daemon=True).start()
    
    # Mantener ventana abierta hasta que la cierres manualmente
    try:
        splash.root.mainloop()
    except:
        pass
