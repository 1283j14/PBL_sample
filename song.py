class Song:
    """楽曲データを管理するクラス"""
    def __init__(self, title, artist, image_url, spotify_id=None, preview_url=None, spotify_uri=None):
        self.title = title
        self.artist = artist
        self.image_url = image_url
        self.spotify_id = spotify_id
        self.preview_url = preview_url
        self.spotify_uri = spotify_uri
    
    def __str__(self):
        return f"{self.title} - {self.artist}"
    
    def __eq__(self, other):
        if isinstance(other, Song):
            return self.title == other.title and self.artist == other.artist
        return False
