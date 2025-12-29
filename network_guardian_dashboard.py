"""
NetworkGuardian - Dashboard Visual
Ventana dedicada con gráficos en tiempo real y gestión de dispositivos.
"""

import customtkinter as ctk
import threading
import time
from datetime import datetime
from typing import Optional
import logging

class NetworkGuardianDashboard(ctk.CTkToplevel):
    """Dashboard visual para NetworkGuardian con gráficos y controles."""
    
    def __init__(self, guardian_instance, parent=None):
        """
        Inicializa el dashboard.
        
        Args:
            guardian_instance: Instancia de NetworkGuardian
            parent: Ventana padre (opcional)
        """
        super().__init__(parent)
        
        self.guardian = guardian_instance
        self.running = True
        self.update_interval = 2000  # 2 segundos
        
        # Historial de tráfico para gráficos
        self.traffic_history = {
            'timestamps': [],
            'upload': [],
            'download': []
        }
        self.max_history_points = 30  # 1 minuto de historia
        
        # Configuración de ventana
        self.title("🛡️ NetworkGuardian Dashboard")
        self.geometry("1100x650")
        self.minsize(900, 550)
        
        # Colores del tema
        self._setup_colors()
        
        # Configurar ventana
        self.configure(fg_color=self.COLORS["bg_primary"])
        
        # Fix para DPI scaling en Toplevel
        self.after(10, self._init_dashboard)
        
        # Protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        logging.info("✓ Dashboard de NetworkGuardian iniciado")
    
    def _init_dashboard(self):
        """Inicializa el dashboard después de que la ventana esté lista."""
        # Crear UI
        self._create_layout()
        
        # Iniciar actualización automática
        self._start_auto_update()
    
    def _setup_colors(self):
        """Define la paleta de colores mejorada."""
        self.COLORS = {
            "bg_primary": "#0B0E1D",
            "bg_secondary": "#151B3B",
            "bg_elevated": "#1E2749",
            "bg_hover": "#2A3358",
            "accent": "#00D9FF",
            "accent_hover": "#00B8D4",
            "accent_glow": "#00E5FF",
            "success": "#00E676",
            "success_dark": "#00C853",
            "warning": "#FFD600",
            "warning_dark": "#FFC400",
            "error": "#FF1744",
            "error_dark": "#D50000",
            "text_primary": "#FFFFFF",
            "text_secondary": "#B0B8D4",
            "text_muted": "#7A8199",
            "border": "#2E3A5F",
            "gradient_start": "#1E2749",
            "gradient_end": "#0B0E1D",
        }
    
    def _create_layout(self):
        """Crea el layout principal del dashboard."""
        
        # ===== HEADER =====
        header = ctk.CTkFrame(self, height=50, fg_color=self.COLORS["bg_secondary"], corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # Título
        title = ctk.CTkLabel(
            header,
            text="🛡️ NetworkGuardian",
            font=("Inter", 16, "bold"),
            text_color=self.COLORS["accent"]
        )
        title.pack(side="left", padx=15, pady=12)
        
        # Estado de vigilancia
        self.status_label = ctk.CTkLabel(
            header,
            text="🔴 Vigilancia: INACTIVA",
            font=("Inter", 10),
            text_color=self.COLORS["error"]
        )
        self.status_label.pack(side="right", padx=15, pady=12)
        
        # ===== CONTENIDO PRINCIPAL =====
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configurar grid
        main_container.grid_columnconfigure(0, weight=2)  # Izquierda más ancha
        main_container.grid_columnconfigure(1, weight=1)  # Derecha
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)
        
        # ===== PANEL IZQUIERDO SUPERIOR: ESTADÍSTICAS =====
        self._create_stats_panel(main_container)
        
        # ===== PANEL IZQUIERDO INFERIOR: DISPOSITIVOS =====
        self._create_devices_panel(main_container)
        
        # ===== PANEL DERECHO SUPERIOR: TRÁFICO =====
        self._create_traffic_panel(main_container)
        
        # ===== PANEL DERECHO INFERIOR: CONTROLES =====
        self._create_controls_panel(main_container)
    
    def _create_stats_panel(self, parent):
        """Crea panel de estadísticas."""
        panel = ctk.CTkFrame(parent, fg_color=self.COLORS["bg_elevated"], corner_radius=12)
        panel.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Título
        title = ctk.CTkLabel(
            panel,
            text="📊 Estadísticas de Red",
            font=("Inter", 14, "bold"),
            text_color=self.COLORS["text_primary"]
        )
        title.pack(pady=(12, 8))
        
        # Frame para stats
        stats_frame = ctk.CTkFrame(panel, fg_color="transparent")
        stats_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Grid de estadísticas
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Crear tarjetas de stats
        self.stat_cards = {}
        stats_config = [
            ("total_devices", "Dispositivos Totales", "📱", self.COLORS["accent"]),
            ("active_devices", "Activos (24h)", "🟢", self.COLORS["success"]),
            ("blocked_devices", "Bloqueados", "🔒", self.COLORS["error"]),
            ("pending_alerts", "Alertas", "🚨", self.COLORS["warning"])
        ]
        
        for i, (key, label, emoji, color) in enumerate(stats_config):
            card = self._create_stat_card(stats_frame, emoji, "0", label, color)
            card.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            self.stat_cards[key] = card
    
    def _create_stat_card(self, parent, emoji, value, label, color):
        """Crea una tarjeta de estadística."""
        card = ctk.CTkFrame(parent, fg_color=self.COLORS["bg_secondary"], corner_radius=10)
        
        # Emoji
        emoji_label = ctk.CTkLabel(
            card,
            text=emoji,
            font=("Segoe UI Emoji", 24)
        )
        emoji_label.pack(pady=(8, 4))
        
        # Valor
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Inter", 22, "bold"),
            text_color=color
        )
        value_label.pack()
        
        # Label
        label_widget = ctk.CTkLabel(
            card,
            text=label,
            font=("Inter", 9),
            text_color=self.COLORS["text_secondary"]
        )
        label_widget.pack(pady=(4, 8))
        
        # Guardar referencia al valor
        card.value_label = value_label
        
        return card
    
    def _create_devices_panel(self, parent):
        """Crea panel de dispositivos."""
        panel = ctk.CTkFrame(parent, fg_color=self.COLORS["bg_elevated"], corner_radius=12)
        panel.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # Header
        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 5))
        
        title = ctk.CTkLabel(
            header,
            text="📱 Dispositivos en Red",
            font=("Inter", 16, "bold"),
            text_color=self.COLORS["text_primary"]
        )
        title.pack(side="left")
        
        # Botón refrescar
        refresh_btn = ctk.CTkButton(
            header,
            text="🔄",
            width=40,
            height=30,
            command=self._refresh_devices,
            fg_color=self.COLORS["accent"],
            hover_color=self.COLORS["accent_hover"],
            corner_radius=8
        )
        refresh_btn.pack(side="right")
        
        # Lista de dispositivos (scrollable)
        self.devices_list = ctk.CTkScrollableFrame(
            panel,
            fg_color=self.COLORS["bg_secondary"],
            corner_radius=10
        )
        self.devices_list.pack(fill="both", expand=True, padx=15, pady=(5, 15))
    
    def _create_traffic_panel(self, parent):
        """Crea panel de tráfico mejorado con gráfico."""
        panel = ctk.CTkFrame(parent, fg_color=self.COLORS["bg_elevated"], corner_radius=12)
        panel.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        # Título
        title = ctk.CTkLabel(
            panel,
            text="📊 Tráfico de Red",
            font=("Inter", 16, "bold"),
            text_color=self.COLORS["text_primary"]
        )
        title.pack(pady=(15, 10))
        
        # Frame de métricas
        metrics_frame = ctk.CTkFrame(panel, fg_color="transparent")
        metrics_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Gráfico simple de barras (visual)
        graph_frame = ctk.CTkFrame(metrics_frame, fg_color=self.COLORS["bg_secondary"], corner_radius=10, height=120)
        graph_frame.pack(fill="x", pady=(0, 10))
        graph_frame.pack_propagate(False)
        
        self.graph_canvas = ctk.CTkLabel(
            graph_frame,
            text="📈 Cargando gráfico...",
            font=("JetBrains Mono", 9),
            text_color=self.COLORS["text_muted"],
            justify="left"
        )
        self.graph_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Velocidad de subida
        upload_frame = ctk.CTkFrame(metrics_frame, fg_color=self.COLORS["bg_secondary"], corner_radius=10)
        upload_frame.pack(fill="x", pady=5)
        
        upload_icon = ctk.CTkLabel(
            upload_frame,
            text="📤",
            font=("Segoe UI Emoji", 18)
        )
        upload_icon.pack(side="left", padx=(12, 8), pady=8)
        
        upload_info = ctk.CTkFrame(upload_frame, fg_color="transparent")
        upload_info.pack(side="left", fill="both", expand=True, pady=10)
        
        ctk.CTkLabel(
            upload_info,
            text="Subida",
            font=("Inter", 11),
            text_color=self.COLORS["text_secondary"],
            anchor="w"
        ).pack(anchor="w")
        
        self.upload_label = ctk.CTkLabel(
            upload_info,
            text="0.00 Mbps",
            font=("Inter", 18, "bold"),
            text_color=self.COLORS["success"],
            anchor="w"
        )
        self.upload_label.pack(anchor="w")
        
        # Velocidad de bajada
        download_frame = ctk.CTkFrame(metrics_frame, fg_color=self.COLORS["bg_secondary"], corner_radius=10)
        download_frame.pack(fill="x", pady=5)
        
        download_icon = ctk.CTkLabel(
            download_frame,
            text="📥",
            font=("Segoe UI Emoji", 18)
        )
        download_icon.pack(side="left", padx=(12, 8), pady=8)
        
        download_info = ctk.CTkFrame(download_frame, fg_color="transparent")
        download_info.pack(side="left", fill="both", expand=True, pady=10)
        
        ctk.CTkLabel(
            download_info,
            text="Bajada",
            font=("Inter", 11),
            text_color=self.COLORS["text_secondary"],
            anchor="w"
        ).pack(anchor="w")
        
        self.download_label = ctk.CTkLabel(
            download_info,
            text="0.00 Mbps",
            font=("Inter", 18, "bold"),
            text_color=self.COLORS["accent"],
            anchor="w"
        )
        self.download_label.pack(anchor="w")
        
        # Total transferido
        total_frame = ctk.CTkFrame(metrics_frame, fg_color=self.COLORS["bg_secondary"], corner_radius=10)
        total_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            total_frame,
            text="📦 Total Transferido",
            font=("Inter", 11),
            text_color=self.COLORS["text_secondary"]
        ).pack(pady=(10, 5))
        
        self.total_label = ctk.CTkLabel(
            total_frame,
            text="↑ 0 GB  ↓ 0 GB",
            font=("Inter", 13, "bold"),
            text_color=self.COLORS["text_primary"]
        )
        self.total_label.pack(pady=(0, 10))
    
    def _create_controls_panel(self, parent):
        """Crea panel de controles."""
        panel = ctk.CTkFrame(parent, fg_color=self.COLORS["bg_elevated"], corner_radius=12)
        panel.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        # Título
        title = ctk.CTkLabel(
            panel,
            text="⚙️ Controles",
            font=("Inter", 14, "bold"),
            text_color=self.COLORS["text_primary"]
        )
        title.pack(pady=(12, 8))
        
        # Frame de botones SCROLLABLE
        buttons_frame = ctk.CTkScrollableFrame(
            panel, 
            fg_color="transparent",
            scrollbar_button_color=self.COLORS["accent"],
            scrollbar_button_hover_color=self.COLORS["accent_hover"]
        )
        buttons_frame.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        
        # Botones de control
        controls = [
            ("🔍 Iniciar Vigilancia", self._toggle_monitoring, self.COLORS["success"]),
            ("📊 Generar Reporte", self._generate_report, self.COLORS["accent"]),
            ("🏰 Modo Fortaleza", self._toggle_fortress, self.COLORS["warning"]),
            ("🚨 Ver Alertas", self._show_alerts, self.COLORS["error"]),
            ("🔄 Escanear Ahora", self._force_scan, self.COLORS["accent"]),
        ]
        
        for text, command, color in controls:
            btn = ctk.CTkButton(
                buttons_frame,
                text=text,
                command=command,
                height=38,
                font=("Inter", 11),
                fg_color=color,
                hover_color=self.COLORS["accent_hover"],
                corner_radius=8
            )
            btn.pack(fill="x", pady=4)
        
        # Guardar referencia al botón de vigilancia
        self.monitor_btn = buttons_frame.winfo_children()[0]
    
    # ===== MÉTODOS DE ACTUALIZACIÓN =====
    
    def _start_auto_update(self):
        """Inicia actualización automática del dashboard."""
        def update_loop():
            while self.running:
                try:
                    self.after(0, self._update_all_data)
                    time.sleep(self.update_interval / 1000)
                except:
                    break
        
        threading.Thread(target=update_loop, daemon=True).start()
    
    def _update_all_data(self):
        """Actualiza todos los datos del dashboard."""
        try:
            # Actualizar estadísticas
            self._update_stats()
            
            # Actualizar tráfico
            self._update_traffic()
            
            # Actualizar estado de vigilancia
            self._update_monitoring_status()
            
        except Exception as e:
            logging.error(f"Error actualizando dashboard: {e}")
    
    def _update_stats(self):
        """Actualiza estadísticas."""
        try:
            stats = self.guardian.db.obtener_estadisticas()
            
            # Actualizar tarjetas
            self.stat_cards["total_devices"].value_label.configure(
                text=str(stats.get("total_devices", 0))
            )
            self.stat_cards["active_devices"].value_label.configure(
                text=str(stats.get("active_devices", 0))
            )
            self.stat_cards["blocked_devices"].value_label.configure(
                text=str(stats.get("blocked_devices", 0))
            )
            self.stat_cards["pending_alerts"].value_label.configure(
                text=str(stats.get("pending_alerts", 0))
            )
        except Exception as e:
            logging.error(f"Error actualizando stats: {e}")
    
    def _update_traffic(self):
        """Actualiza métricas de tráfico."""
        try:
            traffic = self.guardian.traffic.obtener_uso_red_global()
            
            # Velocidades
            upload = traffic.get("velocidad_subida_mbps", 0)
            download = traffic.get("velocidad_bajada_mbps", 0)
            
            self.upload_label.configure(text=f"{upload:.2f} Mbps")
            self.download_label.configure(text=f"{download:.2f} Mbps")
            
            # Totales
            sent_gb = traffic.get("bytes_sent_total", 0) / (1024**3)
            recv_gb = traffic.get("bytes_recv_total", 0) / (1024**3)
            
            self.total_label.configure(text=f"↑ {sent_gb:.2f} GB  ↓ {recv_gb:.2f} GB")
            
        except Exception as e:
            logging.error(f"Error actualizando tráfico: {e}")
    
    def _update_monitoring_status(self):
        """Actualiza estado de vigilancia."""
        try:
            if self.guardian.monitor.esta_activo():
                self.status_label.configure(
                    text="🟢 Vigilancia: ACTIVA",
                    text_color=self.COLORS["success"]
                )
                self.monitor_btn.configure(text="⏹️ Detener Vigilancia")
            else:
                self.status_label.configure(
                    text="🔴 Vigilancia: INACTIVA",
                    text_color=self.COLORS["error"]
                )
                self.monitor_btn.configure(text="🔍 Iniciar Vigilancia")
        except Exception as e:
            logging.error(f"Error actualizando estado: {e}")
    
    def _refresh_devices(self):
        """Refresca la lista de dispositivos."""
        try:
            # Limpiar lista actual
            for widget in self.devices_list.winfo_children():
                widget.destroy()
            
            # Obtener dispositivos
            dispositivos = self.guardian.db.obtener_todos_dispositivos(solo_activos=True)
            
            if not dispositivos:
                no_devices = ctk.CTkLabel(
                    self.devices_list,
                    text="No hay dispositivos activos",
                    font=("Inter", 12),
                    text_color=self.COLORS["text_secondary"]
                )
                no_devices.pack(pady=20)
                return
            
            # Mostrar dispositivos
            for disp in dispositivos[:10]:  # Máximo 10
                self._create_device_card(disp)
                
        except Exception as e:
            logging.error(f"Error refrescando dispositivos: {e}")
    
    def _create_device_card(self, device_info):
        """Crea una tarjeta de dispositivo."""
        card = ctk.CTkFrame(
            self.devices_list,
            fg_color=self.COLORS["bg_primary"],
            corner_radius=8
        )
        card.pack(fill="x", pady=3, padx=5)
        
        # Info del dispositivo
        nombre = device_info.get("custom_name") or device_info.get("device_type") or "Desconocido"
        ip = device_info.get("ip", "N/A")
        trust = device_info.get("trust_level", "unknown")
        
        # Emoji según confianza
        trust_emoji = {"trusted": "✅", "unknown": "❓", "suspicious": "⚠️"}.get(trust, "❓")
        
        # Nombre y emoji
        name_label = ctk.CTkLabel(
            card,
            text=f"{trust_emoji} {nombre}",
            font=("Inter", 12, "bold"),
            text_color=self.COLORS["text_primary"],
            anchor="w"
        )
        name_label.pack(side="left", padx=10, pady=8)
        
        # IP
        ip_label = ctk.CTkLabel(
            card,
            text=ip,
            font=("Inter", 10),
            text_color=self.COLORS["text_secondary"]
        )
        ip_label.pack(side="right", padx=10, pady=8)
    
    # ===== MÉTODOS DE CONTROL =====
    
    def _toggle_monitoring(self):
        """Activa/desactiva vigilancia."""
        try:
            if self.guardian.monitor.esta_activo():
                self.guardian.detener_vigilancia()
            else:
                self.guardian.iniciar_vigilancia()
            
            self._update_monitoring_status()
        except Exception as e:
            logging.error(f"Error toggle monitoring: {e}")
    
    def _generate_report(self):
        """Genera reporte completo."""
        try:
            # Crear ventana de reporte
            report_window = ctk.CTkToplevel(self)
            report_window.title("📄 Reporte de Red")
            report_window.geometry("700x600")
            
            # Textbox con reporte
            textbox = ctk.CTkTextbox(
                report_window,
                font=("JetBrains Mono", 10),
                fg_color=self.COLORS["bg_primary"]
            )
            textbox.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Generar y mostrar reporte
            reporte = self.guardian.generar_reporte_completo()
            textbox.insert("1.0", reporte)
            textbox.configure(state="disabled")
            
        except Exception as e:
            logging.error(f"Error generando reporte: {e}")
    
    def _toggle_fortress(self):
        """Activa modo fortaleza."""
        try:
            resultado = self.guardian.modo_fortaleza(activar=True)
            
            # Mostrar resultado
            dialog = ctk.CTkInputDialog(
                text=resultado,
                title="Modo Fortaleza"
            )
        except Exception as e:
            logging.error(f"Error modo fortaleza: {e}")
    
    def _show_alerts(self):
        """Muestra alertas pendientes."""
        try:
            # Crear ventana de alertas
            alerts_window = ctk.CTkToplevel(self)
            alerts_window.title("🚨 Alertas de Seguridad")
            alerts_window.geometry("600x500")
            
            # Textbox con alertas
            textbox = ctk.CTkTextbox(
                alerts_window,
                font=("Inter", 11),
                fg_color=self.COLORS["bg_primary"]
            )
            textbox.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Obtener y mostrar alertas
            alertas_text = self.guardian.obtener_alertas_pendientes()
            textbox.insert("1.0", alertas_text)
            textbox.configure(state="disabled")
            
        except Exception as e:
            logging.error(f"Error mostrando alertas: {e}")
    
    def _force_scan(self):
        """Fuerza un escaneo inmediato."""
        try:
            self.guardian.monitor.forzar_escaneo()
            self._refresh_devices()
        except Exception as e:
            logging.error(f"Error forzando escaneo: {e}")
    
    def _on_closing(self):
        """Maneja el cierre del dashboard."""
        self.running = False
        self.destroy()
        logging.info("✓ Dashboard cerrado")


# ===== FUNCIÓN DE LANZAMIENTO =====

def abrir_dashboard(guardian_instance, parent=None):
    """
    Abre el dashboard de NetworkGuardian.
    
    Args:
        guardian_instance: Instancia de NetworkGuardian
        parent: Ventana padre (opcional)
    
    Returns:
        Instancia del dashboard
    """
    dashboard = NetworkGuardianDashboard(guardian_instance, parent)
    return dashboard
