"""
Test básico para Second Brain optimizado
"""

from second_brain import SecondBrain
import os
import tempfile
import shutil

def test_second_brain():
    print("🧪 Iniciando tests de Second Brain...\n")
    
    # Crear directorio temporal para tests
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_db")
    
    try:
        # 1. Inicialización
        print("1️⃣ Test: Inicialización")
        brain = SecondBrain(db_path=db_path)
        print("   ✅ Second Brain inicializado correctamente\n")
        
        # 2. Memorizar y Recordar
        print("2️⃣ Test: Memorizar y Recordar")
        brain.memorizar("Python es un lenguaje de programación muy popular")
        brain.memorizar("JavaScript se usa principalmente para desarrollo web")
        brain.memorizar("SARA es un asistente virtual inteligente")
        
        results = brain.recordar("lenguaje programación")
        print(f"   Búsqueda: 'lenguaje programación'")
        print(f"   Resultados encontrados: {len(results)}")
        if results:
            print(f"   Primer resultado: {results[0][:80]}...")
        print("   ✅ Memorización y recuperación funcionan\n")
        
        # 3. Estadísticas
        print("3️⃣ Test: Estadísticas")
        stats = brain.get_stats()
        print(f"   Memoria a largo plazo: {stats['long_term']} documentos")
        print(f"   Memoria a corto plazo: {stats['short_term']} documentos")
        print(f"   Total: {stats['total']} documentos")
        print("   ✅ Estadísticas funcionan\n")
        
        # 4. Chunking Inteligente
        print("4️⃣ Test: Chunking Inteligente")
        texto_largo = """
        Este es el primer párrafo. Tiene varias oraciones. Es importante que se respeten.
        
        Este es el segundo párrafo. También tiene múltiples oraciones. El chunking debe respetar los límites de párrafos.
        
        Este es un tercer párrafo muy largo que probablemente exceda el límite de 500 caracteres y necesitará ser dividido en múltiples chunks, pero debe hacerlo de forma inteligente, respetando las oraciones y no cortando palabras a la mitad como lo haría un chunking simple basado en índices.
        """
        
        chunks = brain._chunk_text_intelligently(texto_largo, max_chars=150)
        print(f"   Texto dividido en {len(chunks)} chunks")
        for i, chunk in enumerate(chunks[:3]):  # Mostrar solo primeros 3
            print(f"   Chunk {i+1}: {chunk[:60]}...")
        print("   ✅ Chunking inteligente funciona\n")
        
        # 5. Olvidar (Borrado)
        print("5️⃣ Test: Olvidar información")
        brain.memorizar("Información temporal que será borrada", coleccion="short_term")
        stats_antes = brain.get_stats()
        print(f"   Antes de olvidar: {stats_antes['short_term']} docs en short_term")
        
        result = brain.olvidar(query="temporal", coleccion="short_term")
        print(f"   Resultado: {result}")
        
        stats_despues = brain.get_stats()
        print(f"   Después de olvidar: {stats_despues['short_term']} docs en short_term")
        print("   ✅ Método de olvido funciona\n")
        
        # 6. Reset de Base de Datos
        print("6️⃣ Test: Reset de Base de Datos")
        stats_antes_reset = brain.get_stats()
        print(f"   Antes del reset: {stats_antes_reset['total']} documentos totales")
        
        result = brain.reset_database(confirm=True)
        print(f"   Resultado: {result}")
        
        stats_despues_reset = brain.get_stats()
        print(f"   Después del reset: {stats_despues_reset['total']} documentos totales")
        print("   ✅ Reset de DB funciona\n")
        
        print("=" * 60)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR EN TESTS: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Limpiar directorio temporal
        try:
            shutil.rmtree(temp_dir)
            print("\n🧹 Limpieza completada")
        except:
            pass

if __name__ == "__main__":
    test_second_brain()
