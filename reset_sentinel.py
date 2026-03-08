
import sqlite3
import hashlib
import secrets
import os
from pathlib import Path
from sentinel_security import obtener_sentinel_security

# Ruta correcta
DB_PATH = Path("security_logs/sentinel.db")

print(f"🔧 Mantenimiento de Sentinel en: {DB_PATH.absolute()}")

def hash_pin(pin):
    salt = secrets.token_bytes(16)
    pin_hash = hashlib.pbkdf2_hmac('sha256', pin.encode(), salt, 100000)
    return f"{salt.hex()}${pin_hash.hex()}"

try:
    # 1. Resetear Estado (Desbloquear)
    sentinel = obtener_sentinel_security()
    
    # Usamos acceso directo a DB para limpieza profunda
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Limpiar bloqueos
        cursor.execute("DELETE FROM config_store WHERE key IN ('failed_attempts', 'lock_until')")
        print("✅ Contadores de bloqueo reiniciados.")
        
        # Resetear PIN a 1234
        new_hash = hash_pin("1234")
        cursor.execute("INSERT OR REPLACE INTO config_store (key, value) VALUES ('pin_hash', ?)", (new_hash,))
        print("✅ PIN restablecido a: 1234")
        
        conn.commit()

    # 2. Verificar
    print("\n--- Verificando Acceso ---")
    res = sentinel.authenticate("1234")
    if res.success:
        print(f"🎉 ÉXITO TOTAL: {res.message}")
    else:
        print(f"❌ FALLO VERIFICACIÓN: {res.message}")

except Exception as e:
    print(f"❌ Error durante mantenimiento: {e}")
    import traceback
    traceback.print_exc()
