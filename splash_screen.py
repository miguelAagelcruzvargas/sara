"""
🎨 SARA - ULTRA SPLASH SCREEN (Neural Core Edition)
===================================================
Diseño generativo avanzado con sistema de partículas,
efectos de neón y animaciones matemáticas fluidas.
"""

import tkinter as tk
import math
import random
import threading
import time

# --- PALETA DE COLORES "CYBER-VOID" ---
C = {
    'bg': '#050510',        # Negro profundo
    'primary': '#00F3FF',   # Cyan Eléctrico
    'secondary': '#BC13FE', # Magenta Neón
    'text': '#E0E0FF',      # Blanco azulado
    'text_sub': '#8888AA',  # Gris azulado (CORREGIDO: Faltaba este color)
    'dim': '#2A2A40',       # Gris oscuro para estructuras
    'grid': '#0A0A15'       # Color de la retícula de fondo
}

class Particle:
    """Representa un nodo de la red neuronal"""
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        self.vx = random.uniform(-0.5, 0.5) # Velocidad X
        self.vy = random.uniform(-0.5, 0.5) # Velocidad Y
        self.size = random.uniform(1, 3)
    
    def move(self):
        self.x += self.vx
        self.y += self.vy
        
        # Rebotar en bordes
        if self.x <= 0 or self.x >= self.w: self.vx *= -1
        if self.y <= 0 or self.y >= self.h: self.vy *= -1

