"""
🎤 SARA - Neural Voice Engine (FINAL PRODUCTION VERSION)
========================================================
Motor de voz optimizado con:
- Event Loop Fix (sin crashes en threads)
- File Lock Fix (limpieza correcta en Windows)
- Latency Fix (24kHz nativo, sin resampling)
- Fast Stop (interrupción inmediata)

Autor: SARA Team
Fecha: 2025-12-30
"""

import os
import threading
import pygame
import asyncio
import edge_tts
import logging
import re
import uuid
import queue
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor

# --- Configuración (Ahora dinámicas) ---
# Variables globales (pueden cambiar en runtime)
VOIZ_NEURAL = "es-ES-ElviraNeural" 
VOICE_RATE = "+10%"      # Velocidad
VOICE_VOLUME = "+0%"     # Volumen
PYGAME_CLOCK_TICK = 20   # Ticks del reloj (ms)
MAX_WORKERS = 3          # Hilos para generación simultánea

class NeuralVoiceEngine:
    def __init__(self):
        # OPTIMIZACIÓN CRÍTICA: 
        # Edge-TTS genera audio a 24kHz. Iniciamos Pygame a la misma frecuencia 
        # para evitar que la CPU pierda tiempo haciendo resampling interno.
        try:
            pygame.mixer.quit() # Asegurar limpieza previa
            pygame.mixer.init(frequency=24000, size=-16, channels=1, buffer=1024)
        except Exception as e:
            logging.error(f"Error iniciando mixer: {e}")
            
        self.cola_audio = queue.Queue()
        self.stop_event = threading.Event()
        self.is_speaking = False
        
        # 🚀 MEJORA 1: Sistema de Caché Inteligente
        self.cache_dir = os.path.join(os.getcwd(), "sara_voice_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        logging.info(f"📁 Caché de voz: {self.cache_dir}")
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        
        # Limpieza inicial de archivos basura
        self._limpiar_temporales()

    def _limpiar_temporales(self):
        """Elimina archivos de audio viejos al inicio para no llenar el disco."""
        try:
            for file in os.listdir():
                if file.startswith("tts_") and file.endswith(".mp3"):
                    try:
                        os.remove(file)
                    except: pass
        except Exception as e:
            logging.error(f"Error limpieza inicial: {e}")

    def _limpiar_texto(self, texto):
        """Limpia y normaliza el texto para mejorar la pronunciación."""
        if not texto: return ""
        
        reemplazos = {
            "►": "", "↑": " subida ", "↓": " bajada ", "@": " arroba ", "%": " por ciento ",
            "GB": " Gigas ", "MB": " Megas ", "GHz": " Gigahertz ", "MHz": " Megahertz ",
            "✅": "", "❌": "", "⚠️": "", "💡": "", "📂": "", "🔴": "", "🟢": "",
            "\n": " " # Eliminar saltos de línea para no cortar frases
        }
        
        for k, v in reemplazos.items(): 
            texto = texto.replace(k, v)
        
        # Regex permitiendo caracteres latinos extendidos (áéíóúñÜ¿¡)
        # Se eliminan símbolos raros que la IA podría intentar leer literalmente
        texto_limpio = re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s,.\¿\?¡\!\-\(\)\"\']', '', texto)
        
        # Eliminar espacios dobles resultantes
        return re.sub(r'\s+', ' ', texto_limpio).strip()

    def _get_cache_filename(self, texto):
        """🚀 MEJORA 1: Genera nombre único para caché basado en texto + config."""
        unique_str = f"{texto}_{VOIZ_NEURAL}_{VOICE_RATE}"
        hash_name = hashlib.md5(unique_str.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{hash_name}.mp3")

    def _generar_chunk_sync(self, texto, filename):
        """
        Wrapper síncrono para ejecutar la corutina async de edge-tts.
        Se ejecuta dentro de un hilo del ThreadPoolExecutor.
        """
        try:
            # Creamos un nuevo loop para este hilo si es necesario
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            communicate = edge_tts.Communicate(
                texto, 
                VOIZ_NEURAL, 
                rate=VOICE_RATE, 
                volume=VOICE_VOLUME
            )
            
            # Ejecutamos la corutina hasta completarse
            loop.run_until_complete(communicate.save(filename))
            loop.close()
            return True
        except Exception as e:
            logging.error(f"⚠️ Error Edge-TTS: {e}. Intentando modo Offline...")
            return self._fallback_offline(texto, filename)

    def _fallback_offline(self, texto, filename):
        """🚀 MEJORA 3: Fallback offline usando pyttsx3 si falla internet."""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.save_to_file(texto, filename)
            engine.runAndWait()
            logging.info("✅ Audio generado en modo offline")
            return True
        except Exception as e:
            logging.error(f"❌ Fallback offline también falló: {e}")
            return False

    def hablar(self, texto):
        """Punto de entrada principal. Gestiona la interrupción y nueva cola."""
        if not texto: return
        
        # 1. Detener lo que se esté diciendo ahora mismo (Interrupt)
        self.detener()
        self.stop_event.clear()
        
        # 2. Limpiar cola de archivos pendientes anteriores
        with self.cola_audio.mutex:
            self.cola_audio.queue.clear()
        
        self.is_speaking = True
        texto_limpio = self._limpiar_texto(texto)
        
        # 3. Lanzar hilos de Producción (TTS) y Consumo (Play)
        t_gen = threading.Thread(
            target=self._hilo_productor_paralelo, 
            args=(texto_limpio,), 
            daemon=True
        )
        t_play = threading.Thread(
            target=self._hilo_consumidor, 
            daemon=True
        )
        t_gen.start()
        t_play.start()

    def _hilo_productor_paralelo(self, texto_completo):
        """
        Estrategia de Streaming:
        1. Genera la primera frase YA y la envía a reproducir.
        2. Manda el resto a generar en segundo plano mientras suena la primera.
        Esto reduce la latencia percibida a casi cero.
        """
        # Dividir por signos de puntuación fuertes (. ! ?)
        frases = re.split(r'(?<=[.!?])\s+', texto_completo)
        frases = [f.strip() for f in frases if f.strip()]
        
        if not frases:
            self.cola_audio.put(None)
            return
        
        # --- FASE 1: Generación Inmediata (Latencia mínima) ---
        primera_frase = frases[0]
        
        # 🚀 MEJORA 1: Revisar Caché antes de generar
        cache_file = self._get_cache_filename(primera_frase)
        
        if os.path.exists(cache_file):
            # Si existe en caché, latencia = 0ms
            logging.debug(f"⚡ Cache HIT: {primera_frase[:30]}...")
            self.cola_audio.put(cache_file)
        else:
            # Si no existe, generar y guardar en caché
            if self._generar_chunk_sync(primera_frase, cache_file):
                self.cola_audio.put(cache_file)
        
        if self.stop_event.is_set(): return

        # --- FASE 2: Generación en Paralelo (Batch) ---
        if len(frases) > 1:
            futures_map = {}
            orden_futures = [] 

            # Lanzar tareas al pool
            for frase in frases[1:]:
                if self.stop_event.is_set(): break
                
                # 🚀 MEJORA 1: Usar caché para cada frase
                cache_file = self._get_cache_filename(frase)
                
                if os.path.exists(cache_file):
                    # Ya existe, agregar directo a la cola
                    self.cola_audio.put(cache_file)
                else:
                    # No existe, generar en paralelo
                    future = self.executor.submit(self._generar_chunk_sync, frase, cache_file)
                    futures_map[future] = cache_file
                    orden_futures.append(future)
            
            # Recoger resultados EN ORDEN para mantener coherencia del habla
            for future in orden_futures:
                if self.stop_event.is_set(): break
                try:
                    # Esperamos el resultado (el audio se genera mientras suena el anterior)
                    if future.result(timeout=20): 
                        filename = futures_map[future]
                        self.cola_audio.put(filename)
                except Exception as e:
                    logging.error(f"Error esperando futuro TTS: {e}")
        
        self.cola_audio.put(None) # Señal de fin de transmisión

    def _hilo_consumidor(self):
        """Consume la cola y reproduce los audios secuencialmente."""
        while not self.stop_event.is_set():
            try:
                # Timeout corto para revisar stop_event frecuentemente
                filename = self.cola_audio.get(timeout=0.2)
                
                if filename is None: # Señal de fin recibida
                    break
                
                # --- Reproducción ---
                if os.path.exists(filename):
                    try:
                        pygame.mixer.music.load(filename)
                        pygame.mixer.music.play()
                        
                        while pygame.mixer.music.get_busy() and not self.stop_event.is_set():
                            pygame.time.Clock().tick(PYGAME_CLOCK_TICK)
                            
                        # CRÍTICO: Descargar archivo para liberar el lock de Windows
                        pygame.mixer.music.unload()
                    except Exception as e:
                        logging.error(f"Error reproduciendo {filename}: {e}")
                    
                    # 🚀 MEJORA 1: Solo borrar si NO está en caché
                    if self.cache_dir not in os.path.abspath(filename):
                        self._safe_remove(filename)
                
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Error fatal en consumidor: {e}")
                break
        
        self.is_speaking = False

    def _safe_remove(self, path):
        """Intenta borrar archivo manejando el 'File in use' de Windows."""
        if not path or not os.path.exists(path): return
        
        for _ in range(10): # Aumentado a 10 intentos
            try:
                os.remove(path)
                break
            except PermissionError:
                time.sleep(0.1)
            except Exception:
                break

    def detener(self):
        """Fuerza la detención del habla."""
        self.stop_event.set()
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
        except: pass
        self.is_speaking = False

    def cambiar_voz(self, nueva_voz="es-MX-DaliaNeural", velocidad="+0%"):
        """🚀 MEJORA 2: Cambiar voz en tiempo real sin reiniciar.
        
        Voces disponibles:
        - es-ES-ElviraNeural (Española, seria)
        - es-MX-DaliaNeural (Mexicana, suave)
        - es-MX-JorgeNeural (Mexicano, hombre)
        - es-AR-ElenaNeural (Argentina)
        """
        global VOIZ_NEURAL, VOICE_RATE
        VOIZ_NEURAL = nueva_voz
        VOICE_RATE = velocidad
        logging.info(f"🔄 Voz cambiada a: {nueva_voz} (velocidad: {velocidad})")
        return f"Voz cambiada a {nueva_voz}"

    def __del__(self):
        self.detener()
        self.executor.shutdown(wait=False)
        pygame.mixer.quit()