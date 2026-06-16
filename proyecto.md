# OBJETIVO DEL PROMPT
Actúa como un Desarrollador Senior de Software experto en Python, Flask, la API de YouTube y automatización multimedia con `yt-dlp`. Tu tarea es generar el código completo, limpio, modular y 100% funcional de una aplicación web local de streaming y descarga de música desde YouTube, siguiendo estrictamente la estructura de archivos y requerimientos detallados a continuación. No uses pseudocódigo ni dejes secciones sin implementar ("TODOs").

---

# PILARES TECNOLÓGICOS Y ARQUITECTURA
- **Backend:** Python 3.11+, Flask.
- **Frontend:** Interfaz monopágina (SPA) usando HTML5, CSS Nativo/Tailwind CSS (vía CDN), y Jinja2 para el renderizado inicial.
- **Extracción de Medios:** `yt-dlp` en modo síncrono para metadatos/streaming, y procesamiento asíncrono nativo (`threading`) junto con FFmpeg para la conversión local a MP3.
- **Autenticación:** Google API Client Library (`google-auth-oauthlib`, `google-api-python-client`) para OAuth 2.0 e integración con la API de YouTube Data v3.

---

# REQUERIMIENTOS TÉCNICOS DETALLADOS

## 1. Autenticación e Integración con YouTube (OAuth 2.0)
- Configura el flujo para solicitar acceso local de tipo offline (`access_type='offline'`) e introduce control para la renovación automática del Access Token usando el **Refresh Token** almacenado en la sesión segura de Flask (`app.secret_key`).
- Rutas requeridas: `/login`, `/callback`, y `/logout`.
- Endpoint para listar las Playlists del usuario, priorizando y extrayendo de manera automática la playlist especial `"Videos que me gustan"` (`LL` o Liked Videos).

## 2. Buscador, Caché y Streaming en Tiempo Real
- El buscador en el backend debe aceptar tanto palabras clave (usando `ytsearch:` con `yt-dlp`) como URLs directas de YouTube.
- **Sistema de Caché de Streaming (Crítico):** Las URLs devueltas por `yt-dlp` expiran. Diseña un diccionario o estructura en memoria dentro de Flask que almacene temporalmente las URLs de streaming (`bestaudio`) indexadas por el `video_id` y su timestamp para evitar llamadas redundantes a YouTube.
- Pasa la URL de streaming directamente al frontend en un elemento `<audio>` nativo de HTML5.

## 3. Descargas Asíncronas en Segundo Plano
- Para evitar congelar el servidor Flask local, la lógica de descarga debe ejecutarse en un hilo secundario (`threading.Thread`).
- El proceso debe usar `yt-dlp` para descargar el flujo de audio y usar FFmpeg (`postprocessors`) para convertirlo a un archivo MP3 limpio con una calidad mínima de `192kbps`.
- Los archivos finales deben guardarse de forma local y organizada en un directorio llamado `downloads/` en la raíz del proyecto.

## 4. Interfaz de Usuario (UI/UX Minimalista Avanzada)
- **Diseño Estético:** Monocromático, moderno, limpio, con amplios espacios en blanco, inspirado en la estética de interfaces como Vercel o Linear.
- **Modo Oscuro:** Implementar soporte nativo mediante Tailwind CSS basado en las preferencias del sistema (`dark:bg-zinc-950`, `dark:text-zinc-50`).
- **Componentes:** 1. Barra de navegación superior fija (Muestra estado de conexión de YouTube y botón Login/Logout).
  2. Panel Central dividido: Izquierda para búsqueda y reproducción; Derecha para explorador de Playlists de YouTube.
  3. Reproductor fijo inferior: Aparece de manera fluida cuando se activa una canción.
- **Control por Teclado (JavaScript):** Añadir código JS para que la barra espaciadora pause/reproduzca la música y las flechas direccionales permitan adelantar/atrasar el audio de forma nativa.

---

# ESTRUCTURA DEL PROYECTO A GENERAR

Debes devolver el código fuente completo e individual para cada uno de los siguientes componentes dentro de bloques de código limpios y etiquetados:

### 1. `requirements.txt`
Incluye las versiones estables y compatibles de: `Flask`, `yt-dlp`, `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`, y cualquier otra dependencia necesaria.

### 2. `app.py`
Debe contener toda la configuración de Flask, el manejo seguro de estados de la sesión, la inicialización del cliente de YouTube, las rutas de la API para streaming/búsqueda, y el gestor de hilos (`Thread`) para la descarga en segundo plano a la carpeta `downloads/`.

### 3. `templates/base.html`
Plantilla maestra HTML5 que incluye el CDN de Tailwind CSS, fuentes tipográficas sans-serif limpias, la estructura básica, estilos base personalizados para scrollbars e interacciones estéticas, y el script global de atajos de teclado para el reproductor de audio.

### 4. `templates/index.html`
El Dashboard principal de la aplicación. Debe renderizar de forma condicional el estado de autenticación (Pantalla de bienvenida limpia si no está conectado; Grid avanzado de playlists y canciones si está autenticado), la barra de búsqueda y el reproductor inferior fijo.

### 5. `README.md` (Instrucciones de Configuración de Google Cloud Console)
Una guía paso a paso clara orientada al usuario sobre cómo entrar a Google Cloud Console, crear un proyecto, activar la **YouTube Data API v3**, configurar la pantalla de consentimiento OAuth (añadiendo el alcance `/auth/youtube.readonly`), crear las credenciales de tipo "Aplicación de escritorio" o "Aplicación Web" (con `http://localhost:5000/callback`), y exportar el archivo `client_secret.json`.