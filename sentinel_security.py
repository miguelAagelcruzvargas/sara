"""
🛡️ SARA - Security Manager (Sentinel)
=====================================
Gestor de seguridad centralizado: Autenticación, Rate Limiting y Auditoría.
🔒 Thread-Safe | 🔑 PBKDF2-HMAC-SHA256 | 📝 Audit Logging
"""

import sqlite3
import logging
import hashlib
import secrets
import re
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from contextlib import contextmanager
from enum import Enum, auto
from dataclasses import dataclass

# --- Estructuras de Datos y Tipos ---

class Severity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"

class SecurityEventType(Enum):
    AUTH_SUCCESS = "AUTH_SUCCESS"
    AUTH_FAIL = "AUTH_FAIL"
    AUTH_LOCKED = "AUTH_LOCKED"
    PIN_CHANGE = "PIN_CHANGE"
    SYSTEM_INIT = "SYSTEM_INIT"

@dataclass
class AuthResult:
    """Objeto de transferencia de datos para resultados de autenticación."""
    success: bool
    message: str
    is_locked: bool = False
    remaining_lock_time: int = 0

@dataclass
class SecurityConfig:
    """Configuración inyectable para el sistema."""
    max_attempts: int = 3
    lockout_seconds: int = 300
    min_pin_length: int = 4
    require_complex_pin: bool = False

# --- Logger Config ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger("SentinelCore")

