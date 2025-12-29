import os
import logging
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import PyPDF2

class SecondBrain:
    def __init__(self, db_path="sara_memory_db"):
        self.db_path = db_path
        
        logging.info("🧠 Inicializando Second Brain (ChromaDB)...")
        try:
            # Inicializar cliente persistente
            self.client = chromadb.PersistentClient(path=db_path)
            
            # Inicializar modelo de embeddings (local, rápido)
            # all-MiniLM-L6-v2 es ideal para CPU (rápido y ligero)
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Crear o recuperar colecciones
            self.short_term = self.client.get_or_create_collection(
                name="short_term_memory",
                metadata={"hnsw:space": "cosine"}
            )
            
            self.long_term = self.client.get_or_create_collection(
                name="long_term_memory", 
                metadata={"hnsw:space": "cosine"}
            )
            
            logging.info("✅ Second Brain listo y cargado.")
            
        except Exception as e:
            logging.error(f"❌ Error crítico en Second Brain: {e}")
            self.client = None

    def memorizar(self, texto, metadata=None, coleccion="long_term"):
        """Guarda un texto en la memoria vectorial"""
        if not self.client: return "Error: Cerebro desconectado"
        
        try:
            target_col = self.short_term if coleccion == "short_term" else self.long_term
            
            # Generar ID único basado en hash o timestamp
            import time
            doc_id = f"mem_{int(time.time()*1000)}"
            
            # Generar embedding (manualmente para tener control, aunque chroma lo hace auto)
            # Usamos la función interna de chroma si no pasamos embeddings, 
            # pero aquí usamos sentence-transformers explícitamente para consistencia.
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
        """Recupera información relevante basada en similitud semántica"""
        if not self.client: return []
        
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

    def ingestar_archivo(self, file_path):
        """Lee un archivo PDF/TXT y lo guarda en la memoria"""
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
            
            # Dividir en chunks (fragmentos) de ~500 caracteres para mejor búsqueda
            chunks = [content[i:i+500] for i in range(0, len(content), 500)]
            
            total_chunks = 0
            for i, chunk in enumerate(chunks):
                self.memorizar(
                    chunk, 
                    metadata={"source": os.path.basename(file_path), "chunk": i, "path": file_path}
                )
                total_chunks += 1
                
            return f"He leído y memorizado {total_chunks} fragmentos de {os.path.basename(file_path)}."
            
        except Exception as e:
            return f"Error leyendo archivo: {e}"
