from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont


class SpotifyAuthDialog(QDialog):
    """Spotify認証ダイアログ"""
    
    def __init__(self, spotify_manager, parent=None):
        super().__init__(parent)
        self.spotify_manager = spotify_manager
        self.setWindowTitle("Spotify認証")
        self.setModal(True)
        self.resize(500, 400)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # タイトル
        title_label = QLabel("🎵 Spotify連携")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #1DB954; margin-bottom: 20px;")
        
        # 説明テキスト
        description = QTextEdit()
        description.setReadOnly(True)
        description.setMaximumHeight(150)
        description.setHtml("""
        <div style="font-family: Arial; font-size: 12px; line-height: 1.5;">
            <p><strong>Spotifyプレイリスト作成の手順：</strong></p>
            <ol>
                <li>「ブラウザで認証」ボタンをクリック</li>
                <li>ブラウザでSpotifyにログイン</li>
                <li>アプリの許可を承認</li>
                <li>リダイレクト後のURLから認証コードをコピー</li>
                <li>下の入力欄に認証コードを貼り付け</li>
                <li>「認証完了」ボタンをクリック</li>
            </ol>
            <p><em>※ 認証は初回のみ必要です</em></p>
        </div>
        """)
        description.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        # 認証ボタン
        self.auth_button = QPushButton("🌐 ブラウザで認証")
        self.auth_button.setStyleSheet("""
            QPushButton {
                background-color: #1DB954;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border: none;
                border-radius: 6px;
                margin: 10px 0px;
            }
            QPushButton:hover {
                background-color: #1ed760;
            }
            QPushButton:pressed {
                background-color: #1aa34a;
            }
        """)
        self.auth_button.clicked.connect(self.open_auth_browser)
        
        # 認証コード入力エリア
        code_label = QLabel("認証コード:")
        code_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("リダイレクト後のURLから 'code=' パラメータの値をコピーして貼り付け")
        self.code_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #1DB954;
            }
        """)
        
        # ボタンエリア
        button_layout = QHBoxLayout()
        
        self.complete_button = QPushButton("✅ 認証完了")
        self.complete_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.complete_button.clicked.connect(self.complete_auth)
        
        cancel_button = QPushButton("キャンセル")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.complete_button)
        button_layout.addWidget(cancel_button)
        
        # レイアウトに追加
        layout.addWidget(title_label)
        layout.addWidget(description)
        layout.addWidget(self.auth_button)
        layout.addWidget(code_label)
        layout.addWidget(self.code_input)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def open_auth_browser(self):
        """ブラウザで認証画面を開く"""
        try:
            auth_url = self.spotify_manager.open_auth_browser()
            QMessageBox.information(
                self, 
                "認証開始", 
                f"ブラウザが開きます。\n\nSpotifyにログインして認証を完了してください。\n\n"
                f"認証後、リダイレクトされたURLから認証コードを取得してください。"
            )
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"認証画面を開けませんでした:\n{e}")
    
    def complete_auth(self):
        """認証を完了"""
        auth_code = self.code_input.text().strip()
        
        if not auth_code:
            QMessageBox.warning(self, "入力エラー", "認証コードを入力してください。")
            return
        
        # 認証コードからアクセストークンを取得
        try:
            success = self.spotify_manager.exchange_code_for_token(auth_code)
            
            if success:
                QMessageBox.information(
                    self, 
                    "認証成功", 
                    "Spotify認証が完了しました！\n\nプレイリストを作成できます。"
                )
                self.accept()
            else:
                QMessageBox.critical(
                    self, 
                    "認証失敗", 
                    "認証に失敗しました。\n\n認証コードが正しいか確認してください。"
                )
        
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"認証処理中にエラーが発生しました:\n{e}")


class PlaylistCreationDialog(QDialog):
    """プレイリスト作成ダイアログ"""
    
    def __init__(self, songs, parent=None):
        super().__init__(parent)
        self.songs = songs
        self.setWindowTitle("プレイリスト作成")
        self.setModal(True)
        self.resize(400, 300)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # タイトル
        title_label = QLabel("🎵 Spotifyプレイリスト作成")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #1DB954; margin-bottom: 20px;")
        
        # プレイリスト名入力
        name_label = QLabel("プレイリスト名:")
        name_label.setStyleSheet("font-weight: bold;")
        
        self.name_input = QLineEdit()
        self.name_input.setText(f"MEET une プレイリスト - {self.get_current_datetime()}")
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #1DB954;
            }
        """)
        
        # 楽曲リスト表示
        songs_label = QLabel(f"追加予定の楽曲 ({len(self.songs)}曲):")
        songs_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        
        songs_text = QTextEdit()
        songs_text.setReadOnly(True)
        songs_text.setMaximumHeight(150)
        
        songs_list = "\n".join([f"♪ {song}" for song in self.songs])
        songs_text.setPlainText(songs_list)
        songs_text.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-family: monospace;
            }
        """)
        
        # ボタンエリア
        button_layout = QHBoxLayout()
        
        create_button = QPushButton("🎵 プレイリスト作成")
        create_button.setStyleSheet("""
            QPushButton {
                background-color: #1DB954;
                color: white;
                font-weight: bold;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1ed760;
            }
        """)
        create_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton("キャンセル")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                font-weight: bold;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(create_button)
        button_layout.addWidget(cancel_button)
        
        # レイアウトに追加
        layout.addWidget(title_label)
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(songs_label)
        layout.addWidget(songs_text)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def get_current_datetime(self):
        """現在の日時を文字列で取得"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M')
    
    def get_playlist_name(self):
        """入力されたプレイリスト名を取得"""
        return self.name_input.text().strip()
