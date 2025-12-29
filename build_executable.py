"""
SARA - Constructor de Ejecutable Mejorado
Genera ejecutables optimizados con PyInstaller
"""

import os
import sys
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess

VERSION = "3.0.3"
APP_NAME = "SARA"

class BuilderGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"Constructor de Ejecutable - {APP_NAME}")
        self.root.geometry("550x600")  # Más compacto
        self.root.resizable(True, True)  # Permitir redimensionar
        
        # Variables
        self.compiler = tk.StringVar(value="pyinstaller")  # pyinstaller o nuitka
        self.icon_path = tk.StringVar(value="")
        self.build_type = tk.StringVar(value="onefile")
        self.include_console = tk.BooleanVar(value=False)
        self.optimize_level = tk.StringVar(value="2")
        self.upx_compress = tk.BooleanVar(value=True)
        
        self.setup_ui()
        
    def setup_ui(self):
        # ===== HEADER =====
        header = tk.Frame(self.root, bg="#1a1a1a", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text=f"🚀 Constructor de {APP_NAME}",
            font=("Segoe UI", 16, "bold"),
            bg="#1a1a1a",
            fg="#00ff41"
        )
        title.pack(pady=15)
        
        # ===== CONTENIDO CON SCROLL =====
        # Frame contenedor
        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True)
        
        # Canvas con scrollbar
        canvas = tk.Canvas(container, bg="#2b2b2b", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        
        # Frame scrolleable
        content = tk.Frame(canvas, bg="#2b2b2b")
        
        # Configurar scroll
        content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # --- COMPILADOR ---
        self.create_section(content, "⚙️ Compilador", 0)
        
        compiler_frame = tk.Frame(content, bg="#2b2b2b")
        compiler_frame.grid(row=1, column=0, sticky="ew", pady=5)
        
        tk.Radiobutton(
            compiler_frame,
            text="PyInstaller (Rápido, probado)",
            variable=self.compiler,
            value="pyinstaller",
            bg="#2b2b2b",
            fg="white",
            selectcolor="#1a1a1a",
            font=("Segoe UI", 8)
        ).pack(anchor="w", padx=5, pady=1)
        
        tk.Radiobutton(
            compiler_frame,
            text="Nuitka (Compila a C++, +30% rendimiento) ⭐",
            variable=self.compiler,
            value="nuitka",
            bg="#2b2b2b",
            fg="white",
            selectcolor="#1a1a1a",
            font=("Segoe UI", 8)
        ).pack(anchor="w", padx=5, pady=1)
        
        # --- ICONO ---
        self.create_section(content, "🎨 Icono del Ejecutable", 2)
        
        icon_frame = tk.Frame(content, bg="#2b2b2b")
        icon_frame.grid(row=3, column=0, sticky="ew", pady=5)
        
        self.icon_label = tk.Label(
            icon_frame,
            text="No seleccionado",
            bg="#2b2b2b",
            fg="#888",
            font=("Segoe UI", 8)
        )
        self.icon_label.pack(side="left", padx=5)
        
        tk.Button(
            icon_frame,
            text="📁 Seleccionar",
            command=self.select_icon,
            bg="#0066cc",
            fg="white",
            font=("Segoe UI", 8),
            relief="flat",
            padx=10,
            pady=3
        ).pack(side="right")
        
        tk.Button(
            icon_frame,
            text="🎨 Generar",
            command=self.generate_icon,
            bg="#9b59b6",
            fg="white",
            font=("Segoe UI", 8),
            relief="flat",
            padx=10,
            pady=3
        ).pack(side="right", padx=3)
        
        # --- TIPO DE BUILD ---
        self.create_section(content, "📦 Tipo de Ejecutable", 4)
        
        build_frame = tk.Frame(content, bg="#2b2b2b")
        build_frame.grid(row=5, column=0, sticky="ew", pady=5)
        
        tk.Radiobutton(
            build_frame,
            text="Un solo archivo (.exe) - Recomendado",
            variable=self.build_type,
            value="onefile",
            bg="#2b2b2b",
            fg="white",
            selectcolor="#1a1a1a",
            font=("Segoe UI", 8)
        ).pack(anchor="w", padx=5, pady=1)
        
        tk.Radiobutton(
            build_frame,
            text="Carpeta (testing)",
            variable=self.build_type,
            value="onedir",
            bg="#2b2b2b",
            fg="white",
            selectcolor="#1a1a1a",
            font=("Segoe UI", 8)
        ).pack(anchor="w", padx=5, pady=1)
        
        # --- OPCIONES AVANZADAS ---
        self.create_section(content, "⚙️ Opciones Avanzadas", 6)
        
        options_frame = tk.Frame(content, bg="#2b2b2b")
        options_frame.grid(row=7, column=0, sticky="ew", pady=5)
        
        tk.Checkbutton(
            options_frame,
            text="Mostrar consola (debugging)",
            variable=self.include_console,
            bg="#2b2b2b",
            fg="white",
            selectcolor="#1a1a1a",
            font=("Segoe UI", 8)
        ).pack(anchor="w", padx=5, pady=1)
        
        tk.Checkbutton(
            options_frame,
            text="Compresión UPX (-40% tamaño)",
            variable=self.upx_compress,
            bg="#2b2b2b",
            fg="white",
            selectcolor="#1a1a1a",
            font=("Segoe UI", 8)
        ).pack(anchor="w", padx=5, pady=1)
        
        # Optimización
        opt_frame = tk.Frame(options_frame, bg="#2b2b2b")
        opt_frame.pack(anchor="w", padx=5, pady=2)
        
        tk.Label(
            opt_frame,
            text="Optimización:",
            bg="#2b2b2b",
            fg="white",
            font=("Segoe UI", 8)
        ).pack(side="left")
        
        for level in ["0", "1", "2"]:
            tk.Radiobutton(
                opt_frame,
                text=level,
                variable=self.optimize_level,
                value=level,
                bg="#2b2b2b",
                fg="white",
                selectcolor="#1a1a1a",
                font=("Segoe UI", 8)
            ).pack(side="left", padx=3)
        
        tk.Label(
            opt_frame,
            text="(2=max)",
            bg="#2b2b2b",
            fg="#888",
            font=("Segoe UI", 7)
        ).pack(side="left")
        
        # --- INFO ---
        self.create_section(content, "ℹ️ Información", 8)
        
        info_text = tk.Text(
            content,
            height=5,
            bg="#1a1a1a",
            fg="#ccc",
            font=("Consolas", 7),
            relief="flat",
            padx=8,
            pady=5
        )
        info_text.grid(row=9, column=0, sticky="ew", pady=3)
        
        info_content = f"""📊 Config: v{VERSION} | Python {sys.version.split()[0]}

💡 Tips:
• Un archivo: Fácil distribución
• UPX: -40% tamaño (más lento)
• Optimización 2: Mejor rendimiento"""
        
        info_text.insert("1.0", info_content)
        info_text.config(state="disabled")
        
        # --- BOTONES ---
        button_frame = tk.Frame(content, bg="#2b2b2b")
        button_frame.grid(row=10, column=0, sticky="ew", pady=10)
        
        tk.Button(
            button_frame,
            text="🚀 GENERAR EJECUTABLE",
            command=self.build,
            bg="#00ff41",
            fg="black",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            padx=15,
            pady=10
        ).pack(fill="x", pady=3)
        
        tk.Button(
            button_frame,
            text="📋 Ver Configuración",
            command=self.show_config,
            bg="#555",
            fg="white",
            font=("Segoe UI", 8),
            relief="flat",
            padx=15,
            pady=6
        ).pack(fill="x")
        
        content.grid_columnconfigure(0, weight=1)
    
    def create_section(self, parent, title, row):
        """Crea un título de sección"""
        label = tk.Label(
            parent,
            text=title,
            bg="#2b2b2b",
            fg="#00d4ff",
            font=("Segoe UI", 10, "bold"),
            anchor="w"
        )
        label.grid(row=row, column=0, sticky="ew", pady=(8, 3))
    
    def select_icon(self):
        """Selector de archivo de icono"""
        filename = filedialog.askopenfilename(
            title="Seleccionar icono",
            filetypes=[("Archivos de icono", "*.ico"), ("Todos los archivos", "*.*")]
        )
        if filename:
            self.icon_path.set(filename)
            self.icon_label.config(
                text=f"✓ {Path(filename).name}",
                fg="#00ff41"
            )
    
    def generate_icon(self):
        """Genera un icono simple usando PIL"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Crear imagen 256x256
            size = 256
            img = Image.new('RGB', (size, size), color='#1a1a1a')
            draw = ImageDraw.Draw(img)
            
            # Dibujar círculo de fondo
            draw.ellipse([20, 20, size-20, size-20], fill='#00ff41')
            
            # Dibujar texto "S"
            try:
                font = ImageFont.truetype("arial.ttf", 150)
            except:
                font = ImageFont.load_default()
            
            draw.text((size//2, size//2), "S", fill='#1a1a1a', font=font, anchor="mm")
            
            # Guardar como .ico
            icon_path = "sara_icon.ico"
            img.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            
            self.icon_path.set(icon_path)
            self.icon_label.config(
                text=f"✓ {icon_path} (generado)",
                fg="#00ff41"
            )
            messagebox.showinfo("Éxito", f"Icono generado: {icon_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el icono:\n{e}\n\nInstala Pillow: pip install pillow")
    
    def show_config(self):
        """Muestra la configuración completa del compilador seleccionado"""
        compiler = self.compiler.get()
        
        if compiler == "pyinstaller":
            args = self.get_pyinstaller_args()
            config_text = "Argumentos de PyInstaller:\n\n" + "\n".join(args)
            title = "Configuración de PyInstaller"
        else:
            args = self.get_nuitka_args()
            config_text = "Argumentos de Nuitka:\n\n" + "\n".join(args)
            title = "Configuración de Nuitka"
        
        # Ventana de configuración
        config_win = tk.Toplevel(self.root)
        config_win.title(title)
        config_win.geometry("500x400")
        
        text = tk.Text(config_win, font=("Consolas", 9), padx=10, pady=10)
        text.pack(fill="both", expand=True)
        text.insert("1.0", config_text)
        text.config(state="disabled")
        
        tk.Button(
            config_win,
            text="Cerrar",
            command=config_win.destroy,
            bg="#555",
            fg="white"
        ).pack(pady=10)
    
    def get_pyinstaller_args(self):
        """Genera los argumentos de PyInstaller"""
        args = [
            'sara.py',
            f'--name={APP_NAME}',
            f'--{"onefile" if self.build_type.get() == "onefile" else "onedir"}',
        ]
        
        # Consola
        if not self.include_console.get():
            args.append('--windowed')
        
        # Icono
        if self.icon_path.get():
            args.append(f'--icon={self.icon_path.get()}')
        
        # Optimización
        args.append(f'--optimize={self.optimize_level.get()}')
        
        # UPX
        if not self.upx_compress.get():
            args.append('--noupx')
        
        # Archivos adicionales
        args.extend([
            '--add-data=.env.example;.',
            '--clean',
        ])
        
        # Dependencias ocultas
        hidden_imports = [
            'pystray', 'PIL', 'pygame', 'edge_tts',
            'google.generativeai', 'groq', 'openai', 'dotenv'
        ]
        for imp in hidden_imports:
            args.append(f'--hidden-import={imp}')
        
        # Directorios
        args.extend([
            '--distpath=dist',
            '--workpath=build',
            '--specpath=.',
        ])
        
        return args
    
    def get_nuitka_args(self):
        """Genera los argumentos de Nuitka"""
        args = [
            'sara.py',
            '--standalone',
        ]
        
        # Tipo de build
        if self.build_type.get() == "onefile":
            args.append('--onefile')
        
        # Consola
        if not self.include_console.get():
            args.append('--windows-disable-console')
        
        # Icono
        if self.icon_path.get():
            args.append(f'--windows-icon-from-ico={self.icon_path.get()}')
        
        # Optimización
        if self.optimize_level.get() == "0":
            args.append('--debug')
        else:
            args.append('--lto=yes')  # Link Time Optimization
        
        # Nombre del ejecutable
        args.append(f'--output-filename={APP_NAME}.exe')
        
        # Plugins necesarios
        args.extend([
            '--enable-plugin=tk-inter',  # Para CustomTkinter
            '--enable-plugin=numpy',      # Si se usa
        ])
        
        # Incluir módulos
        args.extend([
            '--include-package=customtkinter',
            '--include-package=pygame',
            '--include-package=edge_tts',
            '--include-package=google.generativeai',
            '--include-package=groq',
            '--include-package=openai',
            '--include-package=dotenv',
            '--include-package=pystray',
            '--include-package=PIL',
        ])
        
        # Archivos de datos
        args.append('--include-data-files=.env.example=.env.example')
        
        # Optimizaciones adicionales
        args.extend([
            '--assume-yes-for-downloads',
            '--show-progress',
            '--show-memory',
        ])
        
        return args
    
    def build(self):
        """Ejecuta el compilador seleccionado"""
        compiler = self.compiler.get()
        
        try:
            # Verificar que el compilador esté instalado
            if compiler == "pyinstaller":
                try:
                    import PyInstaller
                except ImportError:
                    if messagebox.askyesno(
                        "PyInstaller no encontrado",
                        "PyInstaller no está instalado.\n¿Deseas instalarlo ahora?"
                    ):
                        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
                        import PyInstaller
                    else:
                        return
            else:  # nuitka
                # Verificar Nuitka
                result = subprocess.run(
                    [sys.executable, "-m", "nuitka", "--version"],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    if messagebox.askyesno(
                        "Nuitka no encontrado",
                        "Nuitka no está instalado.\n¿Deseas instalarlo ahora?\n\n"
                        "Nota: Nuitka también requiere un compilador C++ (MSVC o MinGW64)"
                    ):
                        subprocess.run([sys.executable, "-m", "pip", "install", "nuitka"])
                    else:
                        return
            
            # Confirmar
            compiler_name = "PyInstaller" if compiler == "pyinstaller" else "Nuitka"
            if not messagebox.askyesno(
                "Confirmar",
                f"Se generará el ejecutable con {compiler_name}:\n\n"
                f"• Compilador: {compiler_name}\n"
                f"• Tipo: {'Un solo archivo' if self.build_type.get() == 'onefile' else 'Carpeta'}\n"
                f"• Consola: {'Sí' if self.include_console.get() else 'No'}\n"
                f"• Optimización: Nivel {self.optimize_level.get()}\n"
                f"• UPX: {'Sí' if self.upx_compress.get() and compiler == 'pyinstaller' else 'No/N/A'}\n"
                f"• Icono: {Path(self.icon_path.get()).name if self.icon_path.get() else 'Por defecto'}\n\n"
                f"¿Continuar?"
            ):
                return
            
            # Generar
            if compiler == "pyinstaller":
                args = self.get_pyinstaller_args()
            else:
                args = self.get_nuitka_args()
            
            messagebox.showinfo(
                "Generando...",
                f"El proceso puede tomar varios minutos.\n"
                f"{'Nuitka es más lento pero genera ejecutables más rápidos.' if compiler == 'nuitka' else ''}\n"
                f"La ventana se cerrará y verás el progreso en la consola."
            )
            
            self.root.destroy()
            
            # Ejecutar compilador
            print("=" * 60)
            print(f"Generando ejecutable de {APP_NAME} v{VERSION}")
            print(f"Compilador: {compiler_name}")
            print("=" * 60)
            print("\nArgumentos:")
            for arg in args:
                print(f"  {arg}")
            print("\n" + "=" * 60)
            
            if compiler == "pyinstaller":
                import PyInstaller.__main__
                PyInstaller.__main__.run(args)
            else:
                # Ejecutar Nuitka
                subprocess.run([sys.executable, "-m", "nuitka"] + args)
            
            print("\n" + "=" * 60)
            print("✓ Ejecutable generado exitosamente")
            print(f"📁 Ubicación: dist/{APP_NAME}.exe")
            if compiler == "nuitka":
                print("\n💡 Nuitka genera ejecutables compilados a C++")
                print("   Deberían ser ~30% más rápidos que PyInstaller")
            print("=" * 60)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar ejecutable:\n{e}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = BuilderGUI()
    app.run()
