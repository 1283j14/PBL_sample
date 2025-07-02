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
        layout.addWidget(self.list_widget)
        layout.addWidget(self.spotify_button)
        
        self.setLayout(layout)
    
    def add_song(self, song):
        """楽曲をリストに追加"""
        item = QListWidgetItem(f"♪ {song}")
        self.list_widget.addItem(item)
    
    def clear_playlist(self):
        """プレイリストをクリア"""
        self.list_widget.clear()
    
    def on_spotify_button_clicked(self, event):
        """Spotifyボタンクリック時の処理"""
        self.create_spotify_playlist.emit()
