from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from image_loader import ImageLoader


class SongDisplayWidget(QWidget):
    """楽曲表示ウィジェット"""
    def __init__(self):
        super().__init__()
        self.current_song = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 画像表示用ラベル
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(300, 300)
        self.image_label.setStyleSheet("border: 2px solid #ddd; background-color: #f9f9f9; border-radius: 10px;")

        # タイトルラベル
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 15px; color: #333;")

        # アーティストラベル
        self.artist_label = QLabel()
        self.artist_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.artist_label.setStyleSheet("color: #666; font-size: 18px; margin-bottom: 20px;")
        
        # スワイプ指示ラベル
        self.instruction_label = QLabel("← 左スワイプ：プレイリストに追加　　右スワイプ：次の曲 →")
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction_label.setStyleSheet("""
            color: #888; 
            font-size: 14px; 
            padding: 10px; 
            background-color: #f0f0f0; 
            border-radius: 5px;
            margin: 10px;
        """)

        layout.addWidget(self.image_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.artist_label)
        layout.addWidget(self.instruction_label)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.setLayout(layout)
    
    def display_song(self, song):
        """楽曲を表示"""
        self.current_song = song
        self.title_label.setText(song.title)
        self.artist_label.setText(song.artist)
        
        # 画像の読み込み
        pixmap = ImageLoader.load_pixmap_from_url(song.image_url)
        if pixmap:
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText(f"🎵\n{song.title}\n\n画像読み込み中...")
            self.image_label.setStyleSheet("""
                border: 2px solid #ddd; 
                background-color: #f9f9f9; 
                color: #666;
                font-size: 16px;
                border-radius: 10px;
            """)
    
    def show_completion_message(self, playlist_count):
        """完了メッセージを表示"""
        self.title_label.setText("🎉 すべての曲をチェックしました！")
        self.artist_label.setText(f"プレイリストに {playlist_count} 曲追加されました")
        self.image_label.clear()
        self.image_label.setText("完了")
        self.instruction_label.setText("アプリケーションを終了してください")
