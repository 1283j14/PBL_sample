class PlaylistManager:
    """プレイリスト管理クラス"""
    
    def __init__(self):
        self.songs = []  # 楽曲リスト
        self.song_ids = set()  # 重複チェック用のセット
        self.count = 0  # 楽曲数
    
    def add_song(self, song):
        """楽曲をプレイリストに追加"""
        # 楽曲のユニークIDを生成（タイトル + アーティスト）
        song_id = f"{song.title}_{song.artist}"
        
        # 重複チェック
        if song_id in self.song_ids:
            return False  # 既に追加済み
        
        # 楽曲を追加
        self.songs.append(song)
        self.song_ids.add(song_id)
        self.count += 1
        
        print(f"プレイリストに追加: {song.title} - {song.artist}")
        return True
    
    def remove_song(self, song):
        """楽曲をプレイリストから削除"""
        song_id = f"{song.title}_{song.artist}"
        
        if song_id in self.song_ids:
            self.songs.remove(song)
            self.song_ids.remove(song_id)
            self.count -= 1
            print(f"プレイリストから削除: {song.title} - {song.artist}")
            return True
        return False
    
    def get_songs(self):
        """プレイリストの楽曲リストを取得"""
        # 楽曲オブジェクトのリストを文字列のリストに変換
        return [f"{song.title} - {song.artist}" for song in self.songs]
    
    def get_song_objects(self):
        """プレイリストの楽曲オブジェクトリストを取得"""
        return self.songs.copy()
    
    def get_count(self):
        """プレイリストの楽曲数を取得"""
        return self.count
    
    def clear_playlist(self):
        """プレイリストをクリア"""
        self.songs.clear()
        self.song_ids.clear()
        self.count = 0
        print("プレイリストをクリアしました")
    
    def is_empty(self):
        """プレイリストが空かどうかを確認"""
        return self.count == 0
    
    def contains_song(self, song):
        """特定の楽曲がプレイリストに含まれているかチェック"""
        song_id = f"{song.title}_{song.artist}"
        return song_id in self.song_ids
    
    def get_playlist_info(self):
        """プレイリストの情報を取得"""
        return {
            "count": self.count,
            "songs": self.get_songs(),
            "is_empty": self.is_empty()
        }
