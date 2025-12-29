"""
NetworkGuardian - Database Manager
Gestión de base de datos SQLite para dispositivos de red y eventos de seguridad.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
import logging
from typing import List, Dict, Optional, Tuple

# Configuración
DB_FILE = "network_guardian.db"

class DeviceDatabase:
    """Gestor de base de datos para dispositivos de red."""
    
    def __init__(self, db_file: str = DB_FILE):
        self.db_file = db_file
        self.conn = None
        self._conectar()
        self._crear_tablas()
    
    def _conectar(self):
        """Establece conexión con la base de datos."""
        try:
            self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
            logging.info(f"✓ Conectado a base de datos: {self.db_file}")
        except Exception as e:
            logging.error(f"Error conectando a DB: {e}")
            raise
    
    def _crear_tablas(self):
        """Crea las tablas necesarias si no existen."""
        try:
            cursor = self.conn.cursor()
            
            # Tabla de dispositivos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS devices (
                    mac TEXT PRIMARY KEY,
                    ip TEXT,
                    hostname TEXT,
                    device_type TEXT,
                    manufacturer TEXT,
                    trust_level TEXT DEFAULT 'unknown',
                    custom_name TEXT,
                    custom_tags TEXT,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_connections INTEGER DEFAULT 1,
                    is_blocked INTEGER DEFAULT 0,
                    notes TEXT
                )
            ''')
            
            # Tabla de eventos de red
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS network_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    event_type TEXT NOT NULL,
                    mac TEXT,
                    ip TEXT,
                    severity TEXT DEFAULT 'info',
                    details TEXT,
                    FOREIGN KEY (mac) REFERENCES devices(mac)
                )
            ''')
            
            # Tabla de análisis de tráfico
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS traffic_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    mac TEXT,
                    ip TEXT,
                    bytes_sent INTEGER DEFAULT 0,
                    bytes_received INTEGER DEFAULT 0,
                    packets_sent INTEGER DEFAULT 0,
                    packets_received INTEGER DEFAULT 0,
                    FOREIGN KEY (mac) REFERENCES devices(mac)
                )
            ''')
            
            # Tabla de reglas de firewall
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS firewall_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_name TEXT UNIQUE NOT NULL,
                    ip TEXT NOT NULL,
                    action TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active INTEGER DEFAULT 1,
                    reason TEXT
                )
            ''')
            
            # Tabla de alertas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT,
                    mac TEXT,
                    ip TEXT,
                    is_read INTEGER DEFAULT 0,
                    is_dismissed INTEGER DEFAULT 0
                )
            ''')
            
            # Índices para mejorar rendimiento
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON network_events(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_type ON network_events(event_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_traffic_timestamp ON traffic_stats(timestamp)')
            
            self.conn.commit()
            logging.info("✓ Tablas de base de datos creadas/verificadas")
        except Exception as e:
            logging.error(f"Error creando tablas: {e}")
            raise
    
    # ==================== GESTIÓN DE DISPOSITIVOS ====================
    
    def agregar_o_actualizar_dispositivo(self, mac: str, ip: str, hostname: str = None, 
                                        device_type: str = None, manufacturer: str = None) -> bool:
        """Agrega un nuevo dispositivo o actualiza uno existente."""
        try:
            cursor = self.conn.cursor()
            
            # Verificar si existe
            cursor.execute('SELECT mac FROM devices WHERE mac = ?', (mac,))
            existe = cursor.fetchone()
            
            if existe:
                # Actualizar dispositivo existente
                cursor.execute('''
                    UPDATE devices 
                    SET ip = ?, 
                        hostname = COALESCE(?, hostname),
                        device_type = COALESCE(?, device_type),
                        manufacturer = COALESCE(?, manufacturer),
                        last_seen = CURRENT_TIMESTAMP,
                        total_connections = total_connections + 1
                    WHERE mac = ?
                ''', (ip, hostname, device_type, manufacturer, mac))
                
                self.registrar_evento('device_seen', mac, ip, 'info', 'Dispositivo visto en la red')
            else:
                # Insertar nuevo dispositivo
                cursor.execute('''
                    INSERT INTO devices (mac, ip, hostname, device_type, manufacturer)
                    VALUES (?, ?, ?, ?, ?)
                ''', (mac, ip, hostname, device_type, manufacturer))
                
                self.registrar_evento('device_discovered', mac, ip, 'warning', 'Nuevo dispositivo detectado')
                self._crear_alerta('new_device', 'warning', 'Nuevo Dispositivo', 
                                 f'Se detectó un nuevo dispositivo: {device_type or "Desconocido"} ({ip})', 
                                 mac, ip)
            
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error agregando/actualizando dispositivo: {e}")
            return False
    
    def obtener_dispositivo(self, mac: str) -> Optional[Dict]:
        """Obtiene información de un dispositivo por MAC."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM devices WHERE mac = ?', (mac,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logging.error(f"Error obteniendo dispositivo: {e}")
            return None
    
    def obtener_todos_dispositivos(self, solo_activos: bool = False) -> List[Dict]:
        """Obtiene lista de todos los dispositivos."""
        try:
            cursor = self.conn.cursor()
            
            if solo_activos:
                # Dispositivos vistos en las últimas 24 horas
                cursor.execute('''
                    SELECT * FROM devices 
                    WHERE datetime(last_seen) > datetime('now', '-1 day')
                    ORDER BY last_seen DESC
                ''')
            else:
                cursor.execute('SELECT * FROM devices ORDER BY last_seen DESC')
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error obteniendo dispositivos: {e}")
            return []
    
    def actualizar_confianza(self, mac: str, trust_level: str) -> bool:
        """Actualiza el nivel de confianza de un dispositivo (trusted/unknown/suspicious)."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE devices SET trust_level = ? WHERE mac = ?', (trust_level, mac))
            self.conn.commit()
            
            self.registrar_evento('trust_changed', mac, None, 'info', 
                                f'Nivel de confianza cambiado a: {trust_level}')
            return True
        except Exception as e:
            logging.error(f"Error actualizando confianza: {e}")
            return False
    
    def personalizar_dispositivo(self, mac: str, custom_name: str = None, tags: List[str] = None, 
                                notes: str = None) -> bool:
        """Personaliza un dispositivo con nombre, etiquetas y notas."""
        try:
            cursor = self.conn.cursor()
            
            updates = []
            params = []
            
            if custom_name:
                updates.append('custom_name = ?')
                params.append(custom_name)
            
            if tags:
                updates.append('custom_tags = ?')
                params.append(json.dumps(tags))
            
            if notes:
                updates.append('notes = ?')
                params.append(notes)
            
            if updates:
                params.append(mac)
                query = f"UPDATE devices SET {', '.join(updates)} WHERE mac = ?"
                cursor.execute(query, params)
                self.conn.commit()
                return True
            
            return False
        except Exception as e:
            logging.error(f"Error personalizando dispositivo: {e}")
            return False
    
    def bloquear_dispositivo(self, mac: str, razon: str = None) -> bool:
        """Marca un dispositivo como bloqueado."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE devices SET is_blocked = 1 WHERE mac = ?', (mac,))
            self.conn.commit()
            
            self.registrar_evento('device_blocked', mac, None, 'warning', razon or 'Bloqueado manualmente')
            return True
        except Exception as e:
            logging.error(f"Error bloqueando dispositivo: {e}")
            return False
    
    # ==================== EVENTOS DE RED ====================
    
    def registrar_evento(self, event_type: str, mac: str = None, ip: str = None, 
                        severity: str = 'info', details: str = None) -> bool:
        """Registra un evento de red."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO network_events (event_type, mac, ip, severity, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (event_type, mac, ip, severity, details))
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error registrando evento: {e}")
            return False
    
    def obtener_eventos(self, limit: int = 100, event_type: str = None) -> List[Dict]:
        """Obtiene eventos recientes."""
        try:
            cursor = self.conn.cursor()
            
            if event_type:
                cursor.execute('''
                    SELECT * FROM network_events 
                    WHERE event_type = ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (event_type, limit))
            else:
                cursor.execute('''
                    SELECT * FROM network_events 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error obteniendo eventos: {e}")
            return []
    
    # ==================== ALERTAS ====================
    
    def _crear_alerta(self, alert_type: str, severity: str, title: str, message: str,
                     mac: str = None, ip: str = None) -> bool:
        """Crea una nueva alerta."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO alerts (alert_type, severity, title, message, mac, ip)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (alert_type, severity, title, message, mac, ip))
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error creando alerta: {e}")
            return False
    
    def obtener_alertas_pendientes(self) -> List[Dict]:
        """Obtiene alertas no leídas."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM alerts 
                WHERE is_read = 0 AND is_dismissed = 0
                ORDER BY timestamp DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error obteniendo alertas: {e}")
            return []
    
    def marcar_alerta_leida(self, alert_id: int) -> bool:
        """Marca una alerta como leída."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE alerts SET is_read = 1 WHERE id = ?', (alert_id,))
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error marcando alerta: {e}")
            return False
    
    # ==================== ESTADÍSTICAS ====================
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas generales de la red."""
        try:
            cursor = self.conn.cursor()
            
            stats = {}
            
            # Total de dispositivos
            cursor.execute('SELECT COUNT(*) as total FROM devices')
            stats['total_devices'] = cursor.fetchone()['total']
            
            # Dispositivos activos (últimas 24h)
            cursor.execute('''
                SELECT COUNT(*) as active 
                FROM devices 
                WHERE datetime(last_seen) > datetime('now', '-1 day')
            ''')
            stats['active_devices'] = cursor.fetchone()['active']
            
            # Dispositivos bloqueados
            cursor.execute('SELECT COUNT(*) as blocked FROM devices WHERE is_blocked = 1')
            stats['blocked_devices'] = cursor.fetchone()['blocked']
            
            # Dispositivos por nivel de confianza
            cursor.execute('''
                SELECT trust_level, COUNT(*) as count 
                FROM devices 
                GROUP BY trust_level
            ''')
            stats['by_trust'] = {row['trust_level']: row['count'] for row in cursor.fetchall()}
            
            # Alertas pendientes
            cursor.execute('SELECT COUNT(*) as pending FROM alerts WHERE is_read = 0')
            stats['pending_alerts'] = cursor.fetchone()['pending']
            
            # Eventos recientes (última hora)
            cursor.execute('''
                SELECT COUNT(*) as recent 
                FROM network_events 
                WHERE datetime(timestamp) > datetime('now', '-1 hour')
            ''')
            stats['recent_events'] = cursor.fetchone()['recent']
            
            return stats
        except Exception as e:
            logging.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    # ==================== LIMPIEZA ====================
    
    def limpiar_eventos_antiguos(self, dias: int = 30) -> int:
        """Elimina eventos más antiguos que X días."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                DELETE FROM network_events 
                WHERE datetime(timestamp) < datetime('now', ? || ' days')
            ''', (f'-{dias}',))
            self.conn.commit()
            return cursor.rowcount
        except Exception as e:
            logging.error(f"Error limpiando eventos: {e}")
            return 0
    
    def cerrar(self):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()
            logging.info("✓ Conexión a base de datos cerrada")
    
    def __del__(self):
        """Destructor para asegurar cierre de conexión."""
        self.cerrar()
