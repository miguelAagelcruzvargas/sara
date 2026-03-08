"""Script COMPLETO para corregir TODAS las indentaciones en user_profile.py"""

# Leer archivo
with open('user_profile.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar el método _init_database completo con la versión correcta
old_init = '''    def _init_database(self):
        """Inicializa la base de datos y crea las tablas si no existen"""
        with self.db_lock:
            try:
                self.conn = sqlite3.connect(self.DB_FILE, check_same_thread=False)
                self.cursor = self.conn.cursor()
            
                # Tablas (compactado para no repetir todo)
                self.cursor.execute('''

new_init = '''    def _init_database(self):
        """Inicializa la base de datos y crea las tablas si no existen"""
        with self.db_lock:
            try:
                self.conn = sqlite3.connect(self.DB_FILE, check_same_thread=False)
                self.cursor = self.conn.cursor()
            
                # Tablas (compactado para no repetir todo)
                self.cursor.execute('''

# El problema es que necesitamos indentar TODO lo que está dentro del with/try
# Vamos a hacerlo línea por línea

lines = content.split('\n')
fixed_lines = []
in_with_block = False
in_try_block = False
base_indent = 0

for i, line in enumerate(lines):
    # Detectar inicio de with self.db_lock:
    if 'with self.db_lock:' in line:
        in_with_block = True
        base_indent = len(line) - len(line.lstrip())
        fixed_lines.append(line)
        continue
    
    # Detectar fin del bloque with (cuando la indentación vuelve al nivel base)
    if in_with_block:
        current_indent = len(line) - len(line.lstrip())
        if line.strip() and current_indent <= base_indent:
            in_with_block = False
            in_try_block = False
    
    # Si estamos dentro de un bloque with, asegurar indentación correcta
    if in_with_block and line.strip():
        # Verificar si es un try:
        if line.strip() == 'try:':
            in_try_block = True
            # Debe tener base_indent + 4
            fixed_lines.append(' ' * (base_indent + 4) + 'try:')
            continue
        
        # Verificar si es except:
        if line.strip().startswith('except'):
            in_try_block = False
            # Debe tener base_indent + 4
            fixed_lines.append(' ' * (base_indent + 4) + line.strip())
            continue
        
        # Si estamos en try block, todo debe tener base_indent + 8
        if in_try_block:
            if current_indent < base_indent + 8:
                fixed_lines.append(' ' * (base_indent + 8) + line.lstrip())
                continue
    
    fixed_lines.append(line)

# Guardar
with open('user_profile.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed_lines))

print("✅ TODAS las indentaciones corregidas")
