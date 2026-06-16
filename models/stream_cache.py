import time

class StreamCache:
    def __init__(self, ttl=3600):
        self._cache = {}
        self._ttl = ttl

    def get(self, video_id):
        now = time.time()
        if video_id in self._cache:
            cached = self._cache[video_id]
            if cached['expires_at'] > now:
                return cached['url']
            else:
                del self._cache[video_id]
        return None

    def set(self, video_id, url):
        self._cache[video_id] = {
            'url': url,
            'expires_at': time.time() + self._ttl
        }

# Instancia global para ser importada por los controladores
stream_cache = StreamCache()
