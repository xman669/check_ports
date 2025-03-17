import psutil
import os
import platform

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
                conexiones.append({
                    "PID": conn.pid if conn.pid is not None else "N/A",
                    "Proceso": nombre_proceso,
                    "Puerto Local": conn.laddr.port if conn.laddr else "N/A",
                    "Dirección Remota": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                    "Estado": conn.status
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    return conexiones

def mostrar_conexiones():
    """
    Muestra las conexiones activas en un formato legible.
    """
    conexiones = obtener_conexiones()
    print(f"\n{'PID':<10}{'Proceso':<25}{'Puerto Local':<15}{'Dirección Remota':<25}{'Estado':<15}")
    print("-" * 90)
    for conn in conexiones:
        print(f"{conn['PID']:<10}{conn['Proceso']:<25}{conn['Puerto Local']:<15}{conn['Dirección Remota']:<25}{conn['Estado']:<15}")

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