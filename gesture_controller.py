"""
🎮 SARA - Gesture Controller (FINAL PRODUCTION VERSION)
=======================================================
Control de gestos optimizado con:
- Frame Skipping (33% uso de CPU)
- Debounce (Anti-rebote)
- Detección estricta para evitar falsos positivos
- Modo Headless (sin ventana) opcional

Autor: SARA Team
Fecha: 2025-12-30
"""

import cv2
import mediapipe as mp
import threading
import time
import logging
import numpy as np
import os

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GESTURE")

class GestureController:
    """Controlador de gestos eficiente usando MediaPipe."""
    
    def __init__(self, brain_ref=None, callback=None, show_camera=True):
        """
        Args:
            brain_ref: Objeto 'Brain' o 'Kernel' que tenga método .procesar_comando()
            callback: Función opcional para imprimir en UI (ej: print)
            show_camera: Si es True, muestra ventana de debug con video.
        """
        self.brain = brain_ref
        self.callback = callback
        self.show_camera = show_camera
        
        # --- CONFIGURACIÓN OPTIMIZADA DE MEDIAPIPE ---
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,       # Modo video (más rápido)
            max_num_hands=1,               # Solo 1 mano para ahorrar CPU
            min_detection_confidence=0.6,  # Evita detectar "fantasmas"
            min_tracking_confidence=0.5,
            model_complexity=0             # 0 = Lite (Rápido), 1 = Full (Preciso)
        )
        
        self.running = False
        self.camera = None
        
        # --- VARIABLES DE CONTROL TEMPORAL (DEBOUNCE) ---
        self.last_gesture = None
        self.gesture_start_time = 0
        self.confirmation_time = 0.5   # Tiempo (s) para confirmar gesto
        self.cooldown_time = 1.5       # Tiempo (s) de espera tras ejecutar comando
        self.last_command_time = 0

        # --- MAPEO DE GESTOS ---
        # Clave: Gesto detectado -> Valor: (Texto para el Brain, Texto para UI)
        self.gesture_commands = {
            "thumbs_up":   ("sube el volumen", "🔊 Subir Volumen"),
            "thumbs_down": ("baja el volumen", "🔉 Bajar Volumen"),
            "open_hand":   ("pausa", "⏸️ Pausa/Play"),
            "victory":     ("siguiente canción", "⏭️ Siguiente"),
            "fist":        ("silencio", "🔇 Mute"),
            "ok":          ("sara", "🎯 Activar SARA")
        }

    def start(self):
        """Inicia el hilo de detección."""
        if self.running: return
        self.running = True
        threading.Thread(target=self._gesture_loop, daemon=True).start()
        logger.info("✅ Servicio de Gestos Iniciado")

    def stop(self):
        """Detiene la detección y libera la cámara."""
        self.running = False
        time.sleep(0.5) # Dar tiempo al hilo para cerrar
        if self.camera: self.camera.release()
        cv2.destroyAllWindows()
        logger.info("🛑 Servicio de Gestos Detenido")

    def _gesture_loop(self):
        """Bucle principal de visión por computadora."""
        # Selección inteligente de backend de cámara
        backend = cv2.CAP_DSHOW if os.name == 'nt' else cv2.CAP_ANY
        self.camera = cv2.VideoCapture(0, backend)
        
        if not self.camera.isOpened():
            logger.error("❌ No se detectó cámara web.")
            self.running = False
            return

        # Resolución baja para velocidad (suficiente para manos)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        frame_count = 0 
        
        while self.running:
            ret, frame = self.camera.read()
            if not ret: continue

            # --- OPTIMIZACIÓN: FRAME SKIPPING ---
            # Solo procesamos IA 1 de cada 3 frames.
            # Los otros 2 solo se muestran (si show_camera=True).
            process_ai = (frame_count % 3 == 0)
            frame_count += 1

            # Efecto espejo
            frame = cv2.flip(frame, 1)
            
            # Copia para dibujar debug
            debug_frame = frame.copy() if self.show_camera else None
            
            gesture_detected = None

            if process_ai:
                # Convertir a RGB (MediaPipe lo requiere)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb_frame.flags.writeable = False # Mejora velocidad
                
                results = self.hands.process(rgb_frame)
                
                if results.multi_hand_landmarks:
                    for landmarks in results.multi_hand_landmarks:
                        # Dibujar si es necesario
                        if self.show_camera:
                            self.mp_drawing.draw_landmarks(
                                debug_frame, landmarks, self.mp_hands.HAND_CONNECTIONS)
                        
                        # Clasificar Gesto
                        gesture_detected = self._classify_gesture(landmarks)
                
                # Lógica de disparo
                if gesture_detected:
                    self._process_gesture_trigger(gesture_detected)
                else:
                    self.last_gesture = None # Reset si no hay mano o gesto claro

            # --- VISUALIZACIÓN ---
            if self.show_camera and debug_frame is not None:
                # Mostrar estado
                status_color = (0, 255, 0) if self.last_gesture else (0, 0, 255)
                text = f"Gesto: {self.last_gesture if self.last_gesture else '...'}"
                
                # Feedback visual en pantalla
                cv2.rectangle(debug_frame, (0,0), (640, 40), (0,0,0), -1)
                cv2.putText(debug_frame, text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
                
                cv2.imshow("SARA Vision (ESC para salir)", debug_frame)
                
                if cv2.waitKey(1) & 0xFF == 27: # ESC
                    self.stop()
                    break

    def _classify_gesture(self, lm):
        """
        Matemáticas para identificar la pose de la mano.
        lm: Landmarks de MediaPipe
        """
        # Índices de puntas y bases de dedos
        tips = [4, 8, 12, 16, 20] 
        bases = [2, 5, 9, 13, 17]
        
        fingers = []
        
        # 1. Pulgar (Eje X - Horizontal)
        # Si la punta está más lejos del centro que la base
        if lm.landmark[tips[0]].x < lm.landmark[tips[1]].x:
             fingers.append(1)
        else:
             fingers.append(0)

        # 2. Otros 4 dedos (Eje Y - Vertical)
        for i in range(1, 5):
            # En visión por computador, Y=0 es arriba.
            # Por tanto, si punta < base, el dedo está ARRIBA.
            if lm.landmark[tips[i]].y < lm.landmark[bases[i]].y:
                fingers.append(1)
            else:
                fingers.append(0)
        
        total_fingers = sum(fingers)

        # --- REGLAS DE CLASIFICACIÓN ---
        
        # Puño (0 dedos)
        if total_fingers == 0:
            return "fist"
        
        # Mano Abierta (5 dedos)
        if total_fingers == 5:
            return "open_hand"
        
        # Victoria (Indice y Medio arriba, los demás abajo)
        if fingers[1] and fingers[2] and not fingers[3] and not fingers[4]:
            return "victory"
        
        # OK (Pulgar e Indice tocándose)
        # Distancia euclidiana entre punta pulgar(4) y punta indice(8)
        thumb_tip = np.array([lm.landmark[4].x, lm.landmark[4].y])
        index_tip = np.array([lm.landmark[8].x, lm.landmark[8].y])
        dist_ok = np.linalg.norm(thumb_tip - index_tip)
        
        if dist_ok < 0.05 and fingers[2] and fingers[3]: 
            return "ok"

        # Pulgar Arriba/Abajo (Solo pulgar extendido)
        if fingers[0] and total_fingers == 1:
            # Verificar orientación vertical del pulgar
            # Punta(4) vs Base(2)
            if lm.landmark[4].y < lm.landmark[2].y:
                return "thumbs_up"
            else:
                return "thumbs_down"
        
        return None  # No se reconoce el gesto

    def _process_gesture_trigger(self, gesture):
        """
        Sistema de Debounce: Solo ejecuta si el gesto se mantiene estable.
        """
        current_time = time.time()
        
        # Si es un gesto nuevo
        if gesture != self.last_gesture:
            self.last_gesture = gesture
            self.gesture_start_time = current_time
            return
        
        # Si es el mismo gesto, verificar tiempo de confirmación
        time_held = current_time - self.gesture_start_time
        
        # Requiere mantener el gesto 0.5s
        if time_held >= self.confirmation_time:
            # Verificar cooldown (no ejecutar si ya se ejecutó recientemente)
            if (current_time - self.last_command_time) < self.cooldown_time:
                return
            
            # Ejecutar comando
            if gesture in self.gesture_commands:
                command, description = self.gesture_commands[gesture]
                
                logger.info(f"🎮 Gesto: {gesture} -> {description}")
                
                # Callback a UI
                if self.callback:
                    self.callback(f"Gesto: {description}")
                
                # Enviar comando al cerebro
                if self.brain:
                    try:
                        self.brain.procesar(command)
                    except Exception as e:
                        logger.error(f"Error ejecutando comando: {e}")
                
                # Actualizar tiempo de último comando
                self.last_command_time = current_time


# Función helper para brain.py
def crear_gesture_controller(brain_ref, callback=None, show_camera=True):
    """Factory function para crear el controlador."""
    try:
        return GestureController(brain_ref, callback, show_camera)
    except Exception as e:
        logger.error(f"Error creando GestureController: {e}")
        return None


if __name__ == "__main__":
    # Test básico
    print("🎮 Testing GestureController...")
    print("Presiona ESC en la ventana para salir")
    
    class MockBrain:
        def procesar(self, cmd):
            print(f"📝 Comando recibido: {cmd}")
    
    controller = GestureController(MockBrain(), show_camera=True)
    controller.start()
    
    try:
        while controller.running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        controller.stop()
        print("\n✅ Test finalizado")