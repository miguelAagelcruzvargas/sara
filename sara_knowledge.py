"""
SARA Knowledge Base - Auto-conciencia de capacidades
Este módulo contiene toda la información sobre lo que SARA puede hacer
"""

class SaraKnowledge:
    """Base de conocimiento de SARA sobre sí misma"""
    
    # Información básica
    INFO = {
        "nombre": "SARA",
        "version": "3.0.5",
        "descripcion": "Sistema Avanzado de Respuesta y Asistencia",
        "creador": "Miguel",
        "proposito": "Asistente de voz inteligente superior a Alexa"
    }
    
    # Capacidades organizadas por categoría
    CAPACIDADES = {
        "estudio": {
            "descripcion": "Asistente educativo con IA",
            "funciones": [
                "Resumir PDFs con inteligencia artificial",
                "Generar flashcards automáticas sobre cualquier tema",
                "Crear material de estudio personalizado"
            ],
            "comandos": ["resume pdf", "crea flashcards", "genera flashcards"]
        },
        
        "gaming": {
            "descripcion": "Control total de videojuegos",
            "funciones": [
                "Detectar juegos instalados (Steam, Epic, Riot, Blizzard)",
                "Lanzar juegos por voz con búsqueda inteligente",
                "Optimizar rendimiento del sistema para gaming",
                "Cerrar apps pesadas automáticamente"
            ],
            "comandos": ["qué juegos tengo", "abre [juego]", "modo competitivo", "optimiza para jugar"]
        },
        
        "salud": {
            "descripcion": "Monitor de bienestar laboral",
            "funciones": [
                "Recordatorios de descanso personalizados",
                "3 perfiles: Casa (flexible), Oficina (discreto), Pomodoro (concentración)",
                "Tracking de tiempo trabajado",
                "Prevención de fatiga visual y muscular"
            ],
            "comandos": ["voy a trabajar", "cuánto tiempo llevo", "próximo descanso", "terminar trabajo"]
        },
        
        "sistema": {
            "descripcion": "Control completo del PC",
            "funciones": [
                "Control de volumen y brillo",
                "Gestión de ventanas (minimizar, restaurar, maximizar)",
                "Administración de procesos",
                "Capturas de pantalla",
                "Apagado y reinicio del sistema",
                "Limpieza profunda ultra-rápida (scripts BAT nativos)"
            ],
            "comandos": ["sube volumen", "minimiza todo", "lista procesos", "limpieza profunda", "apaga el sistema"]
        },
        
        "productividad": {
            "descripcion": "Herramientas de enfoque",
            "funciones": [
                "Modo Zen (minimiza distracciones + música lofi)",
                "Pomodoro timer integrado",
                "Bloqueo de sitios web (opcional)"
            ],
            "comandos": ["modo zen", "salir de modo zen", "inicia pomodoro"]
        },
        
        "devops": {
            "descripcion": "Automatización de desarrollo",
            "funciones": [
                "Control de Git (status, push, init)",
                "Compartir proyectos con túneles",
                "Revisión de código con IA",
                "Gestión de builds"
            ],
            "comandos": ["git status", "subir cambios", "compartir proyecto"]
        },
        
        "tiempo": {
            "descripcion": "Información temporal",
            "funciones": [
                "Hora actual en formato natural",
                "Fecha con día de la semana en español",
                "Respuestas instantáneas sin IA"
            ],
            "comandos": ["qué hora es", "qué día es", "dime la fecha"]
        }
    }
    
    # Ventajas sobre Alexa
    VENTAJAS_VS_ALEXA = [
        "Resumen de documentos PDF con IA",
        "Generación de material de estudio",
        "Detección y control de juegos PC",
        "Optimización de rendimiento del sistema",
        "Monitor de salud laboral personalizado",
        "Limpieza profunda del sistema",
        "Control total de Git y DevOps",
        "Scripts BAT nativos (3x más rápido)",
        "Procesamiento local sin depender de la nube",
        "Integración profunda con Windows"
    ]
    
    # Tecnologías que usa
    TECNOLOGIAS = {
        "ia": "Google Gemini (generación de texto)",
        "voz": "Google Speech Recognition",
        "lenguaje": "Python 3.10+",
        "ui": "CustomTkinter",
        "optimizacion": "Scripts BAT nativos de Windows",
        "pdfs": "PyPDF2",
        "juegos": "Búsqueda fuzzy con fuzzywuzzy"
    }
    
    # Sinónimos y Raíces para búsqueda flexible (Stemming manual)
    SYNONYMS = {
        "estudio": ["pdf", "resum", "flashcard", "examen", "tarea", "clase", "apunt", "estudi", "lectura"],
        "gaming": ["jueg", "jugar", "gamer", "fps", "lag", "steam", "epic", "valorant", "competitivo"],
        "salud": ["descans", "dolor", "cansad", "ojos", "trabaj", "pomodoro", "oficina", "salud", "fatiga"],
        "sistema": ["volumen", "brillo", "lent", "limpi", "bater", "apag", "reinic", "proc", "optim", "ventan", "pc", "computadora"],
        "productividad": ["zen", "enfoque", "distrac", "concentra"],
        "devops": ["git", "codigo", "repositorio", "commit", "push", "pull", "rama"],
        "tiempo": ["hora", "fecha", "dia", "reloj", "cuando"]
    }
    
    @staticmethod
    def get_capabilities_summary() -> str:
        """Resumen de todas las capacidades"""
        summary = "🤖 SOY SARA - Sistema Avanzado de Respuesta y Asistencia\n\n"
        summary += "Mis capacidades principales:\n\n"
        
        for categoria, info in SaraKnowledge.CAPACIDADES.items():
            summary += f"📌 {categoria.upper()}: {info['descripcion']}\n"
            for func in info['funciones']:
                summary += f"  • {func}\n"
            summary += "\n"
        
        return summary
    
    @staticmethod
    def get_category_info(categoria: str) -> str:
        """Información detallada de una categoría"""
        if categoria in SaraKnowledge.CAPACIDADES:
            info = SaraKnowledge.CAPACIDADES[categoria]
            response = f"📌 {categoria.upper()} - {info['descripcion']}\n\n"
            response += "Funciones:\n"
            for func in info['funciones']:
                response += f"• {func}\n"
            response += f"\nComandos: {', '.join(info['comandos'])}"
            return response
        return "❌ Categoría no encontrada"
    
    @staticmethod
    def why_better_than_alexa() -> str:
        """Explica por qué SARA es mejor que Alexa"""
        response = "🎯 SOY SUPERIOR A ALEXA PORQUE:\n\n"
        for i, ventaja in enumerate(SaraKnowledge.VENTAJAS_VS_ALEXA, 1):
            response += f"{i}. {ventaja}\n"
        response += "\nAlexa NO tiene ninguna de estas capacidades."
        return response
    
    @staticmethod
    def smart_response(query: str) -> str:
        """Respuestas inteligentes sin IA basadas en conocimiento"""
        query_lower = query.lower()
        
        # 1. Identidad básica
        if any(x in query_lower for x in ["quien eres", "que eres", "quién eres", "qué eres"]):
            return f"Soy {SaraKnowledge.INFO['nombre']}, {SaraKnowledge.INFO['descripcion']}. " \
                   f"Versión {SaraKnowledge.INFO['version']}. Fui creada para ser superior a Alexa."
        
        if any(x in query_lower for x in ["que puedes hacer", "qué puedes hacer", "tus funciones", "capacidades", "ayuda"]):
            return SaraKnowledge.get_capabilities_summary()
            
        # 2. Listar comandos (General o por categoría)
        if "comandos" in query_lower:
            # Buscar categoría específica en la query
            for cat, stems in SaraKnowledge.SYNONYMS.items():
                if any(stem in query_lower for stem in stems):
                    return SaraKnowledge.list_commands_by_category(cat)
            return SaraKnowledge.list_all_commands()

        # 3. Comparación con Alexa
        if "alexa" in query_lower or "mejor que" in query_lower:
            return SaraKnowledge.why_better_than_alexa()
            
        # 4. Búsqueda inteligente por categorías (usando stemming)
        matched_categories = []
        for cat, stems in SaraKnowledge.SYNONYMS.items():
            if any(stem in query_lower for stem in stems):
                matched_categories.append(cat)
        
        # Priorizar coincidencias más específicas (si hay múltiples)
        if matched_categories:
            # Si hay varias, tomar la primera o la más relevante. 
            # Por ahora tomamos la primera detectada.
            return SaraKnowledge.get_category_info(matched_categories[0])
            
        # 5. Fallbacks específicos
        if "version" in query_lower or "versión" in query_lower:
            return f"Versión {SaraKnowledge.INFO['version']} - Última actualización: 2024-12-28"
        
        if "creador" in query_lower or "quien te creo" in query_lower:
            return f"Fui creada por {SaraKnowledge.INFO['creador']} para ser el mejor asistente de voz para PC."
        
        return None  # No hay respuesta inteligente, usar IA
    
    @staticmethod
    def list_all_commands() -> str:
        """Lista TODOS los comandos disponibles organizados por categoría"""
        response = "📋 TODOS MIS COMANDOS:\n\n"
        
        # Estudio
        response += "━━━ 📚 ESTUDIO ━━━\n"
        response += "• 'Resume PDF [ruta]'\n"
        response += "• 'Crea flashcards de [tema]'\n"
        response += "• 'Genera flashcards sobre [tema]'\n\n"
        
        # Gaming
        response += "━━━ 🎮 GAMING ━━━\n"
        response += "• 'Qué juegos tengo'\n"
        response += "• 'Abre [juego]'\n"
        response += "• 'Juega [juego]'\n"
        response += "• 'Modo competitivo'\n"
        response += "• 'Optimiza para jugar'\n\n"
        
        # Salud
        response += "━━━ 🏥 SALUD ━━━\n"
        response += "• 'Voy a trabajar'\n"
        response += "• 'Voy a trabajar en oficina'\n"
        response += "• 'Cuánto tiempo llevo'\n"
        response += "• 'Próximo descanso'\n"
        response += "• 'Pausa trabajo'\n"
        response += "• 'Reanudar trabajo'\n"
        response += "• 'Terminar trabajo'\n\n"
        
        # Sistema
        response += "━━━ 💻 SISTEMA ━━━\n"
        response += "• 'Limpieza profunda'\n"
        response += "• 'Sube volumen' / 'Baja volumen'\n"
        response += "• 'Volumen al [número]'\n"
        response += "• 'Minimiza todo'\n"
        response += "• 'Lista procesos'\n"
        response += "• 'Apaga el sistema'\n"
        response += "• 'Captura pantalla'\n\n"
        
        # Productividad
        response += "━━━ 🧘 PRODUCTIVIDAD ━━━\n"
        response += "• 'Modo Zen'\n"
        response += "• 'Salir de modo zen'\n"
        response += "• 'Inicia pomodoro'\n\n"
        
        # DevOps
        response += "━━━ 👨‍💻 DEVOPS ━━━\n"
        response += "• 'Git status'\n"
        response += "• 'Subir cambios'\n"
        response += "• 'Inicializar git'\n\n"
        
        # Tiempo
        response += "━━━ ⏰ TIEMPO ━━━\n"
        response += "• 'Qué hora es'\n"
        response += "• 'Qué día es'\n"
        response += "• 'Dime la fecha'\n\n"
        
        response += "💡 Di 'comandos de [categoría]' para más detalles"
        return response
    
    @staticmethod
    def list_commands_by_category(categoria: str) -> str:
        """Lista comandos de una categoría específica con ejemplos"""
        if categoria not in SaraKnowledge.CAPACIDADES:
            return "❌ Categoría no encontrada"
        
        info = SaraKnowledge.CAPACIDADES[categoria]
        response = f"📌 {info['descripcion'].upper()}\n\n"
        response += "Comandos disponibles:\n"
        
        for i, cmd in enumerate(info['comandos'], 1):
            response += f"{i}. \"{cmd}\"\n"
        
        response += f"\nFunciones:\n"
        for func in info['funciones']:
            response += f"• {func}\n"
        
        return response


# Singleton para acceso global
_knowledge_instance = None

def obtener_knowledge():
    """Obtiene la instancia del knowledge base"""
    global _knowledge_instance
    if _knowledge_instance is None:
        _knowledge_instance = SaraKnowledge()
    return _knowledge_instance
