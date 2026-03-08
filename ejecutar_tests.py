#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧪 SARA - Script de Ejecución de Tests Unitarios
================================================

Script completo para ejecutar todos los tests unitarios de SARA
y generar un reporte detallado.

Uso:
    python ejecutar_tests.py
    python ejecutar_tests.py --verbose
    python ejecutar_tests.py --quick (solo tests rápidos)
"""

import subprocess
import sys
import os
from pathlib import Path
import time
from datetime import datetime

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Imprime un encabezado con estilo"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    """Imprime texto de éxito"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    """Imprime texto de error"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_warning(text):
    """Imprime texto de advertencia"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_info(text):
    """Imprime texto informativo"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def check_pytest():
    """Verifica si pytest está instalado"""
    try:
        import pytest
        return True
    except ImportError:
        return False

def install_pytest():
    """Instala pytest si no está disponible"""
    print_warning("pytest no está instalado")
    print_info("Instalando pytest...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest"], 
                      check=True, capture_output=True)
        print_success("pytest instalado correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Error instalando pytest: {e}")
        return False

def run_tests(verbose=False, quick=False):
    """Ejecuta los tests con pytest"""
    
    # Verificar pytest
    if not check_pytest():
        if not install_pytest():
            return False
    
    # Preparar comando
    cmd = [sys.executable, "-m", "pytest", "tests/"]
    
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    if quick:
        cmd.extend(["-m", "not slow"])
    
    # Agregar opciones adicionales
    cmd.extend([
        "--tb=short",           # Traceback corto
        "--color=yes",          # Colores
        "-ra",                  # Resumen de todos los tests
        "--durations=10",       # Top 10 tests más lentos
    ])
    
    print_info(f"Ejecutando: {' '.join(cmd)}")
    print()
    
    # Ejecutar tests
    start_time = time.time()
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    elapsed_time = time.time() - start_time
    
    print()
    print_info(f"Tiempo total: {elapsed_time:.2f} segundos")
    
    return result.returncode == 0

def generate_report():
    """Genera un reporte HTML de los tests"""
    print_info("Generando reporte HTML...")
    
    cmd = [
        sys.executable, "-m", "pytest", "tests/",
        "--html=test_report.html",
        "--self-contained-html",
        "-v"
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, cwd=Path(__file__).parent)
        print_success("Reporte generado: test_report.html")
        return True
    except subprocess.CalledProcessError:
        print_warning("No se pudo generar el reporte HTML (requiere pytest-html)")
        return False

def run_specific_test(test_name):
    """Ejecuta un test específico"""
    print_info(f"Ejecutando test: {test_name}")
    
    cmd = [
        sys.executable, "-m", "pytest",
        f"tests/{test_name}",
        "-v", "--tb=short"
    ]
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode == 0

def main():
    """Función principal"""
    print_header("🧪 SARA - Test Suite Runner")
    
    # Parsear argumentos
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    quick = "--quick" in sys.argv or "-q" in sys.argv
    html = "--html" in sys.argv
    
    # Verificar si se especificó un test específico
    specific_test = None
    for arg in sys.argv[1:]:
        if arg.startswith("test_"):
            specific_test = arg
            break
    
    # Información del sistema
    print_info(f"Python: {sys.version.split()[0]}")
    print_info(f"Directorio: {Path.cwd()}")
    print_info(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Ejecutar tests
    if specific_test:
        success = run_specific_test(specific_test)
    else:
        success = run_tests(verbose=verbose, quick=quick)
    
    # Generar reporte HTML si se solicitó
    if html and not specific_test:
        generate_report()
    
    # Resultado final
    print()
    print_header("📊 Resultado Final")
    
    if success:
        print_success("TODOS LOS TESTS PASARON ✨")
        return 0
    else:
        print_error("ALGUNOS TESTS FALLARON")
        print_info("Revisa los detalles arriba para más información")
        return 1

if __name__ == "__main__":
    sys.exit(main())
