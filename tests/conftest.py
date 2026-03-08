"""
🧪 SARA - Pytest Configuration and Shared Fixtures
==================================================

Fixtures compartidos para todos los tests de SARA.
"""

import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Agregar directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def temp_dir():
    """Fixture que crea un directorio temporal y lo limpia después"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_file():
    """Fixture que crea un archivo temporal y lo limpia después"""
    fd, temp_path = tempfile.mkstemp()
    os.close(fd)
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def temp_db():
    """Fixture que crea una base de datos SQLite temporal"""
    import sqlite3
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield db_path
    # Cleanup con retry para Windows (SQLite puede mantener locks)
    import time
    import gc
    
    # Forzar garbage collection para cerrar conexiones
    gc.collect()
    
    # Intentar eliminar con retry
    for attempt in range(5):
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
            break
        except PermissionError:
            if attempt < 4:
                time.sleep(0.1)
            # En el último intento, simplemente continuar
            # El archivo se limpiará eventualmente


@pytest.fixture
def mock_ia_callback():
    """Mock para callbacks de IA (evita llamadas reales a APIs)"""
    def mock_callback(prompt, contexto_extra=""):
        return f"Mock IA response for: {prompt[:50]}..."
    return mock_callback


@pytest.fixture
def sample_text_file(temp_dir):
    """Crea un archivo de texto de ejemplo"""
    file_path = os.path.join(temp_dir, "sample.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("Este es un texto de ejemplo para testing.\n")
        f.write("Contiene múltiples líneas.\n")
        f.write("Y caracteres especiales: áéíóúñ\n")
    return file_path


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Limpia archivos de test automáticamente después de cada test"""
    yield
    # Cleanup después del test
    test_patterns = ["test_*.mp3", "test_*.txt", "test_*.db"]
    for pattern in test_patterns:
        for file in Path(".").glob(pattern):
            try:
                file.unlink()
            except:
                pass


@pytest.fixture
def disable_logging():
    """Desactiva logging durante tests para output más limpio"""
    import logging
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)
