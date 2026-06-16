import os
import glob
import subprocess
import platform

# --- PARCHE PARA SUBPROCESOS EN WINDOWS ---
# Previene que los subprocesos de yt-dlp y ffmpeg hereden sockets de Flask,
# lo cual provoca que las llamadas AJAX o la página se queden "cargando" indefinidamente.
if platform.system() == 'Windows':
    original_init = subprocess.Popen.__init__
    def patched_init(self, *args, **kwargs):
        if 'close_fds' not in kwargs:
            kwargs['close_fds'] = True
        original_init(self, *args, **kwargs)
    subprocess.Popen.__init__ = patched_init

# --- CONFIGURACIÓN BÁSICA ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Clave secreta para desarrollo y sesiones
SECRET_KEY = os.environ.get('SECRET_KEY', 'xtractormp3_secret_key_development_3129873918')

# Google OAuth 2.0
CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, "client_secret.json")
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

# Desactivar requerimiento de SSL para desarrollo local
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Directorio de descargas (por defecto)
DOWNLOADS_DIR = os.path.join(BASE_DIR, 'downloads')
USER_CONFIG_FILE = os.path.join(BASE_DIR, "user_config.json")

def load_user_config():
    global DOWNLOADS_DIR
    if os.path.exists(USER_CONFIG_FILE):
        try:
            import json
            with open(USER_CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'downloads_dir' in data:
                    DOWNLOADS_DIR = os.path.abspath(data['downloads_dir'])
                    print(f"[XtractorMP3] Carpeta de descargas cargada de config: {DOWNLOADS_DIR}")
        except Exception as e:
            print(f"[XtractorMP3] Error al cargar user_config.json: {e}")

def save_user_config(data):
    try:
        import json
        with open(USER_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[XtractorMP3] Error al guardar user_config.json: {e}")

# Cargar la configuración guardada del usuario
load_user_config()

# --- DETECCIÓN AUTOMÁTICA DE FFmpeg Y Deno ---
FFMPEG_LOCATION = None
ffmpeg_candidates = [
    os.path.join(BASE_DIR, 'ffmpeg', 'bin'),
    os.path.join(BASE_DIR, 'ffmpeg'),
    BASE_DIR,
]

# Agregar subcarpetas tipo ffmpeg-*-essentials*/bin extraídas del zip
for match in glob.glob(os.path.join(BASE_DIR, 'ffmpeg-*', 'bin')):
    ffmpeg_candidates.insert(0, match)

for candidate in ffmpeg_candidates:
    ffmpeg_exe = os.path.join(candidate, 'ffmpeg.exe')
    ffmpeg_unix = os.path.join(candidate, 'ffmpeg')
    if os.path.isfile(ffmpeg_exe) or os.path.isfile(ffmpeg_unix):
        FFMPEG_LOCATION = candidate
        # Agregar al PATH para procesos externos
        os.environ['PATH'] = candidate + os.pathsep + os.environ.get('PATH', '')
        print(f"[XtractorMP3] FFmpeg detectado en: {candidate}")
        break

if not FFMPEG_LOCATION:
    print("[XtractorMP3] ADVERTENCIA: FFmpeg no encontrado localmente. Las conversiones a MP3 podrían fallar si no está en el PATH global.")

# Autodetectar Deno en Windows
deno_home = os.path.join(os.path.expanduser('~'), '.deno', 'bin')
if os.path.isdir(deno_home):
    os.environ['PATH'] = deno_home + os.pathsep + os.environ.get('PATH', '')
    print(f"[XtractorMP3] Deno detectado en: {deno_home}")
