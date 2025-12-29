import os
import subprocess
import platform

# Configuración
MAX_LINES_GIT_STATUS = 20  # Límite de líneas en git status
MAX_CHARS_GIT_OUTPUT = 300  # Límite de caracteres en salida git

class DevOpsManager:
    """Manejador avanzado para tareas de desarrollo y servidores."""
    
    # Directorio de trabajo por defecto (donde se ejecuta el script al inicio)
    WORK_DIR = os.getcwd() 

    @staticmethod
    def analizar_estado_git():
        """
        Analiza el estado actual del repositorio para dar sugerencias proactivas.
        Retorna: (resumen_texto, sugerencia_accion)
        """
        if not DevOpsManager._es_repositorio_git():
            return "No es un repositorio Git.", "init"
        
        # 1. Cambios sin commitear
        c, out_status, _ = DevOpsManager._ejecutar_git(["status", "--porcelain"])
        cambios = len(out_status.strip().split('\n')) if out_status.strip() else 0
        
        # 2. Ramas y estado remoto
        c, out_branch, _ = DevOpsManager._ejecutar_git(["branch", "-vv"])
        rama_actual = "unknown"
        estado_remoto = "sincronizado"
        
        for linea in out_branch.split('\n'):
            if linea.startswith('*'):
                partes = linea.split()
                if len(partes) > 1: rama_actual = partes[1]
                if "ahead" in linea: estado_remoto = "adelante (necesita push)"
                elif "behind" in linea: estado_remoto = "atras (necesita pull)"
                break

        # Generar reporte inteligente
        reporte = f"📂 Repositorio en rama '{rama_actual}'.\n"
        sugerencia = None
        
        if cambios > 0:
            reporte += f"⚠️ Tienes {cambios} archivos modificados sin guardar."
            sugerencia = "commit"
        elif estado_remoto != "sincronizado":
            reporte += f"☁️ Tu rama está {estado_remoto}."
            sugerencia = "push" if "push" in estado_remoto else "pull"
        else:
            reporte += "✅ Todo limpio y sincronizado."
            
        return reporte, sugerencia

    @classmethod
    def set_work_dir(cls, path):
        """Cambia el directorio donde se ejecutarán los comandos git."""
        if os.path.isdir(path):
            cls.WORK_DIR = path
            return f"✅ Directorio de trabajo cambiado a:\n📂 {path}"
        return f"❌ El directorio no existe: {path}"

    @staticmethod
    def _ejecutar_git(args):
        """Ejecuta comandos git de forma segura y centralizada."""
        return DevOpsManager._ejecutar_comando_stream(["git"] + args, "Git Output")

    @staticmethod
    def _ejecutar_comando_stream(cmd_list, titulo):
        """Ejecuta un comando capturando salida en tiempo real (simulado para GUI)."""
        try:
            startupinfo = None
            if platform.system() == 'Windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
            proc = subprocess.Popen(
                cmd_list,
                cwd=DevOpsManager.WORK_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8', 
                errors='replace',
                startupinfo=startupinfo
            )
            out, err = proc.communicate()
            
            if proc.returncode != 0:
                return -1, out, err # Compatibilidad con git anterior
            return 0, out, err
        except FileNotFoundError:
            return -1, "", f"Comando no encontrado: {cmd_list[0]}"
        except Exception as e:
            return -1, "", str(e)

    @staticmethod
    def _es_repositorio_git():
        """Verifica si el directorio actual es un repo Git."""
        code, _, _ = DevOpsManager._ejecutar_git(["rev-parse", "--is-inside-work-tree"])
        return code == 0

    @staticmethod
    def git_init():
        """Inicializa un nuevo repositorio Git."""
        if DevOpsManager._es_repositorio_git():
            return "ℹ️ Ya hay un repositorio Git en esta carpeta."
        
        code, out, err = DevOpsManager._ejecutar_git(["init"])
        if code == 0:
            return f"✅ Repositorio Git inicializado exitosamente en:\n{DevOpsManager.WORK_DIR}\n💡 Ahora puedes usar 'git status', 'git add .', etc."
        return f"❌ Error al inicializar Git:\n{err}"

    @staticmethod
    def git_status():
        """Muestra el estado del repositorio."""
        if not DevOpsManager._es_repositorio_git():
            return f"❌ No estás en un repositorio Git.\n📂 Carpeta actual: {DevOpsManager.WORK_DIR}\n💡 Usa 'trabajar en [ruta]' para cambiar de carpeta."
        
        code, out, err = DevOpsManager._ejecutar_git(["status"])
        if code != 0:
            return f"❌ Error: {err}"

        # Limpiar y formatear la salida
        lineas = out.split('\n')
        salida = "📊 ESTADO DEL REPOSITORIO:\n"
        salida += "=" * 40 + "\n"
        
        count = 0
        for linea in lineas:
            if linea.strip():
                salida += linea + "\n"
                count += 1
                if count >= MAX_LINES_GIT_STATUS:
                    salida += "... (salida truncada)"
                    break
        return salida

    @staticmethod
    def git_smart_push(mensaje="Update automático"):
        """Automatiza: Add -> Commit -> Push (con manejo de upstream)."""
        if not DevOpsManager._es_repositorio_git():
            return "❌ No es un repositorio Git.\n💡 Configura la carpeta con 'trabajar en...'"

        log = "🔄 Procesando cambios...\n"

        # 1. GIT ADD
        code, _, err = DevOpsManager._ejecutar_git(["add", "."])
        if code != 0: return f"❌ Error en git add: {err}"
        
        # Verificar si hay algo que commitear
        code, _, _ = DevOpsManager._ejecutar_git(["diff", "--cached", "--quiet"])
        if code == 0:
            return "ℹ️ No hay cambios nuevos para subir."

        # 2. GIT COMMIT
        code, out, err = DevOpsManager._ejecutar_git(["commit", "-m", mensaje])
        if code != 0: return f"❌ Error en commit: {out}\n{err}"
        log += f"✅ Commit creado: '{mensaje}'\n"

        # 3. GIT PUSH
        log += "🚀 Subiendo a remoto...\n"
        code, out, err = DevOpsManager._ejecutar_git(["push"])
        
        if code == 0:
            log += "✅ Push completado exitosamente."
        else:
            # Manejo de error "no upstream"
            if "set-upstream" in err or "no upstream" in err.lower():
                # Detectar rama actual
                _, branch_name, _ = DevOpsManager._ejecutar_git(["branch", "--show-current"])
                branch_name = branch_name.strip()
                
                log += f"🔧 Configurando upstream para '{branch_name}'...\n"
                code_up, _, err_up = DevOpsManager._ejecutar_git(["push", "--set-upstream", "origin", branch_name])
                
                if code_up == 0:
                    log += f"✅ Push exitoso (Nueva rama remota creada)."
                else:
                    log += f"❌ Falló configuración upstream: {err_up}"
            
            # Manejo de conflicto (necesita pull)
            elif "fetch first" in err or "non-fast-forward" in err:
                log += "⚠️ CONFLICTO: Hay cambios en el remoto.\n💡 Ejecuta 'git pull' primero."
            else:
                log += f"❌ Error en push: {err}"

        return log

    @staticmethod
    def git_listar_ramas():
        if not DevOpsManager._es_repositorio_git(): return "❌ No es un repo Git."
        code, out, _ = DevOpsManager._ejecutar_git(["branch", "-a"])
        
        if code == 0:
            # Formatear bonito
            lines = out.split('\n')
            res = "🌿 RAMAS DISPONIBLES:\n" + "="*30 + "\n"
            for l in lines:
                if l.strip(): res += l + "\n"
            return res
        return "Error listando ramas."

    @staticmethod
    def git_cambiar_rama(nombre_rama):
        if not DevOpsManager._es_repositorio_git(): return "❌ No es un repo Git."
        
        if not nombre_rama: return "❌ Especifica el nombre de la rama."

        # Intentar switch (Git moderno) o checkout (Git antiguo)
        code, out, err = DevOpsManager._ejecutar_git(["switch", nombre_rama])
        if code != 0:
            code, out, err = DevOpsManager._ejecutar_git(["checkout", nombre_rama])
            
        if code == 0: return f"✅ Cambiado a rama '{nombre_rama}'"
        return f"❌ Error: {err}"

    @staticmethod
    def git_crear_rama(nombre_rama):
        if not DevOpsManager._es_repositorio_git(): return "❌ No es un repo Git."
        if not nombre_rama: return "❌ Especifica el nombre de la rama."

        code, _, err = DevOpsManager._ejecutar_git(["checkout", "-b", nombre_rama])
        if code == 0: return f"✅ Rama '{nombre_rama}' creada y activa."
        return f"❌ Error: {err}"

    @staticmethod
    def git_pull():
        if not DevOpsManager._es_repositorio_git(): return "❌ No es un repo Git."
        code, out, err = DevOpsManager._ejecutar_git(["pull"])
        if code == 0: return f"✅ Pull exitoso:\n{out[:MAX_CHARS_GIT_OUTPUT]}"
        return f"❌ Error en pull: {err}"

    @staticmethod
    def iniciar_tunel_serveo(puerto=8080):
        """Inicia serveo en una ventana separada con auto-aceptación de fingerprint."""
        # -o StrictHostKeyChecking=no evita el prompt de "Are you sure..."
        # -o ServerAliveInterval=60 mantiene la conexión viva
        cmd_str = f"ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=60 -R 80:localhost:{puerto} serveo.net"
        
        try:
            # Lanzar ventana
            subprocess.Popen(f"start cmd /k \"echo Iniciando Tunel SARA... && {cmd_str}\"", shell=True)
            return f"🌐 Procesando túnel en puerto {puerto}...\n(La ventana negra se abrirá y conectará automáticamente).\n\nSi ves una URL verde, ¡es un éxito! ✅"
        except Exception as e:
            return f"❌ Error al lanzar túnel: {e}"

