"""
🧪 SARA - Test Runner Script
============================

Script principal para ejecutar todos los tests de SARA.
Usa pytest para ejecutar los tests y generar reportes.

Uso:
    python run_tests.py              # Ejecutar todos los tests
    python run_tests.py -v           # Modo verbose
    python run_tests.py -k test_name # Ejecutar test específico
"""

import subprocess
import sys
import os

def main():
    """Ejecuta todos los tests de SARA"""
    
    print("=" * 60)
    print("🧪 SARA - Test Suite Runner")
    print("=" * 60)
    print()
    
    # Verificar que pytest está instalado
    try:
        import pytest
    except ImportError:
        print("❌ pytest no está instalado.")
        print("📦 Instalando pytest...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest"])
        import pytest
    
    # Directorio de tests
    tests_dir = os.path.join(os.path.dirname(__file__), "tests")
    
    # Argumentos para pytest
    pytest_args = [
        tests_dir,
        "-v",  # Verbose
        "--tb=short",  # Traceback corto
        "--color=yes",  # Colores
        "-ra",  # Resumen de todos los tests
    ]
    
    # Agregar argumentos adicionales del usuario
    if len(sys.argv) > 1:
        pytest_args.extend(sys.argv[1:])
    
    print(f"📂 Ejecutando tests en: {tests_dir}")
    print(f"🔧 Argumentos: {' '.join(pytest_args)}")
    print()
    
    # Ejecutar pytest
    exit_code = pytest.main(pytest_args)
    
    print()
    print("=" * 60)
    if exit_code == 0:
        print("✅ Todos los tests pasaron exitosamente!")
    else:
        print(f"❌ Algunos tests fallaron (código de salida: {exit_code})")
    print("=" * 60)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
