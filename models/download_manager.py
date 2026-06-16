import os
import threading
import json
import yt_dlp
import config

class DownloadManager:
    def __init__(self):
        self._status = {}
        self._lock = threading.Lock()
        self._history_file = os.path.join(config.BASE_DIR, 'downloads_history.json')
        self._load_history()

    def _load_history(self):
        # Desactivado a petición del usuario para no guardar historial
        pass

    def _save_history(self):
        # Desactivado a petición del usuario para no guardar historial
        pass

    def get_all_statuses(self):
        with self._lock:
            return list(self._status.values())

    def get_status(self, video_id):
        with self._lock:
            return self._status.get(video_id)

    def update_status(self, video_id, status_data):
        with self._lock:
            if video_id not in self._status:
                self._status[video_id] = {}
            self._status[video_id].update(status_data)
            self._save_history()

    def start_download(self, video_id, title):
        # Si ya está descargando o convirtiendo, no iniciar de nuevo
        status = self.get_status(video_id)
        if status and status.get('status') in ['descargando', 'convirtiendo']:
            return False

        # Iniciar hilo de descarga
        thread = threading.Thread(target=self._download_worker, args=(video_id, title))
        thread.daemon = True
        thread.start()
        return True

    def _download_worker(self, video_id, title):
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        downloads_dir = config.DOWNLOADS_DIR
        
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)

        self.update_status(video_id, {
            'video_id': video_id,
            'title': title,
            'status': 'descargando',
            'progress': 0,
            'error': None,
            'filename': None
        })

        def progress_hook(d):
            if d['status'] == 'downloading':
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded_bytes = d.get('downloaded_bytes', 0)
                if total_bytes:
                    progress = int((downloaded_bytes / total_bytes) * 100)
                    self.update_status(video_id, {'progress': progress})
            elif d['status'] == 'finished':
                self.update_status(video_id, {'progress': 99, 'status': 'convirtiendo'})

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(downloads_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'nocheckcertificate': True,
            'prefer_ffmpeg': True
        }

        if config.FFMPEG_LOCATION:
            ydl_opts['ffmpeg_location'] = config.FFMPEG_LOCATION

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                
                # Obtener el título real y actualizarlo en el estado
                real_title = info.get('title', title)
                
                filename = ydl.prepare_filename(info)
                base, _ = os.path.splitext(filename)
                mp3_filename = base + ".mp3"
                basename = os.path.basename(mp3_filename)

                self.update_status(video_id, {
                    'title': real_title,
                    'status': 'completado',
                    'progress': 100,
                    'filename': basename
                })
        except Exception as e:
            print(f"[XtractorMP3] Error descargando {video_id}: {e}")
            self.update_status(video_id, {
                'status': 'fallido',
                'progress': 0,
                'error': str(e)
            })

download_manager = DownloadManager()
