"""
NetworkGuardian - Módulo Principal de Integración
Sistema completo de monitoreo y seguridad de red para SARA.
"""

import logging
from typing import Optional
from monitor import SystemMonitor
from network_guardian_db import DeviceDatabase
from network_guardian_alerts import AlertSystem
from network_guardian_monitor import NetworkMonitor
from network_guardian_traffic import TrafficAnalyzer
from network_guardian_ai import NetworkGuardianAI

class NetworkGuardian:
    """
    Sistema completo de monitoreo y seguridad de red.
    Integra todas las funcionalidades de NetworkGuardian.
    """
    
    def __init__(self, voice_callback: Optional[callable] = None, ia_callback: Optional[callable] = None, auto_start: bool = True):
        """
        Inicializa NetworkGuardian.
        
        Args:
            voice_callback: Función para síntesis de voz (brain.voz.hablar)
            ia_callback: Función para consultar IA (brain.consultar_ia)
            auto_start: Si True, inicia vigilancia automáticamente (default: True)
        """
        logging.info("🛡️ Inicializando NetworkGuardian...")
        
        # Componentes principales
        self.db = DeviceDatabase()
        self.alerts = AlertSystem(voice_callback=voice_callback, db_manager=self.db)
        self.monitor = NetworkMonitor(
            scanner_func=SystemMonitor.escanear_red,
            db_manager=self.db,
            alert_system=self.alerts,
            interval=60  # Escanear cada 60 segundos
        )
        self.traffic = TrafficAnalyzer(db_manager=self.db)
        self.ai = NetworkGuardianAI(ia_callback=ia_callback)
        
        # Estado
        self.initialized = True
        
        # Iniciar vigilancia automáticamente si está configurado
        if auto_start:
            self.iniciar_vigilancia()
            logging.info("✅ Vigilancia iniciada automáticamente")
        
        logging.info("✅ NetworkGuardian inicializado correctamente")
    
    # ==================== CONTROL DEL SISTEMA ====================
    
    def iniciar_vigilancia(self) -> str:
        """Inicia el monitoreo continuo de la red."""
        if self.monitor.iniciar():
            return "🛡️ Vigilancia de red activada. Monitoreando 24/7..."
        return "⚠️ La vigilancia ya está activa"
    
    def detener_vigilancia(self) -> str:
        """Detiene el monitoreo continuo."""
        if self.monitor.detener():
            return "⏹️ Vigilancia de red detenida"
        return "ℹ️ La vigilancia no estaba activa"
    
    def pausar_vigilancia(self) -> str:
        """Pausa temporalmente el monitoreo."""
        self.monitor.pausar()
        return "⏸️ Vigilancia pausada temporalmente"
    
    def reanudar_vigilancia(self) -> str:
        """Reanuda el monitoreo."""
        self.monitor.reanudar()
        return "▶️ Vigilancia reanudada"
    
    def estado_vigilancia(self) -> str:
        """Obtiene el estado actual de la vigilancia."""
        if self.monitor.esta_activo():
            stats = self.monitor.obtener_estadisticas()
            return (f"🟢 Vigilancia ACTIVA\n"
                   f"Escaneos realizados: {stats['total_scans']}\n"
                   f"Dispositivos descubiertos: {stats['devices_discovered']}\n"
                   f"Alertas generadas: {stats['alerts_generated']}")
        elif self.monitor.running and self.monitor.paused:
            return "🟡 Vigilancia PAUSADA"
        else:
            return "🔴 Vigilancia INACTIVA"
    
    # ==================== GESTIÓN DE DISPOSITIVOS ====================
    
    def listar_dispositivos(self, solo_activos: bool = True) -> str:
        """Lista todos los dispositivos conocidos."""
        dispositivos = self.db.obtener_todos_dispositivos(solo_activos=solo_activos)
        
        if not dispositivos:
            return "ℹ️ No hay dispositivos registrados"
        
        reporte = f"📱 DISPOSITIVOS {'ACTIVOS' if solo_activos else 'REGISTRADOS'} ({len(dispositivos)})\n"
        reporte += "=" * 60 + "\n"
        
        for i, disp in enumerate(dispositivos[:15], 1):  # Mostrar máximo 15
            nombre = disp.get('custom_name') or disp.get('device_type') or 'Desconocido'
            ip = disp.get('ip', 'N/A')
            trust = disp.get('trust_level', 'unknown')
            bloqueado = "🔒" if disp.get('is_blocked') else ""
            
            # Emoji según confianza
            trust_emoji = {
                'trusted': '✅',
                'unknown': '❓',
                'suspicious': '⚠️'
            }.get(trust, '❓')
            
            reporte += f"{i}. {trust_emoji} {nombre} {bloqueado}\n"
            reporte += f"   IP: {ip} | MAC: {disp.get('mac', 'N/A')}\n"
            reporte += f"   Visto: {disp.get('last_seen', 'N/A')}\n\n"
        
        if len(dispositivos) > 15:
            reporte += f"... y {len(dispositivos) - 15} dispositivos más\n"
        
        return reporte
    
    def confiar_dispositivo(self, ip_o_mac: str) -> str:
        """Marca un dispositivo como confiable."""
        # Buscar dispositivo
        dispositivos = self.db.obtener_todos_dispositivos(solo_activos=False)
        
        for disp in dispositivos:
            if disp.get('ip') == ip_o_mac or disp.get('mac') == ip_o_mac:
                mac = disp['mac']
                self.db.actualizar_confianza(mac, 'trusted')
                nombre = disp.get('custom_name') or disp.get('device_type') or ip_o_mac
                return f"✅ {nombre} marcado como CONFIABLE"
        
        return f"❌ No se encontró dispositivo: {ip_o_mac}"
    
    def marcar_sospechoso(self, ip_o_mac: str) -> str:
        """Marca un dispositivo como sospechoso."""
        dispositivos = self.db.obtener_todos_dispositivos(solo_activos=False)
        
        for disp in dispositivos:
            if disp.get('ip') == ip_o_mac or disp.get('mac') == ip_o_mac:
                mac = disp['mac']
                self.db.actualizar_confianza(mac, 'suspicious')
                nombre = disp.get('custom_name') or disp.get('device_type') or ip_o_mac
                return f"⚠️ {nombre} marcado como SOSPECHOSO"
        
        return f"❌ No se encontró dispositivo: {ip_o_mac}"
    
    def renombrar_dispositivo(self, ip_o_mac: str, nuevo_nombre: str) -> str:
        """Asigna un nombre personalizado a un dispositivo."""
        dispositivos = self.db.obtener_todos_dispositivos(solo_activos=False)
        
        for disp in dispositivos:
            if disp.get('ip') == ip_o_mac or disp.get('mac') == ip_o_mac:
                mac = disp['mac']
                self.db.personalizar_dispositivo(mac, custom_name=nuevo_nombre)
                return f"✅ Dispositivo renombrado a: {nuevo_nombre}"
        
        return f"❌ No se encontró dispositivo: {ip_o_mac}"
    
    # ==================== SEGURIDAD ====================
    
    def modo_fortaleza(self, activar: bool = True) -> str:
        """
        Activa/desactiva modo fortaleza (bloquea todos los dispositivos no confiables).
        """
        if activar:
            # Obtener dispositivos no confiables
            dispositivos = self.db.obtener_todos_dispositivos(solo_activos=False)
            bloqueados = 0
            
            for disp in dispositivos:
                trust = disp.get('trust_level', 'unknown')
                if trust != 'trusted':
                    mac = disp['mac']
                    ip = disp.get('ip')
                    
                    # Bloquear en firewall
                    resultado = SystemMonitor.bloquear_ip_local(ip)
                    if resultado.get('exito'):
                        self.db.bloquear_dispositivo(mac, "Modo Fortaleza")
                        bloqueados += 1
            
            return f"🏰 MODO FORTALEZA ACTIVADO\n{bloqueados} dispositivos bloqueados"
        else:
            return "🏰 Modo Fortaleza desactivado (función en desarrollo)"
    
    def obtener_alertas_pendientes(self) -> str:
        """Obtiene alertas no leídas."""
        alertas = self.alerts.obtener_alertas_pendientes()
        
        if not alertas:
            return "✅ No hay alertas pendientes"
        
        reporte = f"🚨 ALERTAS PENDIENTES ({len(alertas)})\n"
        reporte += "=" * 50 + "\n"
        
        for alerta in alertas[:10]:  # Mostrar máximo 10
            severity_emoji = {
                'info': 'ℹ️',
                'warning': '⚠️',
                'critical': '🚨'
            }.get(alerta.get('severity'), '📢')
            
            reporte += f"{severity_emoji} {alerta.get('title')}\n"
            reporte += f"   {alerta.get('message')}\n"
            reporte += f"   {alerta.get('timestamp')}\n\n"
        
        if len(alertas) > 10:
            reporte += f"... y {len(alertas) - 10} alertas más\n"
        
        return reporte
    
    # ==================== ANÁLISIS DE TRÁFICO ====================
    
    def analizar_trafico(self) -> str:
        """Obtiene análisis completo de tráfico de red."""
        reporte = self.traffic.obtener_reporte_red_formateado()
        reporte += "\n\n"
        reporte += self.traffic.obtener_reporte_procesos_formateado(top_n=5)
        return reporte
    
    def top_consumidores(self, top_n: int = 5) -> str:
        """Obtiene los procesos que más consumen red."""
        return self.traffic.obtener_reporte_procesos_formateado(top_n=top_n)
    
    def conexiones_activas(self) -> str:
        """Obtiene lista de conexiones activas."""
        return self.traffic.obtener_reporte_conexiones_formateado(limit=15)
    
    # ==================== ANÁLISIS CON IA ====================
    
    def analizar_dispositivo_inteligente(self, ip_o_mac: str) -> str:
        """Analiza un dispositivo usando IA para recomendaciones."""
        # Buscar dispositivo
        dispositivos = self.db.obtener_todos_dispositivos(solo_activos=False)
        
        for disp in dispositivos:
            if disp.get('ip') == ip_o_mac or disp.get('mac') == ip_o_mac:
                # Obtener info adicional si está activo
                if disp.get('ip'):
                    info_detallada = SystemMonitor.investigar_dispositivo(disp['ip'])
                    # Combinar info
                    disp.update(info_detallada)
                
                # Análisis con IA
                return self.ai.analizar_dispositivo_con_ia(disp)
        
        return f"❌ No se encontró dispositivo: {ip_o_mac}"
    
    def explicar_alertas_con_ia(self) -> str:
        """Explica las alertas pendientes en lenguaje simple usando IA."""
        alertas = self.alerts.obtener_alertas_pendientes()
        
        if not alertas:
            return "✅ No hay alertas pendientes"
        
        if not self.ai.ia_disponible:
            return self.obtener_alertas_pendientes()  # Versión sin IA
        
        reporte = "🤖 EXPLICACIÓN INTELIGENTE DE ALERTAS\n"
        reporte += "=" * 50 + "\n\n"
        
        for i, alerta in enumerate(alertas[:5], 1):  # Máximo 5 para no saturar
            titulo = alerta.get('title', 'Sin título')
            explicacion = self.ai.explicar_alerta_con_ia(alerta)
            
            reporte += f"{i}. {titulo}\n"
            reporte += f"   💡 {explicacion}\n\n"
        
        if len(alertas) > 5:
            reporte += f"... y {len(alertas) - 5} alertas más\n"
        
        return reporte
    
    def recomendar_accion(self, situacion: str) -> str:
        """Pide recomendaciones a la IA sobre qué hacer."""
        return self.ai.recomendar_accion_con_ia(situacion)
    
    # ==================== REPORTES ====================
    
    def generar_reporte_completo(self) -> str:
        """Genera un reporte completo del estado de la red."""
        reporte = "🛡️ NETWORKGUARDIAN - REPORTE COMPLETO\n"
        reporte += "=" * 70 + "\n"
        reporte += f"Fecha: {logging.Formatter().formatTime(logging.LogRecord('', 0, '', 0, '', (), None))}\n\n"
        
        # Estado de vigilancia
        reporte += "📊 ESTADO DE VIGILANCIA\n"
        reporte += "-" * 70 + "\n"
        reporte += self.estado_vigilancia() + "\n\n"
        
        # Estadísticas de dispositivos
        stats_db = self.db.obtener_estadisticas()
        reporte += "📱 ESTADÍSTICAS DE DISPOSITIVOS\n"
        reporte += "-" * 70 + "\n"
        reporte += f"Total registrados: {stats_db.get('total_devices', 0)}\n"
        reporte += f"Activos (24h): {stats_db.get('active_devices', 0)}\n"
        reporte += f"Bloqueados: {stats_db.get('blocked_devices', 0)}\n"
        reporte += f"Alertas pendientes: {stats_db.get('pending_alerts', 0)}\n\n"
        
        # Análisis inteligente con IA (si está disponible)
        if self.ai.ia_disponible:
            stats_completas = self.obtener_estadisticas()
            analisis_ia = self.ai.generar_reporte_inteligente(stats_completas)
            reporte += analisis_ia + "\n\n"
        
        # Tráfico de red
        reporte += self.traffic.obtener_reporte_red_formateado()
        reporte += "\n"
        
        # Top procesos
        reporte += self.traffic.obtener_reporte_procesos_formateado(top_n=3)
        
        return reporte
    
    def obtener_estadisticas(self) -> dict:
        """Obtiene estadísticas en formato dict."""
        return {
            'db': self.db.obtener_estadisticas(),
            'monitor': self.monitor.obtener_estadisticas(),
            'traffic': self.traffic.obtener_uso_red_global()
        }
    
    # ==================== CONFIGURACIÓN ====================
    
    def configurar_intervalo_escaneo(self, segundos: int) -> str:
        """Configura el intervalo de escaneo."""
        self.monitor.configurar_intervalo(segundos)
        return f"⏱️ Intervalo de escaneo configurado a {segundos} segundos"
    
    def habilitar_alertas_voz(self, enabled: bool = True) -> str:
        """Habilita/deshabilita alertas por voz."""
        self.alerts.habilitar_voz(enabled)
        return f"🔊 Alertas de voz: {'HABILITADAS' if enabled else 'DESHABILITADAS'}"
    
    def configurar_umbral_voz(self, nivel: str) -> str:
        """
        Configura el nivel mínimo para alertas de voz.
        
        Args:
            nivel: 'info', 'warning', o 'critical'
        """
        self.alerts.configurar_umbral_voz(nivel)
        return f"🔊 Umbral de voz configurado a: {nivel}"
    
    def abrir_dashboard(self, parent=None):
        """
        Abre el dashboard visual de NetworkGuardian.
        
        Args:
            parent: Ventana padre (opcional)
        
        Returns:
            Instancia del dashboard
        """
        try:
            from network_guardian_dashboard import abrir_dashboard
            dashboard = abrir_dashboard(self, parent)
            return dashboard
        except Exception as e:
            logging.error(f"Error abriendo dashboard: {e}")
            return None
    
    # ==================== LIMPIEZA ====================
    
    def limpiar_datos_antiguos(self, dias: int = 30) -> str:
        """Limpia eventos y datos antiguos."""
        eventos_eliminados = self.db.limpiar_eventos_antiguos(dias)
        return f"🧹 Limpieza completada: {eventos_eliminados} eventos eliminados"
    
    def cerrar(self):
        """Cierra NetworkGuardian y libera recursos."""
        logging.info("🛡️ Cerrando NetworkGuardian...")
        self.monitor.detener()
        self.db.cerrar()
        logging.info("✅ NetworkGuardian cerrado")
    
    def __del__(self):
        """Destructor para asegurar limpieza."""
        try:
            self.cerrar()
        except:
            pass


# ==================== INSTANCIA GLOBAL (OPCIONAL) ====================

_guardian_instance = None

def obtener_guardian(voice_callback=None, ia_callback=None, auto_start=True) -> NetworkGuardian:
    """
    Obtiene la instancia global de NetworkGuardian (patrón Singleton).
    
    Args:
        voice_callback: Función de voz (solo necesaria en primera llamada)
        ia_callback: Función de IA (solo necesaria en primera llamada)
        auto_start: Iniciar vigilancia automáticamente (default: True)
    """
    global _guardian_instance
    
    if _guardian_instance is None:
        _guardian_instance = NetworkGuardian(
            voice_callback=voice_callback,
            ia_callback=ia_callback,
            auto_start=auto_start
        )
    
    return _guardian_instance