class SaraUltraSplash:
    def __init__(self):
        self.root = tk.Tk()
        self.width = 700
        self.height = 400
        
        # Configuración de ventana
        self._setup_window()
        
        # --- CANVAS PRINCIPAL ---
        self.canvas = tk.Canvas(
            self.root, width=self.width, height=self.height,
            bg=C['bg'], highlightthickness=0
        )
        self.canvas.pack(fill='both', expand=True)
        
        # --- SISTEMA DE PARTÍCULAS ---
        self.particles = [Particle(self.width, self.height) for _ in range(45)]
        
        # Estado de carga
        self.loading_value = 0
        self.loading_text = "INITIALIZING..."
        self.log_lines = []
        self.is_running = True
        
        # Iniciar loop de animación
        self._animate()
        
    def _setup_window(self):
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws/2) - (self.width/2)
        y = (hs/2) - (self.height/2)
        self.root.geometry('%dx%d+%d+%d' % (self.width, self.height, x, y))
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg=C['bg'])
        
        # Crear borde brillante de ventana
        frame = tk.Frame(self.root, bg=C['primary'])
        frame.place(x=0, y=0, width=self.width, height=2) # Top border glow
        
        # Botón de minimizar (esquina superior derecha)
        minimize_btn = tk.Label(
            self.root,
            text="─",
            font=("Segoe UI", 16, "bold"),
            fg=C['text'],
            bg=C['bg'],
            cursor="hand2"
        )
        minimize_btn.place(x=self.width-30, y=5, width=25, height=25)
        minimize_btn.bind("<Button-1>", lambda e: self.root.iconify())
        
        # Hover effect para el botón
        minimize_btn.bind("<Enter>", lambda e: minimize_btn.config(fg=C['primary']))
        minimize_btn.bind("<Leave>", lambda e: minimize_btn.config(fg=C['text']))

    def _draw_neural_network(self):
        """Dibuja nodos y conexiones si están cerca"""
        c = self.canvas
        # Limpiar canvas
        c.delete("neural") 
        
        for p in self.particles:
            p.move()
            # Dibujar nodo
            c.create_oval(
                p.x-p.size, p.y-p.size, p.x+p.size, p.y+p.size,
                fill=C['primary'], outline='', tags="neural"
            )
            
            # Conectar con vecinos cercanos
            for other in self.particles:
                dist = math.hypot(p.x - other.x, p.y - other.y)
                if dist < 80: # Si están cerca, conectar
                    # Simulamos transparencia con grosor y color grisáceo
                    width = (1 - dist/80) * 1.5
                    c.create_line(
                        p.x, p.y, other.x, other.y,
                        fill=C['dim'] if dist > 50 else '#224466',
                        width=width, tags="neural"
                    )

    def _draw_interface(self):
        """Dibuja la UI estática y dinámica superior"""
        c = self.canvas
        c.delete("ui")
        
        cx, cy = self.width - 100, self.height - 80 # Centro del loader
        radius = 40
        
        # 1. TÍTULO GRANDE
        c.create_text(
            40, 60, text="S.A.R.A.", 
            font=("Segoe UI", 48, "bold"), fill=C['text'], anchor="w", tags="ui"
        )
        c.create_text(
            40, 100, text="SYSTEM v2.0 // NEURAL CORE ACTIVE", 
            font=("Consolas", 10), fill=C['primary'], anchor="w", tags="ui"
        )
        
        # MENSAJE DE BIENVENIDA (solo al 0%)
        if self.loading_value == 0:
            welcome_y = 160
            c.create_text(
                40, welcome_y, 
                text="✨ ¡Bienvenido a tu asistente inteligente!",
                font=("Segoe UI", 14, "bold"), fill=C['primary'], anchor="w", tags="ui"
            )
            c.create_text(
                40, welcome_y + 30,
                text="Preparando todo para ti...",
                font=("Segoe UI", 11), fill=C['text_sub'], anchor="w", tags="ui"
            )
            c.create_text(
                40, welcome_y + 55,
                text="Esto puede tardar unos segundos la primera vez.",
                font=("Segoe UI", 9), fill=C['dim'], anchor="w", tags="ui"
            )
        else:
            # 2. LOG DE CONSOLA (Estilo Hacker) - Solo cuando ya empezó a cargar
            y_start = 160
            # Mostrar últimas 6 líneas
            current_logs = self.log_lines[-6:]
            
            for i, line in enumerate(current_logs): 
                # Lógica de colores corregida:
                # La última línea (i==5 si hay 6) es brillante
                # Las anteriores se van apagando
                is_last = (i == len(current_logs) - 1)
                
                if is_last:
                    color = C['text']
                elif i > len(current_logs) - 3:
                    color = C['text_sub'] # Aquí usamos el color que faltaba
                else:
                    color = '#444455'
                    
                c.create_text(
                    45, y_start + (i*20),
                    text=f"> {line}",
                    font=("Consolas", 9), fill=color, anchor="w", tags="ui"
                )

        # 3. LOADER CIRCULAR (Arcos)
        # Fondo del anillo
        c.create_oval(
            cx-radius, cy-radius, cx+radius, cy+radius,
            outline=C['dim'], width=4, tags="ui"
        )
        
        # Arco de progreso
        angle = (self.loading_value / 100) * 360
        if angle > 0:
            c.create_arc(
                cx-radius, cy-radius, cx+radius, cy+radius,
                start=90, extent=-angle, style='arc',
                outline=C['primary'], width=4, tags="ui"
            )
            
        # Brillo decorativo rotando (simulado)
        rot = (time.time() * 200) % 360
        rad_dec = radius + 8
        dx = math.cos(math.radians(rot)) * rad_dec
        dy = math.sin(math.radians(rot)) * rad_dec
        c.create_oval(
            cx+dx-2, cy+dy-2, cx+dx+2, cy+dy+2,
            fill=C['secondary'], outline='', tags="ui"
        )

        # Texto porcentaje
        c.create_text(
            cx, cy, text=f"{int(self.loading_value)}%",
            font=("Segoe UI", 12, "bold"), fill=C['text'], tags="ui"
        )
        
        # Estado texto
        c.create_text(
            cx, cy + 60, text=self.loading_text,
            font=("Segoe UI", 8), fill=C['text'], tags="ui"
        )

    def _animate(self):
        if not self.is_running: return
        
        try:
            self._draw_neural_network()
            self._draw_interface()
        except Exception as e:
            print(f"Error en animación: {e}")
        
        # Llamar al siguiente frame (aprox 60 FPS)
        if self.is_running:
            self.root.after(16, self._animate)

    def update_status(self, value, text, detail=None):
        """Actualiza el estado del splash (método interno)"""
        self.loading_value = value
        self.loading_text = text
        if detail:
            self.log_lines.append(detail)
        
        # Auto-cerrar cuando llegue al 100%
        if value >= 100 and self.is_running:
            self.root.after(1200, self.close)  # Cerrar después de 1.2 segundos
    
    def update_progress(self, value, status, detail=""):
        """
        Método de compatibilidad para brain.py y sara.py
        
        Args:
            value: Valor de 0-100
            status: Texto principal de estado
            detail: Texto de detalle (opcional)
        """
        self.update_status(value, status, detail if detail else None)
        self.root.update()  # Forzar actualización de UI
    
    def show(self):
        """Muestra el splash screen (compatibilidad con código anterior)"""
        self.root.update()
    
    def close(self):
        # Efecto de cierre "TV apagándose"
        if not self.is_running: return
        
        try:
            for i in range(10):
                h = self.height * (1 - (i/10))
                w = self.width * (1 + (i/20)) # Se ensancha un poco al cerrarse
                
                # Evitar geometría inválida
                if h < 1: h = 1
                if w < 1: w = 1
                
                ws = self.root.winfo_screenwidth()
                hs = self.root.winfo_screenheight()
                x = (ws/2) - (w/2)
                y = (hs/2) - (h/2)
                
                self.root.geometry('%dx%d+%d+%d' % (int(w), int(h), int(x), int(y)))
                self.root.update()
                time.sleep(0.02)
            
            self.is_running = False
            self.root.destroy()
        except tk.TclError:
            pass # La ventana ya se cerró

