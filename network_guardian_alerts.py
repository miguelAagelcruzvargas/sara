"""
NetworkGuardian - Sistema de Alertas y Notificaciones
Gestión de alertas de seguridad con notificaciones de escritorio y voz.
"""

import logging
from typing import Optional, Callable
from datetime import datetime
import threading

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    logging.warning("⚠ plyer no disponible. Instala con: pip install plyer")

class AlertSystem:
    """Sistema de alertas con notificaciones de escritorio y callbacks."""
    
    # Niveles de severidad
    SEVERITY_INFO = "info"
    SEVERITY_WARNING = "warning"
    SEVERITY_CRITICAL = "critical"
    
    # Tipos de alertas
    TYPE_NEW_DEVICE = "new_device"
    TYPE_BLOCKED_DEVICE = "blocked_device_attempt"
    TYPE_SUSPICIOUS_ACTIVITY = "suspicious_activity"
    TYPE_PORT_SCAN = "port_scan_detected"
    TYPE_ARP_SPOOF = "arp_spoofing"
    TYPE_BANDWIDTH_SPIKE = "bandwidth_spike"
    TYPE_DEVICE_OFFLINE = "device_offline"
    
    def __init__(self, voice_callback: Optional[Callable] = None, db_manager = None):
        """
        Inicializa el sistema de alertas.
        
        Args:
            voice_callback: Función para síntesis de voz (ej: brain.voz.hablar)
            db_manager: Instancia de DeviceDatabase para persistencia
        """
        self.voice_callback = voice_callback
        self.db = db_manager
        self.enabled = True
        self.voice_enabled = True
        self.desktop_enabled = PLYER_AVAILABLE
        
        # Configuración de severidad para voz
        self.voice_severity_threshold = self.SEVERITY_WARNING
        
        logging.info("✓ Sistema de alertas inicializado")
    
    def crear_alerta(self, alert_type: str, severity: str, title: str, message: str,
                    mac: str = None, ip: str = None, speak: bool = None) -> bool:
        """
        Crea una nueva alerta y la notifica.
        
        Args:
            alert_type: Tipo de alerta (usar constantes TYPE_*)
            severity: Severidad (info/warning/critical)
            title: Título de la alerta
            message: Mensaje descriptivo
            mac: MAC del dispositivo relacionado (opcional)
            ip: IP del dispositivo relacionado (opcional)
            speak: Forzar/evitar síntesis de voz (None = automático)
        """
        if not self.enabled:
            return False
        
        try:
            # Guardar en base de datos
            if self.db:
                self.db._crear_alerta(alert_type, severity, title, message, mac, ip)
            
            # Notificación de escritorio
            if self.desktop_enabled:
                self._notificar_escritorio(title, message, severity)
            
            # Notificación por voz
            should_speak = speak if speak is not None else self._debe_hablar(severity)
            if should_speak and self.voice_enabled and self.voice_callback:
                self._notificar_voz(title, message, severity)
            
            # Log
            emoji = self._get_emoji_severity(severity)
            logging.info(f"{emoji} ALERTA [{severity.upper()}]: {title} - {message}")
            
            return True
        except Exception as e:
            logging.error(f"Error creando alerta: {e}")
            return False
    
    def _notificar_escritorio(self, title: str, message: str, severity: str):
        """Muestra notificación de escritorio."""
        if not PLYER_AVAILABLE:
            return
        
        try:
            # Configurar icono según severidad
            app_icon = None  # Puedes agregar ruta a iconos personalizados
            
            notification.notify(
                title=f"🛡️ NetworkGuardian - {title}",
                message=message,
                app_name="SARA NetworkGuardian",
                timeout=10 if severity != self.SEVERITY_CRITICAL else 30,
                app_icon=app_icon
            )
        except Exception as e:
            logging.error(f"Error en notificación de escritorio: {e}")
    
    def _notificar_voz(self, title: str, message: str, severity: str):
        """Notifica por síntesis de voz."""
        if not self.voice_callback:
            return
        
        try:
            # Mensaje simplificado para voz
            if severity == self.SEVERITY_CRITICAL:
                voz_msg = f"Alerta crítica. {title}. {message}"
            elif severity == self.SEVERITY_WARNING:
                voz_msg = f"Atención. {title}."
            else:
                voz_msg = f"{title}."
            
            # Ejecutar en thread separado para no bloquear
            threading.Thread(
                target=self.voice_callback,
                args=(voz_msg,),
                daemon=True
            ).start()
        except Exception as e:
            logging.error(f"Error en notificación de voz: {e}")
    
    def _debe_hablar(self, severity: str) -> bool:
        """Determina si debe usar voz según severidad."""
        severity_levels = {
            self.SEVERITY_INFO: 0,
            self.SEVERITY_WARNING: 1,
            self.SEVERITY_CRITICAL: 2
        }
        
        threshold_level = severity_levels.get(self.voice_severity_threshold, 1)
        current_level = severity_levels.get(severity, 0)
        
        return current_level >= threshold_level
    
    def _get_emoji_severity(self, severity: str) -> str:
        """Retorna emoji según severidad."""
        emojis = {
            self.SEVERITY_INFO: "ℹ️",
            self.SEVERITY_WARNING: "⚠️",
            self.SEVERITY_CRITICAL: "🚨"
        }
        return emojis.get(severity, "📢")
    
    # ==================== ALERTAS PREDEFINIDAS ====================
    
    def alerta_nuevo_dispositivo(self, device_info: dict):
        """Alerta de nuevo dispositivo detectado."""
        device_name = device_info.get('custom_name') or device_info.get('tipo') or "Desconocido"
        ip = device_info.get('ip', 'N/A')
        mac = device_info.get('mac')
        
        self.crear_alerta(
            alert_type=self.TYPE_NEW_DEVICE,
            severity=self.SEVERITY_WARNING,
            title="Nuevo Dispositivo Detectado",
            message=f"{device_name} se conectó a la red ({ip})",
            mac=mac,
            ip=ip
        )
    
    def alerta_dispositivo_bloqueado(self, device_info: dict):
        """Alerta de intento de conexión de dispositivo bloqueado."""
        device_name = device_info.get('custom_name') or device_info.get('tipo') or "Desconocido"
        ip = device_info.get('ip', 'N/A')
        mac = device_info.get('mac')
        
        self.crear_alerta(
            alert_type=self.TYPE_BLOCKED_DEVICE,
            severity=self.SEVERITY_CRITICAL,
            title="Dispositivo Bloqueado Detectado",
            message=f"⛔ {device_name} ({ip}) intentó conectarse pero está bloqueado",
            mac=mac,
            ip=ip,
            speak=True  # Forzar voz para dispositivos bloqueados
        )
    
    def alerta_actividad_sospechosa(self, descripcion: str, ip: str = None, mac: str = None):
        """Alerta de actividad sospechosa."""
        self.crear_alerta(
            alert_type=self.TYPE_SUSPICIOUS_ACTIVITY,
            severity=self.SEVERITY_CRITICAL,
            title="Actividad Sospechosa",
            message=descripcion,
            mac=mac,
            ip=ip,
            speak=True
        )
    
    def alerta_port_scan(self, ip_atacante: str, puertos_escaneados: int):
        """Alerta de escaneo de puertos detectado."""
        self.crear_alerta(
            alert_type=self.TYPE_PORT_SCAN,
            severity=self.SEVERITY_CRITICAL,
            title="Escaneo de Puertos Detectado",
            message=f"🔍 IP {ip_atacante} escaneó {puertos_escaneados} puertos",
            ip=ip_atacante,
            speak=True
        )
    
    def alerta_arp_spoofing(self, ip: str, mac_original: str, mac_falsa: str):
        """Alerta de posible ARP spoofing."""
        self.crear_alerta(
            alert_type=self.TYPE_ARP_SPOOF,
            severity=self.SEVERITY_CRITICAL,
            title="Posible ARP Spoofing",
            message=f"⚠️ IP {ip} tiene múltiples MACs: {mac_original} vs {mac_falsa}",
            ip=ip,
            speak=True
        )
    
    def alerta_pico_ancho_banda(self, dispositivo: str, uso_mb: float):
        """Alerta de pico de ancho de banda."""
        self.crear_alerta(
            alert_type=self.TYPE_BANDWIDTH_SPIKE,
            severity=self.SEVERITY_WARNING,
            title="Pico de Ancho de Banda",
            message=f"📊 {dispositivo} está usando {uso_mb:.1f} MB/s",
            speak=False  # No hablar para picos de ancho de banda
        )
    
    # ==================== CONFIGURACIÓN ====================
    
    def habilitar_alertas(self, enabled: bool = True):
        """Habilita o deshabilita el sistema de alertas."""
        self.enabled = enabled
        logging.info(f"Sistema de alertas: {'HABILITADO' if enabled else 'DESHABILITADO'}")
    
    def habilitar_voz(self, enabled: bool = True):
        """Habilita o deshabilita notificaciones por voz."""
        self.voice_enabled = enabled
        logging.info(f"Alertas de voz: {'HABILITADAS' if enabled else 'DESHABILITADAS'}")
    
    def configurar_umbral_voz(self, severity: str):
        """
        Configura el umbral de severidad para alertas de voz.
        
        Args:
            severity: 'info', 'warning', o 'critical'
        """
        if severity in [self.SEVERITY_INFO, self.SEVERITY_WARNING, self.SEVERITY_CRITICAL]:
            self.voice_severity_threshold = severity
            logging.info(f"Umbral de voz configurado a: {severity}")
        else:
            logging.warning(f"Severidad inválida: {severity}")
    
    def obtener_alertas_pendientes(self) -> list:
        """Obtiene alertas no leídas desde la base de datos."""
        if not self.db:
            return []
        
        return self.db.obtener_alertas_pendientes()
    
    def marcar_leida(self, alert_id: int):
        """Marca una alerta como leída."""
        if self.db:
            self.db.marcar_alerta_leida(alert_id)
