"""
NetworkGuardian - Monitor de Red en Tiempo Real
Sistema de monitoreo continuo con detección de cambios y análisis de seguridad.
"""

import threading
import time
import logging
from typing import Dict, List, Set, Optional, Callable
from datetime import datetime, timedelta
import ipaddress

class NetworkMonitor:
    """Monitor de red en tiempo real con detección de cambios."""
    
    def __init__(self, scanner_func: Callable, db_manager, alert_system, interval: int = 60):
        """
        Inicializa el monitor de red.
        
        Args:
            scanner_func: Función de escaneo de red (ej: SystemMonitor.escanear_red)
            db_manager: Instancia de DeviceDatabase
            alert_system: Instancia de AlertSystem
            interval: Intervalo de escaneo en segundos (default: 60)
        """
        self.scanner_func = scanner_func
        self.db = db_manager
        self.alerts = alert_system
        self.interval = interval
        
        # Estado del monitor
        self.running = False
        self.paused = False
        self._thread = None
        
        # Caché de dispositivos
        self.devices_cache: Dict[str, dict] = {}  # mac -> device_info
        self.last_scan_time = None
        
        # Detección de anomalías
        self.arp_table_history: Dict[str, Set[str]] = {}  # ip -> set(macs)
        self.connection_attempts: Dict[str, List[datetime]] = {}  # ip -> [timestamps]
        
        # Estadísticas
        self.total_scans = 0
        self.devices_discovered = 0
        self.alerts_generated = 0
        
        logging.info("✓ NetworkMonitor inicializado")
    
    # ==================== CONTROL DEL MONITOR ====================
    
    def iniciar(self):
        """Inicia el monitoreo continuo."""
        if self.running:
            logging.warning("El monitor ya está en ejecución")
            return False
        
        self.running = True
        self.paused = False
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True, name="NetworkMonitor")
        self._thread.start()
        
        logging.info(f"🔍 Monitor de red iniciado (intervalo: {self.interval}s)")
        return True
    
    def detener(self):
        """Detiene el monitoreo."""
        if not self.running:
            return False
        
        self.running = False
        if self._thread:
            self._thread.join(timeout=5)
        
        logging.info("⏹️ Monitor de red detenido")
        return True
    
    def pausar(self):
        """Pausa el monitoreo temporalmente."""
        self.paused = True
        logging.info("⏸️ Monitor pausado")
    
    def reanudar(self):
        """Reanuda el monitoreo."""
        self.paused = False
        logging.info("▶️ Monitor reanudado")
    
    def esta_activo(self) -> bool:
        """Verifica si el monitor está activo."""
        return self.running and not self.paused
    
    # ==================== LOOP PRINCIPAL ====================
    
    def _monitor_loop(self):
        """Loop principal de monitoreo."""
        logging.info("🔄 Loop de monitoreo iniciado")
        
        # Escaneo inicial
        self._realizar_escaneo()
        
        while self.running:
            try:
                # Esperar intervalo
                for _ in range(self.interval):
                    if not self.running:
                        break
                    time.sleep(1)
                
                # Escanear si no está pausado
                if not self.paused and self.running:
                    self._realizar_escaneo()
                
            except Exception as e:
                logging.error(f"Error en loop de monitoreo: {e}")
                time.sleep(5)  # Esperar antes de reintentar
        
        logging.info("🔄 Loop de monitoreo finalizado")
    
    def _realizar_escaneo(self):
        """Realiza un escaneo de red y procesa resultados."""
        try:
            logging.debug("🔍 Iniciando escaneo de red...")
            
            # Ejecutar escaneo
            resultado = self.scanner_func()
            
            if 'error' in resultado:
                logging.error(f"Error en escaneo: {resultado['error']}")
                return
            
            # Procesar dispositivos encontrados
            dispositivos_actuales = resultado.get('dispositivos', [])
            self.last_scan_time = datetime.now()
            self.total_scans += 1
            
            # Detectar cambios
            self._procesar_dispositivos(dispositivos_actuales)
            
            # Análisis de seguridad
            self._analizar_seguridad(dispositivos_actuales)
            
            # Limpiar caché de dispositivos antiguos
            self._limpiar_cache()
            
            logging.debug(f"✓ Escaneo completado: {len(dispositivos_actuales)} dispositivos")
            
        except Exception as e:
            logging.error(f"Error realizando escaneo: {e}")
    
    # ==================== PROCESAMIENTO DE DISPOSITIVOS ====================
    
    def _procesar_dispositivos(self, dispositivos: List[dict]):
        """Procesa lista de dispositivos y detecta cambios."""
        macs_actuales = set()
        
        for dispositivo in dispositivos:
            mac = dispositivo.get('mac')
            ip = dispositivo.get('ip')
            
            if not mac:
                continue
            
            macs_actuales.add(mac)
            
            # Verificar si es nuevo
            es_nuevo = mac not in self.devices_cache
            
            # Actualizar base de datos
            self.db.agregar_o_actualizar_dispositivo(
                mac=mac,
                ip=ip,
                hostname=dispositivo.get('hostname'),
                device_type=dispositivo.get('tipo'),
                manufacturer=dispositivo.get('manufacturer')
            )
            
            # Obtener info completa de DB
            device_info = self.db.obtener_dispositivo(mac)
            
            if es_nuevo:
                self._manejar_nuevo_dispositivo(device_info)
            else:
                self._manejar_dispositivo_existente(device_info)
            
            # Actualizar caché
            self.devices_cache[mac] = device_info
        
        # Detectar dispositivos desconectados
        self._detectar_desconexiones(macs_actuales)
    
    def _manejar_nuevo_dispositivo(self, device_info: dict):
        """Maneja la detección de un nuevo dispositivo."""
        self.devices_discovered += 1
        
        mac = device_info['mac']
        ip = device_info['ip']
        trust_level = device_info.get('trust_level', 'unknown')
        is_blocked = device_info.get('is_blocked', 0)
        
        logging.info(f"🆕 Nuevo dispositivo: {device_info.get('device_type')} ({ip})")
        
        # Alerta si está bloqueado
        if is_blocked:
            self.alerts.alerta_dispositivo_bloqueado(device_info)
            self.alerts_generated += 1
        # Alerta si es desconocido
        elif trust_level == 'unknown':
            self.alerts.alerta_nuevo_dispositivo(device_info)
            self.alerts_generated += 1
    
    def _manejar_dispositivo_existente(self, device_info: dict):
        """Maneja un dispositivo ya conocido."""
        mac = device_info['mac']
        ip = device_info['ip']
        is_blocked = device_info.get('is_blocked', 0)
        
        # Verificar si está bloqueado
        if is_blocked:
            # Dispositivo bloqueado intentando conectarse
            self.alerts.alerta_dispositivo_bloqueado(device_info)
            self.alerts_generated += 1
            logging.warning(f"⛔ Dispositivo bloqueado detectado: {ip}")
        
        # Verificar cambio de IP
        cached_info = self.devices_cache.get(mac, {})
        old_ip = cached_info.get('ip')
        
        if old_ip and old_ip != ip:
            logging.info(f"🔄 Dispositivo {mac} cambió IP: {old_ip} → {ip}")
            self.db.registrar_evento('ip_changed', mac, ip, 'info', 
                                    f'IP cambió de {old_ip} a {ip}')
    
    def _detectar_desconexiones(self, macs_actuales: Set[str]):
        """Detecta dispositivos que se desconectaron."""
        macs_cache = set(self.devices_cache.keys())
        desconectados = macs_cache - macs_actuales
        
        for mac in desconectados:
            device_info = self.devices_cache[mac]
            ip = device_info.get('ip', 'N/A')
            device_name = device_info.get('custom_name') or device_info.get('device_type') or 'Desconocido'
            
            logging.info(f"📴 Dispositivo desconectado: {device_name} ({ip})")
            
            # Registrar evento
            self.db.registrar_evento('device_disconnected', mac, ip, 'info', 
                                    'Dispositivo desconectado de la red')
            
            # Remover del caché
            del self.devices_cache[mac]
    
    # ==================== ANÁLISIS DE SEGURIDAD ====================
    
    def _analizar_seguridad(self, dispositivos: List[dict]):
        """Realiza análisis de seguridad sobre los dispositivos."""
        # Detectar ARP spoofing
        self._detectar_arp_spoofing(dispositivos)
        
        # Detectar escaneos de puertos (basado en intentos de conexión)
        self._detectar_port_scanning()
        
        # Detectar picos de conexiones
        self._detectar_picos_conexion(dispositivos)
    
    def _detectar_arp_spoofing(self, dispositivos: List[dict]):
        """Detecta posible ARP spoofing (múltiples MACs para una IP)."""
        ip_to_macs: Dict[str, Set[str]] = {}
        
        # Agrupar MACs por IP
        for dispositivo in dispositivos:
            ip = dispositivo.get('ip')
            mac = dispositivo.get('mac')
            
            if ip and mac:
                if ip not in ip_to_macs:
                    ip_to_macs[ip] = set()
                ip_to_macs[ip].add(mac)
        
        # Detectar IPs con múltiples MACs
        for ip, macs in ip_to_macs.items():
            if len(macs) > 1:
                # Posible ARP spoofing
                macs_list = list(macs)
                
                # Verificar historial
                if ip in self.arp_table_history:
                    # Si ya detectamos esto antes, no alertar de nuevo
                    if macs == self.arp_table_history[ip]:
                        continue
                
                # Nueva detección
                logging.warning(f"⚠️ Posible ARP spoofing: IP {ip} tiene MACs: {macs_list}")
                
                self.alerts.alerta_arp_spoofing(ip, macs_list[0], macs_list[1])
                self.alerts_generated += 1
                
                # Guardar en historial
                self.arp_table_history[ip] = macs
                
                # Registrar evento
                self.db.registrar_evento('arp_spoofing_detected', None, ip, 'critical',
                                        f'Múltiples MACs detectadas: {", ".join(macs_list)}')
    
    def _detectar_port_scanning(self):
        """Detecta posibles escaneos de puertos basándose en intentos de conexión."""
        # Esta función requeriría monitoreo de conexiones a nivel de red
        # Por ahora es un placeholder para implementación futura
        pass
    
    def _detectar_picos_conexion(self, dispositivos: List[dict]):
        """Detecta picos inusuales de conexiones."""
        # Contar dispositivos activos
        num_dispositivos = len(dispositivos)
        
        # Si hay un aumento súbito (>50% respecto al promedio), alertar
        if len(self.devices_cache) > 0:
            aumento = (num_dispositivos - len(self.devices_cache)) / len(self.devices_cache)
            
            if aumento > 0.5:  # 50% de aumento
                logging.warning(f"⚠️ Pico de conexiones: {num_dispositivos} dispositivos (+{aumento*100:.0f}%)")
                
                self.alerts.alerta_actividad_sospechosa(
                    f"Pico de conexiones detectado: {num_dispositivos} dispositivos activos"
                )
                self.alerts_generated += 1
    
    # ==================== UTILIDADES ====================
    
    def _limpiar_cache(self):
        """Limpia dispositivos del caché que no se han visto recientemente."""
        # Mantener dispositivos vistos en las últimas 24 horas
        umbral = datetime.now() - timedelta(hours=24)
        
        macs_a_eliminar = []
        for mac, info in self.devices_cache.items():
            last_seen_str = info.get('last_seen')
            if last_seen_str:
                try:
                    last_seen = datetime.fromisoformat(last_seen_str)
                    if last_seen < umbral:
                        macs_a_eliminar.append(mac)
                except:
                    pass
        
        for mac in macs_a_eliminar:
            del self.devices_cache[mac]
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas del monitor."""
        return {
            'running': self.running,
            'paused': self.paused,
            'interval': self.interval,
            'total_scans': self.total_scans,
            'devices_discovered': self.devices_discovered,
            'alerts_generated': self.alerts_generated,
            'devices_in_cache': len(self.devices_cache),
            'last_scan': self.last_scan_time.isoformat() if self.last_scan_time else None
        }
    
    def obtener_dispositivos_activos(self) -> List[dict]:
        """Obtiene lista de dispositivos actualmente activos."""
        return list(self.devices_cache.values())
    
    def configurar_intervalo(self, segundos: int):
        """Cambia el intervalo de escaneo."""
        if segundos < 10:
            logging.warning("Intervalo mínimo: 10 segundos")
            segundos = 10
        
        self.interval = segundos
        logging.info(f"Intervalo de escaneo actualizado: {segundos}s")
    
    def forzar_escaneo(self):
        """Fuerza un escaneo inmediato."""
        if not self.running:
            logging.warning("El monitor no está en ejecución")
            return False
        
        logging.info("🔍 Forzando escaneo inmediato...")
        threading.Thread(target=self._realizar_escaneo, daemon=True).start()
        return True
