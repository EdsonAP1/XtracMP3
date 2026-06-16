# XtractorMP3 - Stream & Download YouTube Music

Una aplicación web local minimalista construida con Python (Flask), `yt-dlp`, OAuth 2.0 de Google y Tailwind CSS, diseñada para buscar, reproducir en tiempo real y descargar audio desde YouTube, convirtiéndolo localmente a MP3 con calidad de 192kbps mediante FFmpeg.

---

## Requisitos Previos e Instalación

### 1. Requisitos del Sistema (FFmpeg)
Para convertir los audios descargados a formato **MP3**, la aplicación necesita **FFmpeg**. 

#### En Windows (Dos métodos disponibles):
*   **Método Rápido (Recomendado):** Descarga el binario compilado de FFmpeg para Windows (como los builds de [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)) y copia los ejecutables `ffmpeg.exe` y `ffprobe.exe` directamente en la raíz de este proyecto (junto a `app.py`).
*   **Método Global:** Extrae FFmpeg en una carpeta de tu sistema (ej. `C:\ffmpeg`) y añade la ruta de la carpeta `bin` (ej. `C:\ffmpeg\bin`) a la variable de entorno `PATH` del sistema.

#### En macOS:
```bash
brew install ffmpeg
```

#### En Linux (Ubuntu/Debian):
```bash
sudo apt update && sudo apt install ffmpeg
```

---

### 2. Configuración de Google Cloud Console (Para OAuth 2.0 de YouTube)

Para poder autenticarte con tu cuenta de YouTube y obtener tus listas de reproducción y videos favoritos, sigue estos pasos detallados:

1.  Ve a la consola de desarrolladores de Google: [Google Cloud Console](https://console.cloud.google.com/).
2.  Inicia sesión con tu cuenta de Google.
3.  **Crea un nuevo proyecto:**
    *   Haz clic en el selector de proyectos en la parte superior izquierda y presiona **Nuevo Proyecto** (New Project).
    *   Dale un nombre como `XtractorMP3` y haz clic en **Crear**.
4.  **Habilita la API de YouTube:**
    *   En la barra lateral izquierda, dirígete a **API y servicios** > **Biblioteca** (APIs & Services > Library).
    *   Busca `"YouTube Data API v3"`.
    *   Haz clic en ella y presiona el botón **Habilitar** (Enable).
5.  **Configura la Pantalla de Consentimiento de OAuth:**
    *   Ve a **API y servicios** > **Pantalla de consentimiento de OAuth** (OAuth consent screen).
    *   Selecciona el tipo de usuario **Externo** (External) y haz clic en **Crear**.
    *   Completa la información básica requerida (Nombre de la aplicación, correo de soporte del usuario, datos de contacto del desarrollador).
    *   En el paso de **Permisos (Scopes)**, haz clic en **Agregar o quitar permisos** y busca o ingresa manualmente el siguiente alcance:
        *   `.../auth/youtube.readonly` (Permite ver tus listas de reproducción y favoritos).
    *   En el paso de **Usuarios de prueba (Test users)**, haz clic en **Agregar usuarios** e introduce la misma dirección de correo de Google con la que harás las pruebas y te autenticarás en la aplicación local. **(Paso sumamente crítico para que Google te permita iniciar sesión estando en modo Testing)**.
    *   Guarda y finaliza el asistente.
6.  **Crea las Credenciales de Acceso:**
    *   Ve a **API y servicios** > **Credenciales** (Credentials).
    *   Haz clic en **Crear credenciales** > **ID de cliente de OAuth** (OAuth client ID).
    *   En **Tipo de aplicación** (Application type), selecciona **Aplicación web** (Web application).
    *   En **Orígenes de JavaScript autorizados**, agrega:
        *   `http://localhost:5000`
    *   En **URIs de redireccionamiento autorizados**, agrega **exactamente**:
        *   `http://localhost:5000/callback`
    *   Haz clic en **Crear**.
7.  **Descarga el archivo secreto:**
    *   En la lista de credenciales creadas, verás tu cliente de OAuth. Haz clic en el botón de **Descargar JSON** (icono de descarga a la derecha).
    *   Guarda ese archivo en la carpeta raíz del proyecto, y cámbiale el nombre exactamente a `client_secret.json`.

---

## Cómo Ejecutar la Aplicación

1.  Abre una terminal en la carpeta raíz del proyecto.
2.  (Opcional) Crea y activa un entorno virtual de Python:
    ```powershell
    # En Windows (PowerShell)
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```
3.  Instala las dependencias necesarias:
    ```bash
    pip install -r requirements.txt
    ```
4.  Asegúrate de que tienes el archivo `client_secret.json` en la raíz.
5.  Inicia el servidor Flask:
    ```bash
    python app.py
    ```
6.  Abre tu navegador y entra a: **`http://localhost:5000`**

---

## Funcionalidades del Teclado (Atajos Globales)

Para mejorar la experiencia de uso (mientras no tengas el cursor enfocado en un campo de texto):
*   `Espacio`: Reproducir / Pausar el audio actual.
*   `Flecha Izquierda`: Retroceder 10 segundos.
*   `Flecha Derecha`: Adelantar 10 segundos.
