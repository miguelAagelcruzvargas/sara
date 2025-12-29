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
from concurrent.futures import ThreadPoolExecutor

# Constantes de configuración de voz OPTIMIZADAS
VOIZ_NEURAL = "es-ES-ElviraNeural" 
VOICE_RATE = "+10%"  # ⚡ Balance entre velocidad y claridad
VOICE_VOLUME = "+0%"
PYGAME_CLOCK_TICK = 20  # ⚡ Más responsivo (antes 10)
MAX_WORKERS = 3  # ⚡ Generación paralela

class NeuralVoiceEngine:
    def __init__(self):
        # OPTIMIZACIÓN: 24kHz Mono (Nativo Edge-TTS) para evitar resampling y overhead
        # Buffer 1024 para evitar crackling pero mantener baja latencia
        pygame.mixer.init(frequency=24000, size=-16, channels=1, buffer=1024)
        self.cola_audio = queue.Queue()
        self.stop_event = threading.Event()
        self.is_speaking = False
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        
        # Limpiar basura anterior
        self._limpiar_temporales()

    def _limpiar_temporales(self):
        """Elimina archivos de audio viejos al inicio"""
        try:
            for file in os.listdir():
                if file.startswith("tts_") and file.endswith(".mp3"):
                    try:
                        os.remove(file)
                    except: pass
        except Exception as e:
            logging.error(f"Error limpieza: {e}")

    def _limpiar_texto(self, texto):
        """Prepara el texto para ser leído naturalmente."""
        reemplazos = {
            "►": "", "↑": " subida ", "↓": " bajada ", "@": " a ", "%": " por ciento ",
            "GB": " Gigas ", "MB": " Megas ", "Mhz": " Megahertz ",
            "✅": "", "❌": "", "⚠": "", "💡": "", "📂": "", "🔴": "", "🟢": ""
        }
        for k, v in reemplazos.items(): 
            texto = texto.replace(k, v)
        
        # Limpiar caracteres especiales manteniendo acentos y puntuación útil
        # Permitimos: Letras (incluidos acentos), Números, y signos de puntuación básicos
        texto_limpio = re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s,.\¿\?¡\!\-\(\)\"\']', '', texto)
        return re.sub(r'\s+', ' ', texto_limpio).strip()

    async def _generar_chunk_async(self, texto, filename):
        """Genera audio de forma asíncrona"""
        try:
            communicate = edge_tts.Communicate(
                texto, 
                VOIZ_NEURAL, 
                rate=VOICE_RATE,
                volume=VOICE_VOLUME
            )
            await communicate.save(filename)
            return True
        except Exception as e:
            logging.error(f"Error TTS: {e}")
            return False

    def _generar_chunk_sync(self, texto, filename):
        """Wrapper síncrono para generación"""
        try:
            communicate = edge_tts.Communicate(
                texto, 
                VOIZ_NEURAL, 
                rate=VOICE_RATE,
                volume=VOICE_VOLUME
            )
            # Solución: Usar asyncio.run que maneja el loop correctamente en threads
            asyncio.run(communicate.save(filename))
            return True
        except Exception as e:
            logging.error(f"Error TTS sync: {e}")
            return False
        except Exception as e:
            logging.error(f"Error TTS sync: {e}")
            return False

    def hablar(self, texto):
        """Habla el texto con latencia mínima"""
        if not texto: 
            return
        
        # Detener audio anterior inmediatamente
        self.stop_event.set()
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        
        # Limpiar cola
        while not self.cola_audio.empty():
            try:
                filename = self.cola_audio.get_nowait()
                if filename:
                    self._safe_remove(filename)
            except queue.Empty:
                break

        self.stop_event.clear()
        self.is_speaking = True

        texto_limpio = self._limpiar_texto(texto)
        
        # ⚡ Iniciar pipeline optimizado
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
        """Genera audio en paralelo para múltiples frases"""
        # Dividir en frases más pequeñas para inicio más rápido
        frases = re.split(r'(?<=[.!?])\s+', texto_completo)
        
        # Filtrar frases vacías
        frases = [f.strip() for f in frases if f.strip()]
        
        if not frases:
            self.cola_audio.put(None)
            return
        
        # ⚡ Generar primera frase inmediatamente (sin esperar)
        primera_frase = frases[0]
        filename_0 = f"tts_{uuid.uuid4().hex[:8]}.mp3"
        
        if self._generar_chunk_sync(primera_frase, filename_0):
            self.cola_audio.put(filename_0)
        
        # ⚡ Generar resto en paralelo (Optimizado con futures_map)
        if len(frases) > 1:
            futures_map = {}
            orden_futures = [] # Para mantener el orden de reproducción

            for frase in frases[1:]:
                if self.stop_event.is_set(): break
                
                filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
                future = self.executor.submit(self._generar_chunk_sync, frase, filename)
                
                futures_map[future] = filename
                orden_futures.append(future)
            
            # Recolectar resultados en ORDEN
            for future in orden_futures:
                if self.stop_event.is_set(): break
                try:
                    # Esperar a que este chunk específico esté listo
                    if future.result(timeout=15): 
                        filename = futures_map[future]
                        self.cola_audio.put(filename)
                except Exception as e:
                    logging.error(f"Error en futuro TTS: {e}")
        
        self.cola_audio.put(None)  # Señal de fin

    def _hilo_consumidor(self):
        """Reproduce audio de la cola"""
        while not self.stop_event.is_set():
            try:
                filename = self.cola_audio.get(timeout=0.5)
                
                if filename is None:  # Fin
                    break
                
                # Reproducir inmediatamente
                try:
                    pygame.mixer.music.load(filename)
                    pygame.mixer.music.play()
                    
                    # Esperar a que termine
                    while pygame.mixer.music.get_busy() and not self.stop_event.is_set():
                        pygame.time.Clock().tick(PYGAME_CLOCK_TICK)
                    
                    pygame.mixer.music.unload() # CRÍTICO: Liberar archivo para poder borrarlo en Windows
                except Exception as e:
                    logging.error(f"Error reproducción: {e}")
                
                # Limpiar archivo con reintentos (Fix Windows File Lock)
                self._safe_remove(filename)
                    
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Error consumidor: {e}")
        
        self.is_speaking = False

    def _safe_remove(self, path):
        """Intenta borrar un archivo con reintentos para evitar errores de bloqueo"""
        if not path or not os.path.exists(path): return
        
        for i in range(5): # 5 intentos
            try:
                os.remove(path)
                return
            except PermissionError:
                time.sleep(0.1) # Esperar un poco
            except Exception as e:
                logging.debug(f"Error borrando {path}: {e}")
                return

    def detener(self):
        """Detiene la reproducción inmediatamente"""
        self.stop_event.set()
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        self.is_speaking = False

    def esta_hablando(self):
        """Verifica si está hablando"""
        return self.is_speaking or pygame.mixer.music.get_busy()
    
    def __del__(self):
        """Limpieza al destruir"""
        self.detener()
        self.executor.shutdown(wait=False)
