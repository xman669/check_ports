import requests
import psutil
import os
import platform
import time

# Clave de API de VirusTotal
API_KEY = "3ebd11a9c4e57438b49ce6eb2655c5c62d4bbbbadc1c92f8aeae24f925fe0d02"

def verificar_ip_virustotal(ip):
    """
    Consulta la API de VirusTotal para comprobar si una IP es maliciosa.
    """
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    headers = {"x-apikey": API_KEY}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            detections = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            malicious = detections.get("malicious", 0)
            suspicious = detections.get("suspicious", 0)

            if malicious > 0:
                return f"⚠️ Maliciosa ({malicious} detecciones)"
            elif suspicious > 0:
                return f"⚠️ Sospechosa ({suspicious} detecciones)"
            else:
                return "✅ Segura"
        else:
            return "❓ No disponible"
    except Exception as e:
        return f"⚠️ Error: {e}"

def obtener_conexiones():
    """
    Obtiene todas las conexiones activas en la PC y muestra información relevante.
    """
    conexiones = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status not in ["LISTEN", "CLOSE_WAIT"]:
            try:
                proceso = psutil.Process(conn.pid) if conn.pid else None
                nombre_proceso = proceso.name() if proceso else "Desconocido"
                ip_remota = conn.raddr.ip if conn.raddr else None

                # Verificar si hay una IP remota
                estado_ip = verificar_ip_virustotal(ip_remota) if ip_remota else "N/A"

                conexiones.append({
                    "PID": conn.pid if conn.pid is not None else "N/A",
                    "Proceso": nombre_proceso,
                    "Puerto Local": conn.laddr.port if conn.laddr else "N/A",
                    "Dirección Remota": f"{ip_remota}:{conn.raddr.port}" if conn.raddr else "N/A",
                    "VirusTotal": estado_ip,
                    "Estado": conn.status
                })

                # Esperar para evitar el rate limit de VirusTotal
                time.sleep(1)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    return conexiones

def mostrar_conexiones():
    """
    Muestra las conexiones activas en un formato legible junto con la información de VirusTotal.
    """
    conexiones = obtener_conexiones()
    print(f"\n{'PID':<10}{'Proceso':<25}{'Puerto Local':<15}{'Dirección Remota':<25}{'VirusTotal':<20}{'Estado':<15}")
    print("-" * 115)
    for conn in conexiones:
        print(f"{conn['PID']:<10}{conn['Proceso']:<25}{conn['Puerto Local']:<15}{conn['Dirección Remota']:<25}{conn['VirusTotal']:<20}{conn['Estado']:<15}")

def cerrar_conexion(pid):
    """
    Cierra una conexión finalizando su proceso.
    """
    try:
        if platform.system() == "Windows":
            os.system(f"taskkill /PID {pid} /F")
        else:
            os.system(f"kill -9 {pid}")
        print(f"✅ Proceso con PID {pid} finalizado exitosamente.")
    except Exception as e:
        print(f"⚠️ Error al cerrar la conexión: {e}")

def menu():
    """
    Menú interactivo para el usuario.
    """
    while True:
        print("\n🔍 Monitoreo de Conexiones de Red")
        mostrar_conexiones()
        
        opcion = input("\n🔴 ¿Deseas cerrar alguna conexión? (s/n): ").strip().lower()
        if opcion == "s":
            try:
                pids = input("📌 Ingresa el PID o PIDs separados por comas: ")
                pids = [int(pid.strip()) for pid in pids.split(",") if pid.strip().isdigit()]
                for pid in pids:
                    cerrar_conexion(pid)
            except ValueError:
                print("❌ Entrada no válida. Debes ingresar números.")
        else:
            print("👋 Saliendo del programa.")
            break

if __name__ == "__main__":
    menu()