# --- Helper para integrarlo en tu sistema principal ---
def crear_splash():
    """Crea la instancia para usar desde brain.py y sara.py"""
    splash = SaraUltraSplash()
    splash.show()
    return splash

# --- SIMULACIÓN DE ARRANQUE (Solo si ejecutas este archivo directo) ---
if __name__ == "__main__":
    app = SaraUltraSplash()
    
    def loader_logic():
        # Secuencia de carga simulada con "logs" técnicos
        sequences = [
            (5, "BOOT_SEQUENCE", "Verificando integridad de memoria..."),
            (12, "LOADING_KERNEL", "Cargando torch_cuda_backend.dll"),
            (25, "NEURAL_HANDSHAKE", "Estableciendo conexión sináptica"),
            (38, "LOADING_MODELS", "Cargando Weights: all-MiniLM-L6-v2"),
            (45, "LOADING_MODELS", "Descomprimiendo tensores (FP16)..."),
            (58, "INIT_AUDIO", "PyAudio Stream: 44100Hz / Stereo"),
            (70, "SECURITY_CHECK", "Validando tokens de API..."),
            (82, "SYNCING_DB", "Conectando a Second Brain (SQLite)"),
            (95, "FINALIZING", "Optimizando UI rendering..."),
            (100, "SYSTEM_READY", "S.A.R.A. está en línea.")
        ]
        
        try:
            for val, text, log in sequences:
                if not app.is_running: break
                
                # Interpolación suave
                current = app.loading_value
                while current < val:
                    if not app.is_running: break
                    current += 1
                    app.update_status(current, text)
                    time.sleep(random.uniform(0.01, 0.03))
                
                app.update_status(val, text, log)
                time.sleep(random.uniform(0.4, 0.8))
            
            time.sleep(1)
            app.close()
        except Exception as e:
            print(f"Error en loading: {e}")

    threading.Thread(target=loader_logic, daemon=True).start()
    app.root.mainloop()