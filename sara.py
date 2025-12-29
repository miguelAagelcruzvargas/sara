import customtkinter as ctk
import speech_recognition as sr
import threading
import datetime
import logging
import logging
import time
import ctypes # Para controlar energía
import cv2
import os


# Configuración de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

VERSION = "3.0.4"
MAX_CHARS_VOZ = 200
VOICE_TIMEOUT = 5.0       # Aumentado de 1.5 a 5.0 para no cortar
VOICE_PHRASE_LIMIT = 15   # Aumentado de 10 a 15 para frases largas
VOICE_AMBIENT_DURATION = 0.5 
VOICE_SLEEP_WHILE_TALKING = 0.1 

class SaraUltimateGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Crear splash screen PRIMERO
        from splash_screen import crear_splash
        splash = crear_splash()
        splash.update_progress(10, "Inicializando SARA...", "Cargando módulos...")
        
        # Callback para actualizar splash
        def update_splash(value, status, detail=""):
            splash.update_progress(value, status, detail)
        
        # Importar brain (puede tardar)
        splash.update_progress(20, "Importando módulos...", "Brain, Voice, DevOps...")
        from brain import SaraBrain
        from config import ConfigManager
        from devops import DevOpsManager
        
        # Inicializar brain con callback
        splash.update_progress(25, "Inicializando Brain...", "Esto puede tardar ~30s la primera vez")
        self.brain = SaraBrain(splash_callback=update_splash)
        
        splash.update_progress(85, "Configurando interfaz...", "Preparando ventana principal")
        
        self.is_listening = False

        # Configuración Ventana (COMPACTA)
        self.title(f"S.A.R.A. {VERSION}")
        self.geometry("550x500")  # Casi cuadrada y más ancha
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
            # width eliminado para dejar que pack maneje el ancho
            fg_color=self.COLORS["bg_primary"],
            segmented_button_fg_color=self.COLORS["bg_secondary"],
            segmented_button_selected_color=self.COLORS["accent"],
            segmented_button_selected_hover_color=self.COLORS["accent_hover"],
            segmented_button_unselected_color=self.COLORS["bg_elevated"],
            segmented_button_unselected_hover_color=self.COLORS["bg_hover"],
            text_color=self.COLORS["text_primary"],
            corner_radius=12
        )
        self.tabview.pack(padx=10, pady=(0, 10), fill="both", expand=True)
        
        self.tab_chat = self.tabview.add("💬 Chat")
        self.tab_config = self.tabview.add("⚙️ Config")
        self.tab_dev = self.tabview.add("🛠️ Dev")
        self.tab_network = self.tabview.add("🌐 Network")

        # --- PESTAÑAS ---
        self.setup_chat_tab()  
        self.setup_config_tab()
        self.setup_dev_tab()
        self.setup_network_tab()

        self.actualizar_estado_global()
        
        # Cerrar splash
        splash.update_progress(100, "¡Listo!", "SARA está lista para usar")
        time.sleep(0.5)
        splash.close()
        
        self.log("SYS", f"✅ Sistema {VERSION} Inicializado.", "sys")
        from devops import DevOpsManager
        self.log("SYS", f"📂 Dir: {DevOpsManager.WORK_DIR}", "dev")
        
        if not self.brain.ia_online:
            self.log("SARA", "💡 Escribe 'configura' para activar la IA.", "sys")
        else:
            # Usar mensaje personalizado del perfil
            saludo = self.brain.perfil.get_welcome_message() if self.brain.perfil else "👋 Hola! Soy SARA. ¿En qué trabajamos hoy?"
            self.log("SARA", saludo, "sara")
            self.brain.voz.hablar(saludo)
    
    def _setup_colors(self):
        """Define la paleta de colores moderna"""
        self.COLORS = {
            # Principales
            "accent": "#00D9FF",
            "accent_hover": "#00B8D4",
            "secondary": "#7C4DFF",
            "success": "#00E676",
            "error": "#FF1744",
            "warning": "#FFD600",
            
            # Fondos
            "bg_primary": "#0A0E27",
            "bg_secondary": "#151B3B",
            "bg_elevated": "#1E2749",
            "bg_hover": "#252D54",
            
            # Textos
            "text_primary": "#FFFFFF",
            "text_secondary": "#B0B8D4",
            "text_disabled": "#6B7599",
        }
    
    def setup_header(self):
        """Header compacto"""
        header = ctk.CTkFrame(
            self,
            height=40,
            fg_color=self.COLORS["bg_secondary"],
            corner_radius=0
        )
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # Header simplificado (Solo estado, sin título repetido)
        self.header_status = ctk.CTkLabel(
            header,
            text="🟢 SISTEMA ONLINE",
            font=("Inter", 11, "bold"),
            text_color=self.COLORS["success"]
        )
        self.header_status.pack(side="right", padx=20, pady=10)

        # Versión pequeña discreta a la izquierda
        ver_label = ctk.CTkLabel(
            header,
            text=f"v{VERSION}",
            font=("Inter", 10),
            text_color=self.COLORS["text_disabled"]
        )
        ver_label.pack(side="left", padx=20, pady=10)

    def setup_chat_tab(self):
        # Frame principal
        main_frame = ctk.CTkFrame(
            self.tab_chat, 
            fg_color="transparent"
        )
        main_frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Área de Chat (más compacta)
        self.chat = ctk.CTkTextbox(
            main_frame,
            width=350,
            height=260,
            state="disabled",
            font=("JetBrains Mono", 10),
            fg_color=self.COLORS["bg_primary"],
            text_color=self.COLORS["text_primary"],
            border_width=1,
            border_color=self.COLORS["bg_elevated"],
            corner_radius=10,
            scrollbar_button_color=self.COLORS["accent"],
            scrollbar_button_hover_color=self.COLORS["accent_hover"]
        )
        self.chat.pack(fill="both", expand=True, pady=(0, 10))
        
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

        # Área de Entrada Flotante y Estilizada
        input_container = ctk.CTkFrame(
            main_frame, 
            fg_color=self.COLORS["bg_secondary"],
            corner_radius=25,
            height=60
        )
        input_container.pack(fill="x", pady=5)
        
        self.entry = ctk.CTkEntry(
            input_container,
            placeholder_text="Escribe un mensaje...",
            height=45,
            font=("Inter", 13),
            border_width=0,
            corner_radius=20,
            fg_color="transparent",
            text_color=self.COLORS["text_primary"],
            placeholder_text_color=self.COLORS["text_disabled"]
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=15, pady=5)
        self.entry.bind("<Return>", self.enviar)
        
        # Botones de Acción Claros
        
        # Botón Voz
        self.btn_voz = ctk.CTkButton(
            input_container,
            text="🎙️",
            width=45,
            height=45,
            command=self.toggle_mic,
            font=("Segoe UI Emoji", 20), # Fuente mejor para emojis
            fg_color=self.COLORS["bg_elevated"],
            hover_color=self.COLORS["error"], # Hover rojo para indicar grabación/acción
            corner_radius=22,
            text_color=self.COLORS["text_primary"]
        )
        self.btn_voz.pack(side="right", padx=(5, 10), pady=5)
        
        # Botón Enviar
        self.btn_send = ctk.CTkButton(
            input_container,
            text="🚀",
            width=45,
            height=45,
            command=self.enviar,
            font=("Segoe UI Emoji", 20),
            fg_color=self.COLORS["accent"],
            hover_color=self.COLORS["accent_hover"],
            corner_radius=20,     # Ligeramente diferente para estilo
            text_color="white"
        )
        self.btn_send.pack(side="right", padx=(0, 5), pady=5)
        
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
        
        # Título dentro de la tarjeta
        ctk.CTkLabel(
            card,
            text="⚙️ AJUSTES DE INTELIGENCIA",
            font=("Inter", 14, "bold"),
            text_color=self.COLORS["accent"]
        ).pack(pady=(20, 25))
        
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

        # Botón guardar
        ctk.CTkButton(
            card,
            text="GUARDAR CAMBIOS",
            command=self.guardar_config,
            height=50,
            font=("Inter", 12, "bold"),
            fg_color=self.COLORS["success"],
            hover_color="#00C853",
            corner_radius=15
        ).pack(fill="x", padx=25, pady=(30, 10))
        
        # Botón Mi Perfil
        ctk.CTkButton(
            card,
            text="👤 MI PERFIL",
            command=self.open_profile_settings,
            height=50,
            font=("Inter", 12, "bold"),
            fg_color=self.COLORS["secondary"],
            hover_color="#6A3DE8",
            corner_radius=15
        ).pack(fill="x", padx=25, pady=(0, 30))

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
        ctk.CTkLabel(self.tab_dev, text="PANEL DE CONTROL", font=("Roboto", 14, "bold"), text_color="#bdc3c7").pack(pady=(10, 5))
        ctk.CTkLabel(self.tab_dev, text="Herramientas de Desarrollo y Sistema", font=("Roboto", 10), text_color="#7f8c8d").pack(pady=(0, 15))

        btn_frame = ctk.CTkFrame(self.tab_dev, fg_color="transparent")
        btn_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        # Paleta "Premium Dark" - Unificada para look profesional
        # Formato: (Emoji, Título, Comando)
        botones_config = [
            ("📊", "Estado Git", "git status"),
            ("🚀", "Subir Cambios", "git push"),
            ("🌐", "Túnel Web", "compartir proyecto"),
            ("📟", "Monitor CPU", "sistema"),
            ("🧪", "Build / Deps", "instalar dependencias"),
            ("💀", "Kill Python", "matar python")
        ]
        
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        
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
            # Layout de 2 columnas
            b.grid(row=i//2, column=i%2, padx=6, pady=6, sticky="nsew")
    
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
            estado = f"🟢 Online | {self.brain.preferred_provider}"
            color = self.COLORS["success"]
        else:
            estado = "🔴 Offline"
            color = self.COLORS["error"]
        
        self.header_status.configure(text=estado, text_color=color)
        
        # Actualizar label de estado en chat tab (Eliminado)
        # if hasattr(self, 'lbl_status'):
        #     ia_text = f"IA: {self.brain.preferred_provider}" if self.brain.ia_online else "IA: OFFLINE"
        #     self.lbl_status.configure(
        #         text=ia_text,
        #         text_color=self.COLORS["success"] if self.brain.ia_online else self.COLORS["text_disabled"]
        #     )

    def animar_texto(self, user, text, tag="sys"):
        """Simula efecto de escritura tipo hacker/IA."""
        ts = datetime.datetime.now().strftime("%H:%M")
        header = f"[{ts}] {user}: "
        
        self.chat.configure(state="normal")
        self.chat.insert("end", header, tag)
        
        # Insertar texto completo (sin animación para mejor rendimiento)
        self.chat.insert("end", f"{text}\n", tag)
        
        self.chat.see("end")
        self.chat.configure(state="disabled")

    def log(self, user, text, tag="sys"):
        # Wrapper thread-safe
        self.after(0, lambda: self._log_impl(user, text, tag))

    def _log_impl(self, user, text, tag="sys"):
        # Usar animación solo para mensajes de SARA importantes
        if user == "SARA" and len(text) < 150:
            self.animar_texto(user, text, tag)
        else:
            # Renderizado instantáneo para logs largos o del sistema
            try:
                self.chat.configure(state="normal")
                ts = datetime.datetime.now().strftime("%H:%M")
                self.chat.insert("end", f"[{ts}] {user}: {text}\n", tag)
                self.chat.see("end")
                self.chat.configure(state="disabled")
            except: pass # Evitar error si se intenta loguear con ventana destruida

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
        t = threading.Thread(target=self._procesar_comando, args=(texto,))
        t.start()
        
    def _procesar_comando(self, texto):
        try:
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
            
            self.log("SARA", resp, "sara")
            
            # Hablar respuesta (solo si no es muy larga o es local)
            if origen == "sara" or origen == "exit" or (len(resp) < MAX_CHARS_VOZ and origen != "code"):
                self.brain.voz.hablar(resp)
            
            # --- MANEJO DE ESTADOS ESPECIALES ---
            if origen == "exit":
                self.log("SYS", "Apagando sistema en 3 segundos...", "sys")
                self.after(3000, self.destroy)

            self.actualizar_estado_global()
        except Exception as e:
            self.log("ERROR", str(e), "error")

    def toggle_mic(self):
        self.is_listening = not self.is_listening
        if self.is_listening:
            self.btn_voz.configure(text="⏹️", fg_color=self.COLORS["error"])
            threading.Thread(target=self.loop_voz, daemon=True).start()
        else:
            self.btn_voz.configure(text="�️", fg_color=self.COLORS["bg_elevated"])
            
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
                            self.btn_voz.configure(text="🎤", fg_color=self.COLORS["secondary"])
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

                        # Lista ampliada de variantes
                        variantes_sara = ["sara", "zara", "sarah", "sahara", "zrah", "ara", "shara"]
                        
                        # Detectar palabra clave O contexto activo
                        if contexto_activo or any(w in txt for w in variantes_sara):
                            if not contexto_activo: 
                                print("DEBUG: WAKE WORD DETECTADA!")
                                # Feedback auditivo
                                try:
                                    import winsound
                                    winsound.Beep(800, 100)
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
                        
                    except: pass
        except Exception as e:
            logging.error(f"Error microfono: {e}")
            self.is_listening = False
            try: 
                self.btn_voz.configure(text="🎤", fg_color=self.COLORS["secondary"])
            except: pass

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

    # --- SENTINELA MODE REMOVED ---


if __name__ == "__main__":
    app = SaraUltimateGUI()
    app.setup_tray() # Iniciar Icono
    app.protocol("WM_DELETE_WINDOW", app.on_closing) # Interceptar botón X
    app.mainloop() 