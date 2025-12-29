"""
NetworkGuardian - Comandos de Voz para SARA
Integración de NetworkGuardian con el sistema de comandos de SARA.
"""

# Este archivo contiene los comandos de voz que se deben agregar a brain.py

NETWORK_GUARDIAN_COMMANDS = {
    # Vigilancia
    "activar vigilancia": "guardian.iniciar_vigilancia()",
    "desactivar vigilancia": "guardian.detener_vigilancia()",
    "pausar vigilancia": "guardian.pausar_vigilancia()",
    "reanudar vigilancia": "guardian.reanudar_vigilancia()",
    "estado de vigilancia": "guardian.estado_vigilancia()",
    "estado de la red": "guardian.estado_vigilancia()",
    
    # Dispositivos
    "listar dispositivos": "guardian.listar_dispositivos()",
    "dispositivos activos": "guardian.listar_dispositivos(solo_activos=True)",
    "todos los dispositivos": "guardian.listar_dispositivos(solo_activos=False)",
    "quién está en mi red": "guardian.listar_dispositivos()",
    
    # Seguridad
    "modo fortaleza": "guardian.modo_fortaleza(activar=True)",
    "desactivar fortaleza": "guardian.modo_fortaleza(activar=False)",
    "alertas pendientes": "guardian.obtener_alertas_pendientes()",
    "mostrar alertas": "guardian.obtener_alertas_pendientes()",
    
    # Tráfico
    "analizar tráfico": "guardian.analizar_trafico()",
    "top consumidores": "guardian.top_consumidores()",
    "conexiones activas": "guardian.conexiones_activas()",
    "uso de red": "guardian.traffic.obtener_reporte_red_formateado()",
    
    # Reportes
    "reporte de red": "guardian.generar_reporte_completo()",
    "reporte completo": "guardian.generar_reporte_completo()",
    
    # Configuración
    "habilitar alertas de voz": "guardian.habilitar_alertas_voz(True)",
    "deshabilitar alertas de voz": "guardian.habilitar_alertas_voz(False)",
    
    # Dashboard
    "abrir dashboard": "guardian.abrir_dashboard()",
    "mostrar dashboard": "guardian.abrir_dashboard()",
    "dashboard de red": "guardian.abrir_dashboard()",
    
    # ===== COMANDOS CON IA =====
    "explicar alertas": "guardian.explicar_alertas_con_ia()",
    "explica las alertas": "guardian.explicar_alertas_con_ia()",
}

# Comandos con parámetros (requieren procesamiento especial)
PARAMETRIC_COMMANDS = {
    "confiar en": "guardian.confiar_dispositivo(ip_o_mac)",
    "confía en": "guardian.confiar_dispositivo(ip_o_mac)",
    "marcar sospechoso": "guardian.marcar_sospechoso(ip_o_mac)",
    "renombrar dispositivo": "guardian.renombrar_dispositivo(ip_o_mac, nuevo_nombre)",
    "escanear cada": "guardian.configurar_intervalo_escaneo(segundos)",
    
    # ===== COMANDOS CON IA =====
    "analizar dispositivo": "guardian.analizar_dispositivo_inteligente(ip_o_mac)",
    "analiza el dispositivo": "guardian.analizar_dispositivo_inteligente(ip_o_mac)",
    "qué hago con": "guardian.recomendar_accion(situacion)",
    "recomienda qué hacer": "guardian.recomendar_accion(situacion)",
}

# Ejemplos de uso para documentación
EJEMPLOS_USO = """
🛡️ NETWORKGUARDIAN - COMANDOS DE VOZ

═══════════════════════════════════════════════════════════

📊 VIGILANCIA
  • "SARA, activar vigilancia"
  • "SARA, estado de vigilancia"
  • "SARA, pausar vigilancia"
  • "SARA, reanudar vigilancia"

📱 DISPOSITIVOS
  • "SARA, quién está en mi red"
  • "SARA, listar dispositivos"
  • "SARA, dispositivos activos"
  • "SARA, confía en 192.168.1.105"
  • "SARA, renombrar dispositivo 192.168.1.105 a Laptop de Juan"

🔒 SEGURIDAD
  • "SARA, modo fortaleza"
  • "SARA, alertas pendientes"
  • "SARA, marcar sospechoso 192.168.1.200"

📊 ANÁLISIS DE TRÁFICO
  • "SARA, analizar tráfico"
  • "SARA, top consumidores"
  • "SARA, conexiones activas"
  • "SARA, uso de red"

📄 REPORTES
  • "SARA, reporte de red"
  • "SARA, reporte completo"

⚙️ CONFIGURACIÓN
  • "SARA, habilitar alertas de voz"
  • "SARA, escanear cada 30 segundos"

═══════════════════════════════════════════════════════════
"""

