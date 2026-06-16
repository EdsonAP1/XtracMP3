import os
import subprocess
import platform
from flask import Blueprint, jsonify, request, send_from_directory
from models.download_manager import download_manager
from models.youtube_client import extract_clean_video_url
import config

download_bp = Blueprint('download', __name__)

@download_bp.route('/api/download/<video_id>')
def api_download(video_id):
    if '?' in video_id:
        video_id = video_id.split('?')[0]

    title = request.args.get('title', 'Canción de YouTube').strip()
    started = download_manager.start_download(video_id, title)
    
    if not started:
        return jsonify({
            "message": "La descarga ya está en progreso o en la cola.", 
            "video_id": video_id
        })
        
    return jsonify({
        "message": "Descarga iniciada en segundo plano.", 
        "video_id": video_id
    })


@download_bp.route('/api/enqueue-url', methods=['POST'])
def api_enqueue_url():
    data = request.json or {}
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({"error": "La URL está vacía."}), 400
        
    clean_url, video_id = extract_clean_video_url(url)
    if not video_id:
        return jsonify({"error": "URL de YouTube no válida o no soportada."}), 400
        
    # Iniciar la descarga de inmediato de forma automatizada
    # y con un título provisional mientras se recupera la información real
    started = download_manager.start_download(video_id, "Obteniendo información...")
    
    return jsonify({
        "success": True,
        "video_id": video_id,
        "message": "Enlace encolado e iniciando descarga asíncrona automáticamente."
    })


@download_bp.route('/api/open-folder', methods=['POST'])
def open_folder():
    try:
        downloads_dir = config.DOWNLOADS_DIR
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)
            
        if platform.system() == 'Windows':
            # explorer.exe fuerza el foco en primer plano de forma más confiable que os.startfile
            subprocess.Popen(['explorer', os.path.normpath(downloads_dir)])
        elif platform.system() == 'Darwin':
            subprocess.Popen(['open', downloads_dir])
        else:
            subprocess.Popen(['xdg-open', downloads_dir])
            
        return jsonify({"success": True, "message": "Carpeta abierta correctamente."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@download_bp.route('/api/select-folder', methods=['POST'])
def select_folder():
    try:
        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        # Diálogo para seleccionar carpeta con parent=root para forzar primer plano (topmost)
        selected_dir = filedialog.askdirectory(
            title="Seleccionar Carpeta para Descargas MP3",
            initialdir=config.DOWNLOADS_DIR,
            parent=root
        )
        
        root.destroy()
        
        if selected_dir:
            normalized_dir = os.path.abspath(selected_dir)
            config.DOWNLOADS_DIR = normalized_dir
            config.save_user_config({"downloads_dir": normalized_dir})
            print(f"[XtractorMP3] Directorio de descargas cambiado a: {normalized_dir}")
            return jsonify({
                "success": True,
                "downloads_dir": normalized_dir,
                "message": f"Carpeta cambiada a: {normalized_dir}"
            })
            
        return jsonify({"success": False, "message": "Selección cancelada."})
    except Exception as e:
        print(f"[XtractorMP3] Error al abrir seleccionador de carpeta: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@download_bp.route('/api/downloads')
def api_downloads():
    return jsonify(download_manager.get_all_statuses())


@download_bp.route('/api/downloads/file/<path:filename>')
def download_file(filename):
    return send_from_directory(config.DOWNLOADS_DIR, filename, as_attachment=True)


@download_bp.route('/api/open-file/<path:filename>', methods=['POST'])
def open_file(filename):
    try:
        file_path = os.path.join(config.DOWNLOADS_DIR, filename)
        if not os.path.exists(file_path):
            return jsonify({"success": False, "error": "El archivo no existe."}), 404
            
        if platform.system() == 'Windows':
            os.startfile(file_path)
        elif platform.system() == 'Darwin':
            subprocess.Popen(['open', file_path])
        else:
            subprocess.Popen(['xdg-open', file_path])
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

