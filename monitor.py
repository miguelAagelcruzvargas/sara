import psutil
import subprocess
import socket
import re
import ipaddress
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

# ==================== UTILIDADES DE RED ====================

def validar_ip(ip_str: str) -> bool:
    """Valida si una cadena es una dirección IP válida."""
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False

def validar_mac(mac_str: str) -> bool:
    """Valida si una cadena es una dirección MAC válida."""
    # Formato: XX:XX:XX:XX:XX:XX o XX-XX-XX-XX-XX-XX
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    return bool(re.match(pattern, mac_str))

def normalizar_mac(mac_str: str) -> str:
    """Normaliza formato de MAC a XX:XX:XX:XX:XX:XX."""
    return mac_str.replace('-', ':').upper()

def obtener_fabricante_extendido(mac: str) -> str:
    """
    Obtiene el fabricante del dispositivo basándose en el OUI (MAC prefix).
    Base de datos extendida de fabricantes.
    """
    mac_prefix = mac[:8].upper()
    
    fabricantes = {
        # Virtualization
        '00:50:56': 'VMware Virtual',
        '00:0C:29': 'VMware Virtual',
        '00:05:69': 'VMware Virtual',
        '08:00:27': 'VirtualBox',
        '00:15:5D': 'Microsoft Hyper-V',
        
        # Raspberry Pi
        'DC:A6:32': 'Raspberry Pi',
        'B8:27:EB': 'Raspberry Pi',
        'E4:5F:01': 'Raspberry Pi',
        '28:CD:C1': 'Raspberry Pi',
        'D8:3A:DD': 'Raspberry Pi',
        
        # TP-Link
        'B0:4E:26': 'TP-Link',
        '50:C7:BF': 'TP-Link',
        'A0:F3:C1': 'TP-Link',
        '14:CC:20': 'TP-Link',
        'C0:25:E9': 'TP-Link',
        
        # Xiaomi
        '18:E8:29': 'Xiaomi',
        '34:CE:00': 'Xiaomi',
        '64:09:80': 'Xiaomi',
        'F4:8E:92': 'Xiaomi',
        '28:6C:07': 'Xiaomi',
        '50:8F:4C': 'Xiaomi',
        
        # Samsung
        '3C:28:6D': 'Samsung',
        '00:12:FB': 'Samsung',
        '00:1D:25': 'Samsung',
        '00:1E:7D': 'Samsung',
        '5C:0A:5B': 'Samsung',
        '68:EB:C5': 'Samsung',
        
        # Google
        '00:1A:11': 'Google',
        'F4:F5:D8': 'Google',
        '54:60:09': 'Google',
        '3C:5A:B4': 'Google Chromecast',
        '6C:AD:F8': 'Google Home',
        
        # Amazon
        'AC:63:BE': 'Amazon Echo',
        '74:C2:46': 'Amazon Echo',
        '00:FC:8B': 'Amazon',
        'F0:D2:F1': 'Amazon Fire TV',
        
        # Apple
        '00:03:93': 'Apple',
        '00:0A:27': 'Apple',
        '00:0A:95': 'Apple',
        '00:0D:93': 'Apple',
        '00:17:F2': 'Apple',
        '00:1B:63': 'Apple',
        '00:1C:B3': 'Apple',
        '00:1E:52': 'Apple',
        '00:1F:5B': 'Apple',
        '00:1F:F3': 'Apple',
        '00:21:E9': 'Apple',
        '00:22:41': 'Apple',
        '00:23:12': 'Apple',
        '00:23:32': 'Apple',
        '00:23:6C': 'Apple',
        '00:23:DF': 'Apple',
        '00:24:36': 'Apple',
        '00:25:00': 'Apple',
        '00:25:4B': 'Apple',
        '00:25:BC': 'Apple',
        '00:26:08': 'Apple',
        '00:26:4A': 'Apple',
        '00:26:B0': 'Apple',
        '00:26:BB': 'Apple',
        
        # Huawei
        '00:E0:FC': 'Huawei',
        '08:7A:4C': 'Huawei',
        '0C:37:DC': 'Huawei',
        '28:6E:D4': 'Huawei',
        '4C:54:99': 'Huawei',
        
        # Intel
        '00:02:B3': 'Intel',
        '00:03:47': 'Intel',
        '00:04:23': 'Intel',
        '00:07:E9': 'Intel',
        '00:0E:0C': 'Intel',
        '00:13:02': 'Intel',
        '00:13:20': 'Intel',
        '00:13:CE': 'Intel',
        '00:15:00': 'Intel',
        '00:16:6F': 'Intel',
        '00:16:76': 'Intel',
        '00:16:EA': 'Intel',
        '00:16:EB': 'Intel',
        
        # Realtek
        '00:E0:4C': 'Realtek',
        '52:54:00': 'Realtek',
        
        # D-Link
        '00:05:5D': 'D-Link',
        '00:0D:88': 'D-Link',
        '00:11:95': 'D-Link',
        '00:13:46': 'D-Link',
        '00:15:E9': 'D-Link',
        '00:17:9A': 'D-Link',
        '00:19:5B': 'D-Link',
        '00:1B:11': 'D-Link',
        '00:1C:F0': 'D-Link',
        '00:1E:58': 'D-Link',
        
        # Cisco
        '00:00:0C': 'Cisco',
        '00:01:42': 'Cisco',
        '00:01:43': 'Cisco',
        '00:01:63': 'Cisco',
        '00:01:64': 'Cisco',
        '00:01:96': 'Cisco',
        '00:01:97': 'Cisco',
        '00:01:C7': 'Cisco',
        '00:01:C9': 'Cisco',
        '00:02:16': 'Cisco',
        '00:02:17': 'Cisco',
        
        # Netgear
        '00:09:5B': 'Netgear',
        '00:0F:B5': 'Netgear',
        '00:14:6C': 'Netgear',
        '00:18:4D': 'Netgear',
        '00:1B:2F': 'Netgear',
        '00:1E:2A': 'Netgear',
        '00:1F:33': 'Netgear',
        '00:22:3F': 'Netgear',
        '00:24:B2': 'Netgear',
        '00:26:F2': 'Netgear',
        
        # Linksys
        '00:04:5A': 'Linksys',
        '00:06:25': 'Linksys',
        '00:0C:41': 'Linksys',
        '00:0E:08': 'Linksys',
        '00:0F:66': 'Linksys',
        '00:12:17': 'Linksys',
        '00:13:10': 'Linksys',
        '00:14:BF': 'Linksys',
        '00:16:B6': 'Linksys',
        '00:18:39': 'Linksys',
        '00:18:F8': 'Linksys',
        '00:1A:70': 'Linksys',
        '00:1C:10': 'Linksys',
        '00:1D:7E': 'Linksys',
        '00:1E:E5': 'Linksys',
        '00:20:E0': 'Linksys',
        '00:21:29': 'Linksys',
        '00:22:6B': 'Linksys',
        '00:23:69': 'Linksys',
        '00:25:9C': 'Linksys',
    }
    
    return fabricantes.get(mac_prefix, "Dispositivo Desconocido")

