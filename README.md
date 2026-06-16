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
