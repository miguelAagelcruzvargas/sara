# 🛡️ NetworkGuardian - Guía de Integración con SARA

## Instalación

### 1. Instalar Dependencias
```bash
pip install plyer
```

### 2. Verificar Archivos Creados
Los siguientes archivos deben estar en el directorio del proyecto:
- `network_guardian.py` - Módulo principal
- `network_guardian_db.py` - Base de datos
- `network_guardian_alerts.py` - Sistema de alertas
- `network_guardian_monitor.py` - Monitor en tiempo real
- `network_guardian_traffic.py` - Análisis de tráfico
- `network_guardian_commands.py` - Comandos de voz
- `monitor.py` (mejorado) - Monitor de sistema

---

## Integración con brain.py

### Paso 1: Importar NetworkGuardian

Agregar al inicio de `brain.py`:

```python
from network_guardian import obtener_guardian
from network_guardian_commands import procesar_comando_guardian, EJEMPLOS_USO
```

### Paso 2: Inicializar en SaraBrain.__init__()

Agregar en el método `__init__` de la clase `SaraBrain`:

```python
def __init__(self):
    # ... código existente ...
    
    # Inicializar NetworkGuardian con IA y auto-inicio
    try:
        self.guardian = obtener_guardian(
            voice_callback=self.voz.hablar,
            ia_callback=self.consultar_ia,  # ← Integración con IA
            auto_start=True  # ← NUEVO: Inicia vigilancia automáticamente
        )
        logging.info("✅ NetworkGuardian inicializado con IA y vigilancia activa")
    except Exception as e:
        logging.error(f"⚠️ Error inicializando NetworkGuardian: {e}")
        self.guardian = None
```

**Nota**: Con `auto_start=True`, NetworkGuardian comienza a monitorear la red automáticamente al iniciar SARA. No necesitas decir "activar vigilancia".

### Paso 3: Agregar Comandos en procesar()

Agregar en el método `procesar()` de `SaraBrain`, **ANTES** del bloque de IA general:

```python
def procesar(self, comando):
    cmd = comando.lower()
    
    # ... comandos existentes ...
    
    # --- NETWORKGUARDIAN ---
    if self.guardian and any(x in cmd for x in [
        "vigilancia", "dispositivos", "red", "fortaleza", 
        "alertas", "tráfico", "consumidores", "conexiones",
        "confía", "confiar", "sospechoso", "renombrar dispositivo"
    ]):
        resultado = procesar_comando_guardian(cmd, self.guardian)
        if resultado:
            return resultado
    
    # Ayuda de NetworkGuardian
    if "comandos de red" in cmd or "ayuda de red" in cmd:
        return EJEMPLOS_USO, "guardian"
    
    # ... resto del código ...
```

### Paso 4: Cerrar NetworkGuardian al salir

Agregar método de limpieza en `SaraBrain`:

```python
def cerrar(self):
    """Cierra recursos de SARA."""
    if self.guardian:
        self.guardian.cerrar()
```

Y llamarlo desde `sara.py` al cerrar la aplicación:

```python
def on_closing(self):
    self.brain.cerrar()  # Agregar esta línea
    self.withdraw()
    # ... resto del código ...
```

---

## Comandos de Voz Disponibles

### 📊 Vigilancia
- `"SARA, activar vigilancia"` - Inicia monitoreo 24/7
- `"SARA, estado de vigilancia"` - Muestra estado actual
- `"SARA, pausar vigilancia"` - Pausa temporalmente
- `"SARA, reanudar vigilancia"` - Reanuda monitoreo

### 📱 Dispositivos
- `"SARA, quién está en mi red"` - Lista dispositivos activos
- `"SARA, listar dispositivos"` - Lista todos los dispositivos
- `"SARA, confía en 192.168.1.105"` - Marca como confiable
- `"SARA, renombrar dispositivo 192.168.1.105 a Laptop de Juan"`

### 🔒 Seguridad
- `"SARA, modo fortaleza"` - Bloquea dispositivos no confiables
- `"SARA, alertas pendientes"` - Muestra alertas no leídas
- `"SARA, marcar sospechoso 192.168.1.200"` - Marca como sospechoso

### 📊 Análisis
- `"SARA, analizar tráfico"` - Análisis completo de red
- `"SARA, top consumidores"` - Procesos que más usan red
- `"SARA, conexiones activas"` - Lista conexiones actuales

### 📄 Reportes
- `"SARA, reporte de red"` - Reporte completo del estado

---

## Uso Programático (sin voz)

```python
# Obtener instancia
from network_guardian import obtener_guardian
guardian = obtener_guardian()

# Iniciar vigilancia
guardian.iniciar_vigilancia()

# Listar dispositivos
dispositivos = guardian.listar_dispositivos()

# Analizar tráfico
trafico = guardian.analizar_trafico()

# Obtener estadísticas
stats = guardian.obtener_estadisticas()

# Cerrar al finalizar
guardian.cerrar()
```

---

## Base de Datos

NetworkGuardian crea automáticamente `network_guardian.db` (SQLite) con:
- Historial de dispositivos
- Eventos de red
- Alertas de seguridad
- Estadísticas de tráfico
- Reglas de firewall

**Ubicación**: Mismo directorio que `sara.py`

---

## Configuración Avanzada

### Cambiar Intervalo de Escaneo
```python
guardian.configurar_intervalo_escaneo(30)  # 30 segundos
```

### Configurar Alertas de Voz
```python
# Solo alertas críticas
guardian.configurar_umbral_voz('critical')

# Todas las alertas
guardian.configurar_umbral_voz('info')

# Deshabilitar voz
guardian.habilitar_alertas_voz(False)
```

### Limpiar Datos Antiguos
```python
# Eliminar eventos de más de 30 días
guardian.limpiar_datos_antiguos(dias=30)
```

---

## Permisos de Administrador

**IMPORTANTE**: Algunas funciones requieren permisos de administrador:
- Bloqueo de IPs en firewall
- Modo fortaleza
- Gestión de reglas de firewall

**Solución**: Ejecutar SARA como administrador (clic derecho → "Ejecutar como administrador")

---

## Troubleshooting

### Error: "plyer no disponible"
```bash
pip install plyer
```

### Error: "No se puede conectar a la base de datos"
- Verificar permisos de escritura en el directorio
- Cerrar otras instancias de SARA

### Alertas de voz no funcionan
- Verificar que `voice_callback` esté configurado
- Comprobar que `self.voz.hablar` funcione correctamente

### Escaneo de red lento
- Reducir intervalo: `guardian.configurar_intervalo_escaneo(120)`
- Verificar conexión de red

---

## Próximas Mejoras (Roadmap)

- [ ] Dashboard visual en pestaña de SARA
- [ ] Exportación de reportes a PDF/HTML
- [ ] Detección avanzada de port scanning
- [ ] Integración con Wake-on-LAN
- [ ] Gráficos de uso histórico
- [ ] API REST para control remoto
- [ ] Modo "Aprendizaje" para detectar patrones

---

## Soporte

Para problemas o sugerencias:
1. Revisar logs en consola
2. Verificar archivo `network_guardian.db`
3. Comprobar permisos de administrador
4. Revisar este archivo de integración

---

**¡NetworkGuardian está listo para proteger tu red! 🛡️**
