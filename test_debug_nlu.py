
import sys
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TEST_NLU")

print("--- INICIANDO DIAGNÓSTICO SARA NLU ---")

try:
    print("1. Probando imports de intent_classifier...")
    from intent_classifier import HybridIntentClassifier
    print("✅ Import exitoso.")
except ImportError as e:
    print(f"❌ Error importando intent_classifier: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error inesperado importando: {e}")
    sys.exit(1)

try:
    print("2. Inicializando HybridIntentClassifier...")
    classifier = HybridIntentClassifier()
    print("✅ Inicialización exitosa.")
except Exception as e:
    print(f"❌ Error inicializando classifier: {e}")
    import traceback
    traceback.print_exc()
    # No salimos, queremos probar system control tambien

try:
    print("3. Probando clasificación (Pattern Match - Layer 1)...")
    intent, params, source = classifier.clasificar("zara sube el volumen")
    print(f"   Cmd: 'zara sube el volumen' -> Intent: {intent}, Source: {source}")
    
    if intent == "VOLUMEN_SUBIR":
        print("✅ Pattern Match OK.")
    else:
        print(f"❌ Falló Pattern Match. Esperaba VOLUMEN_SUBIR, obtuvo {intent}")

    print("4. Probando clasificación (ML - Layer 2)...")
    intent, params, source = classifier.clasificar("hay mucho ruido aqui")
    print(f"   Cmd: 'hay mucho ruido aqui' -> Intent: {intent}, Source: {source}")
    if source == 'ml':
        print("✅ ML Layer OK.")
    else:
        print(f"⚠️ ML Layer no se activó (Source: {source}).")

except Exception as e:
    print(f"❌ Error durante pruebas de clasificación: {e}")

print("\n--- DIAGNÓSTICO SYSTEM CONTROL ---")
try:
    from system_control import SystemControl
    sys_ctrl = SystemControl()
    print("✅ SystemControl inicializado.")
except Exception as e:
    print(f"❌ Error inicializando SystemControl: {e}")
    print("Posible falta de dependencia (pycaw, comtypes, etc)")

print("\n--- FIN DIAGNÓSTICO ---")
