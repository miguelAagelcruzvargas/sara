"""
NetworkGuardian - Integración con IA
Análisis inteligente de red usando IA para detección de amenazas y recomendaciones.
"""

import logging
from typing import Optional, Dict, List

class NetworkGuardianAI:
    """Módulo de IA para análisis inteligente de red."""
    
    def __init__(self, ia_callback: Optional[callable] = None):
        """
        Inicializa el módulo de IA.
        
        Args:
            ia_callback: Función para consultar IA (brain.consultar_ia)
        """
        self.ia_callback = ia_callback
        self.ia_disponible = ia_callback is not None
        
        logging.info(f"✓ NetworkGuardianAI inicializado (IA: {'disponible' if self.ia_disponible else 'no disponible'})")
    
    def analizar_dispositivo_con_ia(self, device_info: Dict) -> str:
        """
        Analiza un dispositivo usando IA para dar recomendaciones.
        
        Args:
            device_info: Información del dispositivo
            
        Returns:
            Análisis y recomendaciones
        """
        if not self.ia_disponible:
            return self._analisis_basico(device_info)
        
        try:
            # Preparar información para la IA
            mac = device_info.get('mac', 'N/A')
            ip = device_info.get('ip', 'N/A')
            hostname = device_info.get('hostname', 'Desconocido')
            device_type = device_info.get('device_type', 'Desconocido')
            manufacturer = device_info.get('manufacturer', 'Desconocido')
            trust_level = device_info.get('trust_level', 'unknown')
            puertos_abiertos = device_info.get('puertos_abiertos', [])
            os_probable = device_info.get('os_probable', 'Desconocido')
            
            prompt = f"""Analiza este dispositivo de red y dame recomendaciones de seguridad:

Dispositivo: {device_type}
Fabricante: {manufacturer}
IP: {ip}
MAC: {mac}
Hostname: {hostname}
OS Probable: {os_probable}
Puertos abiertos: {', '.join(puertos_abiertos) if puertos_abiertos else 'Ninguno detectado'}
Nivel de confianza actual: {trust_level}

Por favor:
1. Evalúa si este dispositivo parece legítimo o sospechoso
2. Recomienda nivel de confianza (trusted/unknown/suspicious)
3. Sugiere acciones de seguridad si es necesario
4. Sé conciso (máximo 3-4 líneas)"""

            respuesta, _ = self.ia_callback(prompt)
            return f"🤖 Análisis IA:\n{respuesta}"
            
        except Exception as e:
            logging.error(f"Error en análisis IA: {e}")
            return self._analisis_basico(device_info)
    
    def _analisis_basico(self, device_info: Dict) -> str:
        """Análisis básico sin IA."""
        device_type = device_info.get('device_type', 'Desconocido')
        trust_level = device_info.get('trust_level', 'unknown')
        puertos = device_info.get('puertos_abiertos', [])
        
        analisis = f"📊 Análisis Básico:\n"
        analisis += f"Tipo: {device_type}\n"
        analisis += f"Confianza: {trust_level}\n"
        
        if puertos:
            analisis += f"⚠️ Puertos abiertos detectados: {len(puertos)}\n"
            analisis += "Recomendación: Revisar si son servicios legítimos"
        else:
            analisis += "✅ No se detectaron puertos abiertos comunes"
        
        return analisis
    
    def detectar_amenaza_con_ia(self, evento: Dict) -> Optional[str]:
        """
        Analiza un evento de red con IA para detectar amenazas.
        
        Args:
            evento: Información del evento
            
        Returns:
            Descripción de amenaza o None
        """
        if not self.ia_disponible:
            return None
        
        try:
            event_type = evento.get('event_type', '')
            details = evento.get('details', '')
            ip = evento.get('ip', 'N/A')
            
            # Solo analizar eventos sospechosos
            eventos_sospechosos = ['arp_spoofing_detected', 'port_scan_detected', 
                                  'suspicious_activity', 'multiple_failed_connections']
            
            if event_type not in eventos_sospechosos:
                return None
            
            prompt = f"""Analiza este evento de seguridad de red:

Tipo: {event_type}
IP: {ip}
Detalles: {details}

¿Es una amenaza real o falso positivo? Responde en 2 líneas máximo."""

            respuesta, _ = self.ia_callback(prompt)
            return respuesta
            
        except Exception as e:
            logging.error(f"Error en detección IA: {e}")
            return None
    
    def recomendar_accion_con_ia(self, contexto: str) -> str:
        """
        Pide recomendaciones a la IA sobre qué hacer.
        
        Args:
            contexto: Descripción de la situación
            
        Returns:
            Recomendación de la IA
        """
        if not self.ia_disponible:
            return "💡 IA no disponible. Consulta la documentación de NetworkGuardian."
        
        try:
            prompt = f"""Como experto en seguridad de redes, recomienda qué hacer en esta situación:

{contexto}

Dame 2-3 acciones concretas que puedo tomar. Sé breve y directo."""

            respuesta, _ = self.ia_callback(prompt)
            return f"💡 Recomendación IA:\n{respuesta}"
            
        except Exception as e:
            logging.error(f"Error obteniendo recomendación: {e}")
            return "❌ Error consultando IA"
    
    def explicar_alerta_con_ia(self, alerta: Dict) -> str:
        """
        Explica una alerta en lenguaje simple usando IA.
        
        Args:
            alerta: Información de la alerta
            
        Returns:
            Explicación simple
        """
        if not self.ia_disponible:
            return alerta.get('message', 'Sin descripción')
        
        try:
            alert_type = alerta.get('alert_type', '')
            message = alerta.get('message', '')
            
            prompt = f"""Explica esta alerta de seguridad en lenguaje simple para un usuario no técnico:

Tipo: {alert_type}
Mensaje: {message}

Explica qué significa y si debe preocuparse. Máximo 2 líneas."""

            respuesta, _ = self.ia_callback(prompt)
            return respuesta
            
        except Exception as e:
            logging.error(f"Error explicando alerta: {e}")
            return message
    
    def generar_reporte_inteligente(self, estadisticas: Dict) -> str:
        """
        Genera un reporte con análisis inteligente de la IA.
        
        Args:
            estadisticas: Estadísticas de la red
            
        Returns:
            Reporte con análisis IA
        """
        if not self.ia_disponible:
            return "📊 Reporte básico disponible. Activa IA para análisis avanzado."
        
        try:
            total_devices = estadisticas.get('db', {}).get('total_devices', 0)
            active_devices = estadisticas.get('db', {}).get('active_devices', 0)
            blocked_devices = estadisticas.get('db', {}).get('blocked_devices', 0)
            pending_alerts = estadisticas.get('db', {}).get('pending_alerts', 0)
            
            velocidad_subida = estadisticas.get('traffic', {}).get('velocidad_subida_mbps', 0)
            velocidad_bajada = estadisticas.get('traffic', {}).get('velocidad_bajada_mbps', 0)
            
            prompt = f"""Analiza el estado de esta red y dame un resumen ejecutivo:

Dispositivos totales: {total_devices}
Dispositivos activos (24h): {active_devices}
Dispositivos bloqueados: {blocked_devices}
Alertas pendientes: {pending_alerts}
Velocidad subida: {velocidad_subida:.2f} Mbps
Velocidad bajada: {velocidad_bajada:.2f} Mbps

Dame:
1. Estado general (bueno/normal/preocupante)
2. Principal recomendación
3. Máximo 4 líneas"""

            respuesta, _ = self.ia_callback(prompt)
            return f"🤖 Análisis Inteligente:\n{respuesta}"
            
        except Exception as e:
            logging.error(f"Error generando reporte IA: {e}")
            return "❌ Error en análisis IA"
    
    def interpretar_comando_natural(self, comando: str) -> Optional[Dict]:
        """
        Interpreta comandos en lenguaje natural usando IA.
        
        Args:
            comando: Comando del usuario
            
        Returns:
            Dict con acción interpretada o None
        """
        if not self.ia_disponible:
            return None
        
        try:
            prompt = f"""El usuario dijo: "{comando}"

Si es un comando relacionado con seguridad de red, responde SOLO con JSON:
{{
  "accion": "listar_dispositivos|analizar_trafico|bloquear_dispositivo|confiar_dispositivo|otro",
  "parametros": {{"ip": "X.X.X.X"}} (si aplica),
  "confianza": 0-100
}}

Si NO es comando de red, responde: {{"accion": "ninguna"}}"""

            respuesta, _ = self.ia_callback(prompt)
            
            # Intentar parsear JSON
            import json
            import re
            
            # Extraer JSON de la respuesta
            json_match = re.search(r'\{.*\}', respuesta, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            return None
            
        except Exception as e:
            logging.error(f"Error interpretando comando: {e}")
            return None
