import re
import google.oauth2.credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from flask import session
import config

def extract_clean_video_url(url_or_query):
    """
    Analiza si la consulta es una URL de YouTube.
    Si lo es, extrae el ID de video de 11 caracteres y devuelve la URL limpia y el ID.
    Si no es una URL de YouTube, devuelve (None, None).
    """
    pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:watch\?v=|embed/|v/|shorts/)|youtu\.be/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url_or_query)
    if match:
        video_id = match.group(1)
        return f"https://www.youtube.com/watch?v={video_id}", video_id
    return None, None

def get_credentials():
    """
    Obtiene las credenciales de la sesión de Flask, las valida
    y las refresca automáticamente si han expirado.
    """
    if 'credentials' not in session:
        return None
    
    creds_info = session['credentials']
    creds = google.oauth2.credentials.Credentials(
        token=creds_info.get('token'),
        refresh_token=creds_info.get('refresh_token'),
        token_uri=creds_info.get('token_uri'),
        client_id=creds_info.get('client_id'),
        client_secret=creds_info.get('client_secret'),
        scopes=creds_info.get('scopes')
    )
    
    # Si las credenciales expiraron y tenemos un Refresh Token, las renovamos
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            session['credentials'] = {
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes
            }
            session.modified = True
        except Exception as e:
            print(f"[XtractorMP3] Error al refrescar las credenciales de YouTube: {e}")
            session.pop('credentials', None)
            return None
            
    return creds

def get_playlists(creds):
    """
    Obtiene las playlists del usuario utilizando YouTube API v3.
    Retorna una lista formateada.
    """
    youtube = build('youtube', 'v3', credentials=creds)
    playlists_response = youtube.playlists().list(
        part="snippet,contentDetails",
        mine=True,
        maxResults=50
    ).execute()
    
    playlists = []
    
    # Playlist de Liked Videos agregada por defecto (ID: 'LL')
    playlists.append({
        'id': 'LL',
        'title': 'Videos que me gustan (Liked)',
        'description': 'Tus videos de YouTube marcados con "Me gusta"',
        'thumbnail': 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=150&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
        'item_count': 'Varios'
    })
    
    for item in playlists_response.get('items', []):
        thumbnails = item.get('snippet', {}).get('thumbnails', {})
        thumb_url = (thumbnails.get('medium', {}) or thumbnails.get('default', {}) or {}).get('url', '')
        
        playlists.append({
            'id': item.get('id'),
            'title': item.get('snippet', {}).get('title'),
            'description': item.get('snippet', {}).get('description', ''),
            'thumbnail': thumb_url,
            'item_count': item.get('contentDetails', {}).get('itemCount', 0)
        })
        
    return playlists

def get_playlist_items(creds, playlist_id, page_token=None):
    """
    Obtiene los elementos de una playlist de YouTube por su ID.
    """
    youtube = build('youtube', 'v3', credentials=creds)
    
    playlist_items_response = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=playlist_id,
        maxResults=50,
        pageToken=page_token
    ).execute()
    
    items = []
    for item in playlist_items_response.get('items', []):
        snippet = item.get('snippet', {})
        resource_id = snippet.get('resourceId', {})
        video_id = resource_id.get('videoId')
        
        thumbnails = snippet.get('thumbnails', {})
        thumb_url = (thumbnails.get('medium', {}) or thumbnails.get('default', {}) or {}).get('url', '')
        
        items.append({
            'video_id': video_id,
            'title': snippet.get('title'),
            'channel': snippet.get('videoOwnerChannelTitle', snippet.get('channelTitle', 'Canal desconocido')),
            'thumbnail': thumb_url,
            'published_at': snippet.get('publishedAt')
        })
        
    return {
        'items': items,
        'nextPageToken': playlist_items_response.get('nextPageToken', '')
    }
