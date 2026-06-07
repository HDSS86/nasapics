import os
import re
import requests
import subprocess
from datetime import datetime

# 1. Diccionario de meses
MESES = {
    1: "january", 2: "february", 3: "march", 4: "april",
    5: "may", 6: "june", 7: "july", 8: "august",
    9: "september", 10: "october", 11: "november", 12: "december"
}

# 2. Leer API Key de app.js
api_key = None
if os.path.exists("app.js"):
    with open("app.js", "r") as f:
        contenido = f.read()
        match = re.search(r"const\s+API_KEY\s*=\s*['\"]([^'\"]+)['\"]", contenido)
        if match:
            api_key = match.group(1)

if not api_key:
    print("❌ No encontramos una API Key válida.")
    exit()

# 3. Rutas y Carpetas Dinámicas
fecha_actual = datetime.now()
nombre_mes = MESES[fecha_actual.month]
año_actual = fecha_actual.year
nombre_carpeta_mes = f"nasapics {nombre_mes} {año_actual}"

# Ruta local dentro de Linux WSL
RUTA_LOCAL = nombre_carpeta_mes
os.makedirs(RUTA_LOCAL, exist_ok=True)

# 4. PUENTE AUTOMÁTICO CON WINDOWS
# Creamos el enlace simbólico desde Python para que aparezca en tu disco C automáticamente
ruta_absoluta_local = os.path.abspath(RUTA_LOCAL)
ruta_windows_target = f"/mnt/c/VS CODE PROJECTS/nasapics/{nombre_carpeta_mes}"

if not os.path.exists(ruta_windows_target):
    try:
        # Ejecuta el comando de enlace de Linux de forma silenciosa si no existe el puente
        subprocess.run(["ln", "-s", ruta_absoluta_local, ruta_windows_target], check=True)
        print(f"🔗 Enlace creado con éxito en Windows para: {nombre_carpeta_mes}")
    except Exception as e:
        # Si por alguna razón de permisos de WSL no puede, el script sigue adelante localmente
        print(f"⚠️ Nota: No se pudo crear el acceso directo en Windows de forma automática: {e}")

# 5. Conexión con la NASA
URL_NASA = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"

try:
    print("🛰️ Conectando con la NASA...")
    respuesta = requests.get(URL_NASA, timeout=15).json()
    
    if "error" in respuesta:
        print(f"❌ Error de la NASA: {respuesta['error']['message']}")
        exit()
        
    if "media_type" in respuesta:
        media_type = respuesta["media_type"]
        titulo = respuesta["title"].replace(" ", "_").lower()
        titulo = "".join(c for c in titulo if c.isalnum() or c == "_")
        fecha_str = fecha_actual.strftime("%Y-%m-%d")
        
        # IMAGEN
        if media_type == "image":
            url_imagen = respuesta["url"]
            extension = url_imagen.split("?")[0].split(".")[-1]
            if len(extension) > 4 or not extension:
                extension = "jpg"
                
            nombre_archivo = f"{fecha_str}-{titulo}.{extension}"
            ruta_final_archivo = os.path.join(RUTA_LOCAL, nombre_archivo)
            
            print(f"🚀 Descargando imagen de hoy: {respuesta['title']}...")
            img_data = requests.get(url_imagen, timeout=15).content
            
            with open(ruta_final_archivo, 'wb') as handler:
                handler.write(img_data)
                
            print(f"✅ ¡Éxito! Guardada en su carpeta: {ruta_final_archivo}")
            
        # VIDEO
        elif media_type == "video":
            url_video = respuesta["url"]
            nombre_archivo = f"{fecha_str}-{titulo}-link_video.txt"
            ruta_final_archivo = os.path.join(RUTA_LOCAL, nombre_archivo)
            
            print("🎥 Guardando link del video...")
            with open(ruta_final_archivo, 'w') as handler:
                handler.write(f"Título: {respuesta['title']}\nEnlace: {url_video}\n")
            print("🔗 ¡Éxito! Link guardado.")
            
except Exception as e:
    print(f"❌ Hubo un error: {e}")