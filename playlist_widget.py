from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt, pyqtSignal

class PlaylistWidget(QWidget):
    """プレイリスト表示ウィジェット"""
    
    # シグナル定義
    create_spotify_playlist = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # タイトル
        self.title_label = QLabel("🎵 お気に入りプレイリスト")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; margin-bottom: 10px;")
        
        # 楽曲数表示ラベル
        self.count_label = QLabel("楽曲数: 0")
        self.count_label.setStyleSheet("font-size: 12px; color: #666; margin-bottom: 10px;")
        
        # プレイリスト表示
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                alternate-background-color: #f9f9f9;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
        """)
        
        # Spotify連携ボタン
        self.spotify_button = QLabel("Spotifyプレイリスト作成")
        self.spotify_button.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spotify_button.setStyleSheet("""
            background-color: #1DB954;
            color: white;
            padding: 15px;
            border-radius: 8px;
            font-weight: bold;
            margin-top: 10px;
        """)
        self.spotify_button.mousePressEvent = self.on_spotify_button_clicked
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.count_label)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.spotify_button)
        
        self.setLayout(layout)
    
    def add_song(self, song):
        """楽曲をリストに追加"""
        item = QListWidgetItem(f"♪ {song}")
        self.list_widget.addItem(item)
        
        # 楽曲数を更新
        self.update_count()
    
    def update_count(self):
        """楽曲数を更新"""
        count = self.list_widget.count()
        self.count_label.setText(f"楽曲数: {count}")
        
        # ボタンの有効/無効を切り替え
        if count > 0:
            self.spotify_button.setStyleSheet("""
                background-color: #1DB954;
                color: white;
                padding: 15px;
                border-radius: 8px;
                font-weight: bold;
                margin-top: 10px;
                cursor: pointer;
            """)
        else:
            self.spotify_button.setStyleSheet("""
                background-color: #cccccc;
                color: #666666;
                padding: 15px;
                border-radius: 8px;
                font-weight: bold;
                margin-top: 10px;
                cursor: not-allowed;
            """)
    
    def clear_playlist(self):
        """プレイリストUIをクリア"""
        self.list_widget.clear()
        self.update_count()
        print("プレイリストUIがクリアされました")
    
    def on_spotify_button_clicked(self, event):
        """Spotifyボタンクリック時の処理"""
        # リストが空の場合は何もしない
        if self.list_widget.count() == 0:
            return
            
        self.create_spotify_playlist.emit()
    
    def get_song_count(self):
        """現在の楽曲数を取得"""
        return self.list_widget.count()
    
    def get_all_songs(self):
        """すべての楽曲を取得"""
        songs = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            # "♪ " プレフィックスを削除
            song_text = item.text().replace("♪ ", "")
            songs.append(song_text)
        return songs
    
    def remove_song(self, song_text):
        """特定の楽曲を削除"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.text() == f"♪ {song_text}":
                self.list_widget.takeItem(i)
                self.update_count()
                break
