from song import Song


class SongManager:
    """楽曲データ管理クラス"""
    def __init__(self):
        self.songs = [
            Song("ブルーバード", "いきものがかり", "https://via.placeholder.com/250x250/4CAF50/white?text=ブルーバード"),
            Song("Pretender", "Official髭男dism", "https://via.placeholder.com/250x250/2196F3/white?text=Pretender"),
            Song("Lemon", "米津玄師", "https://via.placeholder.com/250x250/FF9800/white?text=Lemon"),
            Song("夜に駆ける", "YOASOBI", "https://via.placeholder.com/250x250/9C27B0/white?text=夜に駆ける"),
            Song("炎", "LiSA", "https://via.placeholder.com/250x250/F44336/white?text=炎"),
            Song("紅蓮華", "LiSA", "https://via.placeholder.com/250x250/E91E63/white?text=紅蓮華"),
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
