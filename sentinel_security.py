"""
Sentinel Security - Sistema avanzado de reconocimiento facial
Usa DeepFace (modelo VGG-Face) con OpenCV como respaldo
Optimizado para Windows
"""

import cv2
import os
import time
import pickle
import sqlite3
import datetime
import logging
import numpy as np
from typing import Optional, Tuple, List
from PIL import Image

# Intentar importar DeepFace
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
    logging.info("✅ DeepFace disponible - Usando reconocimiento avanzado")
except ImportError:
    DEEPFACE_AVAILABLE = False
    logging.warning("⚠️ DeepFace no disponible - Usando OpenCV básico")

class SentinelSecurity:
    """Sistema de seguridad con reconocimiento facial usando DeepFace + OpenCV."""
    
    def __init__(self, voice_callback: Optional[callable] = None):
        """
        Inicializa el sistema de seguridad.
        
        Args:
            voice_callback: Función para notificaciones de voz
        """
        self.voice_callback = voice_callback
        self.use_deepface = DEEPFACE_AVAILABLE
        
        # Directorios
        self.faces_dir = "faces_db"
        self.authorized_dir = os.path.join(self.faces_dir, "authorized")
        self.intrusions_dir = os.path.join("security_logs", "intrusions")
        
        # Crear directorios si no existen
        os.makedirs(self.authorized_dir, exist_ok=True)
        os.makedirs(self.intrusions_dir, exist_ok=True)
        
        # Base de datos
        self.db_path = os.path.join("security_logs", "sentinel_security.db")
        self._init_database()
        
        # Cargar clasificador Haar Cascade para detección de rostros
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Cargar rostros autorizados
        self.authorized_users = {}  # {nombre: directorio_fotos}
        self._load_authorized_faces()
        
        # Si no hay DeepFace, usar reconocedor OpenCV
        if not self.use_deepface:
            try:
                if hasattr(cv2, 'face'):
                    self.recognizer = cv2.face.LBPHFaceRecognizer_create()
                else:
                    logging.warning("⚠️ Módulo cv2.face no encontrado. Funciones de reconocimiento OpenCV limitadas.")
                    print("\n⏳ NOTA: Las dependencias de seguridad (opencv-contrib) se están instalando en segundo plano.")
                    print("   Por favor espera unos minutos y reinicia SARA si ves este error.\n")
                    self.recognizer = None
            except AttributeError:
                logging.error("❌ Error accediendo a cv2.face.")
                self.recognizer = None
                
            self.authorized_faces = []
            self.authorized_names = []
            if self.recognizer:
                self._load_opencv_faces()
                self._train_recognizer()
        
        mode = "DeepFace (VGG-Face)" if self.use_deepface else "OpenCV (LBPH)"
        logging.info(f"✅ SentinelSecurity inicializado - Modo: {mode}")
    
    def _init_database(self):
        """Inicializa la base de datos SQLite."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de intentos de acceso
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN,
                face_recognized BOOLEAN,
                person_name TEXT,
                photo_path TEXT,
                unlock_method TEXT,
                confidence REAL,
                notes TEXT
            )
        ''')
        
        # Tabla de rostros autorizados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authorized_faces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                photos_dir TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_used DATETIME,
                photo_count INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_authorized_faces(self):
        """Carga los rostros autorizados desde la base de datos."""
        self.authorized_users = {}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, photos_dir FROM authorized_faces")
        
        for name, photos_dir in cursor.fetchall():
            if os.path.exists(photos_dir):
                self.authorized_users[name] = photos_dir
        
        conn.close()
        logging.info(f"✅ Cargados {len(self.authorized_users)} usuarios autorizados")
    
    def _load_opencv_faces(self):
        """Carga rostros para OpenCV (solo si DeepFace no está disponible)."""
        self.authorized_faces = []
        self.authorized_names = []
        
        for name, photos_dir in self.authorized_users.items():
            for photo_file in os.listdir(photos_dir):
                if photo_file.endswith('.jpg'):
                    photo_path = os.path.join(photos_dir, photo_file)
                    img = cv2.imread(photo_path, cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        self.authorized_faces.append(img)
                        self.authorized_names.append(name)
    
    def _train_recognizer(self):
        """Entrena el reconocedor OpenCV (solo si DeepFace no está disponible)."""
        if not self.recognizer:
            logging.warning("⚠️ No hay reconocedor OpenCV disponible para entrenar.")
            return

        if len(self.authorized_faces) == 0:
            return
        
        try:
            unique_names = list(set(self.authorized_names))
            labels = [unique_names.index(name) for name in self.authorized_names]
            
            self.recognizer.train(self.authorized_faces, np.array(labels))
            self.name_to_id = {name: i for i, name in enumerate(unique_names)}
            self.id_to_name = {i: name for i, name in enumerate(unique_names)}
            
            logging.info(f"✅ Reconocedor OpenCV entrenado con {len(unique_names)} personas")
        except Exception as e:
            logging.error(f"Error entrenando reconocedor: {e}")
    
    def train_face(self, name: str) -> Tuple[str, str]:
        """
        Entrena el sistema con un nuevo rostro (proceso guiado).
        """
        # 1. VERIFICACIÓN CRÍTICA DE DEPENDENCIAS
        if not self.use_deepface and not self.recognizer:
            return "❌ El sistema de visión no está listo. \nEspera a que termine de instalarse 'opencv-contrib-python' y reinicia.", "error"
            
        if not name or len(name) < 2:
            return "❌ Proporciona un nombre válido (mínimo 2 caracteres)", "error"
        
        # Instrucciones de poses
        poses = [
            ("Frente", "Mira directamente a la cámara"),
            ("Izquierda leve", "Gira tu cabeza 30° a la izquierda"),
            ("Derecha leve", "Gira tu cabeza 30° a la derecha"),
            ("Izquierda", "Gira tu cabeza 45° a la izquierda"),
            ("Derecha", "Gira tu cabeza 45° a la derecha"),
            ("Arriba", "Inclina tu cabeza ligeramente hacia arriba"),
            ("Abajo", "Inclina tu cabeza ligeramente hacia abajo"),
            ("Sonriendo", "Sonríe mirando a la cámara"),
            ("Serio", "Pon cara seria mirando a la cámara"),
            ("Lentes (si usas)", "Con lentes puestos"),
            ("Sin lentes", "Sin lentes"),
            ("Luz natural", "Acércate a una ventana"),
            ("Luz artificial", "Aléjate de la ventana"),
            ("Cerca", "Acércate más a la cámara"),
            ("Lejos", "Aléjate un poco"),
        ]
        
        camera = None
        try:
            # Abrir cámara
            camera = cv2.VideoCapture(0, cv2.CAP_DSHOW) # CAP_DSHOW es más rápido en Windows
            if not camera.isOpened():
                return "❌ No se pudo acceder a la cámara. Verifica que no la use otra app.", "error"
            
            # Configurar cámara
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # Crear directorio para este usuario
            user_dir = os.path.join(self.authorized_dir, name)
            os.makedirs(user_dir, exist_ok=True)
            
            captured_count = 0
            
            if self.voice_callback:
                mode_text = "DeepFace avanzado" if self.use_deepface else "OpenCV básico"
                self.voice_callback(f"Iniciando entrenamiento para {name}. Mira a la ventana de cámara.")
            
            # Ventana de previsualización
            WINDOW_NAME = f"Entrenamiento Sentinel: {name}"
            
            # Forzar aparición de ventana
            cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(WINDOW_NAME, 640, 480)
            cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1)
            
            # Loop de poses
            for i, (pose_name, instruction) in enumerate(poses, 1):
                if self.voice_callback:
                    self.voice_callback(f"Pose {i}: {instruction}")
                
                # Cuenta regresiva visual (3 segundos)
                start_time = time.time()
                while time.time() - start_time < 4: # 4 segundos total (3 espera + 1 captura)
                    ret, frame = camera.read()
                    if not ret: break
                    
                    elapsed = time.time() - start_time
                    remaining = int(4 - elapsed)
                    
                    # Dibujar UI en el frame
                    frame_disp = frame.copy()
                    
                    # Instrucción
                    cv2.rectangle(frame_disp, (0,0), (640, 60), (0,0,0), -1)
                    cv2.putText(frame_disp, f"{i}/{len(poses)}: {pose_name}", (20, 40), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    
                    # Subtítulo instrucción
                    cv2.putText(frame_disp, instruction, (20, 450), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                    
                    # Cuenta regresiva central
                    if remaining > 0:
                        cv2.putText(frame_disp, str(remaining), (280, 240), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 255), 5)
                    else:
                        cv2.circle(frame_disp, (320, 240), 50, (0, 255, 0), 5) # Flash verde
                        
                    cv2.imshow(WINDOW_NAME, frame_disp)
                    if cv2.waitKey(1) & 0xFF == 27: # ESC para salir
                        camera.release()
                        cv2.destroyAllWindows()
                        return "🚫 Entrenamiento cancelado por usuario", "sys"
                
                # --- CAPTURA ---
                ret, frame = camera.read()
                if not ret: continue
                
                # (Lógica de guardado igual que antes...)
                # Convertir a escala de grises para detección
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detectar rostros
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))
                
                # Visualizar detección fallida o exitosa brevemente
                if len(faces) == 0:
                    if self.voice_callback: self.voice_callback("Rostro no detectado")
                    # Feedback visual de error
                    cv2.rectangle(frame, (0,0), (640, 480), (0,0,255), 10)
                    cv2.imshow(WINDOW_NAME, frame)
                    cv2.waitKey(500)
                else:
                    captured_count += 1
                    # Feedback visual éxito
                    cv2.rectangle(frame, (0,0), (640, 480), (0,255,0), 10)
                    cv2.imshow(WINDOW_NAME, frame)
                    cv2.waitKey(200)
                    
                    # Guardar lógica...
                    (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
                    if self.use_deepface:
                        photo_path = os.path.join(user_dir, f"face_{i:02d}.jpg")
                        cv2.imwrite(photo_path, frame)
                    else:
                        face_roi = gray[y:y+h, x:x+w]
                        face_roi = cv2.resize(face_roi, (200, 200))
                        photo_path = os.path.join(user_dir, f"face_{i:02d}.jpg")
                        cv2.imwrite(photo_path, face_roi)
            
            camera.release()
            cv2.destroyAllWindows()
            
            if captured_count < 5:
                return f"❌ Solo se capturaron {captured_count} fotos. Se necesitan al menos 5.", "error"
            
            # Registrar en base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO authorized_faces (name, photos_dir, photo_count)
                VALUES (?, ?, ?)
            ''', (name, user_dir, captured_count))
            conn.commit()
            conn.close()
            
            # Recargar rostros
            self._load_authorized_faces()
            if not self.use_deepface:
                self._load_opencv_faces()
                self._train_recognizer()
            
            if self.voice_callback:
                self.voice_callback(f"Entrenamiento completado. {captured_count} fotos capturadas exitosamente.")
            
            return f"✅ Rostro de {name} registrado con {captured_count} fotos", "sys"
            
        except Exception as e:
            logging.error(f"Error en entrenamiento facial: {e}")
            if 'camera' in locals():
                camera.release()
            return f"❌ Error: {e}", "error"
    
    def recognize_face(self) -> Tuple[bool, Optional[str]]:
        """
        Intenta reconocer un rostro autorizado.
        
        Returns:
            Tupla (reconocido, nombre)
        """
        if len(self.authorized_users) == 0:
            return False, None
        
        try:
            camera = cv2.VideoCapture(0)
            if not camera.isOpened():
                return False, None
            
            # Capturar frame
            ret, frame = camera.read()
            camera.release()
            
            if not ret:
                return False, None
            
            # Guardar frame temporal
            temp_path = os.path.join(self.intrusions_dir, "temp_check.jpg")
            cv2.imwrite(temp_path, frame)
            
            if self.use_deepface:
                # Usar DeepFace para reconocimiento
                return self._recognize_with_deepface(temp_path, frame)
            else:
                # Usar OpenCV para reconocimiento
                return self._recognize_with_opencv(frame)
            
        except Exception as e:
            logging.error(f"Error en reconocimiento facial: {e}")
            return False, None
    
    def _recognize_with_deepface(self, temp_path: str, frame) -> Tuple[bool, Optional[str]]:
        """Reconocimiento usando DeepFace."""
        try:
            # Buscar en cada usuario autorizado
            for name, user_dir in self.authorized_users.items():
                try:
                    # Verificar contra el directorio del usuario
                    result = DeepFace.verify(
                        img1_path=temp_path,
                        img2_path=user_dir,
                        model_name="VGG-Face",
                        enforce_detection=False
                    )
                    
                    if result["verified"]:
                        # Actualizar última vez usado
                        conn = sqlite3.connect(self.db_path)
                        cursor = conn.cursor()
                        cursor.execute('''
                            UPDATE authorized_faces 
                            SET last_used = CURRENT_TIMESTAMP 
                            WHERE name = ?
                        ''', (name,))
                        conn.commit()
                        conn.close()
                        
                        # Registrar intento exitoso
                        self.log_access_attempt(True, "face_deepface", name, 
                                              notes=f"Confianza: {result['distance']:.4f}")
                        
                        logging.info(f"✅ Rostro reconocido con DeepFace: {name}")
                        return True, name
                        
                except Exception as e:
                    logging.debug(f"No match con {name}: {e}")
                    continue
            
            # No se reconoció - guardar foto del intruso
            self._save_intruder_photo(frame)
            return False, None
            
        except Exception as e:
            logging.error(f"Error en DeepFace: {e}")
            return False, None
    
    def _recognize_with_opencv(self, frame) -> Tuple[bool, Optional[str]]:
        """Reconocimiento usando OpenCV."""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100)
            )
            
            if len(faces) == 0:
                return False, None
            
            (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (200, 200))
            
            label, confidence = self.recognizer.predict(face_roi)
            
            if confidence < 50:
                name = self.id_to_name.get(label, "Desconocido")
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE authorized_faces 
                    SET last_used = CURRENT_TIMESTAMP 
                    WHERE name = ?
                ''', (name,))
                conn.commit()
                conn.close()
                
                self.log_access_attempt(True, "face_opencv", name, 
                                      notes=f"Confianza: {confidence:.2f}")
                
                logging.info(f"✅ Rostro reconocido con OpenCV: {name}")
                return True, name
            else:
                self._save_intruder_photo(frame)
                return False, None
                
        except Exception as e:
            logging.error(f"Error en OpenCV: {e}")
            return False, None
    
    def _save_intruder_photo(self, frame):
        """Guarda foto de un intruso."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            photo_path = os.path.join(self.intrusions_dir, f"intruso_{timestamp}.jpg")
            cv2.imwrite(photo_path, frame)
            
            self.log_access_attempt(False, "face_attempt", None, 
                                  notes="Rostro no autorizado detectado")
            
            logging.info(f"📸 Foto de intruso guardada: {photo_path}")
        except Exception as e:
            logging.error(f"Error guardando foto de intruso: {e}")
    
    def log_access_attempt(self, success: bool, method: str, person_name: Optional[str] = None, 
                          confidence: float = 0.0, notes: str = ""):
        """Registra un intento de acceso."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO access_attempts 
                (success, face_recognized, person_name, unlock_method, confidence, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (success, person_name is not None, person_name, method, confidence, notes))
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Error registrando intento de acceso: {e}")
    
    def get_recent_logs(self, limit: int = 10) -> List[dict]:
        """Obtiene los logs recientes."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT timestamp, success, face_recognized, person_name, 
                       unlock_method, photo_path, confidence, notes
                FROM access_attempts
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            logs = []
            for row in cursor.fetchall():
                logs.append({
                    'timestamp': row[0],
                    'success': row[1],
                    'face_recognized': row[2],
                    'person_name': row[3],
                    'unlock_method': row[4],
                    'photo_path': row[5],
                    'confidence': row[6],
                    'notes': row[7]
                })
            
            conn.close()
            return logs
        except Exception as e:
            logging.error(f"Error obteniendo logs: {e}")
            return []
    
    def delete_all_faces(self) -> Tuple[str, str]:
        """Elimina todos los rostros autorizados."""
        try:
            # Eliminar directorios de usuarios
            for user_dir in os.listdir(self.authorized_dir):
                user_path = os.path.join(self.authorized_dir, user_dir)
                if os.path.isdir(user_path):
                    import shutil
                    shutil.rmtree(user_path)
            
            # Limpiar base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM authorized_faces")
            conn.commit()
            conn.close()
            
            # Recargar
            self._load_authorized_faces()
            if not self.use_deepface:
                self._load_opencv_faces()
                self._train_recognizer()
            
            return "✅ Todos los rostros eliminados", "sys"
        except Exception as e:
            return f"❌ Error: {e}", "error"


# Singleton
_sentinel_instance = None

def obtener_sentinel_security(voice_callback: Optional[callable] = None) -> SentinelSecurity:
    """Obtiene la instancia singleton de SentinelSecurity."""
    global _sentinel_instance
    if _sentinel_instance is None:
        _sentinel_instance = SentinelSecurity(voice_callback)
    return _sentinel_instance
