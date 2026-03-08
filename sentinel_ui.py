import customtkinter as ctk
import time
import random
import asyncio
import subprocess
import platform
from sentinel_security import obtener_sentinel_security

# Importar psutil si está disponible (para CPU/RAM)
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# Importar weather_api si está disponible
try:
    from weather_api import obtener_weather
    HAS_WEATHER = True
except ImportError:
    HAS_WEATHER = False

# Importar PyAudio y numpy para audio real
try:
    import pyaudio
    import numpy as np
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False
    print("⚠️ PyAudio no disponible. Instalar con: pip install pyaudio numpy")

class SentinelProGUI:
    def __init__(self, parent_window, on_unlock_callback):
        self.parent = parent_window
        self.on_unlock = on_unlock_callback
        self.frame = None
        self.sentinel_logic = obtener_sentinel_security()
        
        # --- CACHÉ DE DATOS ---
        self._weather_cache = None
        self._weather_cache_time = 0
        self._weather_cache_ttl = 900  # 15 minutos (900 segundos)
        
        # --- PALETA ---
        self.colors = {
            "bg_main": "#050505",
            "panel_bg": "#0f0f10",
            "neon_blue": "#00F0FF",
            "neon_dim": "#004d52",
            "text_white": "#FFFFFF",
            "terminal_text": "#00FF41",
            "alert": "#FF2E63"
        }
        
        self.log_lines = [
            "Iniciando protocolo S.A.R.A v4.2...",
            "Escaneando puertos de red...",
            "Encriptación RSA-4096: OK",
            "Monitoreo biométrico: EN ESPERA",
            "Conectando con servidor seguro...",
            "Integridad del sistema: 100%",
            "Detectando intento de acceso...",
            "Modo Centinela: ACTIVO",
            "Sincronizando reloj atómico..."
        ]
        
        # --- AUDIO STREAM ---
        self.audio_stream = None
        self.p_audio = None
        if HAS_AUDIO:
            self._init_audio_stream()

    def activate(self):
        self.parent.attributes("-fullscreen", True)
        self.parent.attributes("-topmost", True)
        self.parent.protocol("WM_DELETE_WINDOW", self._prevent_close)

        self.frame = ctk.CTkFrame(self.parent, fg_color=self.colors["bg_main"], corner_radius=0)
        self.frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.frame.grid_columnconfigure(0, weight=65)
        self.frame.grid_columnconfigure(1, weight=35)
        self.frame.grid_rowconfigure(0, weight=1)

        # IZQUIERDA
        self.left_panel = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        self._build_dashboard_left()

        # DERECHA
        self.right_panel = ctk.CTkFrame(self.frame, fg_color=self.colors["panel_bg"])
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        self._build_login_right()

    def _build_dashboard_left(self):
        ctk.CTkLabel(self.left_panel, text="MODO CENTINELA", font=("Orbitron", 50, "bold"), text_color="white").pack(anchor="w", pady=(20, 0))
        ctk.CTkLabel(self.left_panel, text="● SISTEMA DE VIGILANCIA ACTIVO", font=("Segoe UI", 16, "bold"), text_color=self.colors["terminal_text"]).pack(anchor="w", pady=(0, 40))

        # Canvas para visualizador de espectro circular
        self.visualizer_canvas = ctk.CTkCanvas(
            self.left_panel,
            width=250,
            height=250,
            bg=self.colors["bg_main"],
            highlightthickness=0
        )
        self.visualizer_canvas.pack(pady=20)
        
        # Texto S.A.R.A. en el centro
        self.visualizer_canvas.create_text(
            125, 125,
            text="S.A.R.A.",
            font=("Segoe UI", 20, "bold"),
            fill=self.colors["neon_blue"],
            tags="center_text"
        )
        
        # Inicializar barras del espectro
        self.spectrum_bars = []
        self.num_bars = 32  # Número de barras alrededor del círculo
        self._create_spectrum_bars()

        self.status_label = ctk.CTkLabel(self.left_panel, text="ESPERANDO COMANDO DE VOZ...", font=("Courier New", 14), text_color=self.colors["neon_blue"])
        self.status_label.pack(pady=(10, 30))

        self.log_box = ctk.CTkTextbox(self.left_panel, fg_color="#0a0a0a", text_color=self.colors["terminal_text"], font=("Consolas", 12), height=150, corner_radius=10, border_width=1, border_color="#333")
        self.log_box.pack(fill="x", pady=20)
        self.log_box.insert("0.0", "> Inicializando sistema...\n")

        self._animate_voice_spectrum()
        self._animate_terminal_logs()

    def _build_login_right(self):
        content = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8)

        # 1. ICONO CANDADO
        ctk.CTkLabel(content, text="🔒", font=("Segoe UI Emoji", 40)).pack(pady=(0, 10))

        # 2. HEADER DE ACCESO (Sustituye al placeholder fantasma)
        ctk.CTkLabel(
            content, 
            text="AUTORIZACIÓN REQUERIDA", 
            font=("Segoe UI", 14, "bold"), 
            text_color="gray"
        ).pack(pady=(0, 5))

        # 3. ETIQUETA "INGRESE PIN" (Visible y clara encima de la caja)
        self.lbl_instruction = ctk.CTkLabel(
            content,
            text="> INGRESE CÓDIGO DE SEGURIDAD <",
            font=("Consolas", 14, "bold"),
            text_color=self.colors["neon_blue"]
        )
        self.lbl_instruction.pack(pady=(0, 10))

        # 4. CAJA DE TEXTO (Entry)
        self.pin_entry = ctk.CTkEntry(
            content,
            placeholder_text="",  # Dejamos esto vacío para evitar conflictos
            show="•",
            font=("Segoe UI", 30, "bold"),
            justify="center",
            height=60,
            fg_color="#000000",
            border_color="#333",
            corner_radius=10,
            text_color="white"
        )
        self.pin_entry.pack(fill="x", pady=(0, 20))
        self.pin_entry.bind("<Return>", self._check_pin)
        
        # IMPORTANTE: Retrasamos el foco un poco para asegurar que la UI cargue bien
        self.parent.after(100, lambda: self.pin_entry.focus_set())

        # 5. TECLADO
        pad = ctk.CTkFrame(content, fg_color="transparent")
        pad.pack(pady=10)
        keys = [['1','2','3'], ['4','5','6'], ['7','8','9'], ['C','0','⌫']]
        for r, row in enumerate(keys):
            for c, key in enumerate(row):
                cmd = lambda k=key: self.pin_entry.insert('end', k)
                fg_col, txt_col = "#1a1a1a", "white"
                if key == 'C': 
                    cmd = lambda: self.pin_entry.delete(0, 'end')
                    txt_col = self.colors["alert"]
                elif key == '⌫': 
                    cmd = lambda: self.pin_entry.delete(len(self.pin_entry.get())-1, 'end')

                ctk.CTkButton(
                    pad, text=key, width=70, height=60, 
                    font=("Segoe UI", 20, "bold"), 
                    fg_color=fg_col, hover_color="#333", 
                    text_color=txt_col, corner_radius=12, 
                    command=cmd
                ).grid(row=r, column=c, padx=5, pady=5)

        self.action_btn = ctk.CTkButton(
            content, text="DESBLOQUEAR", height=50, 
            font=("Segoe UI", 16, "bold"), 
            fg_color=self.colors["neon_blue"], text_color="black", 
            hover_color="#00B8D4", corner_radius=25, 
            command=self._check_pin
        )
        self.action_btn.pack(fill="x", pady=20)


    def _create_spectrum_bars(self):
        """Crea las barras del visualizador de espectro circular."""
        import math
        
        center_x, center_y = 125, 125
        inner_radius = 70  # Radio interno
        outer_radius = 110  # Radio externo (máximo)
        
        for i in range(self.num_bars):
            angle = (2 * math.pi * i) / self.num_bars - math.pi / 2  # Empezar arriba
            
            # Posición inicial (radio interno)
            x1 = center_x + inner_radius * math.cos(angle)
            y1 = center_y + inner_radius * math.sin(angle)
            
            # Posición final (mínima al inicio)
            x2 = center_x + (inner_radius + 5) * math.cos(angle)
            y2 = center_y + (inner_radius + 5) * math.sin(angle)
            
            # Crear línea (barra)
            bar = self.visualizer_canvas.create_line(
                x1, y1, x2, y2,
                fill=self.colors["neon_blue"],
                width=3,
                tags=f"bar_{i}"
            )
            self.spectrum_bars.append(bar)
    
    def _animate_voice_spectrum(self):
        """Anima el espectro de voz con datos simulados o reales del micrófono."""
        if not self.frame: return
        
        try:
            if not self.visualizer_canvas.winfo_exists():
                return
            
            import math
            
            center_x, center_y = 125, 125
            inner_radius = 70
            max_bar_length = 40  # Longitud máxima de las barras
            
            # Obtener niveles de audio (simulados por ahora, puedes integrar pyaudio después)
            audio_levels = self._get_audio_levels()
            
            # Actualizar cada barra
            for i, bar_id in enumerate(self.spectrum_bars):
                angle = (2 * math.pi * i) / self.num_bars - math.pi / 2
                
                # Nivel de audio para esta barra
                level = audio_levels[i % len(audio_levels)]
                bar_length = 5 + (max_bar_length * level)  # Mínimo 5px
                
                # Calcular posiciones
                x1 = center_x + inner_radius * math.cos(angle)
                y1 = center_y + inner_radius * math.sin(angle)
                x2 = center_x + (inner_radius + bar_length) * math.cos(angle)
                y2 = center_y + (inner_radius + bar_length) * math.sin(angle)
                
                # Color basado en nivel (más brillante si hay más audio)
                if level > 0.7:
                    color = self.colors["neon_blue"]
                elif level > 0.3:
                    color = "#0088AA"
                else:
                    color = self.colors["neon_dim"]
                
                # Actualizar barra
                self.visualizer_canvas.coords(bar_id, x1, y1, x2, y2)
                self.visualizer_canvas.itemconfig(bar_id, fill=color)
            
            # Repetir animación cada 50ms (20 FPS)
            self.parent.after(50, self._animate_voice_spectrum)
        except Exception:
            return
    
    
    def _init_audio_stream(self):
        """Inicializa el stream de audio del micrófono."""
        try:
            self.p_audio = pyaudio.PyAudio()
            self.audio_stream = self.p_audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=2048,
                stream_callback=None
            )
            print("✅ Micrófono inicializado - Visualizador reactivo al audio")
        except Exception as e:
            print(f"⚠️ No se pudo inicializar micrófono: {e}")
            print("   Usando modo simulación")
            self.audio_stream = None
    
    def _get_audio_levels(self):
        """Obtiene niveles de audio REALES del micrófono o simulados."""
        # Intentar obtener audio real
        if self.audio_stream and HAS_AUDIO:
            try:
                # Leer datos del micrófono
                data = self.audio_stream.read(2048, exception_on_overflow=False)
                
                # Convertir a numpy array
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Calcular FFT (Fast Fourier Transform)
                fft = np.fft.fft(audio_data)
                fft_magnitude = np.abs(fft[:len(fft)//2])
                
                # Dividir en bandas de frecuencia (32 barras)
                band_size = max(1, len(fft_magnitude) // self.num_bars)
                levels = []
                
                for i in range(self.num_bars):
                    start = i * band_size
                    end = min(start + band_size, len(fft_magnitude))
                    
                    if start < len(fft_magnitude):
                        # Energía promedio de la banda
                        band_energy = np.mean(fft_magnitude[start:end])
                        
                        # Normalizar (ajustar según tu micrófono)
                        # Valores típicos: 1000-10000 para voz normal
                        normalized = min(1.0, band_energy / 8000)
                        
                        # Suavizar (evitar barras en 0)
                        normalized = max(0.05, normalized)
                        
                        levels.append(normalized)
                    else:
                        levels.append(0.05)
                
                return levels
                
            except Exception as e:
                # Si falla, usar simulación
                pass
        
        # Fallback: Simulación (si no hay audio o falla)
        return self._get_simulated_levels()
    
    def _get_simulated_levels(self):
        """Simulación de audio (fallback)."""
        import math
        import random
        
        t = time.time() * 2
        levels = []
        
        for i in range(self.num_bars):
            base_wave = (math.sin(t + i * 0.3) + 1) / 2
            noise = random.random() * 0.3
            level = max(0, min(1, base_wave * 0.4 + noise * 0.6))
            levels.append(level)
        
        return levels

    def _animate_terminal_logs(self):
        """Muestra datos reales del sistema en el terminal."""
        if not self.frame: return
        
        try:
            # Verificar que el widget aún existe
            if not self.log_box.winfo_exists():
                return
            
            # Obtener un dato real aleatorio
            log_entry = self._get_real_system_data()
            
            if log_entry:
                timestamp = time.strftime('%H:%M:%S')
                line = f"[{timestamp}] > {log_entry}\n"
                self.log_box.insert("end", line)
                self.log_box.see("end")
            
            # Repetir cada 2-4 segundos
            self.parent.after(random.randint(2000, 4000), self._animate_terminal_logs)
        except Exception:
            # Widget destruido, detener animación
            return
    
    def _get_real_system_data(self):
        """Obtiene un dato real del sistema de forma aleatoria."""
        data_sources = []
        
        # 1. Latencia WiFi (ping)
        data_sources.append(("wifi", self._get_wifi_latency))
        
        # 2. Uso de CPU/RAM (si psutil está disponible)
        if HAS_PSUTIL:
            data_sources.append(("cpu", self._get_cpu_usage))
            data_sources.append(("ram", self._get_ram_usage))
        
        # 3. Clima (si weather_api está disponible)
        if HAS_WEATHER:
            data_sources.append(("weather", self._get_weather_data))
        
        # 4. Hora del sistema
        data_sources.append(("time", self._get_system_time))
        
        # 5. Estado de red
        data_sources.append(("network", self._get_network_status))
        
        # 6. Uptime del sistema (cuántas horas lleva encendida)
        if HAS_PSUTIL:
            data_sources.append(("uptime", self._get_system_uptime))
        
        # 7. Batería (si es laptop)
        if HAS_PSUTIL:
            data_sources.append(("battery", self._get_battery_status))
        
        # 8. Espacio en disco
        if HAS_PSUTIL:
            data_sources.append(("disk", self._get_disk_space))
        
        # 9. Logs de seguridad del Sentinel
        data_sources.append(("security", self._get_security_logs))
        
        # Seleccionar una fuente aleatoria
        if data_sources:
            source_type, source_func = random.choice(data_sources)
            try:
                return source_func()
            except Exception as e:
                return f"Error obteniendo {source_type}: {str(e)[:30]}"
        
        return "Sistema operativo"
    
    def _get_wifi_latency(self):
        """Obtiene la latencia WiFi mediante ping."""
        try:
            # Detectar sistema operativo
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            
            # Ping a Google DNS (8.8.8.8) con 1 paquete
            result = subprocess.run(
                ['ping', param, '1', '8.8.8.8'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            # Parsear latencia
            if platform.system().lower() == 'windows':
                # Buscar "tiempo=XXms" o "time=XXms"
                import re
                match = re.search(r'tiempo[=<](\d+)ms|time[=<](\d+)ms', result.stdout, re.IGNORECASE)
                if match:
                    latency = match.group(1) or match.group(2)
                    return f"Latencia WiFi: {latency}ms | Conexión estable"
            else:
                # Linux/Mac: buscar "time=XX.X ms"
                import re
                match = re.search(r'time=(\d+\.?\d*)\s*ms', result.stdout)
                if match:
                    latency = float(match.group(1))
                    return f"Latencia WiFi: {latency:.0f}ms | Conexión estable"
            
            return "Red: Conectado | Ping OK"
        except subprocess.TimeoutExpired:
            return "Red: Timeout detectado | Verificando..."
        except Exception:
            return "Red: Monitoreo activo"
    
    def _get_cpu_usage(self):
        """Obtiene el uso de CPU."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            return f"CPU: {cpu_percent:.1f}% | {psutil.cpu_count()} núcleos"
        except:
            return "CPU: Monitoreo activo"
    
    def _get_ram_usage(self):
        """Obtiene el uso de RAM."""
        try:
            ram = psutil.virtual_memory()
            used_gb = ram.used / (1024**3)
            total_gb = ram.total / (1024**3)
            return f"RAM: {used_gb:.1f}GB / {total_gb:.1f}GB ({ram.percent:.1f}%)"
        except:
            return "RAM: Monitoreo activo"
    
    
    def _get_weather_data(self):
        """Obtiene datos del clima con sistema de caché (consulta cada 15 min)."""
        try:
            # Verificar si el caché es válido
            current_time = time.time()
            cache_age = current_time - self._weather_cache_time
            
            if self._weather_cache and cache_age < self._weather_cache_ttl:
                # Usar dato cacheado
                return self._weather_cache
            
            # El caché expiró o no existe, hacer nueva consulta
            weather = obtener_weather()
            
            # Ejecutar de forma síncrona en un thread separado
            import threading
            result = [None]
            
            def fetch_weather():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result[0] = loop.run_until_complete(weather.get_current_weather())
                finally:
                    loop.close()
            
            thread = threading.Thread(target=fetch_weather, daemon=True)
            thread.start()
            thread.join(timeout=3)  # Esperar máximo 3 segundos
            
            if result[0]:
                # Extraer solo temperatura y condición (simplificado)
                import re
                match = re.search(r'(\d+)°C,\s*([^.]+)', result[0])
                if match:
                    temp, condition = match.groups()
                    weather_data = f"Clima: {temp}°C | {condition.strip()}"
                    
                    # Guardar en caché
                    self._weather_cache = weather_data
                    self._weather_cache_time = current_time
                    
                    return weather_data
                return "Clima: Consultando API..."
            else:
                # Si falla pero hay caché antiguo, usarlo
                if self._weather_cache:
                    return f"{self._weather_cache} (caché)"
                return "Clima: Timeout en consulta"
        except Exception as e:
            # Si hay error pero existe caché, usarlo
            if self._weather_cache:
                return f"{self._weather_cache} (caché)"
            return "Clima: Servicio no disponible"
    
    def _get_system_time(self):
        """Obtiene la hora del sistema."""
        now = time.localtime()
        fecha = time.strftime('%d/%m/%Y', now)
        hora = time.strftime('%H:%M:%S', now)
        return f"Sincronización temporal: {fecha} {hora}"
    
    def _get_network_status(self):
        """Obtiene el estado de la red."""
        try:
            if HAS_PSUTIL:
                net_io = psutil.net_io_counters()
                sent_mb = net_io.bytes_sent / (1024**2)
                recv_mb = net_io.bytes_recv / (1024**2)
                return f"Red: ↑{sent_mb:.1f}MB ↓{recv_mb:.1f}MB | Encriptación activa"
            else:
                return "Red: Monitoreo de tráfico activo"
        except:
            return "Red: Estado nominal"
    
    def _get_system_uptime(self):
        """Obtiene el tiempo que lleva encendida la computadora."""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            
            # Convertir a horas y minutos
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            if hours > 24:
                days = hours // 24
                hours = hours % 24
                return f"Uptime: {days}d {hours}h {minutes}m | Sistema estable"
            else:
                return f"Uptime: {hours}h {minutes}m | Sistema activo"
        except:
            return "Uptime: Monitoreo activo"
    
    def _get_battery_status(self):
        """Obtiene el estado de la batería (si es laptop)."""
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                # No es laptop o no tiene batería
                return "Energía: AC conectado | Desktop"
            
            percent = battery.percent
            plugged = battery.secsleft
            
            if battery.power_plugged:
                if percent >= 100:
                    return f"Batería: {percent}% | Carga completa"
                else:
                    return f"Batería: {percent}% | Cargando..."
            else:
                # Calcular tiempo restante
                if plugged == psutil.POWER_TIME_UNLIMITED:
                    return f"Batería: {percent}% | Descargando"
                else:
                    hours_left = plugged // 3600
                    mins_left = (plugged % 3600) // 60
                    return f"Batería: {percent}% | {hours_left}h {mins_left}m restantes"
        except:
            return "Batería: No disponible"
    
    def _get_disk_space(self):
        """Obtiene el espacio disponible en disco."""
        try:
            # Disco C: en Windows, / en Linux/Mac
            disk_path = 'C:\\' if platform.system().lower() == 'windows' else '/'
            disk = psutil.disk_usage(disk_path)
            
            free_gb = disk.free / (1024**3)
            total_gb = disk.total / (1024**3)
            percent_used = disk.percent
            
            # Alerta si queda poco espacio
            if percent_used > 90:
                return f"Disco: {free_gb:.1f}GB libres de {total_gb:.1f}GB | ⚠️ Espacio crítico"
            elif percent_used > 80:
                return f"Disco: {free_gb:.1f}GB libres de {total_gb:.1f}GB | Espacio bajo"
            else:
                return f"Disco: {free_gb:.1f}GB libres de {total_gb:.1f}GB | {percent_used:.0f}% usado"
        except:
            return "Disco: Monitoreo activo"
    
    def _get_security_logs(self):
        """Obtiene información de los logs de seguridad del Sentinel."""
        try:
            # Obtener últimos eventos del audit log
            logs = self.sentinel_logic.get_audit_log(limit=5)
            
            if not logs:
                return "Seguridad: Sin eventos recientes | Sistema limpio"
            
            # Contar eventos por tipo
            success_count = sum(1 for log in logs if log.get('success'))
            fail_count = len(logs) - success_count
            
            # Obtener el último evento
            last_event = logs[0]
            event_type = last_event.get('event_type', 'UNKNOWN')
            
            if 'FAIL' in event_type or 'LOCKED' in event_type:
                return f"Seguridad: {fail_count} intentos fallidos detectados | Alerta"
            elif 'SUCCESS' in event_type:
                return f"Seguridad: Último acceso autorizado | {len(logs)} eventos registrados"
            else:
                return f"Seguridad: {len(logs)} eventos en auditoría | Monitoreo activo"
        except:
            return "Seguridad: Auditoría activa | Sin amenazas"


    def _prevent_close(self): pass

    def _check_pin(self, event=None):
        pin = self.pin_entry.get()
        auth = self.sentinel_logic.authenticate(pin)
        if auth.success:
            self.action_btn.configure(fg_color="#00FF00", text="ACCESO CONCEDIDO")
            self.lbl_instruction.configure(text="> IDENTIDAD CONFIRMADA <", text_color="#00FF00")
            self.parent.after(1000, lambda: self._finish(True, "OK"))
        else:
            self.pin_entry.delete(0, "end")
            self.lbl_instruction.configure(text="> ERROR: PIN INVÁLIDO <", text_color=self.colors["alert"])
            self.pin_entry.configure(border_color=self.colors["alert"])
            
            # Restaurar estado después de 1.5 seg
            self.parent.after(1500, lambda: self._reset_ui_state())

    def _reset_ui_state(self):
        if not self.frame: return
        self.lbl_instruction.configure(text="> INGRESE CÓDIGO DE SEGURIDAD <", text_color=self.colors["neon_blue"])
        self.pin_entry.configure(border_color="#333")

    def _finish(self, success, msg):
        # Cerrar stream de audio si existe
        if self.audio_stream:
            try:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            except:
                pass
        if self.p_audio:
            try:
                self.p_audio.terminate()
            except:
                pass
        
        self.frame.destroy()
        self.parent.attributes("-fullscreen", False)
        if self.on_unlock: self.on_unlock(success, msg)