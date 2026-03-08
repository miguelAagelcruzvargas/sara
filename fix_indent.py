"""Script mejorado para corregir TODAS las indentaciones en user_profile.py"""

# Leer archivo
with open('user_profile.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Línea 39 (índice 38): necesita 4 espacios más
if lines[38].strip().startswith('self.cursor.execute("ALTER'):
    lines[38] = '                    ' + lines[38].lstrip()

# Guardar archivo corregido
with open('user_profile.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Indentación corregida completamente")