# ====================================================================
#   REDES Y PROCESOS (SYSTEM OPS)
# ====================================================================
class SystemOps:
    @staticmethod
    def obtener_ip_local():
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return f"🏠 IP Local: {ip}"
        except:
            return "❌ No se pudo determinar la IP local."

    @staticmethod
    def obtener_ip_publica():
        try:
            import urllib.request
            ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
            return f"🌍 IP Pública: {ip}"
        except:
            return "❌ No se pudo conectar para obtener IP pública."

    @staticmethod
    def buscar_proceso_por_puerto(puerto):
        """Devuelve PID y nombre del proceso usando un puerto."""
        import psutil
        try:
            puerto = int(puerto)
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    for conn in proc.connections(kind='inet'):
                        if conn.laddr.port == puerto:
                            return proc
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    continue
            return None
        except ValueError:
            return None

    @staticmethod
    def quien_usa_puerto(puerto):
        proc = SystemOps.buscar_proceso_por_puerto(puerto)
        if proc:
            return f"🚨 El puerto {puerto} está ocupado por:\nPID: {proc.info['pid']} - {proc.info['name']}"
        return f"✅ El puerto {puerto} está libre."

    @staticmethod
    def liberar_puerto(puerto):
        proc = SystemOps.buscar_proceso_por_puerto(puerto)
        if proc:
            try:
                proc.terminate()
                return f"💀 Proceso {proc.info['name']} (PID {proc.info['pid']}) terminado. Puerto {puerto} libre."
            except Exception as e:
                return f"❌ Error matando proceso: {e}"
        return f"ℹ️ Nada escuchando en el puerto {puerto}."

    @staticmethod
    def organizar_archivos(ruta):
        """Organiza archivos sueltos en carpetas por categoría."""
        import shutil
        
        if "escritorio" in ruta.lower():
            target_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        elif "descargas" in ruta.lower():
            target_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        elif "documentos" in ruta.lower():
            target_dir = os.path.join(os.path.expanduser("~"), "Documents")
        else:
            if os.path.isdir(ruta): target_dir = ruta
            else: return f"❌ Carpeta no encontrada: {ruta}"
            
        # Categorías
        extensiones = {
            "Imágenes": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
            "Documentos": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".md"],
            "Instaladores": [".exe", ".msi", ".dmg", ".deb", ".iso", ".zip", ".rar"],
            "Código": [".py", ".js", ".html", ".css", ".java", ".cpp", ".json"],
            "Audio_Video": [".mp3", ".wav", ".mp4", ".mkv", ".mov"]
        }
        
        movidos = 0
        try:
            for archivo in os.listdir(target_dir):
                ruta_archivo = os.path.join(target_dir, archivo)
                
                # Ignorar carpetas y enlaces (solo archivos)
                if not os.path.isfile(ruta_archivo) or archivo.startswith("."):
                    continue
                    
                nombre, ext = os.path.splitext(archivo)
                ext = ext.lower()
                
                carpeta_destino = None
                for categoria, exts in extensiones.items():
                    if ext in exts:
                        carpeta_destino = categoria
                        break
                
                if carpeta_destino:
                    # Crear carpeta si no existe
                    path_destino = os.path.join(target_dir, carpeta_destino)
                    if not os.path.exists(path_destino):
                        os.makedirs(path_destino)
                    
                    # Manejo de colisiones (Renombrar si existe)
                    path_final = os.path.join(path_destino, archivo)
                    contador = 1
                    nombre_base, extension = os.path.splitext(archivo)
                    
                    while os.path.exists(path_final):
                        nuevo_nombre = f"{nombre_base}_{contador}{extension}"
                        path_final = os.path.join(path_destino, nuevo_nombre)
                        contador += 1
                    
                    # Mover archivo (Cortar y Pegar)
                    try:
                        shutil.move(ruta_archivo, path_final)
                        movidos += 1
                    except: pass
                    
            if movidos > 0:
                return f"🧹 Limpieza completada. Organicé {movidos} archivos en {target_dir}."
            return "✅ El escritorio ya está ordenado."
            
        except Exception as e:
            return f"❌ Error organizando: {e}"

