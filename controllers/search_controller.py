from flask import Blueprint, jsonify, request
import yt_dlp
from models.youtube_client import (
    get_credentials, 
    get_playlists, 
    get_playlist_items, 
    extract_clean_video_url
)
from models.stream_cache import stream_cache

search_bp = Blueprint('search', __name__)

@search_bp.route('/api/playlists')
def api_playlists():
    creds = get_credentials()
    if not creds:
        return jsonify({"error": "No autenticado. Por favor inicia sesión."}), 401
        
    try:
        playlists = get_playlists(creds)
        return jsonify(playlists)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@search_bp.route('/api/playlist/<playlist_id>')
def api_playlist_items(playlist_id):
    creds = get_credentials()
    if not creds:
        return jsonify({"error": "No autenticado. Por favor inicia sesión."}), 401
        
    next_page_token = request.args.get('nextPageToken', '')
    try:
        data = get_playlist_items(creds, playlist_id, page_token=next_page_token)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@search_bp.route('/api/search')
def api_search():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({"error": "El término de búsqueda está vacío."}), 400
        
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': True,
        'nocheckcertificate': True
    }
    
    # Comprobar si es un enlace de playlist de YouTube
    is_playlist = "list=" in query or "/playlist" in query
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if is_playlist:
                info = ydl.extract_info(query, download=False)
                results = []
                if 'entries' in info:
                    for entry in info['entries']:
                        if entry:
                            results.append({
                                'video_id': entry.get('id'),
                                'title': entry.get('title'),
                                'channel': entry.get('uploader', info.get('title', 'Desconocido')),
                                'thumbnail': f"https://img.youtube.com/vi/{entry.get('id')}/mqdefault.jpg" if entry.get('id') else '',
                                'duration': entry.get('duration')
                            })
                return jsonify({
                    "type": "playlist",
                    "playlist_title": info.get('title', 'Lista de reproducción'),
                    "songs": results
                })
                
            # Detectar y limpiar URL de YouTube individual
            clean_url, video_id = extract_clean_video_url(query)
            is_url = clean_url is not None
            search_target = clean_url if is_url else query
            
            if is_url:
                info = ydl.extract_info(search_target, download=False)
                if 'entries' in info:
                    results = []
                    for entry in info['entries']:
                        if entry:
                            results.append({
                                'video_id': entry.get('id'),
                                'title': entry.get('title'),
                                'channel': entry.get('uploader', 'Desconocido'),
                                'thumbnail': f"https://img.youtube.com/vi/{entry.get('id')}/mqdefault.jpg" if entry.get('id') else '',
                                'duration': entry.get('duration')
                            })
                else:
                    results = [{
                        'video_id': info.get('id'),
                        'title': info.get('title'),
                        'channel': info.get('uploader', 'Desconocido'),
                        'thumbnail': info.get('thumbnail') or f"https://img.youtube.com/vi/{info.get('id')}/mqdefault.jpg",
                        'duration': info.get('duration')
                    }]
            else:
                search_query = f"ytsearch5:{search_target}"
                info = ydl.extract_info(search_query, download=False)
                results = []
                for entry in info.get('entries', []):
                    if entry:
                        results.append({
                            'video_id': entry.get('id'),
                            'title': entry.get('title'),
                            'channel': entry.get('uploader', entry.get('channel', 'Desconocido')),
                            'thumbnail': entry.get('thumbnail') or f"https://img.youtube.com/vi/{entry.get('id')}/mqdefault.jpg",
                            'duration': entry.get('duration')
                        })
                        
            return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@search_bp.route('/api/stream/<video_id>')
def api_stream(video_id):
    # Validar que el video_id no contenga parámetros de consulta adicionales pegados
    if '?' in video_id:
        video_id = video_id.split('?')[0]

    cached_url = stream_cache.get(video_id)
    if cached_url:
        return jsonify({"stream_url": cached_url, "cached": True})
        
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'skip_download': True,
        'nocheckcertificate': True
    }
    
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            stream_url = info.get('url')
            if not stream_url:
                return jsonify({"error": "No se pudo extraer la URL del stream de audio"}), 404
                
            stream_cache.set(video_id, stream_url)
            return jsonify({"stream_url": stream_url, "cached": False})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
