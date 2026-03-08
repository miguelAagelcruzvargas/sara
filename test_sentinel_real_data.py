"""
Script de prueba para verificar el terminal de datos reales del Modo Centinela
"""
import customtkinter as ctk
import sys
import os

# Agregar el directorio actual al path para importar sentinel_ui
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sentinel_ui import SentinelProGUI

def on_unlock(success, message):
    """Callback cuando se desbloquea."""
    print(f"Desbloqueo: {success} - {message}")
    if success:
        app.quit()

if __name__ == "__main__":
    # Crear ventana principal
    app = ctk.CTk()
    app.geometry("1200x700")
    ctk.set_appearance_mode("Dark")
    
    print("🛡️ Iniciando Modo Centinela con datos reales...")
    print("📊 El terminal mostrará:")
    print("  • Latencia WiFi (ping)")
    print("  • Uso de CPU y RAM")
    print("  • Clima actual")
    print("  • Hora del sistema")
    print("  • Estado de red")
    print("\n🔑 PIN por defecto: 1234")
    print("⚠️  Presiona ESC o cierra la ventana para salir (solo en modo prueba)\n")
    
    # Activar Sentinel
    sentinel = SentinelProGUI(app, on_unlock)
    sentinel.activate()
    
    # Permitir cerrar con ESC en modo prueba
    app.bind("<Escape>", lambda e: app.quit())
    
    app.mainloop()