# ==================== CLASE PRINCIPAL ====================

class SystemMonitor:
    @staticmethod
    def obtener_reporte_completo():
        # CPU
        cpu_uso = psutil.cpu_percent(interval=0.1)
        cpu_freq = psutil.cpu_freq().current if psutil.cpu_freq() else 0
        
        # RAM
        ram = psutil.virtual_memory()
        ram_total = round(ram.total / (1024**3), 1)
        ram_uso = ram.percent

        # DISCO
        disco = psutil.disk_usage('/')
        disco_libre = round(disco.free / (1024**3), 1)

        # BATERÍA
        bateria = psutil.sensors_battery()
        bat_info = f"{bateria.percent}%" if bateria else "AC/PC"
        enchufado = "Cargando" if bateria and bateria.power_plugged else "Batería"

        # RED
        red = psutil.net_io_counters()
        bytes_env = round(red.bytes_sent / (1024**2), 1)
        bytes_rec = round(red.bytes_recv / (1024**2), 1)

        reporte = (
            f"📊 ESTADO DEL SISTEMA:\n"
            f"► CPU: {cpu_uso}% @ {cpu_freq:.0f}Mhz\n"
            f"► RAM: {ram_uso}% de {ram_total}GB\n"
            f"► Disco C: {disco_libre} GB Libres\n"
            f"► Energía: {bat_info} ({enchufado})\n"
            f"► Red: ↑{bytes_env}MB  ↓{bytes_rec}MB"
        )
        return reporte
    
    @staticmethod
    def escanear_red():
        """Escanea la red local - Fuerza actualización de ARP con ping masivo"""
        try:
            # Obtener IP local
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            base_ip = '.'.join(local_ip.split('.')[:-1])
            
            # PASO 1: Hacer ping masivo a todo el rango para forzar respuestas ARP
            # Esto actualiza el cache ARP con TODOS los dispositivos activos
            import concurrent.futures
            
            def ping_rapido(ip):
                """Ping ultra rápido solo para actualizar ARP"""
                try:
                    subprocess.run(
                        f"ping -n 1 -w 100 {ip}",
                        shell=True,
                        capture_output=True,
                        timeout=0.5
                    )
                except:
                    pass
            
            # Ejecutar pings en paralelo a todo el rango
            with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
                ips_a_escanear = [f"{base_ip}.{i}" for i in range(1, 255)]
                executor.map(ping_rapido, ips_a_escanear)
            
            # PASO 2: Esperar un momento para que el cache ARP se actualice
            import time
            time.sleep(0.5)
            
            # PASO 3: Leer TODO el cache ARP (ahora debería tener todos los dispositivos)
            dispositivos = {}
            
            try:
                result = subprocess.check_output(
                    "arp -a", 
                    shell=True, 
                    text=True,
                    timeout=3
                )
                
                for line in result.split('\n'):
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+([\da-fA-F\-:]+)', line)
                    if match:
                        ip = match.group(1)
                        mac = match.group(2).replace('-', ':')
                        
                        # Filtrar solo IPs de nuestra red y válidas
                        if (ip.startswith(base_ip) and 
                            not ip.endswith('.255') and
                            mac.lower() != 'ff:ff:ff:ff:ff:ff' and
                            len(mac) >= 17):  # MAC válido
                            
                            tipo = SystemMonitor._identificar_dispositivo(mac, ip, local_ip)
                            dispositivos[ip] = {
                                'ip': ip,
                                'mac': mac,
                                'tipo': tipo
                            }
            except Exception as e:
                pass
            
            # Convertir a lista y ordenar
            lista_dispositivos = list(dispositivos.values())
            lista_dispositivos.sort(key=lambda x: [int(n) for n in x['ip'].split('.')])
            
            return {
                'total': len(lista_dispositivos),
                'dispositivos': lista_dispositivos,
                'ip_local': local_ip
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def _identificar_dispositivo(mac, ip, local_ip):
        """Intenta identificar el tipo de dispositivo con base de datos extendida."""
        # Validar MAC
        if not validar_mac(mac):
            return "Dispositivo Inválido"
        
        # Normalizar MAC
        mac = normalizar_mac(mac)
        
        # Si es la IP local
        if ip == local_ip:
            return "Este PC"
        
        # Gateway (usualmente .1 o .254)
        if ip.endswith('.1') or ip.endswith('.254'):
            return "Router/Gateway"
        
        # Usar base de datos extendida de fabricantes
        return obtener_fabricante_extendido(mac)
    
    @staticmethod
    def investigar_dispositivo(ip):
        """Investiga un dispositivo específico en detalle"""
        info = {
            'ip': ip,
            'activo': False,
            'hostname': 'Desconocido',
            'puertos_abiertos': [],
            'os_probable': 'Desconocido',
            'latencia': 'N/A'
        }
        
        try:
            # 1. Ping para verificar si está activo
            result = subprocess.run(
                f"ping -n 1 -w 1000 {ip}",
                capture_output=True,
                text=True,
                timeout=3,
                shell=True
            )
            
            if result.returncode == 0:
                info['activo'] = True
                
                # Extraer latencia
                if 'tiempo=' in result.stdout or 'time=' in result.stdout:
                    try:
                        latencia_str = result.stdout.split('tiempo=')[1].split('ms')[0] if 'tiempo=' in result.stdout else result.stdout.split('time=')[1].split('ms')[0]
                        info['latencia'] = f"{latencia_str.strip()}ms"
                    except:
                        pass
                
                # Detectar OS por TTL
                if 'TTL=' in result.stdout:
                    try:
                        ttl = int(result.stdout.split('TTL=')[1].split()[0])
                        if ttl <= 64:
                            info['os_probable'] = 'Linux/Mac/Android'
                        elif ttl <= 128:
                            info['os_probable'] = 'Windows'
                        else:
                            info['os_probable'] = 'Router/IoT'
                    except:
                        pass
        except:
            pass
        
        # 2. Intentar resolver hostname
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            info['hostname'] = hostname
        except:
            pass
        
        # 3. Escanear puertos comunes (solo si está activo)
        if info['activo']:
            puertos_comunes = {
                80: 'HTTP',
                443: 'HTTPS',
                22: 'SSH',
                3389: 'RDP',
                445: 'SMB',
                8080: 'HTTP-Alt',
                21: 'FTP',
                23: 'Telnet'
            }
            
            for puerto, servicio in puertos_comunes.items():
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.3)
                try:
                    result = sock.connect_ex((ip, puerto))
                    if result == 0:
                        info['puertos_abiertos'].append(f"{puerto} ({servicio})")
                except:
                    pass
                finally:
                    sock.close()
        
        return info
    
    @staticmethod
    def bloquear_ip_local(ip):
        """Bloquea una IP en el firewall de Windows (requiere admin)"""
        try:
            # Crear regla de firewall para bloquear salida
            cmd = f'netsh advfirewall firewall add rule name="SARA_Block_{ip}" dir=out action=block remoteip={ip}'
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return {
                    'exito': True,
                    'mensaje': f"✅ IP {ip} bloqueada en firewall local.\nNo podrás comunicarte con este dispositivo desde este PC."
                }
            else:
                # Verificar si es por falta de permisos
                if 'acceso' in result.stderr.lower() or 'denied' in result.stderr.lower():
                    return {
                        'exito': False,
                        'mensaje': f"❌ Error: Se requieren permisos de administrador.\nEjecuta SARA como administrador para bloquear dispositivos."
                    }
                else:
                    return {
                        'exito': False,
                        'mensaje': f"❌ Error al bloquear: {result.stderr[:100]}"
                    }
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f"❌ Error: {str(e)}"
            }
    
    @staticmethod
    def desbloquear_ip_local(ip):
        """Desbloquea una IP del firewall de Windows"""
        try:
            # Eliminar regla de firewall
            cmd = f'netsh advfirewall firewall delete rule name="SARA_Block_{ip}"'
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return {
                    'exito': True,
                    'mensaje': f"✅ IP {ip} desbloqueada.\nAhora puedes comunicarte normalmente con este dispositivo."
                }
            else:
                return {
                    'exito': False,
                    'mensaje': f"⚠️ No se encontró ninguna regla de bloqueo para {ip}.\nQuizás ya estaba desbloqueada."
                }
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f"❌ Error: {str(e)}"
            }
