class PlaylistManager:
    """プレイリスト管理クラス"""
    def __init__(self):
        self.liked_songs = []
    
    def add_song(self, song):
        """楽曲をプレイリストに追加"""
        if song not in self.liked_songs:
            self.liked_songs.append(song)
            return True
        return False
    
    def remove_song(self, song):
        """楽曲をプレイリストから削除"""
        if song in self.liked_songs:
            self.liked_songs.remove(song)
            return True
        return False
    
    def get_songs(self):
        """プレイリストの楽曲リストを取得"""
        return self.liked_songs.copy()
    
    def get_count(self):
        """プレイリストの楽曲数を取得"""
        return len(self.liked_songs)
    
    def clear(self):
        """プレイリストをクリア"""
        self.liked_songs.clear()
