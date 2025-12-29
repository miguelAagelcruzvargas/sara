"""
SARA - Configuración Inicial (First Run Setup)
GUI para configurar API keys en el primer inicio
"""

import customtkinter as ctk
import webbrowser
from config import ConfigManager
import sys
import os

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class FirstRunSetup(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuración de ventana
        self.title("S.A.R.A. - Configuración Inicial")
        self.geometry("700x650")
        self.resizable(False, False)
        
        # Variables
        self.gemini_key = ctk.StringVar()
        self.groq_key = ctk.StringVar()
        self.openai_key = ctk.StringVar()
        self.provider = ctk.StringVar(value="Gemini")
        
        self.show_gemini = False
        self.show_groq = False
        self.show_openai = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # ===== HEADER =====
        header = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        
        title = ctk.CTkLabel(
            header,
            text="🤖 Bienvenido a S.A.R.A.",
            font=("Consolas", 28, "bold"),
            text_color="#00ff41"
        )
        title.pack(pady=20)
        
        subtitle = ctk.CTkLabel(
            header,
            text="Sistema Asistente de Respuesta Automática",
            font=("Consolas", 14),
            text_color="#888"
        )
        subtitle.pack(pady=(0, 20))
        
        # ===== INSTRUCCIONES =====
        info_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        info_frame.pack(fill="x", padx=20, pady=20)
        
        info_text = ctk.CTkLabel(
            info_frame,
            text="Para usar SARA necesitas al menos UNA API key de IA.\n"
                 "Todas las opciones tienen planes gratuitos. Elige la que prefieras:",
            font=("Consolas", 11),
            text_color="#ccc",
            justify="left"
        )
        info_text.pack(padx=15, pady=15)
        
        # ===== CONFIGURACIÓN DE APIS =====
        config_frame = ctk.CTkFrame(self, fg_color="transparent")
        config_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # --- GEMINI ---
        self.create_api_section(
            config_frame,
            "🔷 Google Gemini (Recomendado)",
            "Gratis • Rápido • Multimodal",
            "https://aistudio.google.com/app/apikey",
            self.gemini_key,
            "gemini",
            row=0
        )
        
        # --- GROQ ---
        self.create_api_section(
            config_frame,
            "⚡ Groq",
            "Gratis • Ultra-rápido • Llama 3.3",
            "https://console.groq.com/keys",
            self.groq_key,
            "groq",
            row=1
        )
        
        # --- OPENAI ---
        self.create_api_section(
            config_frame,
            "🟢 OpenAI (Opcional)",
            "De pago • GPT-4 • Muy preciso",
            "https://platform.openai.com/api-keys",
            self.openai_key,
            "openai",
            row=2
        )
        
        # ===== PROVEEDOR PREFERIDO =====
        provider_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        provider_frame.pack(fill="x", padx=20, pady=10)
        
        provider_label = ctk.CTkLabel(
            provider_frame,
            text="Proveedor preferido:",
            font=("Consolas", 12, "bold")
        )
        provider_label.pack(side="left", padx=15, pady=10)
        
        provider_menu = ctk.CTkOptionMenu(
            provider_frame,
            variable=self.provider,
            values=["Gemini", "Groq", "OpenAI"],
            font=("Consolas", 11),
            width=150
        )
        provider_menu.pack(side="left", padx=10, pady=10)
        
        # ===== BOTONES =====
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Guardar y Continuar",
            command=self.guardar_configuracion,
            font=("Consolas", 14, "bold"),
            fg_color="#00ff41",
            text_color="#000",
            hover_color="#00cc33",
            height=45
        )
        save_btn.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        skip_btn = ctk.CTkButton(
            button_frame,
            text="⏭ Configurar Después",
            command=self.salir,
            font=("Consolas", 12),
            fg_color="#555",
            hover_color="#666",
            height=45
        )
        skip_btn.pack(side="left", padx=(10, 0))
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=("Consolas", 10),
            text_color="#ff4444"
        )
        self.status_label.pack(pady=(0, 10))
    
    def create_api_section(self, parent, title, description, url, var, api_name, row):
        """Crea una sección para configurar una API"""
        frame = ctk.CTkFrame(parent, fg_color="#2b2b2b")
        frame.grid(row=row, column=0, sticky="ew", pady=5)
        parent.grid_columnconfigure(0, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=5)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=("Consolas", 13, "bold"),
            anchor="w"
        )
        title_label.pack(side="left")
        
        desc_label = ctk.CTkLabel(
            header_frame,
            text=description,
            font=("Consolas", 9),
            text_color="#888",
            anchor="w"
        )
        desc_label.pack(side="left", padx=10)
        
        # Input frame
        input_frame = ctk.CTkFrame(frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Entry
        entry = ctk.CTkEntry(
            input_frame,
            textvariable=var,
            placeholder_text="Pega tu API key aquí...",
            font=("Consolas", 10),
            show="●" if not getattr(self, f"show_{api_name}") else ""
        )
        entry.pack(side="left", expand=True, fill="x", padx=(0, 5))
        setattr(self, f"entry_{api_name}", entry)
        
        # Toggle visibility button
        toggle_btn = ctk.CTkButton(
            input_frame,
            text="👁",
            width=35,
            command=lambda: self.toggle_visibility(api_name),
            fg_color="#444",
            hover_color="#555"
        )
        toggle_btn.pack(side="left", padx=2)
        
        # Link button
        link_btn = ctk.CTkButton(
            input_frame,
            text="🔗",
            width=35,
            command=lambda: webbrowser.open(url),
            fg_color="#0066cc",
            hover_color="#0052a3"
        )
        link_btn.pack(side="left")
    
    def toggle_visibility(self, api_name):
        """Alterna la visibilidad de la API key"""
        current = getattr(self, f"show_{api_name}")
        setattr(self, f"show_{api_name}", not current)
        
        entry = getattr(self, f"entry_{api_name}")
        entry.configure(show="" if not current else "●")
    
    def guardar_configuracion(self):
        """Guarda la configuración y cierra la ventana"""
        gemini = self.gemini_key.get().strip()
        groq = self.groq_key.get().strip()
        openai = self.openai_key.get().strip()
        provider = self.provider.get()
        
        # Validar que haya al menos una key
        if not gemini and not groq and not openai:
            self.status_label.configure(
                text="⚠ Debes configurar al menos una API key",
                text_color="#ff4444"
            )
            return
        
        # Validar que la key del proveedor seleccionado exista
        if provider == "Gemini" and not gemini:
            self.status_label.configure(
                text="⚠ Gemini seleccionado pero no hay API key",
                text_color="#ff4444"
            )
            return
        elif provider == "Groq" and not groq:
            self.status_label.configure(
                text="⚠ Groq seleccionado pero no hay API key",
                text_color="#ff4444"
            )
            return
        elif provider == "OpenAI" and not openai:
            self.status_label.configure(
                text="⚠ OpenAI seleccionado pero no hay API key",
                text_color="#ff4444"
            )
            return
        
        # Guardar
        exito = ConfigManager.guardar_api_keys(
            gemini_key=gemini,
            groq_key=groq,
            openai_key=openai,
            provider=provider
        )
        
        if exito:
            self.status_label.configure(
                text="✓ Configuración guardada correctamente",
                text_color="#00ff41"
            )
            self.after(1000, self.destroy)
        else:
            self.status_label.configure(
                text="✗ Error al guardar la configuración",
                text_color="#ff4444"
            )
    
    def salir(self):
        """Cierra la ventana sin guardar"""
        self.destroy()

if __name__ == "__main__":
    app = FirstRunSetup()
    app.mainloop()
