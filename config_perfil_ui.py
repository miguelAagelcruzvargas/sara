"""
SARA - Configuración de Perfil de Usuario
GUI para configurar preferencias personales
"""
import customtkinter as ctk
from user_profile import obtener_perfil

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ConfiguracionPerfil(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.perfil = obtener_perfil()
        
        # Configuración de ventana (COMPACTA)
        self.title("SARA - Mi Perfil")
        self.geometry("450x550")
        self.resizable(False, False)
        
        # Variables
        self.nombre = ctk.StringVar(value=self.perfil.profile["user"]["name"])
        self.nombre_preferido = ctk.StringVar(value=self.perfil.profile["user"]["preferred_name"])
        self.idioma = ctk.StringVar(value=self.perfil.profile["voice"]["language"])
        self.tipo_voz = ctk.StringVar(value=self.perfil.profile["voice"]["type"])
        self.velocidad = ctk.StringVar(value=self.perfil.profile["voice"]["speed"])
        self.perfil_trabajo = ctk.StringVar(value=self.perfil.profile["work"]["default_profile"])
        self.hora_inicio = ctk.StringVar(value=self.perfil.profile["work"]["work_hours"]["start"])
        self.hora_fin = ctk.StringVar(value=self.perfil.profile["work"]["work_hours"]["end"])
        
        self.setup_ui()
    
    def setup_ui(self):
        # ===== HEADER =====
        header = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        
        title = ctk.CTkLabel(
            header,
            text="👤 Mi Perfil",
            font=("Inter", 16, "bold"),
            text_color="#00ff41"
        )
        title.pack(pady=8)
        
        # ===== CONTENIDO =====
        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=5)
        
        # --- INFORMACIÓN PERSONAL ---
        self.create_section(content, "👤 Información Personal")
        
        ctk.CTkLabel(content, text="Nombre:", font=("Inter", 10)).pack(anchor="w", pady=(3, 0))
        ctk.CTkEntry(content, textvariable=self.nombre, font=("Inter", 10), height=30).pack(fill="x", pady=3)
        
        ctk.CTkLabel(content, text="Llamarme:", font=("Inter", 10)).pack(anchor="w", pady=(3, 0))
        ctk.CTkEntry(content, textvariable=self.nombre_preferido, font=("Inter", 10), height=30).pack(fill="x", pady=3)
        
        # --- PREFERENCIAS DE VOZ ---
        self.create_section(content, "🎤 Preferencias de Voz")
        
        ctk.CTkLabel(content, text="Idioma:", font=("Inter", 10)).pack(anchor="w", pady=(3, 0))
        ctk.CTkOptionMenu(
            content,
            variable=self.idioma,
            values=["es-ES", "en-US"],
            font=("Inter", 10),
            height=30
        ).pack(fill="x", pady=3)
        
        ctk.CTkLabel(content, text="Voz:", font=("Inter", 10)).pack(anchor="w", pady=(3, 0))
        ctk.CTkOptionMenu(
            content,
            variable=self.tipo_voz,
            values=["female", "male"],
            font=("Inter", 10),
            height=30
        ).pack(fill="x", pady=3)
        
        ctk.CTkLabel(content, text="Velocidad:", font=("Inter", 10)).pack(anchor="w", pady=(3, 0))
        ctk.CTkOptionMenu(
            content,
            variable=self.velocidad,
            values=["slow", "normal", "fast"],
            font=("Inter", 10),
            height=30
        ).pack(fill="x", pady=3)
        
        # --- PERFIL DE TRABAJO ---
        self.create_section(content, "💼 Perfil de Trabajo")
        
        ctk.CTkLabel(content, text="Perfil:", font=("Inter", 10)).pack(anchor="w", pady=(3, 0))
        ctk.CTkOptionMenu(
            content,
            variable=self.perfil_trabajo,
            values=["casa", "oficina", "pomodoro"],
            font=("Inter", 10),
            height=30
        ).pack(fill="x", pady=3)
        
        ctk.CTkLabel(content, text="Horario:", font=("Inter", 10)).pack(anchor="w", pady=(5, 0))
        
        horario_frame = ctk.CTkFrame(content, fg_color="transparent")
        horario_frame.pack(fill="x", pady=3)
        
        ctk.CTkLabel(horario_frame, text="Inicio:", font=("Inter", 9)).pack(side="left", padx=(0, 3))
        ctk.CTkEntry(horario_frame, textvariable=self.hora_inicio, width=70, font=("Inter", 10), height=28).pack(side="left", padx=3)
        
        ctk.CTkLabel(horario_frame, text="Fin:", font=("Inter", 9)).pack(side="left", padx=(15, 3))
        ctk.CTkEntry(horario_frame, textvariable=self.hora_fin, width=70, font=("Inter", 10), height=28).pack(side="left", padx=3)
        
        # ===== BOTONES =====
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=10)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Guardar",
            command=self.guardar_configuracion,
            font=("Inter", 11, "bold"),
            fg_color="#00ff41",
            text_color="#000",
            hover_color="#00cc33",
            height=35
        )
        save_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="✖ Cancelar",
            command=self.destroy,
            font=("Inter", 10),
            fg_color="#555",
            hover_color="#666",
            height=35,
            width=90
        )
        cancel_btn.pack(side="left", padx=(5, 0))
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=("Consolas", 10),
            text_color="#00ff41"
        )
        self.status_label.pack(pady=(0, 10))
    
    def create_section(self, parent, title):
        """Crea un separador de sección"""
        separator = ctk.CTkFrame(parent, height=1, fg_color="#333")
        separator.pack(fill="x", pady=(10, 3))
        
        label = ctk.CTkLabel(
            parent,
            text=title,
            font=("Inter", 11, "bold"),
            text_color="#00ff41"
        )
        label.pack(anchor="w", pady=(3, 5))
    
    def guardar_configuracion(self):
        """Guarda la configuración y aplica cambios en tiempo real"""
        try:
            # Actualizar información personal
            self.perfil.update_user_info(
                name=self.nombre.get(),
                preferred_name=self.nombre_preferido.get()
            )
            
            # Actualizar preferencias de voz
            self.perfil.update_voice_preferences(
                language=self.idioma.get(),
                voice_type=self.tipo_voz.get(),
                speed=self.velocidad.get()
            )
            
            # Actualizar perfil de trabajo
            self.perfil.update_work_profile(
                default_profile=self.perfil_trabajo.get(),
                start_time=self.hora_inicio.get(),
                end_time=self.hora_fin.get()
            )
            
            # Marcar setup como completado
            self.perfil.mark_setup_complete()
            
            # ===== APLICAR CAMBIOS EN TIEMPO REAL =====
            # Recargar motor de voz con nuevas preferencias
            try:
                # Acceder al brain desde la ventana padre (SARA)
                if hasattr(self.master, 'brain'):
                    brain = self.master.brain
                    # Reinicializar motor de voz con nuevas preferencias
                    from voice import NeuralVoiceEngine
                    brain.voz = NeuralVoiceEngine()
                    
                    # Confirmar con voz nueva
                    nombre = self.nombre_preferido.get() or self.nombre.get() or "Usuario"
                    brain.voz.hablar(f"Perfil actualizado. Hola {nombre}!")
            except Exception as e:
                import logging
                logging.error(f"Error recargando voz: {e}")
            
            self.status_label.configure(
                text="✓ Cambios aplicados en tiempo real",
                text_color="#00ff41"
            )
            
            self.after(1500, self.destroy)
            
        except Exception as e:
            self.status_label.configure(
                text=f"✗ Error: {e}",
                text_color="#ff4444"
            )

def abrir_configuracion(parent=None):
    """Abre la ventana de configuración"""
    if parent is None:
        # Crear ventana temporal si no hay parent
        root = ctk.CTk()
        root.withdraw()
        config = ConfiguracionPerfil(root)
        config.mainloop()
    else:
        config = ConfiguracionPerfil(parent)
        return config
