"""
🎯 SARA - Comprehensive Intent Training Examples (BALANCED & ROBUST)
===================================================================
Dataset original RESPETADO y AUMENTADO.
- Se mantuvieron todas las intenciones originales.
- Se agregaron ejemplos a las categorías pequeñas (Git, Network, Health) para evitar sesgos.
- Se agregaron errores fonéticos (ASR noise).
"""

INTENT_EXAMPLES_FULL = {
    # ========== COMANDOS BÁSICOS ==========
    
    "MEMORIZAR": [
        "memoriza que la clave es 777", "guarda esto: dato importante",
        "recuerda que mañana tengo cita", "anota el código ABC123",
        "no olvides que el wifi es password123", "apunta que debo llamar a Juan",
        "registra que el proyecto se entrega el viernes", "toma nota de que María llamó",
        "anota mi número de cuenta 12345", "guarda mi dirección calle 123",
        # Modismos y Errores
        "apúntale que tengo junta a las 3", "no se te olvide que debo pagar la luz",
        "acuérdate que hoy es cumpleaños de mi mamá", "anótale que necesito comprar leche",
        "memoriza qué la clave es 777", "guarda está información",
        "graba que el password es 123", "almacena este dato",
        "haz una nota mental de esto", "que no se te pase esto",
    ],
    
    "VOLUMEN_SUBIR": [
        "sube el volumen", "súbele volumen", "más alto", "aumenta el sonido",
        "volumen arriba", "ponle más recio", "échale más volumen", "métele más",
        "dale más duro", "ponlo más fuerte", "no te escucho sube",
        "volumen al máximo", "ponlo al 100", "aumenta audio", "más duro",
        "súbele al audio", "aumenta el audio", "ponle más volumen",
        "rompe las bocinas", "que suene fuerte", "súbele todo",
    ],
    
    "VOLUMEN_BAJAR": [
        "baja el volumen", "bájale volumen", "más bajo", "disminuye el sonido",
        "volumen abajo", "bajar volumen", "baja volumen", "bájale",
        "ponle más bajito", "échale menos volumen", "quítale volumen",
        "bájale tantito", "bajale volumen", "está muy alto baja",
        "volumen al mínimo", "ponlo bajito", "disminuye audio",
        "menos fuerte", "más suave", "me dejas sordo", "bájale dos rayitas",
    ],
    
    "SILENCIO": [
        "silencio", "mute", "cállate", "silencia", "mutea",
        "quita el sonido", "sin sonido", "apaga el audio",
        "quita audio", "calla", "shh", "silencio total",
        "mutear", "pon mute", "desactivar audio", "modo silencio",
    ],
    
    "ABRIR_APP": [
        "abre chrome", "abrir chrome", "abre google chrome", "abre firefox", "abre edge",
        "abre visual studio code", "abrir vscode", "abre vs code",
        "abre notepad", "abre bloc de notas", "abre word", "abre excel",
        "abre discord", "abrir discord", "abre whatsapp", "abre telegram", "abre slack",
        "abre spotify", "abrir spotify", "abre vlc",
        "lanza chrome", "ejecuta notepad", "inicia discord", "arranca spotify",
        # Errores fonéticos
        "habre word", "ejecutar exel", "lanzar pwerpoint", "iniciar crhom",
    ],
    
    "BUSCAR_WEB": [
        "busca en google inteligencia artificial", "busca python", "busca recetas de pasta",
        "busca noticias de tecnología", "busca cómo hacer pan",
        "investiga sobre machine learning", "investiga sobre python",
        "googlea recetas de pasta", "googlea noticias", "googlea python tutorial",
        "qué es machine learning", "qué es python", "cómo funciona la IA",
        "cuál es la capital de Francia", "búscame información de tensorflow",
        "búscame tutoriales de python", "búscame recetas mexicanas",
        "échame una búsqueda de python", "investígame sobre IA",
        "goglea precio del dolar", "búscalo en internet",
    ],
    
    "LEER_DOCUMENTO": [
        "lee este archivo", "lee este documento", "qué dice esta página",
        "que dice esta página", "lee esta web", "que dice este pdf",
        "lee este pdf", "abre este documento", "lee el archivo",
        "qué dice el documento", "lee la página", "muéstrame este archivo",
        "dime qué dice", "lee esto", "qué contiene este archivo",
        "analiza el texto en pantalla", "léeme el contenido",
    ],
    
    "REPRODUCIR_MEDIA": [
        "pon música", "pon rock", "pon lofi", "pon una canción", "pon reggaeton",
        "reproduce rock", "reproduce en youtube", "reproduce música", "reproduce lofi",
        "ponle música", "ponle rock", "ponle lofi", "pon música relajante",
        "reproduce música para estudiar", "pon algo de rock", "ponme música",
        "échale música", "métele rock", "dale play a lofi", "ponte algo chido",
    ],
    
    "ALARMA": [
        "alarma en 5 minutos", "alarma en 10 minutos", "alarma en 30 minutos",
        "pon alarma en 5 minutos", "pon una alarma en 10 minutos",
        "recuérdame en 5 minutos", "recuérdame en 10 minutos", "recuérdame en media hora",
        "pon un timer de 5 minutos", "timer de 10 minutos", "temporizador de 30 minutos",
        "avísame en 5 minutos", "avísame en una hora", "avísame en 10",
        "programa alarma 5 minutos", "configura timer 10 minutos",
    ],
    
    "CLIMA": [
        "qué clima hace", "que clima hace", "cómo está el clima", "como está el clima",
        "temperatura actual", "cuál es la temperatura", "va a llover hoy",
        "qué tiempo hace", "cómo está el tiempo", "clima de hoy",
        "pronóstico del tiempo", "hace frío", "hace calor", "temperatura",
        "clima de mañana", "va a llover mañana", "pronóstico para mañana",
        "cómo estará mañana", "clima para esta semana", "pronóstico semanal",
    ],
    
    "HORA_FECHA": [
        "qué hora es", "que hora es", "hora actual", "dime la hora",
        "cuál es la hora", "qué horas son", "qué día es hoy", "que día es hoy",
        "fecha de hoy", "cuál es la fecha", "qué fecha es", "día de hoy",
        "en qué fecha estamos", "a cuántos estamos",
        "me dices la hora", "dime qué hora es", "a qué hora estamos",
        "qué hora tienes", "la hora actual", "hora exacta",
    ],
    
    "TRADUCIR": [
        "traduce esto al inglés", "traduce al inglés hola",
        "cómo se dice hola en inglés", "como se dice hola en inglés",
        "tradúceme al inglés", "traduce hello al español",
        "cómo se dice hello en español", "tradúceme al español",
        "cómo se dice hola en francés", "traduce al francés",
        "traduce esto al alemán", "ponlo en otro idioma",
        "significado en inglés", "dime la traducción",
    ],
    
    "CALCULAR": [
        "cuánto es 50 por 3", "cuanto es 50 por 3", "calcula 50 por 3",
        "multiplica 50 por 3", "50 por 3", "cuánto es 100 más 50",
        "calcula 100 más 50", "suma 100 más 50", "100 más 50",
        "cuánto es 100 menos 50", "calcula 100 menos 50", "resta 100 menos 50",
        "cuánto es 200 entre 4", "divide 200 entre 4", "200 entre 4",
        "sácame la cuenta", "resuelve esta operación",
    ],
    
    "MODO_ZEN": [
        "activa modo zen", "modo zen", "modo concentración",
        "necesito concentrarme", "modo zen on", "activa zen",
        "pon modo zen", "quiero concentrarme", "modo focus",
        "activa modo focus", "necesito enfocarme", "quita distracciones",
        "silencia notificaciones", "modo no molestar",
    ],
    
    # ========== CALENDARIO Y AGENDA ==========
    
    "AGENDA_VER": [
        "qué tengo hoy", "que tengo hoy", "qué tengo mañana",
        "ver agenda", "ver calendario", "lee mi agenda",
        "dime mi agenda", "eventos de hoy", "eventos de mañana",
        "próximos eventos", "proximos eventos", "qué sigue en mi agenda",
        "reuniones de hoy", "citas de hoy", "compromisos de hoy",
        "agenda para hoy", "calendario de hoy", "revisar schedule",
    ],
    
    "CAMBIAR_UBICACION": [
        "cambia mi ubicación a", "cambia mi ciudad a", "configura mi ciudad en",
        "pon mi ciudad en", "pon mi ubicación en", "cambiar mi ciudad a",
        "mi ciudad es", "estoy en", "ubicación actual",
        "actualiza mi zona", "dile al sistema que estoy en madrid",
    ],
    
    # ========== DEVOPS Y GIT (Aumentado para balancear) ==========
    
    "GIT_STATUS": [
        "git status", "estado de git", "ver estado git",
        "qué cambios tengo", "que cambios tengo", "archivos modificados",
        "check git", "status del repo", "cómo va el repositorio",
        "dime el status", "hay cambios pendientes", "ver estatus",
    ],
    
    "GIT_PUSH": [
        "git push", "subir cambios", "sube cambios", "push",
        "enviar cambios", "subir a github", "sube a git",
        "pushea los cambios", "haz un push", "manda el commit",
        "empuja la rama", "upload cambios", "subir al remoto",
    ],
    
    "GIT_INIT": [
        "git init", "inicializar git", "crear repositorio",
        "iniciar git", "nuevo repositorio", "crear repo git",
        "comenzar control de versiones", "init git", "arranca git aquí",
        "inicializa el repositorio", "haz un git init",
    ],
    
    "GIT_PULL": [
        "git pull", "traer cambios", "actualizar repositorio",
        "pull", "bajar cambios", "pulea los cambios",
        "haz un pull", "actualiza la rama", "bájate lo nuevo",
        "sincroniza el repo", "descargar del remoto",
    ],
    
    "CAMBIAR_DIRECTORIO": [
        "trabajar en", "cambiar directorio", "cambiar carpeta",
        "ir a", "navegar a", "abrir carpeta", "muévete a la carpeta",
        "entra en el directorio", "cd a", "cambia ruta",
    ],
    
    "DIAGNOSTICO_RED": [
        # IP y configuración
        "mi ip", "cuál es mi ip", "cual es mi ip",
        "ip local", "ip pública", "dirección ip",
        "dime mi dirección ip", "en qué ip estoy",
        "ver red", "muéstrame la ip", "configuración ip",
        # Estado de conexión
        "cómo está mi conexión", "como esta mi conexion",
        "tengo internet", "hay internet", "estoy conectado",
        "revisa mi red", "verifica mi wifi", "checa mi conexión",
        "qué tan rápido está mi internet", "velocidad de internet",
        "mi conexión está lenta", "por qué está lento el internet",
        "diagnóstico de red", "estado de la red", "calidad de conexión",
        "latencia", "ping", "cuánto ping tengo",
    ],
    
    "LIBERAR_PUERTO": [
        "libera el puerto", "matar puerto", "cerrar puerto",
        "quien usa el puerto", "qué usa el puerto", "desbloquea el puerto",
        "kill port", "cierra la conexión del puerto", "limpia el puerto",
    ],
    
    "INSTALAR_DEPENDENCIAS": [
        "instalar dependencias", "instalar paquetes", "install",
        "instala requirements", "pip install", "npm install",
        "corre el npm install", "instala los paquetes del requirements",
        "baja las librerías", "actualiza node modules", "instalar todo",
    ],
    
    "BUILD_PROYECTO": [
        "construir proyecto", "build", "compilar",
        "hacer build", "construir", "correr el build",
        "bildea el proyecto", "make build", "npm build",
        "genera el ejecutable", "compila el código",
    ],
    
    # ========== HEALTH MONITOR (Aumentado para diferenciar de Rutinas) ==========
    
    "HEALTH_INICIAR": [
        "voy a trabajar", "empezar trabajo", "iniciar trabajo",
        "trabajar en casa", "trabajar en oficina", "empezar jornada",
        "comenzar trabajo", "inicio de jornada", "fichar entrada",
        "empieza a contar mi tiempo", "arranca jornada laboral",
        "marcar entrada", "iniciar turno",
    ],
    
    "HEALTH_PAUSAR": [
        "pausa trabajo", "pausar trabajo", "descanso",
        "tomar descanso", "pausa", "descansar", "voy a comer",
        "break time", "dame un respiro", "pausa el contador",
        "salgo a comer", "pausar jornada",
    ],
    
    "HEALTH_REANUDAR": [
        "reanudar trabajo", "continuar trabajo", "volver al trabajo",
        "seguir trabajando", "reanudar", "continuar",
        "regresé del baño", "fin del descanso", "back to work",
        "sigue contando", "estoy de vuelta", "reanudar jornada",
    ],
    
    "HEALTH_TERMINAR": [
        "terminar trabajo", "fin de jornada", "acabar trabajo",
        "terminar jornada", "fin del día", "acabar jornada",
        "ya acabé por hoy", "cierra el día", "fichar salida",
        "stop work", "hasta mañana", "cerrar turno",
    ],
    
    "HEALTH_TIEMPO": [
        "cuánto tiempo llevo", "cuanto tiempo llevo", "tiempo trabajado",
        "cuánto llevo trabajando", "tiempo de trabajo",
        "cuántas horas llevo", "mi cronómetro laboral",
        "revisar horas trabajadas",
    ],
    
    "HEALTH_PROXIMO_DESCANSO": [
        "próximo descanso", "proximo descanso", "siguiente descanso",
        "cuándo descanso", "cuando descanso", "falta mucho para descanso",
        "a qué hora es mi break", "cuánto falta para comer",
    ],
    
    # ========== STUDY ASSISTANT (Aumentado) ==========
    
    "STUDY_RESUME_PDF": [
        "resume pdf", "resumir pdf", "resumen de pdf",
        "resume este pdf", "haz un resumen del pdf",
        "sácame lo importante del documento", "analiza este pdf",
        "dame los puntos clave del archivo", "leer y resumir pdf",
    ],
    
    "STUDY_FLASHCARDS": [
        "crea flashcards", "genera flashcards", "flashcards de",
        "hacer flashcards", "flashcards sobre",
        "hazme tarjetas de estudio", "preguntas de repaso",
        "quiero estudiar con tarjetas", "generar cuestionario",
    ],

    "STUDY_YOUTUBE": [
        "resume video", "resume este video", "resumen de video",
        "sacar resumen de youtube", "flashcards de video",
        "flashcards del video", "estudiar con video",
        "resume youtube", "analiza este video", "explícame el video",
    ],

    "STUDY_EXAM": [
        "genera examen", "crea examen", "hazme un examen",
        "examen de", "quiero un examen", "prepara examen",
        "genera un test", "crea un test", "hazme un test",
        "ponme a prueba", "simulacro de examen",
    ],

    "STUDY_SUMMARY_SIMPLE": [
        "resumen simple", "resumen fácil", "explica simple",
        "explícame fácil", "modo simple", "versión simple",
        "como para niños", "explica básico", "dímelo en fácil",
        "explícamelo como si tuviera 5 años",
    ],

    "STUDY_SUMMARY_ADVANCED": [
        "resumen avanzado", "resumen técnico", "resumen experto",
        "explicación técnica", "modo experto", "versión avanzada",
        "detalles técnicos", "análisis profundo", "dame los datos duros",
        "explicación universitaria",
    ],

    "MODO_ESTUDIO": [
        "modo estudio", "modo de estudio", "voy a estudiar",
        "quiero estudiar", "activar modo estudio", "iniciar estudio",
        "ponerme a estudiar", "hora de estudiar", "tiempo de estudio",
        "sesion de estudio", "abrir asistente de estudio",
        "necesito estudiar", "tengo que estudiar",
        "modo studio", "voy a estudir", "activar estdio", # Typos
    ],
    
    # ========== GAME CONTROLLER (Aumentado) ==========
    
    "GAMES_LISTAR": [
        "qué juegos tengo", "que juegos tengo", "lista juegos",
        "mis juegos", "ver juegos", "mostrar juegos",
        "biblioteca de juegos", "a qué puedo jugar", "enséñame los juegos",
    ],
    
    "GAMES_ESCANEAR": [
        "escanear juegos", "buscar juegos", "detectar juegos",
        "encontrar juegos", "scan juegos",
        "busca juegos nuevos", "actualiza mi lista de juegos",
    ],
    
    "GAMES_ABRIR": [
        "abre valorant", "juega valorant", "lanza valorant",
        "abre league", "juega minecraft", "lanza fortnite",
        "abre apex", "jugar valorant", "quiero jugar",
        "abre steam", "run game", "inicia el juego",
    ],
    
    "GAMES_OPTIMIZAR": [
        "optimiza para jugar", "modo gaming", "modo competitivo",
        "optimizar juegos", "modo gamer", "optimización gaming",
        "libera ram para jugar", "acelera la pc", "boost fps",
    ],
    
    "GAMES_CERRAR": [
        "cierra juego", "cerrar juego", "cierra valorant",
        "cerrar league", "matar juego", "sal del juego",
        "terminar partida", "cierra el videojuego",
    ],
    
    # ========== PERFIL DE USUARIO ==========
    
    "PERFIL_VER": [
        "mi perfil", "ver perfil", "mostrar perfil",
        "configuración personal", "ver mi configuración",
        "quién soy yo", "mis datos", "mostrar usuario",
    ],
    
    "PERFIL_NOMBRE": [
        "llámame", "llamame", "mi nombre es",
        "dime", "quiero que me digas", "cámbiame el nombre",
        "configura mi apodo",
    ],
    
    "PERFIL_IDIOMA": [
        "cambiar idioma", "idioma", "cambiar voz",
        "habla en inglés", "habla en español",
        "cambia a inglés", "ponte en español",
    ],
    
    # ========== SYSTEM CONTROL ==========
    
    "BRILLO": [
        "sube el brillo", "baja el brillo", "brillo al máximo",
        "brillo al mínimo", "aumenta brillo", "disminuye brillo",
        "ajustar luminosidad", "me lastima la luz", "no veo nada",
    ],
    
    "MEDIA_CONTROL": [
        "play", "pause", "pausa", "siguiente canción",
        "canción anterior", "next", "prev", "play pause",
        "detén la música", "pásala", "regresa la rola",
    ],
    
    "BLOQUEAR_PANTALLA": [
        "bloquea la pantalla", "bloquear pantalla", "lock",
        "bloquea el equipo", "bloquear pc", "win L",
        "suspender sesión", "candado a la pantalla",
    ],
    
    "APAGAR_PANTALLA": [
        "apaga la pantalla", "apagar pantalla", "apaga el monitor",
        "apagar monitor", "pantalla off", "solo el monitor",
        "apagar display", "monitor negro",
    ],
    
    "MATAR_PROCESO": [
        "matar", "cerrar", "mata chrome", "cierra chrome",
        "matar proceso", "cerrar proceso", "finalizar tarea",
        "forzar cierre", "kill process",
    ],
    
    "MINIMIZAR_TODO": [
        "minimiza el escritorio", "minimiza todo", "minimizar todo",
        "mostrar escritorio", "escritorio", "win d",
        "esconde las ventanas", "limpia la pantalla",
    ],
    
    "MAXIMIZAR": [
        "maximiza", "maximizar", "maximiza ventana",
        "maximizar ventana", "pantalla completa", "agrandar ventana",
    ],
    
    "APAGAR_SISTEMA": [
        "apaga el sistema", "apagar", "shutdown",
        "apaga la pc", "apagar computadora", "apaga en 5 minutos",
        "cerrar sistema", "turn off", "vete a dormir",
    ],
    
    "REINICIAR_SISTEMA": [
        "reinicia el sistema", "reiniciar", "restart",
        "reinicia la pc", "reiniciar computadora", "reinicia en 5 minutos",
        "reboot", "resetea la pc", "vuelve a iniciar",
    ],
    
    "CANCELAR_APAGADO": [
        "cancela el apagado", "cancelar apagado", "cancela shutdown",
        "no apagues", "detener apagado", "abortar apagado",
        "espera no te apagues", "cancela la orden",
    ],
    
    "VACIAR_PAPELERA": [
        "vacía la papelera", "vaciar papelera", "empty recycle bin",
        "limpiar papelera", "borrar papelera", "elimina la basura",
        "limpia la papelera de reciclaje",
    ],
    
    "CAPTURA_PANTALLA": [
        "captura pantalla", "screenshot", "toma captura",
        "captura de pantalla", "tomar screenshot", "pantallazo",
        "guarda la pantalla", "foto a la pantalla",
    ],
    
    "LIMPIAR_TEMP": [
        "limpia archivos temporales", "limpiar temp", "borrar temporales",
        "limpiar archivos temp", "clean temp", "borra caché",
        "eliminar archivos basura",
    ],
    
    "PROCESOS_PESADOS": [
        "procesos pesados", "qué consume RAM", "que consume RAM",
        "procesos que consumen", "heavy processes",
        "qué me está alentando la pc", "uso de cpu",
    ],
    
    "LIMPIEZA_PROFUNDA": [
        "limpieza profunda", "limpia sistema", "limpia todo",
        "limpia temporales y papelera", "deep clean",
        "mantenimiento completo", "limpieza total",
    ],
    
    # ========== RUTINAS (Diferenciadas de Health) ==========
    
    "RUTINA_BUENOS_DIAS": [
        "rutina buenos días", "rutina buenos dias", "rutina mañana",
        "buenos días", "buenos dias", "rutina de mañana",
        "iniciar mi día", "comenzar día",
    ],
    
    "RUTINA_TRABAJO": [
        "rutina trabajo", "modo trabajo", "rutina laboral",
        "empezar rutina trabajo", "configura el entorno de trabajo",
        "prepara todo para trabajar", "ponme en modo oficina",
    ],
    
    "RUTINA_FIN_TRABAJO": [
        "rutina fin trabajo", "fin de trabajo", "rutina descanso",
        "terminar rutina trabajo", "desactiva modo trabajo",
        "modo casa", "ya no quiero trabajar",
    ],
    
    "RUTINAS_LISTAR": [
        "lista rutinas", "rutinas disponibles", "qué rutinas tengo",
        "que rutinas tengo", "ver rutinas", "mis automatizaciones",
    ],
    
    # ========== NETWORK GUARDIAN (Aumentado) ==========
    
    "NETWORK_DISPOSITIVOS": [
        "dispositivos en la red", "ver dispositivos", "qué está conectado",
        "que esta conectado", "dispositivos wifi", "ver red",
        "quién me roba wifi", "listar ips", "escaneo de red",
        "muéstrame los intrusos",
    ],
    
    "NETWORK_ESCANEAR": [
        "escanear red", "escanear wifi", "scan red",
        "buscar dispositivos", "detectar dispositivos",
        "haz un barrido de red", "actualiza la lista de equipos",
    ],
    
    "NETWORK_DASHBOARD": [
        "dashboard red", "panel red", "fortaleza",
        "ver panel red", "network dashboard",
        "abrir monitor de red", "estado de la seguridad",
    ],
    
    # ========== POMODORO ==========
    
    "POMODORO_INICIAR": [
        "inicia pomodoro", "empezar pomodoro", "pomodoro",
        "comenzar pomodoro", "start pomodoro", "pon un tomate",
        "técnica pomodoro", "ciclo de concentración",
    ],
    
    "POMODORO_PAUSAR": [
        "pausa pomodoro", "pausar pomodoro", "detener pomodoro",
        "para el reloj pomodoro", "congela el pomodoro",
    ],
    
    "POMODORO_ESTADO": [
        "estado pomodoro", "cómo va el pomodoro", "como va el pomodoro",
        "tiempo pomodoro", "pomodoro status", "cuánto falta del pomodoro",
    ],
    
    # ========== SEGURIDAD (SENTINEL) ==========

    "SENTINEL_ACTIVAR": [
        "activar centinela", "activa sentinela", "modo guardia",
        "activar modo centinela", "protege el sistema", "bloquea el acceso",
        "iniciar protocolo de seguridad", "activa la seguridad",
        "sentinel on", "activar vigilancia", "ponte en guardia",
    ],

    "SENTINEL_DESACTIVAR": [
        "desactivar centinela", "desactiva sentinela", "quita el modo guardia",
        "desactivar modo centinela", "apagar centinela", "ya llegué",
        "desbloquea el sistema", "apaga la seguridad", "descansar centinela",
        "sentinel off", "terminar vigilancia", "falsa alarma",
    ],

    # ========== AYUDA Y CONFIGURACIÓN ==========
    
    "AYUDA": [
        "ayuda", "comandos", "qué puedes hacer", "que puedes hacer",
        "lista de comandos", "help", "qué sabes hacer",
        "muéstrame tus funciones", "manual de usuario", "estoy perdido",
    ],
    
    "ABRIR_CONFIGURACION": [
        "abre configuración", "abre configuracion", "abrir configuración",
        "abrir configuracion", "abre ajustes", "abrir ajustes",
        "abre settings", "configuración", "ajustes", "settings",
        "panel de control", "preferencias",
    ],
    
    "ABRIR_PERFIL": [
        "abre mi perfil", "mi perfil", "configurar perfil",
        "editar perfil", "perfil de usuario", "ver mi perfil",
        "mis datos de usuario", "ajustes de cuenta",
    ],
    
    # ========== MONITOR DE SISTEMA ==========
    
    "SISTEMA_ESTADO": [
        "sistema", "estado", "monitor", "estado del sistema",
        "cómo está el sistema", "como esta el sistema",
        "rendimiento del sistema", "salud del equipo",
        "diagnóstico del pc", "resumen de recursos",
    ],
    
    # ========== CONVERSACIÓN GENERAL ==========
    
    "CONVERSACION": [
        "hola", "qué tal", "que tal", "cómo estás", "como estas",
        "buenos días", "buenas tardes", "buenas noches",
        "gracias", "de nada", "adiós", "adios", "hasta luego",
        "cuéntame un chiste", "cuentame un chiste",
        "háblame de ti", "hablame de ti", "quién eres", "quien eres",
        "dime algo gracioso", "estás ahí", "sara estás viva",
    ],
    
    # ========== NUEVO: MANEJO DE ERRORES (IMPIDEN FALSOS POSITIVOS) ==========
    "OUT_OF_SCOPE": [
        "hazme un sandwich", "tengo hambre", "te quieres casar conmigo",
        "quién ganó el mundial del 86", "cuál es el sentido de la vida",
        "baila para mi", "vuela hasta la luna", "cocina algo rico",
        "limpia mi cuarto", "saca la basura", "insúltame",
        "dime tu opinión política", "crees en dios", "cuánto pesas",
        "te gusta la pizza", "dame un consejo de amor",
        "asdfasdf", "ruido de fondo", "bla bla bla",
    ]
}