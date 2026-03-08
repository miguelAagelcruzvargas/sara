import customtkinter as ctk
import speech_recognition as sr
import threading
import datetime 
import logging
import logging
import time
import ctypes # Para controlar energía

import os
import difflib  # Para fuzzy matching de wake words
import math  # Para animaciones de ondas
import pyaudio  # Para captura de audio en tiempo real
import struct  # Para procesar datos de audio


# Configuración de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

VERSION = "3.0.4"
MAX_CHARS_VOZ = 200
VOICE_TIMEOUT = 5.0       # Aumentado de 1.5 a 5.0 para no cortar
VOICE_PHRASE_LIMIT = 15   # Aumentado de 10 a 15 para frases largas
VOICE_AMBIENT_DURATION = 0.5 
VOICE_SLEEP_WHILE_TALKING = 0.1 

# Importar módulos necesarios globalmente
from config import ConfigManager
from devops import DevOpsManager

class SaraUltimateGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Importar brain directamente (como antes)
        from brain import SaraBrain
        
        # Inicializar brain
        self.brain = SaraBrain()
        
        self.is_listening = False
        self.visualizer_running = False
        self.audio_level = 0  # Nivel de audio actual (0-100)
        self.audio_stream = None  # Stream de PyAudio

        # Configuración Ventana (COMPACTA Y MODERNA)
        self.title(f"S.A.R.A. {VERSION}")
        self.geometry("480x420")  # Más compacta pero elegante
        self.minsize(450, 380)  # Tamaño mínimo
        ctk.set_appearance_mode("Dark")
        
        # Colores modernos
        self._setup_colors()
        
        # Configurar tema personalizado
        self.configure(fg_color=self.COLORS["bg_primary"])
        
        # --- HEADER COMPACTO ---
        self.setup_header()
        
        # --- TABVIEW (Pestañas Modernas) ---
        self.tabview = ctk.CTkTabview(
            self, 
            fg_color=self.COLORS["bg_primary"],
            segmented_button_fg_color=self.COLORS["bg_secondary"],
            segmented_button_selected_color=self.COLORS["accent"],
            segmented_button_selected_hover_color=self.COLORS["accent_hover"],
            segmented_button_unselected_color=self.COLORS["bg_elevated"],
            segmented_button_unselected_hover_color=self.COLORS["bg_hover"],
            text_color=self.COLORS["text_primary"],
            corner_radius=10
        )
        self.tabview.pack(padx=8, pady=(0, 8), fill="both", expand=True)
        
        self.tab_chat = self.tabview.add("💬")
        self.tab_config = self.tabview.add("⚙️")
        self.tab_dev = self.tabview.add("🛠️")
        self.tab_network = self.tabview.add("🌐")

        # --- PESTAÑAS ---
        self.setup_chat_tab()  
        self.setup_config_tab()
        self.setup_dev_tab()
        self.setup_network_tab()

        self.actualizar_estado_global()
        
        from devops import DevOpsManager
        self.log("SYS", f"✅ Sistema {VERSION} Inicializado.", "sys")
        self.log("SYS", f"📂 Dir: {DevOpsManager.WORK_DIR}", "dev")
        
        if not self.brain.ia_online:
            self.log("SARA", "💡 Escribe 'configura' para activar la IA.", "sys")
        else:
            # Usar mensaje personalizado del perfil
            saludo = self.brain.perfil.get_welcome_message() if self.brain.perfil else "👋 Hola! Soy SARA. ¿En qué trabajamos hoy?"
            self.log("SARA", saludo, "sara")
            self.brain.voz.hablar(saludo)
    
    def _setup_colors(self):
        """Define la paleta de colores moderna y premium"""
        self.COLORS = {
            # Principales (más vibrantes)
            "accent": "#00E5FF",  # Cyan más brillante
            "accent_hover": "#00B8D4",
            "accent_glow": "#00E5FF40",  # Glow effect
            "secondary": "#8B5CF6",  # Púrpura más suave
            "success": "#10B981",  # Verde más moderno
            "error": "#EF4444",  # Rojo más suave
            "warning": "#F59E0B",  # Ámbar moderno
            
            # Fondos (más profundos y elegantes)
            "bg_primary": "#0F172A",  # Azul muy oscuro (slate-900)
            "bg_secondary": "#1E293B",  # slate-800
            "bg_elevated": "#334155",  # slate-700
            "bg_hover": "#475569",  # slate-600
            "bg_card": "#1E293B",  # Para tarjetas
            
            # Textos (mejor contraste)
            "text_primary": "#F8FAFC",  # Casi blanco
            "text_secondary": "#CBD5E1",  # Gris claro
            "text_disabled": "#64748B",  # Gris medio
            "text_muted": "#94A3B8",  # Gris suave
        }
    
    def setup_header(self):
        """Header compacto y elegante"""
        header = ctk.CTkFrame(
            self,
            height=45,
            fg_color=self.COLORS["bg_secondary"],
            corner_radius=0
        )
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # Logo/Título a la izquierda (más elegante)
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=15, pady=8)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="SARA",
            font=("Inter", 16, "bold"),
            text_color=self.COLORS["accent"]
        )
        title_label.pack(side="left", padx=(0, 8))
        
        ver_label = ctk.CTkLabel(
            title_frame,
            text=f"v{VERSION}",
            font=("Inter", 9),
            text_color=self.COLORS["text_muted"]
        )
        ver_label.pack(side="left")
        
        # Estado a la derecha (más compacto)
        status_frame = ctk.CTkFrame(header, fg_color="transparent")
        status_frame.pack(side="right", padx=15, pady=8)
        
        self.header_status = ctk.CTkLabel(
            status_frame,
            text="● ONLINE",
            font=("Inter", 10, "bold"),
            text_color=self.COLORS["success"]
        )
        self.header_status.pack(side="right")

    def setup_chat_tab(self):
        # Frame principal (más compacto)
        main_frame = ctk.CTkFrame(
            self.tab_chat, 
            fg_color="transparent"
        )
        main_frame.pack(fill="both", expand=True, padx=6, pady=6)

        # Área de Chat (compacta y elegante)
        self.chat = ctk.CTkTextbox(
            main_frame,
            width=350,
            height=220,  # Más compacta
            state="disabled",
            font=("Segoe UI", 10),  # Fuente más legible
            fg_color=self.COLORS["bg_card"],
            text_color=self.COLORS["text_primary"],
            border_width=1,
            border_color=self.COLORS["bg_elevated"],
            corner_radius=12,
            scrollbar_button_color=self.COLORS["accent"],
            scrollbar_button_hover_color=self.COLORS["accent_hover"]
        )
        self.chat.pack(fill="both", expand=True, pady=(0, 8))
        
        # Tags de colores modernos
        tags = {
            "tu": self.COLORS["secondary"],
            "sara": self.COLORS["accent"],
            "dev": self.COLORS["warning"],
            "error": self.COLORS["error"],
            "sys": self.COLORS["text_secondary"],
            "ai": self.COLORS["success"]
        }
        for k, v in tags.items(): 
            self.chat.tag_config(k, foreground=v)
            
        # WORKAROUND: CTk forbids font in tag_config. We access the underlying Tkinter Text widget.
        # This allows us to have bold text.
        try:
            self.chat._textbox.tag_config("bold", font=("Segoe UI", 10, "bold"))
        except Exception as e:
            print(f"Warning: Could not configure bold font: {e}")

        # Área de Entrada Moderna y Compacta
        input_container = ctk.CTkFrame(
            main_frame, 
            fg_color=self.COLORS["bg_card"],
            corner_radius=16,
            height=52,
            border_width=1,
            border_color=self.COLORS["bg_elevated"]
        )
        input_container.pack(fill="x", pady=(0, 0))
        input_container.pack_propagate(False)
        
        self.entry = ctk.CTkEntry(
            input_container,
            placeholder_text="Escribe o habla...",
            height=40,
            font=("Segoe UI", 11),
            border_width=0,
            corner_radius=12,
            fg_color="transparent",
            text_color=self.COLORS["text_primary"],
            placeholder_text_color=self.COLORS["text_muted"]
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=12, pady=6)
        self.entry.bind("<Return>", self.enviar)
        
        # Botones modernos y elegantes
        buttons_frame = ctk.CTkFrame(input_container, fg_color="transparent")
        buttons_frame.pack(side="right", padx=8, pady=6)
        
        # Botón Adjuntar Archivo (PDF)
        self.btn_file = ctk.CTkButton(
            buttons_frame,
            text="📎",
            width=42,
            height=40,
            command=self.seleccionar_archivo,
            font=("Segoe UI Emoji", 18),
            fg_color=self.COLORS["bg_elevated"],
            hover_color=self.COLORS["warning"],
            corner_radius=12,
            text_color=self.COLORS["text_primary"],
            border_width=0
        )
        self.btn_file.pack(side="left", padx=(0, 8))
        self.btn_file.pack_forget()  # Oculto por defecto, se muestra solo en modo estudio
        
        # Botón Voz con indicador visual
        self.btn_voz = ctk.CTkButton(
            buttons_frame,
            text="🎤",
            width=42,
            height=40,
            command=self.toggle_mic,
            font=("Segoe UI Emoji", 18),
            fg_color=self.COLORS["bg_elevated"],
            hover_color=self.COLORS["secondary"],
            corner_radius=12,
            text_color=self.COLORS["text_primary"],
            border_width=0
        )
        self.btn_voz.pack(side="left", padx=(0, 8))
        
        # Indicador de grabación (invisible inicialmente)
        self.recording_indicator = ctk.CTkLabel(
            buttons_frame,
            text="●",
            font=("Segoe UI", 12),
            text_color=self.COLORS["error"],
            width=8
        )
        self.recording_indicator.pack(side="left", padx=(0, 0))
        self.recording_indicator.pack_forget()  # Oculto inicialmente
        
        # NUEVO: Visualizador de voz (canvas para ondas animadas)
        self.visualizer_frame = ctk.CTkFrame(
            input_container,
            fg_color=self.COLORS["bg_secondary"],
            corner_radius=12,
            height=60
        )
        self.visualizer_frame.pack(side="left", fill="x", expand=True, padx=(8, 0), pady=6)
        self.visualizer_frame.pack_forget()  # Oculto inicialmente
        
        # Canvas para dibujar ondas
        self.visualizer_canvas = ctk.CTkCanvas(
            self.visualizer_frame,
            bg=self.COLORS["bg_secondary"],
            highlightthickness=0,
            height=50
        )
        self.visualizer_canvas.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Botón Enviar moderno
        self.btn_send = ctk.CTkButton(
            buttons_frame,
            text="Enviar",
            width=70,
            height=40,
            command=self.enviar,
            font=("Segoe UI", 11, "bold"),
            fg_color=self.COLORS["accent"],
            hover_color=self.COLORS["accent_hover"],
            corner_radius=12,
            text_color="white",
            border_width=0
        )
        self.btn_send.pack(side="left")
        
        # Etiqueta de estado eliminada para ganar espacio (ya está en el header)

    def setup_config_tab(self):
        conf = ConfigManager.cargar_config()
        
        # Frame principal con SCROLL CENTRADO
        # Usamos ScrollableFrame para que quepa todo sin importar la altura de ventan
        main_scroll = ctk.CTkScrollableFrame(
            self.tab_config,
            fg_color="transparent",
            width=480 # Ancho suficiente
        )
        main_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # --- TARJETA DE CONFIGURACIÓN ---
        # Dentro del scroll ponemos la tarjeta
        card = ctk.CTkFrame(
            main_scroll,
            fg_color=self.COLORS["bg_elevated"],
            corner_radius=20
        )
        card.pack(fill="x", padx=10, pady=10) # fill=x para que use el ancho disponible
        
        # Título dentro de la tarjeta (más compacto)
        ctk.CTkLabel(
            card,
            text="⚙️ AJUSTES DE INTELIGENCIA",
            font=("Inter", 13, "bold"),
            text_color=self.COLORS["accent"]
        ).pack(pady=(15, 20))
        
        # Contenedor de Formulario (Margenes internos)
        form_frame = ctk.CTkFrame(card, fg_color="transparent")
        form_frame.pack(fill="x", padx=25) # Margen lateral uniforme para TODO

        # Selector de proveedor
        self._crear_label_input(form_frame, "PROVEEDOR PRINCIPAL")
        self.pv = ctk.StringVar(value=conf.get("provider", "Gemini"))
        
        # OptionMenu con ancho consistente
        ctk.CTkOptionMenu(
            form_frame,
            values=["Gemini", "Groq", "ChatGPT"],
            variable=self.pv,
            height=42, # Misma altura que los inputs
            font=("Inter", 12),
            fg_color=self.COLORS["bg_secondary"],
            button_color=self.COLORS["accent"],
            button_hover_color=self.COLORS["accent_hover"],
            text_color=self.COLORS["text_primary"],
            dropdown_fg_color=self.COLORS["bg_secondary"],
            dropdown_hover_color=self.COLORS["bg_hover"],
            dropdown_text_color=self.COLORS["text_primary"],
            corner_radius=12
        ).pack(fill="x", pady=(0, 25))

        # API Keys
        self.e_gem = self._crear_input_estilizado(form_frame, "GEMINI PRO / FLASH KEY", conf.get("gemini_key"))
        self.e_groq = self._crear_input_estilizado(form_frame, "GROQ CLOUD KEY", conf.get("groq_key"))
        self.e_open = self._crear_input_estilizado(form_frame, "OPENAI API KEY", conf.get("openai_key"))

        # Botón guardar (más compacto)
        ctk.CTkButton(
            card,
            text="GUARDAR CAMBIOS",
            command=self.guardar_config,
            height=44,
            font=("Inter", 11, "bold"),
            fg_color=self.COLORS["success"],
            hover_color="#059669",
            corner_radius=12
        ).pack(fill="x", padx=25, pady=(20, 8))
        
        # Botón Mi Perfil (más compacto)
        ctk.CTkButton(
            card,
            text="👤 MI PERFIL",
            command=self.open_profile_settings,
            height=44,
            font=("Inter", 11, "bold"),
            fg_color=self.COLORS["secondary"],
            hover_color="#7C3AED",
            corner_radius=12
        ).pack(fill="x", padx=25, pady=(0, 20))

    def _crear_label_input(self, parent, text):
        ctk.CTkLabel(
            parent,
            text=text,
            font=("Inter", 10, "bold"),
            text_color=self.COLORS["text_secondary"],
            anchor="w"
        ).pack(anchor="w", pady=(0, 8))

    def _crear_input_estilizado(self, parent, label, valor=""):
        self._crear_label_input(parent, label)
        
        entry = ctk.CTkEntry(
            parent,
            height=40,
            font=("JetBrains Mono", 11),
            fg_color=self.COLORS["bg_primary"],
            border_width=1,
            border_color=self.COLORS["bg_hover"],
            text_color=self.COLORS["text_primary"],
            corner_radius=12,
            show="•"
        )
        entry.pack(fill="x", pady=(0, 20))
        
        if valor:
            entry.insert(0, valor)
        return entry

    def setup_dev_tab(self):
        # Título más elegante
        header = ctk.CTkFrame(self.tab_dev, fg_color="transparent")
        header.pack(fill="x", pady=(10, 5))
        
        ctk.CTkLabel(header, text="PANEL DE CONTROL", font=("Roboto", 14, "bold"), text_color="#bdc3c7").pack()
        ctk.CTkLabel(header, text="Herramientas de Desarrollo y Sistema", font=("Roboto", 10), text_color="#7f8c8d").pack()

        # NUEVO: Frame scrollable para que todos los botones sean visibles
        scrollable_frame = ctk.CTkScrollableFrame(
            self.tab_dev,
            fg_color="transparent",
            scrollbar_button_color=self.COLORS["bg_hover"]
        )
        scrollable_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        btn_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        btn_frame.pack(fill="both", expand=True)
        
        # Paleta "Premium Dark" - Unificada para look profesional
        # Formato: (Emoji, Título, Comando)
        botones_config = [
            ("📊", "Estado Git", "git status"),
            ("🚀", "Subir Cambios", "git push"),
            ("🌐", "Túnel Web", "compartir proyecto"),
            ("📟", "Monitor CPU", "sistema"),
            ("🧪", "Build / Deps", "instalar dependencias"),
            ("💀", "Kill Python", "matar python"),
            ("🎮", "Control Gestos", "activa gestos")  # NUEVO
        ]
        
        # Configurar grid con más filas para que todos los botones sean visibles
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        btn_frame.grid_rowconfigure(0, weight=1)
        btn_frame.grid_rowconfigure(1, weight=1)
        btn_frame.grid_rowconfigure(2, weight=1)
        btn_frame.grid_rowconfigure(3, weight=1)  # Fila extra para el botón de gestos
        
        for i, btn in enumerate(botones_config):
            icon, title, cmd = btn
            
            # Botón con diseño "Card" uniforme
            b = ctk.CTkButton(
                btn_frame, 
                text=f"{icon}  {title}", 
                command=lambda c=cmd: self.ejecutar_comando(c),
                fg_color=self.COLORS["bg_elevated"], 
                hover_color=self.COLORS["bg_hover"],
                border_width=1,
                border_color=self.COLORS["bg_hover"],
                text_color=self.COLORS["text_primary"],
                height=50,
                font=("Roboto Medium", 11),
                corner_radius=8,
                anchor="w" # Alinear texto a la izquierda para look más limpio
            )
            # Layout de 2 columnas con más espacio vertical
            b.grid(row=i//2, column=i%2, padx=6, pady=8, sticky="nsew")
    
    def setup_network_tab(self):
        """Pestaña de Network Guardian Dashboard"""
        # Frame principal
        main_frame = ctk.CTkFrame(self.tab_network, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color=self.COLORS["bg_secondary"], corner_radius=12)
        header_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="🌐 NETWORK GUARDIAN",
            font=("Inter", 16, "bold"),
            text_color=self.COLORS["accent"]
        ).pack(side="left", padx=15, pady=10)
        
        # Botón Dashboard Completo
        ctk.CTkButton(
            header_frame,
            text="📊 DASHBOARD",
            width=120,
            height=40,
            command=self.open_network_dashboard,
            fg_color=self.COLORS["secondary"],
            hover_color="#6A3DE8",
            corner_radius=10,
            font=("Inter", 11, "bold")
        ).pack(side="right", padx=(0, 10), pady=5)
        
        # Botón refrescar
        ctk.CTkButton(
            header_frame,
            text="🔄",
            width=40,
            height=40,
            command=self.refresh_network_data,
            fg_color=self.COLORS["accent"],
            hover_color=self.COLORS["accent_hover"],
            corner_radius=10
        ).pack(side="right", padx=5, pady=5)
        
        # Panel de estadísticas
        stats_frame = ctk.CTkFrame(main_frame, fg_color=self.COLORS["bg_elevated"], corner_radius=12)
        stats_frame.pack(fill="x", pady=(0, 10))
        
        # Grid de estadísticas
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        
        # Dispositivos totales
        self.net_total_label = ctk.CTkLabel(
            stats_frame,
            text="📱 0\nDispositivos",
            font=("Inter", 12),
            text_color=self.COLORS["text_primary"]
        )
        self.net_total_label.grid(row=0, column=0, padx=10, pady=15)
        
        # Dispositivos activos
        self.net_active_label = ctk.CTkLabel(
            stats_frame,
            text="🟢 0\nActivos",
            font=("Inter", 12),
            text_color=self.COLORS["success"]
        )
        self.net_active_label.grid(row=0, column=1, padx=10, pady=15)
        
        # Alertas
        self.net_alerts_label = ctk.CTkLabel(
            stats_frame,
            text="⚠️ 0\nAlertas",
            font=("Inter", 12),
            text_color=self.COLORS["warning"]
        )
        self.net_alerts_label.grid(row=0, column=2, padx=10, pady=15)
        
        # Lista de dispositivos
        devices_label = ctk.CTkLabel(
            main_frame,
            text="Dispositivos Conectados",
            font=("Inter", 12, "bold"),
            text_color=self.COLORS["text_secondary"]
        )
        devices_label.pack(anchor="w", pady=(0, 5))
        
        # Scrollable frame para dispositivos
        self.devices_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color=self.COLORS["bg_primary"],
            height=180
        )
        self.devices_frame.pack(fill="both", expand=True)
        
        # Botones de acción
        actions_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkButton(
            actions_frame,
            text="🔍 Escanear Red",
            command=lambda: self.ejecutar_comando("escanea red"),
            height=40,
            fg_color=self.COLORS["accent"],
            hover_color=self.COLORS["accent_hover"],
            corner_radius=10
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(
            actions_frame,
            text="🛡️ Modo Fortaleza",
            command=lambda: self.ejecutar_comando("modo fortaleza"),
            height=40,
            fg_color=self.COLORS["error"],
            hover_color="#CC0000",
            corner_radius=10
        ).pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        # Cargar datos iniciales
        self.refresh_network_data()
    
    def refresh_network_data(self):
        """Actualiza los datos del dashboard de red"""
        if not self.brain.guardian:
            return
        
        try:
            # Obtener dispositivos directamente de la base de datos
            dispositivos = self.brain.guardian.db.obtener_todos_dispositivos(solo_activos=False)
            
            # Actualizar estadísticas
            total = len(dispositivos)
            activos = sum(1 for d in dispositivos if d.get('is_active', False))
            
            # Obtener alertas pendientes
            try:
                alertas = self.brain.guardian.obtener_alertas_pendientes()
                num_alertas = len(alertas) if alertas else 0
            except:
                num_alertas = 0
            
            # Actualizar labels
            self.net_total_label.configure(text=f"📱 {total}\nDispositivos")
            self.net_active_label.configure(text=f"🟢 {activos}\nActivos")
            self.net_alerts_label.configure(text=f"⚠️ {num_alertas}\nAlertas")
            
            # Limpiar lista de dispositivos
            for widget in self.devices_frame.winfo_children():
                widget.destroy()
            
            # Mostrar dispositivos
            if total == 0:
                ctk.CTkLabel(
                    self.devices_frame,
                    text="No hay dispositivos. Ejecuta 'Escanear Red'",
                    font=("Inter", 11),
                    text_color=self.COLORS["text_disabled"]
                ).pack(pady=20)
            else:
                for i, device in enumerate(dispositivos[:10]):  # Mostrar máximo 10
                    self._create_device_card(device, i)
                    
        except Exception as e:
            logging.error(f"Error actualizando network data: {e}")
            # Mostrar mensaje de error en el dashboard
            for widget in self.devices_frame.winfo_children():
                widget.destroy()
            ctk.CTkLabel(
                self.devices_frame,
                text=f"Error: {str(e)}\nIntenta escanear la red primero",
                font=("Inter", 11),
                text_color=self.COLORS["error"]
            ).pack(pady=20)
    
    def _create_device_card(self, device, index):
        """Crea una tarjeta de dispositivo"""
        card = ctk.CTkFrame(
            self.devices_frame,
            fg_color=self.COLORS["bg_elevated"],
            corner_radius=8
        )
        card.pack(fill="x", pady=3)
        
        # Obtener datos del dispositivo
        nombre = device.get('custom_name') or device.get('device_type') or 'Desconocido'
        ip = device.get('ip', 'N/A')
        is_active = device.get('is_active', False)
        trust_level = device.get('trust_level', 'unknown')
        is_blocked = device.get('is_blocked', False)
        
        # Iconos
        status_icon = "🟢" if is_active else "🔴"
        trust_icon = {
            'trusted': '✅',
            'unknown': '❓',
            'suspicious': '⚠️'
        }.get(trust_level, '❓')
        block_icon = "🔒" if is_blocked else ""
        
        info_label = ctk.CTkLabel(
            card,
            text=f"{status_icon} {trust_icon} {nombre} {block_icon}\n   {ip}",
            font=("Inter", 10),
            text_color=self.COLORS["text_primary"],
            anchor="w",
            justify="left"
        )
        info_label.pack(side="left", padx=10, pady=8)



    def open_settings_tab(self):
        """Abre la pestaña de configuración"""
        try:
            self.tabview.set("⚙️ Config")
            return "Abriendo configuración..."
        except Exception as e:
            logging.error(f"Error abriendo configuración: {e}")
            return "No pude abrir la configuración."
    
    def open_profile_settings(self):
        """Abre la ventana de configuración de perfil de usuario"""
        try:
            from config_perfil_ui import abrir_configuracion
            # Abrir ventana de configuración de perfil
            abrir_configuracion(parent=self)
            return "Abriendo tu perfil..."
        except Exception as e:
            logging.error(f"Error abriendo perfil: {e}")
            return f"No pude abrir tu perfil: {e}"
    
    def open_network_dashboard(self):
        """Abre el dashboard dedicado de NetworkGuardian"""
        try:
            if not self.brain.guardian:
                self.log("ERROR", "Network Guardian no está disponible", "error")
                return
            
            from network_guardian_dashboard import abrir_dashboard
            abrir_dashboard(self.brain.guardian, parent=self)
            self.log("SARA", "Dashboard de red abierto", "sys")
        except Exception as e:
            logging.error(f"Error abriendo dashboard: {e}")
            self.log("ERROR", f"No pude abrir el dashboard: {e}", "error")
    
    def guardar_config(self):
        try:
            provider = self.pv.get()
            gemini = self.e_gem.get().strip()
            groq = self.e_groq.get().strip()
            openai = self.e_open.get().strip()
            
            # Guardar API keys en .env
            exito = ConfigManager.guardar_api_keys(
                gemini_key=gemini,
                groq_key=groq,
                openai_key=openai,
                provider=provider
            )
            
            if not exito:
                self.log("ERR", "Error al guardar las API keys", "error")
                return
            
            # Guardar configuración no sensible en JSON
            ConfigManager.guardar_config({"provider": provider})
            
            # Volver a pestaña principal
            self.tabview.set("💬 Chat")
            
            # Reconectar IAs con las nuevas keys
            conectado = self.brain.conectar_ias()
            self.actualizar_estado_global()
            
            msg = "✅ Configuración guardada en .env" if conectado else "⚠ Guardado pero sin conexión IA"
            self.log("SYS", msg, "sys" if conectado else "error")
        except Exception as e:
            self.log("ERR", f"Error: {e}", "error")

    def actualizar_estado_global(self):
        """Actualiza el indicador de estado en el header"""
        if self.brain.ia_online:
            estado = f"● {self.brain.preferred_provider}"
            color = self.COLORS["success"]
        else:
            estado = "● OFFLINE"
            color = self.COLORS["error"]
        
        self.header_status.configure(text=estado, text_color=color)
        
        # Actualizar label de estado en chat tab (Eliminado)
        # if hasattr(self, 'lbl_status'):
        #     ia_text = f"IA: {self.brain.preferred_provider}" if self.brain.ia_online else "IA: OFFLINE"
        #     self.lbl_status.configure(
        #         text=ia_text,
        #         text_color=self.COLORS["success"] if self.brain.ia_online else self.COLORS["text_disabled"]
        #     )

    def insert_markdown(self, text, base_tag):
        """Inserta texto parseando negritas **text**"""
        try:
            parts = text.split("**")
            for i, part in enumerate(parts):
                if not part: continue
                
                # Pares = Normal, Impares = Negrita
                # Combinamos el tag base (color) con 'bold' si aplica
                if i % 2 == 1:
                    # Nota: CTkTextbox acepta tags como tupla? Probemos string space-separated si falla tupla
                    # Tkinter standard usa tupla.
                    self.chat.insert("end", part, (base_tag, "bold"))
                else:
                    self.chat.insert("end", part, base_tag)
            self.chat.insert("end", "\n")
        except Exception as e:
            # Fallback por seguridad
            self.chat.insert("end", f"{text}\n", base_tag)

    def animar_texto(self, user, text, tag="sys"):
        """Simula efecto de escritura tipo hacker/IA."""
        ts = datetime.datetime.now().strftime("%H:%M")
        header = f"[{ts}] {user}: "
        
        self.chat.configure(state="normal")
        self.chat.insert("end", header, tag)
        
        # Usar el renderizador markdown
        self.insert_markdown(text, tag)
        
        self.chat.see("end")
        self.chat.configure(state="disabled")

    def log(self, user, text, tag="sys"):
        # Wrapper thread-safe
        self.after(0, lambda: self._log_impl(user, text, tag))

    def _log_impl(self, user, text, tag="sys"):
        # Usar animación solo para mensajes de SARA importantes
        if user == "SARA" and len(text) < 300: # Aumenté límite para el clima
            self.animar_texto(user, text, tag)
        else:
            # Renderizado instantáneo
            try:
                self.chat.configure(state="normal")
                ts = datetime.datetime.now().strftime("%H:%M")
                
                # Header
                self.chat.insert("end", f"[{ts}] {user}: ", tag)
                
                # Body con markdown
                self.insert_markdown(text, tag)
                
                self.chat.see("end")
                self.chat.configure(state="disabled")
            except: pass

    def seleccionar_archivo(self):
        """Abre un diálogo para seleccionar PDF y lo procesa automáticamente"""
        from tkinter import filedialog
        
        archivo = filedialog.askopenfilename(
            title="Selecciona un PDF para estudiar",
            filetypes=[
                ("Archivos PDF", "*.pdf"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if archivo:
            # Mostrar archivo seleccionado
            nombre_archivo = archivo.split("/")[-1].split("\\")[-1]
            self.log("TU", f"📎 Archivo: {nombre_archivo}", "tu")
            
            # Preguntar qué hacer con el archivo
            self.log("SARA", "¿Qué quieres hacer con este PDF?\n1️⃣ Resumir\n2️⃣ Crear flashcards\n3️⃣ Generar examen", "sara")
            
            # Guardar ruta temporalmente
            self.archivo_temporal = archivo

    def enviar(self, event=None):
        txt = self.entry.get()
        if txt:
            self.entry.delete(0, "end")
            self.log("TU", txt, "tu")
            self.procesar_hilo(txt)

    def ejecutar_comando(self, cmd):
        self.log("CMD", cmd, "tu")
        thread = threading.Thread(target=self.procesar_hilo, args=(cmd,), daemon=True)
        thread.start()

    def procesar_hilo(self, texto):
        with open("debug_trace.txt", "a", encoding="utf-8") as f:
            f.write(f"DEBUG_FILE: procesar_hilo called with '{texto}'\n")
        print(f"DEBUG SARA: procesar_hilo called with '{texto}'")
        t = threading.Thread(target=self._procesar_comando, args=(texto,))
        t.start()
        print("DEBUG SARA: Thread started")
        
    def _procesar_comando(self, texto):
        try:
            with open("debug_trace.txt", "a", encoding="utf-8") as f:
                f.write(f"DEBUG_FILE: Inside _procesar_comando with '{texto}'\n")
            print(f"DEBUG SARA: Inside _procesar_comando with '{texto}'")
            resp, origen = self.brain.procesar(texto)
            
            # --- MANEJO DE COMANDOS UI ESPECIALES ---
            if origen == "ui_command":
                if resp == "OPEN_SETTINGS_TAB":
                    mensaje = self.open_settings_tab()
                    self.log("SARA", mensaje, "sara")
                    self.brain.voz.hablar(mensaje)
                    return
                elif resp == "OPEN_PROFILE_SETTINGS":
                    mensaje = self.open_profile_settings()
                    self.log("SARA", mensaje, "sara")
                    self.brain.voz.hablar(mensaje)
                    return
            
            # --- MANEJO DE MODO CENTINELA ---
            if origen == "sentinel_on":
                self.after(0, self.activate_sentinel)
                self.log("SARA", resp, "sara")
                return
            elif origen == "sentinel_off":
                self.after(0, self.deactivate_sentinel)
                self.log("SARA", resp, "sara")
                return

            # --- MANEJO DE MODO ESTUDIO ---
            if origen == "study":
                # Mostrar botón de archivo cuando se activa modo estudio
                if "Modo Estudio Activado" in resp:
                    # Thread-safe UI update
                    self.after(0, lambda: self.btn_file.pack(side="left", padx=(0, 8)))
                    self.log("SYS", "💡 Usa el botón 📎 para adjuntar PDFs", "sys")
            
            self.log("SARA", resp, "sara")
            
            # Hablar respuesta (solo si no es muy larga o es local)
            if origen == "sara" or origen == "exit" or (len(resp) < MAX_CHARS_VOZ and origen != "code"):
                self.brain.voz.hablar(resp)
            
            # --- MANEJO DE ESTADOS ESPECIALES ---
            if origen == "exit":
                self.log("SYS", "Apagando sistema en 3 segundos...", "sys")
                self.after(3000, self.destroy)

            self.after(0, self.actualizar_estado_global)
        except Exception as e:
            self.log("ERROR", str(e), "error")

    def toggle_mic(self):
        try:
            self.is_listening = not self.is_listening
            if self.is_listening:
                # Activar grabación
                self.btn_voz.configure(
                    text="⏹",
                    fg_color=self.COLORS["error"],
                    hover_color="#DC2626"
                )
                # Mostrar indicador de grabación (dot rojo)
                if hasattr(self, 'recording_indicator'):
                    self.recording_indicator.pack(side="left", padx=(0, 8))
                
                # NUEVO: Iniciar visualizador en modo listening
                self.start_visualizer(mode="listening")
                
                # Iniciar loop de voz
                threading.Thread(target=self.loop_voz, daemon=True).start()
                self.log("SYS", "🎤 Micrófono activado", "sys")
            else:
                # Desactivar grabación
                self.btn_voz.configure(
                    text="🎤",
                    fg_color=self.COLORS["bg_elevated"],
                    hover_color=self.COLORS["secondary"]
                )
                # Ocultar indicador
                if hasattr(self, "recording_indicator"):
                    self.recording_indicator.pack_forget()
                
                # NUEVO: Detener visualizador
                self.stop_visualizer()
                
                self.log("SYS", "🔇 Micrófono desactivado", "sys")
        except Exception as e:
            logging.error(f"Error en toggle_mic: {e}")
            self.is_listening = False
            self.btn_voz.configure(
                text="🎤",
                fg_color=self.COLORS["bg_elevated"]
            )
            if hasattr(self, "recording_indicator"):
                self.recording_indicator.pack_forget()
            # Detener visualizador en caso de error
            self.stop_visualizer()
            
    def loop_voz(self):
        try:
            r = sr.Recognizer()
            # Ajuste de sensibilidad para que te escuche sin gritar y NO CORTE
            r.energy_threshold = 300 
            r.dynamic_energy_threshold = True
            r.dynamic_energy_adjustment_damping = 0.15
            r.dynamic_energy_ratio = 1.5
            
            # Tiempos aún más largos
            r.pause_threshold = 2.5  # Muy tolerante a pausas
            r.non_speaking_duration = 0.5
            
            with sr.Microphone() as source:
                # Calibración rápida inicial
                r.adjust_for_ambient_noise(source, duration=0.5)
                
                while self.is_listening:
                    if self.brain.voz.esta_hablando():
                        time.sleep(VOICE_SLEEP_WHILE_TALKING)
                        continue
                    try:
                        # phrase_time_limit=15 para frases largas
                        audio = r.listen(source, timeout=VOICE_TIMEOUT, phrase_time_limit=15)
                        txt = r.recognize_google(audio, language="es-ES").lower()
                        
                        # Normalizar acentos para evitar problemas con Google Speech
                        import unicodedata
                        txt = ''.join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn')
                        
                        self.log("VOZ", txt, "text_disabled") # Log de depuración
                        
                        if self.brain.dictation_mode:
                            if "terminar dictado" in txt:
                                self.brain.dictation_mode = False
                                self.log("SARA", "Dictado finalizado.", "sara")
                                self.brain.voz.hablar("Dictado finalizado.")
                            else:
                                import pyautogui
                                pyautogui.write(txt + " ")
                                self.log("📝", txt, "dev")
                            continue
                        
                        # Comando para desactivar modo continuo
                        if "modo discontinuo" in txt and "sara" in txt:
                            self.is_listening = False
                            self.btn_voz.configure(
                                text="🎤", 
                                fg_color=self.COLORS["bg_elevated"],
                                hover_color=self.COLORS["secondary"]
                            )
                            self.recording_indicator.pack_forget()
                            self.log("SARA", "Modo discontinuo activado. Presiona el botón para volver a escuchar.", "sara")
                            self.brain.voz.hablar("Modo discontinuo activado")
                            break
                        
                        # --- COMANDOS DIRECTOS (SIN WAKE WORD) ---
                        # REDUCIDO DRASTICAMENTE PARA EVITAR RUIDO
                        # Solo se permiten comandos de emergencia o muy específicos sin decir "SARA"
                        comandos_directos = [
                            "silencio", "pausa", "mute", "detente", "cállate", # Emergencia
                            "contesta", "responde" # Teléfono (futuro)
                        ]
                        
                        # Si hay conversación fluida activa (menos de 15s desde última respuesta de SARA)
                        # TODO: Implementar lógica de conversación activa real
                        
                        if any(txt.strip() == c for c in comandos_directos): # Coincidencia exacta o muy cercana
                            self.log("VOZ (Directo)", txt, "tu")
                            self.procesar_hilo(txt)
                            continue

                        # Debug: Ver qué llega realmente
                        print(f"DEBUG VOZ: '{txt}'")
                        
                        # --- EXCEPCIÓN DE CONTEXTO ---
                        # Si SARA acaba de preguntar "¿A qué ciudad?", permitimos responder sin "SARA"
                        # Esto soluciona si se cortó el comando anterior y el usuario dice solo "Loma Bonita"
                        contexto_activo = False
                        if self.brain.memory:
                            last_turn = self.brain.memory.get_last_turn()
                            # Si la última respuesta de SARA fue una pregunta sobre ciudad
                            if last_turn and last_turn.get("bot", "").endswith("¿A qué ciudad quieres cambiar?"):
                                print("DEBUG: Contexto activo (Ciudad) - Wake Word no requerida")
                                contexto_activo = True

                        # Lista AMPLIADA de variantes de wake words
                        variantes_sara = [
                            "sara", "zara", "sarah", "sahara", "zrah", "ara", "shara",
                            "sarra", "zarah", "sarita", "hey sara", "oye sara", "ok sara"
                        ]
                        
                        # FUZZY MATCHING: Detectar wake word con tolerancia a errores
                        wake_word_detectada = False
                        palabra_detectada = None
                        

                        
                        # Primero intentar coincidencia exacta (más rápido)
                        if any(w in txt for w in variantes_sara):
                            wake_word_detectada = True
                            palabra_detectada = next(w for w in variantes_sara if w in txt)
                        else:
                            # Si no hay coincidencia exacta, usar fuzzy matching
                            palabras_txt = txt.split()
                            for palabra in palabras_txt:
                                # Buscar similitud con variantes (umbral 0.75 = 75% similar)
                                matches = difflib.get_close_matches(palabra, variantes_sara, n=1, cutoff=0.75)
                                if matches:
                                    wake_word_detectada = True
                                    palabra_detectada = matches[0]
                                    print(f"DEBUG: Fuzzy match: '{palabra}' -> '{matches[0]}'")
                                    break
                        
                        # Detectar palabra clave O contexto activo
                        if contexto_activo or wake_word_detectada:
                            if not contexto_activo: 
                                print(f"DEBUG: WAKE WORD DETECTADA! ({palabra_detectada})")
                                # Feedback auditivo mejorado (beep más agradable)
                                try:
                                    import winsound
                                    # Beep doble para confirmar detección
                                    winsound.Beep(800, 80)  # Primera nota
                                    time.sleep(0.05)
                                    winsound.Beep(1000, 80)  # Segunda nota (más alta)
                                except: pass

                            # Limpiar el comando
                            cmd = txt
                            if not contexto_activo:
                                for w in variantes_sara:
                                    cmd = cmd.replace(f"oye {w}", "").replace(w, "")
                            
                            cmd = cmd.strip()
                            
                            # Caso especial: Si está en contexto de cambio de ubicación, inyectar el comando completo
                            if contexto_activo:
                                cmd = f"cambia mi ciudad a {cmd}"
                            
                            if cmd:
                                self.log("VOZ", cmd, "tu")
                                self.procesar_hilo(cmd)
                            else:
                                self.brain.voz.hablar("Dime.")
                        else:
                            print("DEBUG: Ignorado por falta de wake word")
                        # Si no detecta "SARA", ignorar (no procesar)
                        
                    except sr.WaitTimeoutError:
                        # Timeout esperando que empiece a hablar - Ignorar silenciosamente
                        pass
                    except sr.UnknownValueError:
                        # Ruido ambiental o voz no reconocida - Ignorar silenciosamente
                        pass
                    except sr.RequestError as e:
                        logging.warning(f"Error conexión Google Speech: {e}")
                    except Exception as e:
                        print(f"DEBUG CRITICAL ERROR IN VOICE LOOP: {e}")
                        import traceback
                        traceback.print_exc()
        except Exception as e:
            logging.error(f"Error microfono: {e}")
            self.is_listening = False
            try: 
                self.btn_voz.configure(
                    text="🎤", 
                    fg_color=self.COLORS["bg_elevated"],
                    hover_color=self.COLORS["secondary"]
                )
                if hasattr(self, 'recording_indicator'):
                    self.recording_indicator.pack_forget()
            except: pass

    # --- VISUALIZADOR DE VOZ (ONDAS ANIMADAS) ---
    def start_visualizer(self, mode="listening"):
        """Inicia el visualizador de voz
        
        Args:
            mode: 'listening' (ondas azules) o 'speaking' (ondas verdes)
        """
        if not hasattr(self, 'visualizer_canvas'):
            return
        
        self.visualizer_running = True
        self.visualizer_mode = mode
        
        # Mostrar visualizador
        self.entry.pack_forget()
        self.visualizer_frame.pack(side="left", fill="x", expand=True, padx=(8, 0), pady=6)
        
        # Iniciar animación en thread separado
        threading.Thread(target=self._animate_visualizer, daemon=True).start()
    
    def stop_visualizer(self):
        """Detiene el visualizador de voz"""
        self.visualizer_running = False
        
        # Ocultar visualizador y mostrar entry
        if hasattr(self, 'visualizer_frame'):
            self.visualizer_frame.pack_forget()
        if hasattr(self, 'entry'):
            self.entry.pack(side="left", fill="x", expand=True, padx=12, pady=6)
    
    def _animate_visualizer(self):
        """Captura audio en tiempo real y anima las ondas"""
        try:
            # Inicializar PyAudio
            p = pyaudio.PyAudio()
            
            # Configuración de audio
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100
            
            # Abrir stream de audio
            self.audio_stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            while self.visualizer_running:
                try:
                    # Leer datos de audio
                    data = self.audio_stream.read(CHUNK, exception_on_overflow=False)
                    
                    # Convertir bytes a valores numéricos
                    values = struct.unpack(str(CHUNK) + 'h', data)
                    
                    # Calcular amplitud (RMS - Root Mean Square)
                    rms = sum(v**2 for v in values) / len(values)
                    amplitude = math.sqrt(rms)
                    
                    # Normalizar a 0-100 (AJUSTADO: divisor reducido para mayor sensibilidad)
                    self.audio_level = min(100, amplitude / 30)  # Antes: 100, Ahora: 30 (3x más sensible)
                    
                    # Actualizar visualizador
                    self.after(0, self._draw_waves)
                    
                    time.sleep(0.01)  # ~100 FPS para captura suave
                except Exception as e:
                    logging.error(f"Error capturando audio: {e}")
                    break
        
        except Exception as e:
            logging.error(f"Error inicializando audio stream: {e}")
        finally:
            # Limpiar
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            p.terminate()
    
    def _draw_waves(self):
        """Dibuja las ondas basadas en el nivel de audio REAL"""
        if not hasattr(self, 'visualizer_canvas'):
            return
        
        try:
            # Limpiar canvas
            self.visualizer_canvas.delete("all")
            
            # Obtener dimensiones
            width = self.visualizer_canvas.winfo_width()
            height = self.visualizer_canvas.winfo_height()
            
            if width <= 1 or height <= 1:
                return
            
            center_y = height // 2
            
            # Color según modo
            if self.visualizer_mode == "listening":
                color = self.COLORS["accent"]  # Cyan
            else:  # speaking
                color = self.COLORS["success"]  # Verde
            
            # Amplitud basada en nivel de audio REAL
            # audio_level va de 0 a 100
            base_amplitude = max(5, self.audio_level * 0.6)  # Antes: 0.3, Ahora: 0.6 (2x más visible)
            
            # Dibujar barras verticales (estilo ecualizador)
            num_bars = 40
            bar_width = width // num_bars
            
            for i in range(num_bars):
                x = i * bar_width
                
                # Variar altura de barras con efecto de onda
                wave_effect = math.sin(i * 0.3 + time.time() * 3) * 0.5 + 0.5
                bar_height = base_amplitude * (0.5 + wave_effect)
                
                # Dibujar barra
                y1 = center_y - bar_height
                y2 = center_y + bar_height
                
                # Opacidad basada en posición
                if i % 2 == 0:
                    self.visualizer_canvas.create_rectangle(
                        x, y1, x + bar_width - 2, y2,
                        fill=color,
                        outline=""
                    )
            
            # Dibujar línea central si hay poco audio
            if self.audio_level < 5:
                self.visualizer_canvas.create_line(
                    0, center_y, width, center_y,
                    fill=color,
                    width=2
                )
        
        except Exception as e:
            logging.error(f"Error dibujando visualizador: {e}")

    # --- SYSTEM TRAY (MODO FANTASMA) ---
    def setup_tray(self):
        from pystray import MenuItem as item
        import pystray
        from PIL import Image, ImageDraw

        def create_image(width, height, color1, color2):
            image = Image.new('RGB', (width, height), color1)
            dc = ImageDraw.Draw(image)
            dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
            dc.rectangle((0, height // 2, width // 2, height), fill=color2)
            return image

        def on_open(icon, item):
            self.deiconify()
            self.attributes('-topmost', True)
            
        def on_exit(icon, item):
            icon.stop()
            self.quit()

        image = create_image(64, 64, '#2c3e50', '#3498db')
        self.tray_icon = pystray.Icon("SARA", image, "S.A.R.A.", menu=pystray.Menu(
            item('Restaurar', on_open),
            item('Salir', on_exit)
        ))
        
        # Ejecutar en hilo aparte
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def on_closing(self):
        self.withdraw() # Solo ocultar ventana
        self.brain.voz.hablar("Minimizando a segundo plano.")
        self.log("SYS", "Minimizado al System Tray", "sys")

    # --- MODULO CENTINELA (LOCK SCREEN) ---
    # --- MODULO CENTINELA (LOCK SCREEN) ---
    def activate_sentinel(self):
        """Activa la pantalla de bloqueo (Modo Centinela)."""
        try:
            # Lazy import del nuevo módulo UI con visualizador de espectro
            from sentinel_ui import SentinelProGUI
            
            if not hasattr(self, "sentinel_ui_manager") or not self.sentinel_ui_manager:
                self.sentinel_ui_manager = SentinelProGUI(self, self._on_sentinel_unlock)
            
            self.sentinel_ui_manager.activate()
        except Exception as e:
            logging.error(f"❌ Error activando Sentinel: {e}")
            import traceback
            traceback.print_exc()
            self.log("ERROR", f"No pude activar el Modo Centinela: {str(e)}", "error")
            self.brain.voz.hablar("Error al activar el modo centinela")

    def deactivate_sentinel(self):
        """Desactiva la pantalla de bloqueo."""
        try:
            if hasattr(self, "sentinel_ui_manager") and self.sentinel_ui_manager:
                self.sentinel_ui_manager.deactivate()
        except Exception as e:
            logging.error(f"❌ Error desactivando Sentinel: {e}")
            self.log("ERROR", f"Error al desactivar Sentinel: {str(e)}", "error")

    def _on_sentinel_unlock(self, success, message):
        """Callback al intentar desbloquear."""
        if success:
            self.log("SARA", f"🔓 {message}", "sara")
            self.brain.voz.hablar(message)
        else:
            # Feedback solo verbal para error
            self.brain.voz.hablar("Acceso denegado.")




if __name__ == "__main__":
    try:
        app = SaraUltimateGUI()
        app.setup_tray() # Iniciar Icono
        app.protocol("WM_DELETE_WINDOW", app.on_closing) # Interceptar botón X
        app.mainloop()
    except Exception as e:
        logging.error(f"❌ Error crítico al iniciar SARA: {e}")
        import traceback
        traceback.print_exc()
        input("Presiona Enter para cerrar...") 