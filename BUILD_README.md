# 🚀 Constructor de Ejecutable SARA

## Características

El nuevo `build_executable.py` es una **GUI interactiva** que te permite generar ejecutables profesionales con PyInstaller.

### ✨ Funcionalidades

#### 🎨 Gestión de Icono
- **Selector de archivo**: Elige cualquier archivo `.ico`
- **Generador automático**: Crea un icono con la letra "S" en verde
- **Vista previa**: Muestra el icono seleccionado

#### 📦 Tipos de Build
- **Un solo archivo** (Recomendado): `SARA.exe` standalone
- **Carpeta**: Más rápido de generar, útil para testing

#### ⚙️ Opciones Avanzadas
- **Consola**: Mostrar/ocultar ventana de consola
- **Compresión UPX**: Reduce tamaño ~40% (requiere UPX instalado)
- **Optimización**: Niveles 0, 1, 2 (2 = máximo rendimiento)

#### 📋 Vista Previa
- Ver todos los argumentos de PyInstaller antes de generar
- Información del sistema y configuración actual

---

## 🎯 Cómo Usar

### 1. Ejecutar el Constructor

```bash
python build_executable.py
```

### 2. Configurar Opciones

1. **Seleccionar Icono** (opcional):
   - Click en "📁 Seleccionar .ico" para elegir un archivo
   - O click en "🎨 Generar Icono" para crear uno automático

2. **Elegir Tipo de Build**:
   - ✅ "Un solo archivo" - Recomendado para distribución
   - "Carpeta" - Más rápido, para testing

3. **Opciones Avanzadas**:
   - Consola: Desmarcado (GUI sin consola)
   - UPX: Marcado (comprime el ejecutable)
   - Optimización: 2 (máximo rendimiento)

### 3. Generar Ejecutable

Click en **"🚀 GENERAR EJECUTABLE"**

El proceso toma 2-5 minutos dependiendo de:
- Tipo de build
- Compresión UPX
- Velocidad del PC

---

## 📁 Resultado

### Un Solo Archivo
```
dist/
└── SARA.exe  (30-50 MB)
```

### Carpeta
```
dist/
└── SARA/
    ├── SARA.exe
    ├── python310.dll
    ├── _internal/
    └── ...
```

---

## 🎨 Generar Icono Personalizado

### Opción 1: Generador Automático
1. Click en "🎨 Generar Icono"
2. Se crea `sara_icon.ico` con la letra "S"
3. Automáticamente se selecciona

### Opción 2: Icono Personalizado
1. Crea tu icono en formato `.ico`
2. Usa herramientas online:
   - https://www.icoconverter.com/
   - https://convertio.co/es/png-ico/
3. Click en "📁 Seleccionar .ico"

### Opción 3: Desde Imagen
```bash
# Instalar Pillow
pip install pillow

# Convertir PNG a ICO
from PIL import Image
img = Image.open('mi_imagen.png')
img.save('sara_icon.ico', format='ICO', sizes=[(256,256), (128,128), (64,64), (32,32), (16,16)])
```

---

## ⚙️ Configuraciones Recomendadas

### Para Distribución
```
✅ Un solo archivo
❌ Mostrar consola
✅ Compresión UPX
✅ Optimización: 2
```
**Resultado**: Ejecutable compacto y profesional

### Para Testing
```
❌ Un solo archivo (usar Carpeta)
✅ Mostrar consola
❌ Compresión UPX
✅ Optimización: 2
```
**Resultado**: Build rápido con debugging

### Para Debugging
```
❌ Un solo archivo
✅ Mostrar consola
❌ Compresión UPX
❌ Optimización: 0
```
**Resultado**: Errores visibles en consola

---

## 🔧 Dependencias

### Requeridas
```bash
pip install pyinstaller
```

### Opcionales
```bash
# Para generar iconos
pip install pillow

# Para compresión UPX (Windows)
# Descargar de: https://github.com/upx/upx/releases
# Agregar a PATH
```

---

## 📊 Comparación de Tamaños

| Configuración | Tamaño Aproximado |
|---------------|-------------------|
| Sin UPX | 70-90 MB |
| Con UPX | 30-50 MB |
| Carpeta | 80-100 MB total |

---

## 🐛 Troubleshooting

### "PyInstaller no encontrado"
```bash
pip install pyinstaller
```

### "No se pudo generar el icono"
```bash
pip install pillow
```

### "UPX no funciona"
1. Descarga UPX: https://github.com/upx/upx/releases
2. Extrae en `C:\upx`
3. Agrega a PATH:
   ```
   Sistema → Variables de entorno → Path → Nuevo → C:\upx
   ```

### "El ejecutable no inicia"
1. Genera con "Mostrar consola" activado
2. Ejecuta y lee el error en la consola
3. Verifica que todas las dependencias estén en `requirements.txt`

### "Falta un módulo"
Edita `build_executable.py` y agrega a `hidden_imports`:
```python
hidden_imports = [
    'pystray', 'PIL', 'pygame', 'edge_tts',
    'google.generativeai', 'groq', 'openai', 'dotenv',
    'tu_modulo_faltante'  # ← Agregar aquí
]
```

---

## 📝 Notas Importantes

### Primera Ejecución del .exe
- Mostrará la GUI de `first_run_setup.py`
- El usuario configura sus API keys
- Se guardan en `%APPDATA%\SARA\.env`

### Antivirus
Algunos antivirus marcan ejecutables de PyInstaller como falsos positivos:
- **Solución**: Firma digital (requiere certificado)
- **Alternativa**: Agrega excepción en el antivirus

### Tamaño del Ejecutable
Es normal que sea grande (30-90 MB) porque incluye:
- Python completo
- Todas las librerías
- CustomTkinter
- Pygame
- Edge TTS
- etc.

---

## 🎯 Próximos Pasos

Después de generar el ejecutable:

1. **Probar en tu PC**:
   ```
   dist\SARA.exe
   ```

2. **Probar en PC limpia** (sin Python):
   - Copia `SARA.exe` a otra PC
   - Ejecuta y verifica que funcione

3. **Crear Instalador** (opcional):
   - Usa Inno Setup
   - Crea instalador profesional con desinstalador

4. **Distribuir**:
   - Sube a GitHub Releases
   - Comparte con usuarios

---

*Constructor mejorado - Versión 3.0.3*
