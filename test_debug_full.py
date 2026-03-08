
import sys
import os
import logging
import time

logging.basicConfig(level=logging.INFO)

print("--- DIAGNÓSTICO FUNCIONAL SARA ---")

# 1. TEST SYSTEM CONTROL
print("\n1. Probando SystemControl (Hardware)...")
try:
    from system_control import SystemControl
    sys_ctrl = SystemControl()
    
    if sys_ctrl.volume:
        vol = sys_ctrl.get_volume()
        print(f"✅ Volumen actual leído: {vol}%")
        
        # Intentar cambiar volumen (solo +/- 1 para no asustar)
        print("   Intentando subir volumen +1%...")
        res = sys_ctrl.adjust_volume(1)
        print(f"   Resultado: {res}")
    else:
        print("❌ SystemControl.volume es NONE (Fallo en pycaw/hardware)")

except Exception as e:
    print(f"❌ Error crítico SystemControl: {e}")

# 2. TEST VOZ
print("\n2. Probando Motor de Voz (Edge-TTS + Pygame)...")
try:
    from voice import NeuralVoiceEngine
    import pygame
    
    voz = NeuralVoiceEngine()
    print("✅ Motor inicializado.")
    
    texto = "Prueba de sistema de audio iniciada."
    print(f"   Hablando: '{texto}'")
    voz.hablar(texto)
    
    # Esperar a que termine
    print("   Esperando audio...")
    timeout = 0
    while voz.esta_hablando() and timeout < 10:
        time.sleep(0.5)
        timeout += 0.5
        print(".", end="", flush=True)
    
    if timeout >= 10:
        print("\n❌ Timeout esperando audio (No sonó o se colgó).")
    else:
        print("\n✅ Audio finalizado.")
        
    voz.detener()

except Exception as e:
    print(f"❌ Error crítico Voz: {e}")
    import traceback
    traceback.print_exc()

print("\n--- FIN DIAGNÓSTICO ---")
