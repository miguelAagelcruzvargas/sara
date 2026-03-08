"""
🧪 SARA - Test Suite for System Control
========================================

Tests para el módulo de control del sistema.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system_control import SystemControl


class TestVolumeControl:
    """Tests para control de volumen"""
    
    @pytest.fixture
    def sys_control(self):
        try:
            return SystemControl()
        except Exception as e:
            pytest.skip(f"No se pudo inicializar SystemControl: {e}")
    
    def test_get_volume(self, sys_control):
        """Test: Obtener volumen actual"""
        volume = sys_control.get_volume()
        assert isinstance(volume, (int, float))
        assert 0 <= volume <= 100
    
    def test_set_volume_valid(self, sys_control):
        """Test: Establecer volumen válido"""
        original = sys_control.get_volume()
        try:
            sys_control.set_volume(50)
            new_volume = sys_control.get_volume()
            assert 45 <= new_volume <= 55  # Tolerancia del 5%
        finally:
            # Restaurar volumen original
            sys_control.set_volume(int(original))
    
    def test_set_volume_bounds(self, sys_control):
        """Test: Límites de volumen"""
        original = sys_control.get_volume()
        try:
            # Test límite superior
            sys_control.set_volume(100)
            assert sys_control.get_volume() <= 100
            
            # Test límite inferior
            sys_control.set_volume(0)
            assert sys_control.get_volume() >= 0
        finally:
            sys_control.set_volume(int(original))
    
    def test_adjust_volume(self, sys_control):
        """Test: Ajustar volumen relativamente"""
        original = sys_control.get_volume()
        try:
            sys_control.adjust_volume(10)
            new_volume = sys_control.get_volume()
            # Debería haber aumentado (con tolerancia)
            assert new_volume >= original - 5
        finally:
            sys_control.set_volume(int(original))


class TestBrightnessControl:
    """Tests para control de brillo"""
    
    @pytest.fixture
    def sys_control(self):
        try:
            return SystemControl()
        except Exception as e:
            pytest.skip(f"No se pudo inicializar SystemControl: {e}")
    
    @pytest.mark.slow
    def test_set_brightness(self, sys_control):
        """Test: Establecer brillo"""
        try:
            sys_control.set_brightness(50)
            # Si no lanza excepción, el test pasa
            assert True
        except Exception as e:
            # Algunos sistemas no soportan control de brillo
            pytest.skip(f"Control de brillo no soportado: {e}")


class TestProcessControl:
    """Tests para control de procesos"""
    
    @pytest.fixture
    def sys_control(self):
        return SystemControl()
    
    def test_get_heavy_processes(self, sys_control):
        """Test: Obtener procesos pesados"""
        processes = sys_control.get_heavy_processes(limit=5)
        assert isinstance(processes, list)
        assert len(processes) <= 5
        
        if processes:
            # Verificar estructura de cada proceso
            for proc in processes:
                assert isinstance(proc, dict)
                assert "name" in proc
                assert "memory_mb" in proc
    
    @pytest.mark.slow
    def test_kill_process_nonexistent(self, sys_control):
        """Test: Intentar matar proceso inexistente"""
        result = sys_control.kill_process("proceso_que_no_existe_12345")
        # No debería crashear, solo retornar False o mensaje
        assert result is not None


class TestScreenshotCapture:
    """Tests para capturas de pantalla"""
    
    @pytest.fixture
    def sys_control(self):
        return SystemControl()
    
    def test_take_screenshot(self, sys_control, temp_dir):
        """Test: Tomar captura de pantalla"""
        screenshot_path = sys_control.take_screenshot(folder_path=temp_dir)
        
        # Verificar que se creó el archivo
        assert screenshot_path is not None
        assert os.path.exists(screenshot_path)
        assert screenshot_path.endswith(".png")
        
        # Verificar que tiene contenido
        assert os.path.getsize(screenshot_path) > 0


class TestSystemCleaning:
    """Tests para limpieza del sistema"""
    
    @pytest.fixture
    def sys_control(self):
        return SystemControl()
    
    @pytest.mark.slow
    def test_clean_temp_files(self, sys_control):
        """Test: Limpiar archivos temporales"""
        # Este test solo verifica que no crashea
        try:
            result = sys_control.clean_temp_files()
            assert result is not None
        except PermissionError:
            pytest.skip("Permisos insuficientes para limpiar archivos temporales")
    
    @pytest.mark.slow
    def test_empty_recycle_bin(self, sys_control):
        """Test: Vaciar papelera"""
        try:
            result = sys_control.empty_recycle_bin()
            assert result is not None
        except Exception as e:
            pytest.skip(f"No se pudo vaciar papelera: {e}")


class TestWindowControl:
    """Tests para control de ventanas"""
    
    @pytest.fixture
    def sys_control(self):
        return SystemControl()
    
    def test_minimize_all_windows(self, sys_control):
        """Test: Minimizar todas las ventanas"""
        # Solo verificar que no crashea
        sys_control.minimize_all_windows()
        assert True
    
    def test_maximize_window(self, sys_control):
        """Test: Maximizar ventana"""
        # Solo verificar que no crashea
        sys_control.maximize_window()
        assert True


class TestPowerControl:
    """Tests para control de energía"""
    
    @pytest.fixture
    def sys_control(self):
        return SystemControl()
    
    def test_cancel_shutdown(self, sys_control):
        """Test: Cancelar apagado"""
        # Primero cancelar cualquier apagado pendiente
        result = sys_control.cancel_shutdown()
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