def procesar_comando_guardian(comando: str, guardian_instance):
    """
    Procesa comandos de NetworkGuardian desde SARA.
    
    Args:
        comando: Comando de voz del usuario (en minúsculas)
        guardian_instance: Instancia de NetworkGuardian
        
    Returns:
        (respuesta, origen) o None si no es un comando de guardian
    """
    import re
    import time
    
    cmd = comando.lower().strip()
    
    # ===== DETECCIÓN AUTOMÁTICA DE COMANDOS DE RED =====
    # Si el usuario menciona red/wifi/panel, abrir dashboard automáticamente
    palabras_clave_dashboard = [
        "panel de wifi", "panel wifi", "panel de red", "panel red",
        "ver red", "ver wifi", "mostrar red", "mostrar wifi",
        "control de red", "gestión de red", "administrar red"
    ]
    
    for palabra in palabras_clave_dashboard:
        if palabra in cmd:
            # Abrir dashboard automáticamente
            try:
                guardian_instance.abrir_dashboard()
                return "🛡️ Dashboard de red abierto. Aquí puedes ver todos los dispositivos y controlar la seguridad.", "guardian"
            except Exception as e:
                return f"❌ Error abriendo dashboard: {e}", "error"
    
    # ===== INICIAR VIGILANCIA AUTOMÁTICAMENTE SI NO ESTÁ ACTIVA =====
    # Si el usuario pregunta sobre dispositivos y la vigilancia no está activa, activarla
    if any(x in cmd for x in ["quién está", "dispositivos", "cuántos dispositivos", "ver dispositivos"]):
        if not guardian_instance.monitor.esta_activo():
            guardian_instance.iniciar_vigilancia()
            # Esperar un momento para que escanee
            time.sleep(2)
    
    # Comandos simples (sin parámetros)
    for patron, accion in NETWORK_GUARDIAN_COMMANDS.items():
        if patron in cmd:
            try:
                # Ejecutar comando
                resultado = eval(accion, {"guardian": guardian_instance})
                
                # Si es un comando de listar dispositivos, también abrir dashboard
                if "listar_dispositivos" in accion and "dashboard" not in cmd:
                    try:
                        guardian_instance.abrir_dashboard()
                    except:
                        pass  # No fallar si no se puede abrir
                
                return resultado, "guardian"
            except Exception as e:
                return f"❌ Error ejecutando comando: {e}", "error"
    
    # Comandos con parámetros
    
    # Confiar en dispositivo
    if "confía en" in cmd or "confiar en" in cmd:
        # Extraer IP o MAC
        ip_match = re.search(r'\d+\.\d+\.\d+\.\d+', cmd)
        if ip_match:
            ip = ip_match.group(0)
            return guardian_instance.confiar_dispositivo(ip), "guardian"
        return "❌ No encontré una IP válida. Ejemplo: 'confía en 192.168.1.105'", "error"
    
    # Marcar sospechoso
    if "marcar sospechoso" in cmd or "marca sospechoso" in cmd:
        ip_match = re.search(r'\d+\.\d+\.\d+\.\d+', cmd)
        if ip_match:
            ip = ip_match.group(0)
            return guardian_instance.marcar_sospechoso(ip), "guardian"
        return "❌ No encontré una IP válida", "error"
    
    # Renombrar dispositivo
    if "renombrar dispositivo" in cmd or "renombra dispositivo" in cmd:
        # Buscar patrón: "renombrar dispositivo [IP] a [nombre]"
        match = re.search(r'renombr(?:ar|a) dispositivo (\d+\.\d+\.\d+\.\d+) a (.+)', cmd)
        if match:
            ip = match.group(1)
            nombre = match.group(2).strip()
            return guardian_instance.renombrar_dispositivo(ip, nombre), "guardian"
        return "❌ Formato: 'renombrar dispositivo 192.168.1.105 a Laptop de Juan'", "error"
    
    # Configurar intervalo
    if "escanear cada" in cmd:
        # Buscar número
        match = re.search(r'(\d+)\s*segundo', cmd)
        if match:
            segundos = int(match.group(1))
            return guardian_instance.configurar_intervalo_escaneo(segundos), "guardian"
        return "❌ Formato: 'escanear cada 30 segundos'", "error"
    
    # ===== COMANDOS CON IA =====
    
    # Analizar dispositivo con IA
    if "analizar dispositivo" in cmd or "analiza el dispositivo" in cmd or "analiza dispositivo" in cmd:
        ip_match = re.search(r'\d+\.\d+\.\d+\.\d+', cmd)
        if ip_match:
            ip = ip_match.group(0)
            return guardian_instance.analizar_dispositivo_inteligente(ip), "guardian"
        return "❌ No encontré una IP válida. Ejemplo: 'analizar dispositivo 192.168.1.105'", "error"
    
    # Recomendar acción con IA
    if "qué hago con" in cmd or "recomienda qué hacer" in cmd or "qué debo hacer" in cmd:
        # Extraer contexto después de "con" o "hacer"
        
        if "qué hago con" in cmd:
            contexto = cmd.split("qué hago con")[1].strip()
        elif "qué debo hacer" in cmd:
            contexto = cmd.split("qué debo hacer")[1].strip() if "con" in cmd else "la situación actual"
        else:
            contexto = "la situación actual de la red"
        
        if contexto:
            return guardian_instance.recomendar_accion(contexto), "guardian"
        return "❌ Especifica la situación. Ejemplo: 'qué hago con dispositivo sospechoso'", "error"
    
    # No es un comando de guardian
    return None