# ====================================================================
#   AUTOMATIZACIÓN DE BUILDS (BUILD MANAGER)
# ====================================================================
class BuildManager:
    @staticmethod
    def detectar_proyecto():
        cwd = DevOpsManager.WORK_DIR
        if os.path.exists(os.path.join(cwd, "package.json")):
            return "node"
        elif os.path.exists(os.path.join(cwd, "requirements.txt")):
            return "python"
        elif os.path.exists(os.path.join(cwd, "go.mod")):
            return "go"
        elif os.path.exists(os.path.join(cwd, "pom.xml")):
            return "java"
        return None

    @staticmethod
    def instalar_dependencias():
        tipo = BuildManager.detectar_proyecto()
        cwd = DevOpsManager.WORK_DIR
        
        cmds = {
            "node": ["npm", "install"],
            "python": ["pip", "install", "-r", "requirements.txt"],
            "go": ["go", "mod", "download"],
            "java": ["mvn", "install"]
        }
        
        if tipo in cmds:
            return DevOpsManager._ejecutar_comando_stream(cmds[tipo], f"Instalando deps ({tipo})")
        return "❌ No detecto un tipo de proyecto conocido (Node, Python, Go, Java)."

    @staticmethod
    def construir_proyecto():
        tipo = BuildManager.detectar_proyecto()
        
        cmds = {
            "node": ["npm", "run", "build"],
            "python": ["python", "-m", "py_compile", "."], # Build simple
            "go": ["go", "build", "."],
            "java": ["mvn", "package"]
        }
        
        if tipo in cmds:
            return DevOpsManager._ejecutar_comando_stream(cmds[tipo], f"Construyendo ({tipo})")
        return "❌ No detecto un tipo de proyecto soportado para build."
