// Definimos la dirección de la NASA y la clave de acceso de prueba
const API_KEY = 'DEMO_KEY';
const URL_NASA = `https://api.nasa.gov/planetary/apod?api_key=${API_KEY}`;

// Traemos los elementos del HTML para poder cambiarlos desde acá
const picTitle = document.getElementById('pic-title');
const picImage = document.getElementById('pic-image');
const picExplanation = document.getElementById('pic-explanation');

// Creamos la función que viaja a internet a buscar la foto
async function obtenerFotoNasa() {
    try {
        // Hacemos el llamado a los servidores de la NASA
        const respuesta = await fetch(URL_NASA);
        
        // Convertimos la respuesta cruda en un objeto JSON fácil de leer
        const datos = await respuesta.json();
        
        // Reemplazamos los textos del HTML con la info real de la NASA
        picTitle.innerText = datos.title;
        picExplanation.innerText = datos.explanation;
        
        // Le pasamos la URL de la imagen a nuestra etiqueta <img> y la hacemos visible
        picImage.src = datos.url;
        picImage.style.display = 'block';

    } catch (error) {
        // Si algo falla (ej: te quedaste sin internet), mostramos el error
        console.error("Hubo un error al conectar con la NASA:", error);
        picTitle.innerText = "❌ Error al conectar con el espacio";
        picExplanation.innerText = "No pudimos recibir la señal de la NASA. Revisa tu conexión a internet.";
    }
}

// Ejecutamos la función apenas se carga la página
obtenerFotoNasa();