from song import Song


class SongManager:
    """楽曲データ管理クラス"""
    def __init__(self):
        self.songs = [
            # image_urlの後に、spotify_id=None, preview_url=None, spotify_uri='...' を追加
            Song("ブルーバード", "いきものがかり", "https://via.placeholder.com/250x250/4CAF50/white?text=ブルーバード",
                 spotify_id="7rVjP6H6g8pQ8fN3Jg9n", # 例: 適当なID。Spotifyの実際のIDに置き換える
                 preview_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
                 spotify_uri="spotify:track:YOUR_BLUEBIRD_URI"), # <-- 実際のURIに置き換える
            Song("Pretender", "Official髭男dism", "https://via.placeholder.com/250x250/2196F3/white?text=Pretender",
                 spotify_id="2K98C8W3qDkL2Q3w4q5y", # 例: 適当なID。
                 preview_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
                 spotify_uri="spotify:track:YOUR_PRETENDER_URI"), # <-- 実際のURIに置き換える
            # 他の曲も同様に spotify_id と spotify_uri を追加
            # Spotify APIから取得する際はこれらの情報が提供されます
        ]
        self.current_index = 0
    
    def get_current_song(self):
        """現在の楽曲を取得"""
        if self.current_index < len(self.songs):
            return self.songs[self.current_index]
        return None
    
    def next_song(self):
        """次の楽曲に移動"""
        self.current_index += 1
        return self.get_current_song()
    
    def has_next_song(self):
        """次の楽曲があるかチェック"""
        return self.current_index < len(self.songs)
    
    def reset(self):
        """楽曲インデックスをリセット"""
        self.current_index = 0
