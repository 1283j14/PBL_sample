import sys
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QMessageBox

from song_manager import SongManager
from playlist_manager import PlaylistManager
from swipeable_widget import SwipeableWidget
from song_display_widget import SongDisplayWidget
from playlist_widget import PlaylistWidget


class SwipeApp(QWidget):
    """メインアプリケーションクラス"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MEET une - Swipe Demo")
        
        # 各種マネージャーの初期化
        self.song_manager = SongManager()
        self.playlist_manager = PlaylistManager()
        
        self.init_ui()
        self.connect_signals()
        self.load_current_song()

    def init_ui(self):
        # メインレイアウト（横分割）
        main_layout = QHBoxLayout()
        
        # 左側：スワイプ可能な楽曲表示エリア
        self.swipe_widget = SwipeableWidget()
        swipe_layout = QVBoxLayout()
        
        self.song_display = SongDisplayWidget()
        swipe_layout.addWidget(self.song_display)
        self.swipe_widget.setLayout(swipe_layout)
        
        # 右側：プレイリストエリア
        self.playlist_widget = PlaylistWidget()
        self.playlist_widget.setMaximumWidth(300)
        
        # メインレイアウトに追加
        main_layout.addWidget(self.swipe_widget, 2)  # 左側を大きく
        main_layout.addWidget(self.playlist_widget, 1)  # 右側を小さく
        
        self.setLayout(main_layout)
    
    def connect_signals(self):
        """シグナルとスロットを接続"""
        self.swipe_widget.swipe_left.connect(self.on_swipe_left)
        self.swipe_widget.swipe_right.connect(self.on_swipe_right)
        self.playlist_widget.create_spotify_playlist.connect(self.on_create_spotify_playlist)
    
    def load_current_song(self):
        """現在の楽曲を読み込み"""
        current_song = self.song_manager.get_current_song()
        if current_song:
            self.song_display.display_song(current_song)
        else:
            self.song_display.show_completion_message(self.playlist_manager.get_count())
    
    def on_swipe_right(self):
        """右スワイプ：次の曲へ"""
        print("右スワイプ：次の曲へ")
        self.song_manager.next_song()
        self.load_current_song()
    
    def on_swipe_left(self):
        """左スワイプ：プレイリストに追加"""
        current_song = self.song_manager.get_current_song()
        if current_song:
            if self.playlist_manager.add_song(current_song):
                self.playlist_widget.add_song(current_song)
                print(f"プレイリストに追加: {current_song}")
            else:
                print("この曲は既にプレイリストに追加されています")
            
            # 次の曲へ
            self.song_manager.next_song()
            self.load_current_song()
    
    def on_create_spotify_playlist(self):
        """Spotifyプレイリスト作成（プレースホルダー）"""
        liked_songs = self.playlist_manager.get_songs()
        
        if not liked_songs:
            QMessageBox.information(self, "情報", "プレイリストが空です。まず楽曲を追加してください。")
            return
        
        # 実際のSpotify API連携はここに実装予定
        message = f"Spotifyプレイリストを作成します：\n\n"
        message += "\n".join([f"• {song}" for song in liked_songs])
        message += f"\n\n合計 {len(liked_songs)} 曲"
        
        QMessageBox.information(self, "Spotify連携", message)
        print("Spotify API連携機能は今後実装予定です")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SwipeApp()
    window.resize(800, 600)
    window.show()
    
    print("クラス分割版スワイプアプリケーションが起動しました")
    print("操作方法:")
    print("- 右スワイプ（右にドラッグ）：次の曲へ")
    print("- 左スワイプ（左にドラッグ）：プレイリストに追加")
    print("- ウィンドウを閉じるか、Ctrl+Cで終了")
    
    sys.exit(app.exec())