class SentinelSecurity:
    """
    Gestor de seguridad centralizado con arquitectura robusta.
    Maneja autenticación, autorización y auditoría.
    """

    def __init__(self, db_path: str = "security_logs/sentinel.db", config: SecurityConfig = SecurityConfig()):
        self.config = config
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()  # Thread-safety para operaciones concurrentes
        self._init_database()
        logger.info(f"🛡️ SentinelSecurity activo. DB: {self.db_path.name} | Thread-Safe: ✅")

    @contextmanager
    def _db_connection(self):
        """Context Manager robusto para transacciones atómicas (Thread-Safe)."""
        # IMPORTANTE: check_same_thread=False permite uso multihilo con lock externo
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row # Permite acceder columnas por nombre
        try:
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Database Error: {e}")
            raise RuntimeError(f"Error crítico de base de datos: {e}")
        finally:
            conn.close()

    def _init_database(self):
        """Inicialización de esquema idempotente."""
        # Protegemos la inicialización con el lock
        with self._lock:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                
                # Tabla KV para configuración interna
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS config_store (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                ''')
                
                # Tabla de auditoría
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS audit_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        event_type TEXT NOT NULL,
                        description TEXT,
                        severity TEXT NOT NULL,
                        success BOOLEAN,
                        metadata JSON
                    )
                ''')

                # PIN Default (1234) solo si no existe
                cursor.execute("SELECT 1 FROM config_store WHERE key = 'pin_hash'")
                if not cursor.fetchone():
                    self._set_pin_hash(cursor, "1234")
                    logger.warning("⚠️ Sistema inicializado con PIN por defecto (1234)")

    # --- Lógica Criptográfica Privada ---

    def _hash_pin(self, pin: str, salt: bytes = None) -> str:
        """Genera hash PBKDF2."""
        if salt is None:
            salt = secrets.token_bytes(16)
        
        # 100k iteraciones es el estándar OWASP actual
        pin_hash = hashlib.pbkdf2_hmac('sha256', pin.encode(), salt, 100000)
        return f"{salt.hex()}${pin_hash.hex()}"

    def _verify_hash(self, pin: str, stored_val: str) -> bool:
        """Verifica hash con protección contra timing attacks."""
        try:
            salt_hex, hash_hex = stored_val.split('$')
            salt = bytes.fromhex(salt_hex)
            new_hash = hashlib.pbkdf2_hmac('sha256', pin.encode(), salt, 100000)
            return secrets.compare_digest(new_hash.hex(), hash_hex)
        except ValueError:
            return False

    def _set_pin_hash(self, cursor, pin: str):
        """Guarda el PIN en la transacción actual."""
        secure_val = self._hash_pin(pin)
        cursor.execute("INSERT OR REPLACE INTO config_store (key, value) VALUES ('pin_hash', ?)", (secure_val,))

    # --- Gestión de Estado (Rate Limiting) ---

    def _get_lockout_status(self, cursor) -> Tuple[bool, int]:
        """Calcula si el sistema está bloqueado y por cuánto tiempo."""
        # Obtener intentos fallidos
        cursor.execute("SELECT value FROM config_store WHERE key = 'failed_attempts'")
        row = cursor.fetchone()
        attempts = int(row['value']) if row else 0

        # Obtener timestamp de bloqueo
        cursor.execute("SELECT value FROM config_store WHERE key = 'lock_until'")
        row = cursor.fetchone()
        lock_until_str = row['value'] if row else None

        if lock_until_str:
            lock_until = datetime.fromisoformat(lock_until_str)
            if datetime.now() < lock_until:
                return True, int((lock_until - datetime.now()).total_seconds())
            else:
                # El tiempo expiró, limpiamos el bloqueo
                self._reset_counters(cursor)
                return False, 0
        
        return False, 0

    def _handle_auth_failure(self, cursor) -> AuthResult:
        """Maneja la lógica de incremento de fallos y bloqueo."""
        cursor.execute("SELECT value FROM config_store WHERE key = 'failed_attempts'")
        row = cursor.fetchone()
        attempts = (int(row['value']) if row else 0) + 1
        
        cursor.execute("INSERT OR REPLACE INTO config_store (key, value) VALUES ('failed_attempts', ?)", (str(attempts),))
        
        if attempts >= self.config.max_attempts:
            lock_until = datetime.now() + timedelta(seconds=self.config.lockout_seconds)
            cursor.execute("INSERT OR REPLACE INTO config_store (key, value) VALUES ('lock_until', ?)", (lock_until.isoformat(),))
            self._audit(cursor, SecurityEventType.AUTH_LOCKED, f"Sistema bloqueado por {attempts} intentos", Severity.WARNING, False)
            return AuthResult(False, f"⛔ Sistema bloqueado por seguridad.", True, self.config.lockout_seconds)
            
        remaining = self.config.max_attempts - attempts
        self._audit(cursor, SecurityEventType.AUTH_FAIL, f"PIN incorrecto. Intento {attempts}/{self.config.max_attempts}", Severity.WARNING, False)
        return AuthResult(False, f"❌ PIN Incorrecto. Intentos restantes: {remaining}")

    def _reset_counters(self, cursor):
        """Reinicia los contadores de seguridad tras éxito o expiración."""
        cursor.execute("DELETE FROM config_store WHERE key IN ('failed_attempts', 'lock_until')")

    # --- Métodos Públicos (API) ---

    def authenticate(self, pin: str) -> AuthResult:
        """Punto de entrada principal para validar acceso."""
        if not pin:
            return AuthResult(False, "PIN vacío")

        with self._lock: # Lock para thread-safety en toda la operación
            with self._db_connection() as conn:
                cursor = conn.cursor()
                
                # 1. Verificar si está bloqueado
                is_locked, seconds = self._get_lockout_status(cursor)
                if is_locked:
                    self._audit(cursor, SecurityEventType.AUTH_LOCKED, "Intento de acceso durante bloqueo", Severity.WARNING, False)
                    return AuthResult(False, f"⛔ Bloqueado. Espere {seconds}s", True, seconds)

                # 2. Verificar PIN
                cursor.execute("SELECT value FROM config_store WHERE key = 'pin_hash'")
                stored_data = cursor.fetchone()
                
                if stored_data and self._verify_hash(pin, stored_data['value']):
                    self._reset_counters(cursor)
                    self._audit(cursor, SecurityEventType.AUTH_SUCCESS, "Acceso autorizado", Severity.INFO, True)
                    return AuthResult(True, "✅ Acceso concedido")
                else:
                    return self._handle_auth_failure(cursor)

    def change_pin(self, current_pin: str, new_pin: str) -> AuthResult:
        """Cambio de PIN seguro."""
        # 1. Validar autenticación actual (ya usa lock internamente)
        auth_result = self.authenticate(current_pin)
        if not auth_result.success:
            return auth_result 

        # 2. Validar reglas de negocio del nuevo PIN
        if not new_pin.isdigit():
            return AuthResult(False, "❌ El PIN debe contener solo números")
        
        if len(new_pin) < self.config.min_pin_length:
            return AuthResult(False, f"❌ El PIN debe tener al menos {self.config.min_pin_length} dígitos")

        if self.config.require_complex_pin:
             # Ejemplo simple: no permitir números repetidos como 1111
             if len(set(new_pin)) == 1:
                 return AuthResult(False, "❌ El PIN es demasiado simple (dígitos repetidos)")

        # 3. Guardar cambios
        with self._lock:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                self._set_pin_hash(cursor, new_pin)
                self._audit(cursor, SecurityEventType.PIN_CHANGE, "PIN actualizado exitosamente", Severity.CRITICAL, True)
        
        return AuthResult(True, "✅ PIN cambiado correctamente")

    def get_audit_log(self, limit: int = 50) -> List[Dict]:
        """Obtiene el historial de eventos formateado."""
        with self._lock:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT timestamp, event_type, description, severity, success 
                    FROM audit_log ORDER BY id DESC LIMIT ?
                ''', (limit,))
                return [dict(row) for row in cursor.fetchall()]

    # --- Auditoría Interna ---

    def _audit(self, cursor, event: SecurityEventType, desc: str, severity: Severity, success: bool):
        """Registra evento en la transacción actual."""
        cursor.execute('''
            INSERT INTO audit_log (event_type, description, severity, success)
            VALUES (?, ?, ?, ?)
        ''', (event.value, desc, severity.value, success))

# --- Singleton Global Access ---

_sentinel_instance = None

def obtener_sentinel_security() -> SentinelSecurity:
    """Implementación Singleton para acceso global (Thread-Safe implícita por GIL en assignación simple)."""
    global _sentinel_instance
    if _sentinel_instance is None:
        # Configuración por defecto para instancias globales
        config = SecurityConfig(max_attempts=3, lockout_seconds=60, require_complex_pin=True)
        _sentinel_instance = SentinelSecurity(config=config)
    return _sentinel_instance

# --- Ejemplo de Uso (Main) ---

if __name__ == "__main__":
    # Configuración personalizada (Diseño Flexible)
    config = SecurityConfig(max_attempts=3, lockout_seconds=60, require_complex_pin=True)
    sentinel = SentinelSecurity(config=config)

    # 1. Intento fallido
    print("\n--- Intento Fallido ---")
    res = sentinel.authenticate("0000")
    print(f"Resultado: {res.message} | Bloqueado: {res.is_locked}")

    # 2. Intento correcto (Default 1234)
    print("\n--- Intento Correcto ---")
    res = sentinel.authenticate("1234")
    print(f"Resultado: {res.message}")

    # 3. Intento cambio de PIN inseguro
    print("\n--- Cambio PIN Inseguro ---")
    res = sentinel.change_pin("1234", "1111")
    print(f"Resultado: {res.message}")
    
    # 4. Ver Logs
    print("\n--- Logs ---")
    for log in sentinel.get_audit_log(3):
        print(f"[{log['timestamp']}] {log['event_type']}: {log['description']}")