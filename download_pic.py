import os
import re
import requests
import subprocess
from datetime import datetime

# 1. Diccionario para pasar el nombre del mes a inglés limpio
MESES = {
    1: "january", 2: "february", 3: "march", 4: "april",
    5: "may", 6: "june", 7: "july", 8: "august",
    9: "september", 10: "october", 11: "november", 12: "december"
}

# 2. Extracción de la API Key desde tu app.js (Tal cual funcionaba antes)
api_key = None
if os.path.exists("app.js"):
    with open("app.js", "r") as f:
        contenido = f.read()
        match = re.search(r"const\s+API_KEY\s*=\s*['\"]([^'\"]+)['\"]", contenido)
        if match:
            api_key = match.group(1)

if not api_key or api_key == "DEMO_KEY" or "AQUÍ" in api_key:
    print("❌ No encontramos una API Key válida en tu app.js.")
    exit()

print(f"✅ API Key encontrada (últimos 4 caracteres): ...{api_key[-4:]}")

# 3. Configuración de Carpetas Dinámicas por Mes y Año
fecha_actual = datetime.now()
nombre_mes = MESES[fecha_actual.month]
año_actual = fecha_actual.year

# Nombre de la carpeta: "nasapics june 2026"
nombre_carpeta_mes = f"nasapics {nombre_mes} {año_actual}"

# Creamos la carpeta de forma local en Linux para que no se cuelgue WSL
RUTA_LOCAL = nombre_carpeta_mes
os.makedirs(RUTA_LOCAL, exist_ok=True)

# 4. Enlace automático con tu disco C de Windows (solo en WSL local)
# Skip this in GitHub Actions environment
if not os.getenv("GITHUB_ACTIONS"):
    ruta_absoluta_local = os.path.abspath(RUTA_LOCAL)
    ruta_windows_target = f"/mnt/c/VS CODE PROJECTS/nasapics/{nombre_carpeta_mes}"
    
    if not os.path.exists(ruta_windows_target):
        try:
            # Ejecuta el comando de Linux para crear el acceso directo en Windows de forma automática
            subprocess.run(["ln", "-s", ruta_absoluta_local, ruta_windows_target], check=True)
            print(f"🔗 Enlace creado automáticamente con Windows para: {nombre_carpeta_mes}")
        except Exception as e:
            print(f"⚠️ Nota sobre el enlace de Windows: {e}")
else:
    print(f"📁 Corriendo en GitHub Actions. Las imágenes se guardarán en: {RUTA_LOCAL}")

# 5. Petición y descarga a la API de la NASA
URL_NASA = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"

try:
    print("🛰️ Conectando con la API de la NASA...")
    respuesta_raw = requests.get(URL_NASA)
    
    # Check if the request was successful
    if respuesta_raw.status_code != 200:
        print(f"❌ Error HTTP {respuesta_raw.status_code}: {respuesta_raw.text}")
        exit()
    
    respuesta = respuesta_raw.json()
    
    if "error" in respuesta:
        print(f"❌ Error de la NASA: {respuesta['error']['message']}")
        exit()
        
    if "media_type" in respuesta:
        media_type = respuesta["media_type"]
        titulo = respuesta["title"].replace(" ", "_").lower()
        titulo = "".join(c for c in titulo if c.isalnum() or c == "_")
        fecha_str = fecha_actual.strftime("%Y-%m-%d")
        
        # CASO 1: SI ES UNA IMAGEN
        if media_type == "image":
            url_imagen = respuesta["url"]
            url_sin_parametros = url_imagen.split("?")[0]
            extension = url_sin_parametros.split(".")[-1]
            if len(extension) > 4 or not extension:
                extension = "jpg"
                
            # Guardamos el archivo adentro de la carpeta mensual
            nombre_archivo = f"{fecha_str}-{titulo}.{extension}"
            ruta_final_archivo = os.path.join(RUTA_LOCAL, nombre_archivo)
            
            print(f"🚀 Descargando imagen de hoy: {respuesta['title']}...")
            img_data = requests.get(url_imagen).content
            with open(ruta_final_archivo, 'wb') as handler:
                handler.write(img_data)
            print(f"✅ ¡Éxito! Imagen guardada en: {ruta_final_archivo}")
            
        # CASO 2: SI ES UN VIDEO
        elif media_type == "video":
            url_video = respuesta["url"]
            nombre_archivo = f"{fecha_str}-{titulo}-link_video.txt"
            ruta_final_archivo = os.path.join(RUTA_LOCAL, nombre_archivo)
            
            print(f"🎥 ¡Hoy la NASA publicó un video!: {respuesta['title']}")
            with open(ruta_final_archivo, 'w') as handler:
                handler.write(f"Título: {respuesta['title']}\nEnlace: {url_video}\n")
            print(f"🔗 Guardado link del video en: {ruta_final_archivo}")
            
    else:
        print("❌ Estructura inesperada de la respuesta de la NASA.")

except Exception as e:
    print(f"❌ Hubo un error inesperado: {e}")