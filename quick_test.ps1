# 🧪 SARA - Quick Test Script
# ===========================
# Script rápido para ejecutar tests específicos

# Ejecutar todos los tests
Write-Host "🧪 Ejecutando todos los tests..." -ForegroundColor Cyan
python run_tests.py

# Descomentar para ejecutar tests específicos:

# # Solo tests de intent classifier
# python run_tests.py tests/test_intent_classifier.py

# # Solo tests de voice
# python run_tests.py tests/test_voice.py

# # Solo tests de config
# python run_tests.py tests/test_config.py

# # Test específico
# python run_tests.py -k test_volumen_subir

# # Con coverage (requiere pytest-cov)
# python -m pytest tests/ --cov=. --cov-report=html
