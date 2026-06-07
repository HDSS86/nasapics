import os
import re
import requests
from datetime import datetime

# Buscamos la API Key que ya guardaste y funciona en tu archivo app.js
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

URL_NASA = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"

try:
    respuesta = requests.get(URL_NASA).json()
    
    if "error" in respuesta:
        print(f"❌ Error de la NASA: {respuesta['error']['message']}")
        exit()
        
    if "media_type" in respuesta:
        media_type = respuesta["media_type"]
        titulo = respuesta["title"].replace(" ", "_").lower()
        titulo = "".join(c for c in titulo if c.isalnum() or c == "_")
        fecha = datetime.now().strftime("%Y-%m-%d")
        
        # SI ES UNA IMAGEN
        if media_type == "image":
            url_imagen = respuesta["url"]
            
            # Limpieza inteligente de la extensión (por si viene con cosas como ?download=true)
            url_sin_parametros = url_imagen.split("?")[0]
            extension = url_sin_parametros.split(".")[-1]
            
            # Si no detecta extensión válida, le mandamos jpg por defecto
            if len(extension) > 4 or not extension:
                extension = "jpg"
                
            nombre_archivo = f"{fecha}-{titulo}.{extension}"
            
            print(f"🚀 Descargando imagen de hoy: {respuesta['title']}...")
            img_data = requests.get(url_imagen).content
            with open(nombre_archivo, 'wb') as handler:
                handler.write(img_data)
            print(f"✅ ¡Éxito! Imagen guardada como: {nombre_archivo}")
            
        # SI ES UN VIDEO
        elif media_type == "video":
            url_video = respuesta["url"]
            nombre_archivo = f"{fecha}-{titulo}-link_video.txt"
            print(f"🎥 ¡Hoy la NASA publicó un video!: {respuesta['title']}")
            with open(nombre_archivo, 'w') as handler:
                handler.write(f"Título: {respuesta['title']}\nEnlace: {url_video}\n")
            print(f"🔗 Guardado link del video en: {nombre_archivo}")
            
    else:
        print("❌ Estructura inesperada de la respuesta de la NASA.")

except Exception as e:
    print(f"❌ Hubo un error: {e}")