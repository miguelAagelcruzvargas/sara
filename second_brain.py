"""
🧠 SARA - Second Brain (Memoria Vectorial)
==========================================
Sistema de memoria a largo y corto plazo usando ChromaDB.

Mejoras v2.0:
- 🔒 Thread-Safe para uso concurrente
- 🗑️ Método de olvido (borrado selectivo)
- ✂️ Chunking inteligente (respeta párrafos y oraciones)
- 🔄 Reset de DB para cambios de modelo
- 📊 Estadísticas de memoria
"""

import os
import logging
import threading
import time
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import PyPDF2
from typing import Optional, List, Dict

class SecondBrain:
    def __init__(self, db_path="sara_memory_db", shared_model=None):
        """
        Inicializa Second Brain con ChromaDB.
        
        Args:
            db_path: Ruta a la base de datos ChromaDB
            shared_model: Modelo SentenceTransformer compartido (opcional).
                         ADVERTENCIA: Si está en GPU, puede causar conflictos en multithreading.
                         Recomendado: usar modelo CPU-only o None (ChromaDB maneja embeddings).
        """
        self.db_path = db_path
        self._lock = threading.Lock()  # Thread-safety para operaciones concurrentes
        
        logging.info("🧠 Inicializando Second Brain (ChromaDB)...")
        try:
            # Inicializar cliente persistente
            self.client = chromadb.PersistentClient(path=db_path)
            
            # Usar modelo compartido si está disponible, sino crear uno nuevo
            if shared_model is not None:
                logging.warning("⚠️ Usando modelo compartido. Asegúrate de que esté en CPU para thread-safety.")
                self.embedder = shared_model
                self.use_shared_model = True
            else:
                logging.info("📥 Cargando nuevo modelo para Second Brain")
                # Inicializar modelo de embeddings multilingüe (mejor para español)
                self.embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                self.use_shared_model = False
            
            # Crear o recuperar colecciones
            self.short_term = self.client.get_or_create_collection(
                name="short_term_memory",
                metadata={"hnsw:space": "cosine"}
            )
            
            self.long_term = self.client.get_or_create_collection(
                name="long_term_memory", 
                metadata={"hnsw:space": "cosine"}
            )
            
            logging.info("✅ Second Brain listo y cargado | Thread-Safe: ✅")
            
        except Exception as e:
            logging.error(f"❌ Error crítico en Second Brain: {e}")
            self.client = None

    def memorizar(self, texto, metadata=None, coleccion="long_term"):
        """Guarda un texto en la memoria vectorial (Thread-Safe)."""
        if not self.client: return "Error: Cerebro desconectado"
        
        with self._lock:  # Protección thread-safe
            try:
                target_col = self.short_term if coleccion == "short_term" else self.long_term
                
                # Generar ID único basado en timestamp
                doc_id = f"mem_{int(time.time()*1000)}"
                
                # Generar embedding
                embedding = self.embedder.encode(texto).tolist()
                
                target_col.add(
                    documents=[texto],
                    embeddings=[embedding],
                    metadatas=[metadata or {"source": "user_voice", "date": time.ctime()}],
                    ids=[doc_id]
                )
                return f"Memorizado: {texto[:50]}..."
            except Exception as e:
                return f"Error al memorizar: {e}"

    def recordar(self, query, n_results=3, coleccion="long_term"):
        """Recupera información relevante basada en similitud semántica (Thread-Safe)."""
        if not self.client: return []
        
        with self._lock:  # Protección thread-safe
            try:
                target_col = self.short_term if coleccion == "short_term" else self.long_term
                
                embedding = self.embedder.encode(query).tolist()
                
                results = target_col.query(
                    query_embeddings=[embedding],
                    n_results=n_results
                )
                
                # Formatear resultados
                memories = []
                if results['documents']:
                    for i, doc in enumerate(results['documents'][0]):
                        meta = results['metadatas'][0][i]
                        memories.append(f"{doc} (Fuente: {meta.get('source', 'unknown')})")
                
                return memories
            except Exception as e:
                logging.error(f"Error recordando: {e}")
                return []

    def olvidar(self, query: Optional[str] = None, doc_ids: Optional[List[str]] = None, coleccion="long_term"):
        """
        Borra información de la memoria (Thread-Safe).
        
        Args:
            query: Busca y borra documentos similares a esta consulta (usa similitud semántica)
            doc_ids: Lista de IDs específicos para borrar
            coleccion: "short_term" o "long_term"
        
        Returns:
            Mensaje de confirmación
        """
        if not self.client: return "Error: Cerebro desconectado"
        
        with self._lock:
            try:
                target_col = self.short_term if coleccion == "short_term" else self.long_term
                
                # Opción 1: Borrar por IDs específicos
                if doc_ids:
                    target_col.delete(ids=doc_ids)
                    return f"🗑️ Borrados {len(doc_ids)} documentos por ID."
                
                # Opción 2: Buscar por similitud y borrar
                elif query:
                    embedding = self.embedder.encode(query).tolist()
                    results = target_col.query(
                        query_embeddings=[embedding],
                        n_results=5  # Buscar top 5 más similares
                    )
                    
                    if results['ids'] and results['ids'][0]:
                        ids_to_delete = results['ids'][0]
                        target_col.delete(ids=ids_to_delete)
                        return f"🗑️ Borrados {len(ids_to_delete)} documentos relacionados con '{query}'."
                    else:
                        return f"ℹ️ No encontré documentos relacionados con '{query}'."
                
                else:
                    return "❌ Debes proporcionar 'query' o 'doc_ids' para borrar."
                    
            except Exception as e:
                return f"❌ Error al olvidar: {e}"

    def _chunk_text_intelligently(self, text: str, max_chars=500) -> List[str]:
        """
        Divide texto respetando párrafos y oraciones.
        
        Estrategia:
        1. Dividir por párrafos dobles (\n\n)
        2. Si un párrafo es muy largo, dividir por oraciones (.)
        3. Si una oración es muy larga, dividir por comas (,)
        4. Último recurso: dividir por espacios
        
        Args:
            text: Texto a dividir
            max_chars: Tamaño máximo de cada chunk
        
        Returns:
            Lista de chunks
        """
        chunks = []
        
        # Paso 1: Dividir por párrafos
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            # Si el párrafo cabe completo, agregarlo
            if len(para) <= max_chars:
                chunks.append(para)
            else:
                # Paso 2: Dividir por oraciones
                sentences = para.replace('! ', '!|').replace('? ', '?|').replace('. ', '.|').split('|')
                current_chunk = ""
                
                for sent in sentences:
                    sent = sent.strip()
                    if not sent:
                        continue
                    
                    # Si agregar esta oración no excede el límite
                    if len(current_chunk) + len(sent) + 1 <= max_chars:
                        current_chunk += sent + " "
                    else:
                        # Guardar chunk actual si no está vacío
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        
                        # Si la oración sola es muy larga, dividir por comas
                        if len(sent) > max_chars:
                            parts = sent.split(', ')
                            temp_chunk = ""
                            for part in parts:
                                if len(temp_chunk) + len(part) + 2 <= max_chars:
                                    temp_chunk += part + ", "
                                else:
                                    if temp_chunk:
                                        chunks.append(temp_chunk.strip())
                                    temp_chunk = part + ", "
                            if temp_chunk:
                                chunks.append(temp_chunk.strip())
                            current_chunk = ""
                        else:
                            current_chunk = sent + " "
                
                # Agregar último chunk si existe
                if current_chunk:
                    chunks.append(current_chunk.strip())
        
        return [c for c in chunks if c]  # Filtrar vacíos

    def ingestar_archivo(self, file_path):
        """Lee un archivo PDF/TXT y lo guarda en la memoria con chunking inteligente."""
        if not os.path.exists(file_path):
            return "Archivo no encontrado."
        
        ext = file_path.lower().split('.')[-1]
        content = ""
        
        try:
            if ext == 'pdf':
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        content += page.extract_text() + "\n"
            elif ext == 'txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                return "Formato no soportado (solo PDF o TXT)."
            
            # Usar chunking inteligente en lugar de cortar cada 500 caracteres
            chunks = self._chunk_text_intelligently(content, max_chars=500)
            
            total_chunks = 0
            for i, chunk in enumerate(chunks):
                self.memorizar(
                    chunk, 
                    metadata={"source": os.path.basename(file_path), "chunk": i, "path": file_path}
                )
                total_chunks += 1
                
            return f"📚 He leído y memorizado {total_chunks} fragmentos de {os.path.basename(file_path)}."
            
        except Exception as e:
            return f"❌ Error leyendo archivo: {e}"

    def reset_database(self, confirm=False):
        """
        Borra completamente la base de datos (Thread-Safe).
        Útil cuando cambias de modelo de embeddings.
        
        Args:
            confirm: Debe ser True para ejecutar (seguridad)
        
        Returns:
            Mensaje de confirmación
        """
        if not confirm:
            return "⚠️ Debes confirmar explícitamente (confirm=True) para borrar la DB."
        
        with self._lock:
            try:
                # Borrar colecciones
                try:
                    self.client.delete_collection("short_term_memory")
                except:
                    pass
                try:
                    self.client.delete_collection("long_term_memory")
                except:
                    pass
                
                # Recrear colecciones
                self.short_term = self.client.create_collection(
                    name="short_term_memory",
                    metadata={"hnsw:space": "cosine"}
                )
                self.long_term = self.client.create_collection(
                    name="long_term_memory",
                    metadata={"hnsw:space": "cosine"}
                )
                
                return "✅ Base de datos reseteada completamente."
            except Exception as e:
                return f"❌ Error reseteando DB: {e}"

    def get_stats(self) -> Dict:
        """Retorna estadísticas de la memoria (Thread-Safe)."""
        if not self.client:
            return {"error": "Cerebro desconectado"}
        
        with self._lock:
            try:
                short_count = self.short_term.count()
                long_count = self.long_term.count()
                
                return {
                    "short_term": short_count,
                    "long_term": long_count,
                    "total": short_count + long_count,
                    "db_path": str(self.db_path),
                    "shared_model": self.use_shared_model
                }
            except Exception as e:
                return {"error": str(e)}
