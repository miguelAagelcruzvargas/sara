"""
NetworkGuardian - Análisis de Tráfico de Red
Monitoreo de ancho de banda y análisis de consumo por dispositivo/proceso.
"""

import psutil
import time
import logging
from typing import Dict, List, Tuple
from datetime import datetime
from collections import defaultdict

class TrafficAnalyzer:
    """Analizador de tráfico de red con estadísticas por proceso y dispositivo."""
    
    def __init__(self, db_manager=None):
        """
        Inicializa el analizador de tráfico.
        
        Args:
            db_manager: Instancia de DeviceDatabase para persistencia
        """
        self.db = db_manager
        
        # Estadísticas de red anteriores para calcular deltas
        self.last_net_io = None
        self.last_check_time = None
        
        # Estadísticas por proceso
        self.process_stats = {}
        
        logging.info("✓ TrafficAnalyzer inicializado")
    
    # ==================== ANÁLISIS GLOBAL ====================
    
    def obtener_uso_red_global(self) -> Dict:
        """
        Obtiene estadísticas globales de uso de red.
        
        Returns:
            Dict con bytes_sent, bytes_recv, velocidad_subida, velocidad_bajada
        """
        try:
            current_io = psutil.net_io_counters()
            current_time = time.time()
            
            stats = {
                'bytes_sent_total': current_io.bytes_sent,
                'bytes_recv_total': current_io.bytes_recv,
                'packets_sent_total': current_io.packets_sent,
                'packets_recv_total': current_io.packets_recv,
                'errors_in': current_io.errin,
                'errors_out': current_io.errout,
                'drops_in': current_io.dropin,
                'drops_out': current_io.dropout,
                'velocidad_subida_mbps': 0.0,
                'velocidad_bajada_mbps': 0.0
            }
            
            # Calcular velocidad si tenemos datos anteriores
            if self.last_net_io and self.last_check_time:
                time_delta = current_time - self.last_check_time
                
                if time_delta > 0:
                    bytes_sent_delta = current_io.bytes_sent - self.last_net_io.bytes_sent
                    bytes_recv_delta = current_io.bytes_recv - self.last_net_io.bytes_recv
                    
                    # Convertir a Mbps
                    stats['velocidad_subida_mbps'] = (bytes_sent_delta / time_delta) / (1024 * 1024)
                    stats['velocidad_bajada_mbps'] = (bytes_recv_delta / time_delta) / (1024 * 1024)
            
            # Guardar para próxima comparación
            self.last_net_io = current_io
            self.last_check_time = current_time
            
            return stats
        except Exception as e:
            logging.error(f"Error obteniendo uso de red global: {e}")
            return {}
    
    def obtener_reporte_red_formateado(self) -> str:
        """Obtiene reporte formateado de uso de red."""
        stats = self.obtener_uso_red_global()
        
        if not stats:
            return "❌ Error obteniendo estadísticas de red"
        
        reporte = "📊 ESTADÍSTICAS DE RED\n"
        reporte += "=" * 40 + "\n"
        reporte += f"📤 Subida Total: {stats['bytes_sent_total'] / (1024**3):.2f} GB\n"
        reporte += f"📥 Bajada Total: {stats['bytes_recv_total'] / (1024**3):.2f} GB\n"
        reporte += f"⚡ Velocidad Subida: {stats['velocidad_subida_mbps']:.2f} Mbps\n"
        reporte += f"⚡ Velocidad Bajada: {stats['velocidad_bajada_mbps']:.2f} Mbps\n"
        reporte += f"📦 Paquetes Enviados: {stats['packets_sent_total']:,}\n"
        reporte += f"📦 Paquetes Recibidos: {stats['packets_recv_total']:,}\n"
        
        if stats['errors_in'] > 0 or stats['errors_out'] > 0:
            reporte += f"\n⚠️ Errores: ↓{stats['errors_in']} ↑{stats['errors_out']}\n"
        
        if stats['drops_in'] > 0 or stats['drops_out'] > 0:
            reporte += f"⚠️ Paquetes Perdidos: ↓{stats['drops_in']} ↑{stats['drops_out']}\n"
        
        return reporte
    
    # ==================== ANÁLISIS POR PROCESO ====================
    
    def obtener_procesos_red(self, top_n: int = 10) -> List[Dict]:
        """
        Obtiene los procesos con más conexiones de red activas.
        
        Args:
            top_n: Número de procesos a retornar
            
        Returns:
            Lista de diccionarios con info de procesos
        """
        try:
            process_connections = defaultdict(lambda: {
                'pid': 0,
                'name': '',
                'connections': 0,
                'tcp': 0,
                'udp': 0,
                'listening': 0,
                'established': 0
            })
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    pid = proc.info['pid']
                    name = proc.info['name']
                    
                    connections = proc.connections(kind='inet')
                    
                    if connections:
                        process_connections[pid]['pid'] = pid
                        process_connections[pid]['name'] = name
                        process_connections[pid]['connections'] = len(connections)
                        
                        for conn in connections:
                            # Tipo de conexión
                            if conn.type == 1:  # SOCK_STREAM (TCP)
                                process_connections[pid]['tcp'] += 1
                            elif conn.type == 2:  # SOCK_DGRAM (UDP)
                                process_connections[pid]['udp'] += 1
                            
                            # Estado
                            if hasattr(conn, 'status'):
                                if conn.status == 'LISTEN':
                                    process_connections[pid]['listening'] += 1
                                elif conn.status == 'ESTABLISHED':
                                    process_connections[pid]['established'] += 1
                
                except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
                    continue
            
            # Convertir a lista y ordenar por número de conexiones
            result = list(process_connections.values())
            result.sort(key=lambda x: x['connections'], reverse=True)
            
            return result[:top_n]
        except Exception as e:
            logging.error(f"Error obteniendo procesos de red: {e}")
            return []
    
    def obtener_reporte_procesos_formateado(self, top_n: int = 10) -> str:
        """Obtiene reporte formateado de procesos con actividad de red."""
        procesos = self.obtener_procesos_red(top_n)
        
        if not procesos:
            return "ℹ️ No se detectaron procesos con actividad de red"
        
        reporte = f"🔝 TOP {len(procesos)} PROCESOS CON ACTIVIDAD DE RED\n"
        reporte += "=" * 50 + "\n"
        
        for i, proc in enumerate(procesos, 1):
            reporte += f"{i}. {proc['name']} (PID: {proc['pid']})\n"
            reporte += f"   Conexiones: {proc['connections']} "
            reporte += f"(TCP: {proc['tcp']}, UDP: {proc['udp']})\n"
            
            if proc['established'] > 0:
                reporte += f"   Establecidas: {proc['established']}\n"
            if proc['listening'] > 0:
                reporte += f"   Escuchando: {proc['listening']}\n"
            
            reporte += "\n"
        
        return reporte
    
    # ==================== ANÁLISIS POR INTERFAZ ====================
    
    def obtener_interfaces_red(self) -> Dict[str, Dict]:
        """Obtiene estadísticas por interfaz de red."""
        try:
            interfaces = {}
            net_io_per_nic = psutil.net_io_counters(pernic=True)
            
            for interface_name, stats in net_io_per_nic.items():
                interfaces[interface_name] = {
                    'bytes_sent': stats.bytes_sent,
                    'bytes_recv': stats.bytes_recv,
                    'packets_sent': stats.packets_sent,
                    'packets_recv': stats.packets_recv,
                    'errors_in': stats.errin,
                    'errors_out': stats.errout,
                    'drops_in': stats.dropin,
                    'drops_out': stats.dropout
                }
            
            return interfaces
        except Exception as e:
            logging.error(f"Error obteniendo interfaces: {e}")
            return {}
    
    def obtener_reporte_interfaces_formateado(self) -> str:
        """Obtiene reporte formateado de interfaces de red."""
        interfaces = self.obtener_interfaces_red()
        
        if not interfaces:
            return "❌ No se detectaron interfaces de red"
        
        reporte = "🌐 INTERFACES DE RED\n"
        reporte += "=" * 50 + "\n"
        
        for name, stats in interfaces.items():
            # Filtrar interfaces sin actividad
            if stats['bytes_sent'] == 0 and stats['bytes_recv'] == 0:
                continue
            
            reporte += f"\n📡 {name}\n"
            reporte += f"   ↑ Enviado: {stats['bytes_sent'] / (1024**2):.2f} MB\n"
            reporte += f"   ↓ Recibido: {stats['bytes_recv'] / (1024**2):.2f} MB\n"
            reporte += f"   📦 Paquetes: ↑{stats['packets_sent']:,} ↓{stats['packets_recv']:,}\n"
            
            if stats['errors_in'] > 0 or stats['errors_out'] > 0:
                reporte += f"   ⚠️ Errores: {stats['errors_in'] + stats['errors_out']}\n"
        
        return reporte
    
    # ==================== DETECCIÓN DE ANOMALÍAS ====================
    
    def detectar_picos_trafico(self, threshold_mbps: float = 10.0) -> Tuple[bool, str]:
        """
        Detecta picos inusuales de tráfico.
        
        Args:
            threshold_mbps: Umbral en Mbps para considerar pico
            
        Returns:
            (hay_pico, descripcion)
        """
        stats = self.obtener_uso_red_global()
        
        velocidad_subida = stats.get('velocidad_subida_mbps', 0)
        velocidad_bajada = stats.get('velocidad_bajada_mbps', 0)
        
        if velocidad_subida > threshold_mbps:
            return True, f"Pico de subida: {velocidad_subida:.2f} Mbps"
        
        if velocidad_bajada > threshold_mbps:
            return True, f"Pico de bajada: {velocidad_bajada:.2f} Mbps"
        
        return False, "Tráfico normal"
    
    def obtener_conexiones_activas(self) -> List[Dict]:
        """Obtiene lista de todas las conexiones activas en el sistema."""
        try:
            conexiones = []
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    for conn in proc.connections(kind='inet'):
                        conexiones.append({
                            'pid': proc.info['pid'],
                            'process': proc.info['name'],
                            'local_addr': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A",
                            'remote_addr': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                            'status': conn.status if hasattr(conn, 'status') else "N/A",
                            'type': 'TCP' if conn.type == 1 else 'UDP'
                        })
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    continue
            
            return conexiones
        except Exception as e:
            logging.error(f"Error obteniendo conexiones activas: {e}")
            return []
    
    def obtener_reporte_conexiones_formateado(self, limit: int = 20) -> str:
        """Obtiene reporte formateado de conexiones activas."""
        conexiones = self.obtener_conexiones_activas()
        
        if not conexiones:
            return "ℹ️ No hay conexiones activas"
        
        # Filtrar solo conexiones establecidas
        establecidas = [c for c in conexiones if c['status'] == 'ESTABLISHED']
        
        reporte = f"🔗 CONEXIONES ACTIVAS ({len(establecidas)} establecidas de {len(conexiones)} totales)\n"
        reporte += "=" * 70 + "\n"
        
        for i, conn in enumerate(establecidas[:limit], 1):
            reporte += f"{i}. {conn['process']} ({conn['type']})\n"
            reporte += f"   Local: {conn['local_addr']} → Remoto: {conn['remote_addr']}\n"
        
        if len(establecidas) > limit:
            reporte += f"\n... y {len(establecidas) - limit} conexiones más\n"
        
        return reporte
