"""
🌐 SARA - Web Agent (FINAL PRODUCTION VERSION)
==============================================
Navegador web inteligente con:
- Rate Limiting (anti-ban)
- Cache con TTL
- Manejo robusto de cookies GDPR
- Timeout adaptativo
- Wrappers síncronos para brain.py

Autor: SARA Team
Fecha: 2025-12-30
"""

import logging
import asyncio
import time
import hashlib
from datetime import datetime, timedelta
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# Configuración de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - SARA-WEB - %(levelname)s - %(message)s')
logger = logging.getLogger("WEB_AGENT")

class SaraWebSurfer:
    def __init__(self, headless=True, cache_ttl=300, min_delay=2.0):
        """
        Args:
            headless: Ejecutar sin ventana visible
            cache_ttl: Tiempo de vida del cache en segundos (default: 5 min)
            min_delay: Delay mínimo entre requests en segundos (default: 2s)
        """
        self.headless = headless
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        # --- RATE LIMITING ---
        self.last_request_time = 0
        self.min_delay = min_delay
        
        # --- CACHE SYSTEM ---
        self.cache = {}  # {hash: (resultado, timestamp)}
        self.cache_ttl = cache_ttl
        
        # --- COOKIE PATTERNS ---
        self.cookie_patterns = [
            "Aceptar todo", "Accept all", "Acepto", "I accept",
            "Continuar", "Continue", "Entendido", "Got it",
            "Aceptar", "Accept", "OK", "Permitir todo"
        ]

    def _get_cache_key(self, method, *args):
        """Genera clave de cache única."""
        key_str = f"{method}:{':'.join(map(str, args))}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def _get_from_cache(self, cache_key):
        """Obtiene resultado del cache si es válido."""
        if cache_key in self.cache:
            resultado, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                logger.info(f"⚡ Cache Hit: {cache_key[:8]}...")
                return resultado
            else:
                # Cache expirado
                del self.cache[cache_key]
        return None

    def _save_to_cache(self, cache_key, resultado):
        """Guarda resultado en cache."""
        self.cache[cache_key] = (resultado, datetime.now())
        # Limitar tamaño del cache
        if len(self.cache) > 100:
            # Eliminar el más antiguo
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]

    async def _apply_rate_limit(self):
        """Aplica rate limiting para evitar bans."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_delay:
            wait_time = self.min_delay - elapsed
            logger.debug(f"⏳ Rate limit: esperando {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
        self.last_request_time = time.time()

    async def _handle_cookies(self, page):
        """Manejo robusto de cookies GDPR."""
        for pattern in self.cookie_patterns:
            try:
                botones = page.get_by_role("button", name=pattern)
                if await botones.count() > 0:
                    await botones.first.click()
                    logger.debug(f"✅ Cookie aceptada: {pattern}")
                    await asyncio.sleep(0.5)
                    return True
            except:
                continue
        return False

    async def _navegar(self, url, accion_callback, wait_selector=None):
        """
        Núcleo asíncrono con rate limiting y timeout adaptativo.
        """
        # Aplicar rate limiting
        await self._apply_rate_limit()
        
        async with async_playwright() as p:
            # Argumentos Anti-Detección
            browser_args = [
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-infobars'
            ]

            try:
                browser = await p.chromium.launch(headless=self.headless, args=browser_args)
                
                context = await browser.new_context(
                    user_agent=self.user_agent,
                    viewport={'width': 1280, 'height': 720},
                    locale='es-MX'
                )
                
                page = await context.new_page()
                
                # Inyección JS Anti-Bot
                await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

                logger.info(f"🌐 Navegando a: {url[:50]}...")
                
                # Timeout adaptativo
                timeout = 15000 if "google.com" in url else 30000
                
                # Goto Asíncrono
                await page.goto(url, timeout=timeout, wait_until="domcontentloaded")

                if wait_selector:
                    try:
                        await page.wait_for_selector(wait_selector, timeout=5000)
                    except:
                        logger.warning(f"⚠️ Timeout esperando selector {wait_selector}")

                # Ejecutamos la acción
                resultado = await accion_callback(page)
                
                await browser.close()
                return resultado

            except PlaywrightTimeout:
                return "Error: La página tardó demasiado en responder."
            except Exception as e:
                logger.error(f"❌ Error navegación: {e}")
                return f"Error interno web: {str(e)}"

    async def buscar_google(self, query):
        """Busca en Google con cache."""
        # Verificar cache
        cache_key = self._get_cache_key("google", query)
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        async def accion(page):
            # Manejo robusto de cookies
            await self._handle_cookies(page)

            # Extraer resultados
            resultados = await page.locator('.g').all()
            
            data = []
            for res in resultados[:5]:
                try:
                    titulo_el = res.locator('h3').first
                    link_el = res.locator('a').first
                    
                    if await titulo_el.count() == 0 or await link_el.count() == 0:
                        continue

                    titulo = await titulo_el.inner_text()
                    link = await link_el.get_attribute('href')
                    
                    # Extracción de snippet
                    texto_bloque = await res.inner_text()
                    lines = [line for line in texto_bloque.split('\n') if len(line) > 30 and line != titulo]
                    snippet = lines[0] if lines else "Sin resumen."

                    if link and link.startswith('http'):
                        data.append(f"📌 {titulo}\n   📝 {snippet}\n   🔗 {link}")
                except:
                    continue
            
            return "\n\n".join(data) if data else "Google bloqueó la búsqueda o no hay resultados."

        q = query.replace(" ", "+")
        url = f"https://www.google.com/search?q={q}&hl=es&gl=mx"
        resultado = await self._navegar(url, accion, wait_selector="#search")
        
        # Guardar en cache
        self._save_to_cache(cache_key, resultado)
        return resultado

    async def leer_pagina(self, url):
        """Lee contenido con cache."""
        # Verificar cache
        cache_key = self._get_cache_key("leer", url)
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        if not url.startswith("http"):
            url = "https://" + url
        
        async def accion(page):
            # Manejo de cookies
            await self._handle_cookies(page)
            
            # Limpieza DOM vía JS
            await page.evaluate("""() => {
                const basura = document.querySelectorAll('script, style, nav, footer, iframe, svg, noscript, .ads');
                basura.forEach(el => el.remove());
            }""")
            
            # Selectores inteligentes
            locators = page.locator('article p, main p, .content p, h1, h2, h3')
            contenido = await locators.all_inner_texts()
            
            texto_limpio = "\n".join([line for line in contenido if len(line.strip()) > 20])
            
            if not texto_limpio:
                body_txt = await page.inner_text("body")
                return body_txt[:2000]

            return f"📄 {url}\n{'-'*30}\n{texto_limpio[:3500]}..."

        resultado = await self._navegar(url, accion)
        
        # Guardar en cache
        self._save_to_cache(cache_key, resultado)
        return resultado

    async def capturar_web(self, url, output_path="screenshot.png"):
        """Captura con scroll asíncrono (sin cache)."""
        if not url.startswith("http"):
            url = "https://" + url
        
        async def accion(page):
            # Scroll suave para Lazy Load
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1.5)
            await page.evaluate("window.scrollTo(0, 0)")
            
            await page.screenshot(path=output_path, full_page=True)
            return f"📸 Captura guardada: {output_path}"
            
        return await self._navegar(url, accion)

    # --- WRAPPERS SÍNCRONOS PARA BRAIN.PY ---
    
    def buscar_google_sync(self, query):
        """Versión síncrona para brain.py"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.buscar_google(query))

    def leer_pagina_sync(self, url):
        """Versión síncrona para brain.py"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.leer_pagina(url))

    def capturar_web_sync(self, url, output_path="screenshot.png"):
        """Versión síncrona para brain.py"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.capturar_web(url, output_path))


# --- TESTING ---
if __name__ == "__main__":
    async def main():
        bot = SaraWebSurfer(headless=True, cache_ttl=300, min_delay=2.0)
        
        print("🔍 Test 1: Búsqueda en Google...")
        res = await bot.buscar_google("Python async vs sync performance")
        print(res[:300])
        
        print("\n🔍 Test 2: Búsqueda repetida (debe usar cache)...")
        res2 = await bot.buscar_google("Python async vs sync performance")
        print("Cache funcionó!" if res == res2 else "Cache falló")
        
        print("\n📖 Test 3: Leer página...")
        if "🔗" in res:
            first_link = res.split("🔗")[1].split("\n")[0].strip()
            content = await bot.leer_pagina(first_link)
            print(content[:200])

    asyncio.run(main())