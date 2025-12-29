from playwright.sync_api import sync_playwright
import logging
import time

class SaraWebSurfer:
    def __init__(self, headless=False):
        self.headless = headless
        
    def _navegar(self, url, accion_callback):
        """Método base para iniciar navegador y realizar acción"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                page = browser.new_page()
                page.goto(url)
                
                resultado = accion_callback(page)
                
                browser.close()
                return resultado
        except Exception as e:
            logging.error(f"Error navegando: {e}")
            return f"Error web: {e}"

    def buscar_google(self, query):
        """Busca en Google y extrae títulos y resúmenes"""
        def accion(page):
            # Esperar a los resultados
            page.wait_for_selector("#search")
            
            # Extraer resultados orgánicos
            resultados = page.query_selector_all(".g")
            
            resumen = []
            for i, res in enumerate(resultados[:4]): # Top 4
                try:
                    titulo = res.query_selector("h3").inner_text()
                    link = res.query_selector("a").get_attribute("href")
                    # Intentar sacar snippet. A veces es .VwiC3b, a veces otro.
                    snippet_el = res.query_selector(".VwiC3b") or res.query_selector(".IsZvec")
                    snippet = snippet_el.inner_text() if snippet_el else "Sin resumen"
                    
                    resumen.append(f"{i+1}. {titulo}\n   {snippet}\n   Link: {link}")
                except: continue
                
            return "\n".join(resumen) if resumen else "No encontré resultados legibles."

        # Construir URL
        q = query.replace(" ", "+")
        url = f"https://www.google.com/search?q={q}"
        
        return self._navegar(url, accion)

    def leer_pagina(self, url):
        """Lee el contenido principal de una página"""
        if not url.startswith("http"): url = "https://" + url
        
        def accion(page):
            # Intentar sacar el contenido principal
            # Estrategia: buscar <main>, <article> o body
            texto = ""
            for selector in ["main", "article", "body"]:
                el = page.query_selector(selector)
                if el:
                    texto = el.inner_text()
                    break
            
            # Limpiar un poco (tomar primeros 2000 chars para no saturar memoria)
            return texto[:2000] + "\n...(contenido truncado)" if texto else "No pude leer el contenido."

        return self._navegar(url, accion)

    def capturar_web(self, url, output_path="screenshot_web.png"):
        """Toma una captura de pantalla"""
        if not url.startswith("http"): url = "https://" + url
        
        def accion(page):
            page.screenshot(path=output_path)
            return f"Captura guardada en {output_path}"
            
        return self._navegar(url, accion)
