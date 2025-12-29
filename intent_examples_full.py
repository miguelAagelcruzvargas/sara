"""
🎯 SARA - Comprehensive Intent Training Examples
=================================================

Dataset completo con TODOS los comandos de SARA.
Incluye 40+ intenciones con variaciones mexicanas y errores de voz.

Total: ~1000+ ejemplos de entrenamiento
"""

INTENT_EXAMPLES_FULL = {
    # ========== COMANDOS BÁSICOS (14 intenciones originales) ==========
    
    "MEMORIZAR": [
        # Variaciones estándar
        "memoriza que la clave es 777",
        "guarda esto: dato importante",
        "recuerda que mañana tengo cita",
        "anota el código ABC123",
        "no olvides que el wifi es password123",
        "apunta que debo llamar a Juan",
        "registra que el proyecto se entrega el viernes",
        "toma nota de que María llamó",
        "anota mi número de cuenta 12345",
        "guarda mi dirección calle 123",
        # Modismos mexicanos
        "apúntale que tengo junta a las 3",
        "no se te olvide que debo pagar la luz",
        "acuérdate que hoy es cumpleaños de mi mamá",
        "anótale que necesito comprar leche",
        # Errores comunes
        "memoriza qué la clave es 777",
        "memoriza está clave es 777",
        "guarda está información",
        "memoriza qué tengo cita",
        # Sin artículos
        "memoriza clave es 777",
        "guarda dato importante",
        "anota código ABC",
        # Variaciones de verbo
        "almacena que la reunión es mañana",
        "graba que el password es 123",
        "registra mi cumpleaños es el 15",
    ],
    
    "VOLUMEN_SUBIR": [
        "sube el volumen", "súbele volumen", "más alto", "aumenta el sonido",
        "volumen arriba", "subir volumen", "sube volumen", "súbele",
        "ponle más recio", "échale más volumen", "métele más", "dale más duro",
        "ponlo más fuerte", "subele volumen", "no te escucho sube",
        "volumen al máximo", "ponlo al 100", "aumenta audio", "más duro",
        "más fuerte", "volumen alto",
    ],
    
    "VOLUMEN_BAJAR": [
        "baja el volumen", "bájale volumen", "más bajo", "disminuye el sonido",
        "volumen abajo", "bajar volumen", "baja volumen", "bájale",
        "ponle más bajito", "échale menos volumen", "quítale volumen",
        "bájale tantito", "bajale volumen", "está muy alto baja",
        "volumen al mínimo", "ponlo bajito", "disminuye audio",
        "menos fuerte", "más suave",
    ],
    
    "SILENCIO": [
        "silencio", "mute", "cállate", "silencia", "mutea",
        "quita el sonido", "sin sonido", "apaga el audio",
        "quita audio", "calla", "shh", "silencio total",
        "mutear", "pon mute",
    ],
    
    "ABRIR_APP": [
        # Navegadores
        "abre chrome", "abrir chrome", "abre google chrome", "abre firefox", "abre edge",
        # Editores
        "abre visual studio code", "abrir vscode", "abre vs code",
        "abre notepad", "abre bloc de notas", "abre word", "abre excel",
        # Comunicación
        "abre discord", "abrir discord", "abre whatsapp", "abre telegram", "abre slack",
        # Multimedia
        "abre spotify", "abrir spotify", "abre vlc",
        # Variaciones
        "lanza chrome", "ejecuta notepad", "inicia discord", "arranca spotify",
    ],
    
    "BUSCAR_WEB": [
        "busca en google inteligencia artificial", "busca python", "busca recetas de pasta",
        "busca noticias de tecnología", "busca cómo hacer pan",
        "investiga sobre machine learning", "investiga sobre python",
        "investiga inteligencia artificial", "googlea recetas de pasta",
        "googlea noticias", "googlea python tutorial",
        "qué es machine learning", "qué es python", "cómo funciona la IA",
        "cuál es la capital de Francia", "búscame información de tensorflow",
        "búscame tutoriales de python", "búscame recetas mexicanas",
        "échame una búsqueda de python", "investígame sobre IA",
        "busca inteligencia artificial", "investiga python",
    ],
    
    "LEER_DOCUMENTO": [
        "lee este archivo", "lee este documento", "qué dice esta página",
        "que dice esta página", "lee esta web", "que dice este pdf",
        "lee este pdf", "abre este documento", "lee el archivo",
        "qué dice el documento", "lee la página", "muéstrame este archivo",
        "dime qué dice", "lee esto", "qué contiene este archivo",
    ],
    
    "REPRODUCIR_MEDIA": [
        "pon música", "pon rock", "pon lofi", "pon una canción", "pon reggaeton",
        "reproduce rock", "reproduce en youtube", "reproduce música", "reproduce lofi",
        "ponle música", "ponle rock", "ponle lofi", "pon música relajante",
        "reproduce música para estudiar", "pon algo de rock", "ponme música",
        "échale música", "métele rock", "dale play a lofi",
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
        "temperatura actual", "cuál es la temperatura", "va a llover hoy", "va a llover",
        "qué tiempo hace", "cómo está el tiempo", "clima de hoy",
        "pronóstico del tiempo", "hace frío", "hace calor", "temperatura",
    ],
    
    "HORA_FECHA": [
        "qué hora es", "que hora es", "hora actual", "dime la hora",
        "cuál es la hora", "qué horas son", "qué día es hoy", "que día es hoy",
        "fecha de hoy", "cuál es la fecha", "qué fecha es", "día de hoy",
        "en qué fecha estamos", "a cuántos estamos",
    ],
    
    "TRADUCIR": [
        "traduce esto al inglés", "traduce al inglés hola",
        "cómo se dice hola en inglés", "como se dice hola en inglés",
        "tradúceme al inglés", "traduce hello al español",
        "cómo se dice hello en español", "tradúceme al español",
        "cómo se dice hola en francés", "traduce al francés", "traduce esto al alemán",
    ],
    
    "CALCULAR": [
        "cuánto es 50 por 3", "cuanto es 50 por 3", "calcula 50 por 3",
        "multiplica 50 por 3", "50 por 3", "cuánto es 100 más 50",
        "calcula 100 más 50", "suma 100 más 50", "100 más 50",
        "cuánto es 100 menos 50", "calcula 100 menos 50", "resta 100 menos 50",
        "cuánto es 200 entre 4", "divide 200 entre 4", "200 entre 4", "200 dividido 4",
    ],
    
    "MODO_ZEN": [
        "activa modo zen", "modo zen", "modo concentración",
        "necesito concentrarme", "modo zen on", "activa zen",
        "pon modo zen", "quiero concentrarme", "modo focus",
        "activa modo focus", "necesito enfocarme",
    ],
    
    # ========== CALENDARIO Y AGENDA ==========
    
    "AGENDA_VER": [
        "qué tengo hoy", "que tengo hoy", "qué tengo mañana",
        "ver agenda", "ver calendario", "lee mi agenda",
        "dime mi agenda", "eventos de hoy", "eventos de mañana",
        "próximos eventos", "proximos eventos", "qué sigue en mi agenda",
        "reuniones de hoy", "citas de hoy", "compromisos de hoy",
        "agenda para hoy", "calendario de hoy",
    ],
    
    # ========== CAMBIO DE UBICACIÓN ==========
    
    "CAMBIAR_UBICACION": [
        "cambia mi ubicación a", "cambia mi ciudad a", "configura mi ciudad en",
        "pon mi ciudad en", "pon mi ubicación en", "cambiar mi ciudad a",
        "mi ciudad es", "estoy en", "ubicación actual",
    ],
    
    # ========== DEVOPS Y GIT ==========
    
    "GIT_STATUS": [
        "git status", "estado de git", "ver estado git",
        "qué cambios tengo", "que cambios tengo", "archivos modificados",
    ],
    
    "GIT_PUSH": [
        "git push", "subir cambios", "sube cambios", "push",
        "enviar cambios", "subir a github", "sube a git",
    ],
    
    "GIT_INIT": [
        "git init", "inicializar git", "crear repositorio",
        "iniciar git", "nuevo repositorio",
    ],
    
    "GIT_PULL": [
        "git pull", "traer cambios", "actualizar repositorio",
        "pull", "bajar cambios",
    ],
    
    "CAMBIAR_DIRECTORIO": [
        "trabajar en", "cambiar directorio", "cambiar carpeta",
        "ir a", "navegar a", "abrir carpeta",
    ],
    
    "MI_IP": [
        "mi ip", "cuál es mi ip", "cual es mi ip",
        "ip local", "ip pública", "dirección ip",
    ],
    
    "LIBERAR_PUERTO": [
        "libera el puerto", "matar puerto", "cerrar puerto",
        "quien usa el puerto", "qué usa el puerto",
    ],
    
    "INSTALAR_DEPENDENCIAS": [
        "instalar dependencias", "instalar paquetes", "install",
        "instala requirements", "pip install",
    ],
    
    "BUILD_PROYECTO": [
        "construir proyecto", "build", "compilar",
        "hacer build", "construir",
    ],
    
    # ========== HEALTH MONITOR ==========
    
    "HEALTH_INICIAR": [
        "voy a trabajar", "empezar trabajo", "iniciar trabajo",
        "trabajar en casa", "trabajar en oficina", "empezar jornada",
        "comenzar trabajo", "inicio de jornada",
    ],
    
    "HEALTH_PAUSAR": [
        "pausa trabajo", "pausar trabajo", "descanso",
        "tomar descanso", "pausa", "descansar",
    ],
    
    "HEALTH_REANUDAR": [
        "reanudar trabajo", "continuar trabajo", "volver al trabajo",
        "seguir trabajando", "reanudar", "continuar",
    ],
    
    "HEALTH_TERMINAR": [
        "terminar trabajo", "fin de jornada", "acabar trabajo",
        "terminar jornada", "fin del día", "acabar jornada",
    ],
    
    "HEALTH_TIEMPO": [
        "cuánto tiempo llevo", "cuanto tiempo llevo", "tiempo trabajado",
        "cuánto llevo trabajando", "tiempo de trabajo",
    ],
    
    "HEALTH_PROXIMO_DESCANSO": [
        "próximo descanso", "proximo descanso", "siguiente descanso",
        "cuándo descanso", "cuando descanso", "falta mucho para descanso",
    ],
    
    # ========== STUDY ASSISTANT ==========
    
    "STUDY_RESUME_PDF": [
        "resume pdf", "resumir pdf", "resumen de pdf",
        "resume este pdf", "haz un resumen del pdf",
    ],
    
    "STUDY_FLASHCARDS": [
        "crea flashcards", "genera flashcards", "flashcards de",
        "hacer flashcards", "flashcards sobre",
    ],
    
    # ========== GAME CONTROLLER ==========
    
    "GAMES_LISTAR": [
        "qué juegos tengo", "que juegos tengo", "lista juegos",
        "mis juegos", "ver juegos", "mostrar juegos",
    ],
    
    "GAMES_ESCANEAR": [
        "escanear juegos", "buscar juegos", "detectar juegos",
        "encontrar juegos", "scan juegos",
    ],
    
    "GAMES_ABRIR": [
        "abre valorant", "juega valorant", "lanza valorant",
        "abre league", "juega minecraft", "lanza fortnite",
        "abre apex", "jugar valorant",
    ],
    
    "GAMES_OPTIMIZAR": [
        "optimiza para jugar", "modo gaming", "modo competitivo",
        "optimizar juegos", "modo gamer", "optimización gaming",
    ],
    
    "GAMES_CERRAR": [
        "cierra juego", "cerrar juego", "cierra valorant",
        "cerrar league", "matar juego",
    ],
    
    # ========== PERFIL DE USUARIO ==========
    
    "PERFIL_VER": [
        "mi perfil", "ver perfil", "mostrar perfil",
        "configuración personal", "ver mi configuración",
    ],
    
    "PERFIL_NOMBRE": [
        "llámame", "llamame", "mi nombre es",
        "dime", "quiero que me digas",
    ],
    
    "PERFIL_IDIOMA": [
        "cambiar idioma", "idioma", "cambiar voz",
        "habla en inglés", "habla en español",
    ],
    
    # ========== SYSTEM CONTROL ==========
    
    "BRILLO": [
        "sube el brillo", "baja el brillo", "brillo al máximo",
        "brillo al mínimo", "aumenta brillo", "disminuye brillo",
    ],
    
    "MEDIA_CONTROL": [
        "play", "pause", "pausa", "siguiente canción",
        "canción anterior", "next", "prev", "play pause",
    ],
    
    "BLOQUEAR_PANTALLA": [
        "bloquea la pantalla", "bloquear pantalla", "lock",
        "bloquea el equipo", "bloquear pc",
    ],
    
    "APAGAR_PANTALLA": [
        "apaga la pantalla", "apagar pantalla", "apaga el monitor",
        "apagar monitor", "pantalla off",
    ],
    
    "MATAR_PROCESO": [
        "matar", "cerrar", "mata chrome", "cierra chrome",
        "matar proceso", "cerrar proceso",
    ],
    
    "MINIMIZAR_TODO": [
        "minimiza el escritorio", "minimiza todo", "minimizar todo",
        "mostrar escritorio", "escritorio", "win d",
    ],
    
    "MAXIMIZAR": [
        "maximiza", "maximizar", "maximiza ventana",
        "maximizar ventana", "pantalla completa",
    ],
    
    "APAGAR_SISTEMA": [
        "apaga el sistema", "apagar", "shutdown",
        "apaga la pc", "apagar computadora", "apaga en 5 minutos",
    ],
    
    "REINICIAR_SISTEMA": [
        "reinicia el sistema", "reiniciar", "restart",
        "reinicia la pc", "reiniciar computadora", "reinicia en 5 minutos",
    ],
    
    "CANCELAR_APAGADO": [
        "cancela el apagado", "cancelar apagado", "cancela shutdown",
        "no apagues", "detener apagado",
    ],
    
    "VACIAR_PAPELERA": [
        "vacía la papelera", "vaciar papelera", "empty recycle bin",
        "limpiar papelera", "borrar papelera",
    ],
    
    "CAPTURA_PANTALLA": [
        "captura pantalla", "screenshot", "toma captura",
        "captura de pantalla", "tomar screenshot",
    ],
    
    "LIMPIAR_TEMP": [
        "limpia archivos temporales", "limpiar temp", "borrar temporales",
        "limpiar archivos temp", "clean temp",
    ],
    
    "PROCESOS_PESADOS": [
        "procesos pesados", "qué consume RAM", "que consume RAM",
        "procesos que consumen", "heavy processes",
    ],
    
    "LIMPIEZA_PROFUNDA": [
        "limpieza profunda", "limpia sistema", "limpia todo",
        "limpia temporales y papelera", "deep clean",
    ],
    
    # ========== RUTINAS ==========
    
    "RUTINA_BUENOS_DIAS": [
        "rutina buenos días", "rutina buenos dias", "rutina mañana",
        "buenos días", "buenos dias", "rutina de mañana",
    ],
    
    "RUTINA_TRABAJO": [
        "rutina trabajo", "modo trabajo", "rutina laboral",
        "empezar rutina trabajo",
    ],
    
    "RUTINA_FIN_TRABAJO": [
        "rutina fin trabajo", "fin de trabajo", "rutina descanso",
        "terminar rutina trabajo",
    ],
    
    "RUTINAS_LISTAR": [
        "lista rutinas", "rutinas disponibles", "qué rutinas tengo",
        "que rutinas tengo", "ver rutinas",
    ],
    
    # ========== NETWORK GUARDIAN ==========
    
    "NETWORK_DISPOSITIVOS": [
        "dispositivos en la red", "ver dispositivos", "qué está conectado",
        "que esta conectado", "dispositivos wifi", "ver red",
    ],
    
    "NETWORK_ESCANEAR": [
        "escanear red", "escanear wifi", "scan red",
        "buscar dispositivos", "detectar dispositivos",
    ],
    
    "NETWORK_DASHBOARD": [
        "dashboard red", "panel red", "fortaleza",
        "ver panel red", "network dashboard",
    ],
    
    # ========== POMODORO ==========
    
    "POMODORO_INICIAR": [
        "inicia pomodoro", "empezar pomodoro", "pomodoro",
        "comenzar pomodoro", "start pomodoro",
    ],
    
    "POMODORO_PAUSAR": [
        "pausa pomodoro", "pausar pomodoro", "detener pomodoro",
    ],
    
    "POMODORO_ESTADO": [
        "estado pomodoro", "cómo va el pomodoro", "como va el pomodoro",
        "tiempo pomodoro", "pomodoro status",
    ],
    
    # ========== AYUDA Y CONFIGURACIÓN ==========
    
    "AYUDA": [
        "ayuda", "comandos", "qué puedes hacer", "que puedes hacer",
        "lista de comandos", "help", "qué sabes hacer",
    ],
    
    "ABRIR_CONFIGURACION": [
        "abre configuración", "abre configuracion", "abrir configuración",
        "abrir configuracion", "abre ajustes", "abrir ajustes",
        "abre settings", "configuración", "ajustes", "settings",
    ],
    
    "ABRIR_PERFIL": [
        "abre mi perfil", "mi perfil", "configurar perfil",
        "editar perfil", "perfil de usuario", "ver mi perfil",
    ],
    
    # ========== MONITOR DE SISTEMA ==========
    
    "SISTEMA_ESTADO": [
        "sistema", "estado", "monitor", "estado del sistema",
        "cómo está el sistema", "como esta el sistema",
        "rendimiento del sistema",
    ],
    
    # ========== CONVERSACIÓN GENERAL ==========
    
    "CONVERSACION": [
        "hola", "qué tal", "que tal", "cómo estás", "como estas",
        "buenos días", "buenas tardes", "buenas noches",
        "gracias", "de nada", "adiós", "adios", "hasta luego",
        "cuéntame un chiste", "cuentame un chiste",
        "háblame de ti", "hablame de ti", "quién eres", "quien eres",
    ],
}
