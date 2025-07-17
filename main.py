# main.py (完成版)
import sys
import random
import os
import urllib.parse
import webbrowser
import requests
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, 
                             QMessageBox, QPushButton, QLineEdit, QDialog, QLabel,
                             QInputDialog, QProgressDialog, QCheckBox)
from PyQt6.QtCore import QTimer, Qt, QUrl, QThread, pyqtSignal
from song_manager import SongManager
from playlist_manager import PlaylistManager
from swipeable_widget import SwipeableWidget
from song_display_widget import SongDisplayWidget
from playlist_widget import PlaylistWidget
from spotify_auth import SpotifyAuthenticator, SpotifyClient
from emotion_song_manager import EmotionSongManager

class PlaylistCreationThread(QThread):
    """プレイリスト作成を別スレッドで実行"""
    progress_updated = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, spotify_client, playlist_name, songs, is_public=False):
        super().__init__()
        self.spotify_client = spotify_client
        self.playlist_name = playlist_name
        self.songs = songs
        self.is_public = is_public
        
    def run(self):
        try:
            # ユーザー情報を取得
            self.progress_updated.emit("ユーザー情報を取得中...")
            user_info = self.spotify_client.get_current_user()
            if not user_info:
                self.finished_signal.emit(False, "ユーザー情報の取得に失敗しました")
                return
            
            user_id = user_info.get("id")
            self.progress_updated.emit(f"ユーザー: {user_info.get('display_name', user_id)}")
            
            # プレイリストを作成
            self.progress_updated.emit("プレイリストを作成中...")
            playlist_description = f"MEET une アプリで作成 - {datetime.now().strftime('%Y年%m月%d日')}"
            playlist_info = self.spotify_client.create_playlist(
                user_id, 
                self.playlist_name, 
                playlist_description, 
                self.is_public
            )
            
            if not playlist_info:
                self.finished_signal.emit(False, "プレイリストの作成に失敗しました")
                return
            
            playlist_id = playlist_info.get("id")
            self.progress_updated.emit(f"プレイリスト「{self.playlist_name}」を作成しました")
            
            # 楽曲を検索してURIを取得
            track_uris = []
            failed_tracks = []
            
            for i, song in enumerate(self.songs):
                self.progress_updated.emit(f"楽曲を検索中... ({i+1}/{len(self.songs)}): {song}")
                
                # 楽曲を検索
                search_results = self.spotify_client.search_tracks(song, limit=1)
                if search_results and search_results.get("tracks", {}).get("items"):
                    track = search_results["tracks"]["items"][0]
                    track_uris.append(track["uri"])
                    self.progress_updated.emit(f"✓ 見つかりました: {track['name']} - {track['artists'][0]['name']}")
                else:
                    failed_tracks.append(song)
                    self.progress_updated.emit(f"✗ 見つかりませんでした: {song}")
            
            # 見つかった楽曲をプレイリストに追加
            if track_uris:
                self.progress_updated.emit("楽曲をプレイリストに追加中...")
                
                # Spotify APIは一度に最大100曲まで追加可能
                for i in range(0, len(track_uris), 100):
                    batch = track_uris[i:i+100]
                    result = self.spotify_client.add_tracks_to_playlist(playlist_id, batch)
                    if not result:
                        self.finished_signal.emit(False, f"楽曲の追加に失敗しました (バッチ {i//100 + 1})")
                        return
                
                success_count = len(track_uris)
                failed_count = len(failed_tracks)
                
                success_message = f"プレイリスト「{self.playlist_name}」を作成しました！\n\n"
                success_message += f"✓ 追加された楽曲: {success_count}曲\n"
                if failed_count > 0:
                    success_message += f"✗ 見つからなかった楽曲: {failed_count}曲\n"
                    success_message += f"見つからなかった楽曲: {', '.join(failed_tracks[:3])}"
                    if len(failed_tracks) > 3:
                        success_message += f" など{len(failed_tracks)}曲"
                
                success_message += f"\n\nSpotifyアプリでプレイリストを確認できます。"
                
                self.finished_signal.emit(True, success_message)
            else:
                self.finished_signal.emit(False, "追加できる楽曲が見つかりませんでした")
                
        except Exception as e:
            self.finished_signal.emit(False, f"エラーが発生しました: {str(e)}")

import sys
import random
import os
import urllib.parse
import webbrowser
import requests
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, 
                             QMessageBox, QPushButton, QLineEdit, QDialog, QLabel,
                             QInputDialog, QProgressDialog, QCheckBox)
from PyQt6.QtCore import QTimer, Qt, QUrl, QThread, pyqtSignal
from song_manager import SongManager
from playlist_manager import PlaylistManager
from swipeable_widget import SwipeableWidget
from song_display_widget import SongDisplayWidget
from playlist_widget import PlaylistWidget
from spotify_auth import SpotifyAuthenticator, SpotifyClient
from emotion_song_manager import EmotionSongManager

class PlaylistCreationThread(QThread):
    """プレイリスト作成を別スレッドで実行"""
    progress_updated = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, spotify_client, playlist_name, songs, is_public=False):
        super().__init__()
        self.spotify_client = spotify_client
        self.playlist_name = playlist_name
        self.songs = songs
        self.is_public = is_public
        
    def run(self):
        try:
            # ユーザー情報を取得
            self.progress_updated.emit("ユーザー情報を取得中...")
            user_info = self.spotify_client.get_current_user()
            if not user_info:
                self.finished_signal.emit(False, "ユーザー情報の取得に失敗しました")
                return
            
            user_id = user_info.get("id")
            self.progress_updated.emit(f"ユーザー: {user_info.get('display_name', user_id)}")
            
            # プレイリストを作成
            self.progress_updated.emit("プレイリストを作成中...")
            playlist_description = f"MEET une アプリで作成 - {datetime.now().strftime('%Y年%m月%d日')}"
            playlist_info = self.spotify_client.create_playlist(
                user_id, 
                self.playlist_name, 
                playlist_description, 
                self.is_public
            )
            
            if not playlist_info:
                self.finished_signal.emit(False, "プレイリストの作成に失敗しました")
                return
            
            playlist_id = playlist_info.get("id")
            self.progress_updated.emit(f"プレイリスト「{self.playlist_name}」を作成しました")
            
            # 楽曲を検索してURIを取得
            track_uris = []
            failed_tracks = []
            
            for i, song in enumerate(self.songs):
                self.progress_updated.emit(f"楽曲を検索中... ({i+1}/{len(self.songs)}): {song}")
                
                # 楽曲を検索
                search_results = self.spotify_client.search_tracks(song, limit=1)
                if search_results and search_results.get("tracks", {}).get("items"):
                    track = search_results["tracks"]["items"][0]
                    track_uris.append(track["uri"])
                    self.progress_updated.emit(f"✓ 見つかりました: {track['name']} - {track['artists'][0]['name']}")
                else:
                    failed_tracks.append(song)
                    self.progress_updated.emit(f"✗ 見つかりませんでした: {song}")
            
            # 見つかった楽曲をプレイリストに追加
            if track_uris:
                self.progress_updated.emit("楽曲をプレイリストに追加中...")
                
                # Spotify APIは一度に最大100曲まで追加可能
                for i in range(0, len(track_uris), 100):
                    batch = track_uris[i:i+100]
                    result = self.spotify_client.add_tracks_to_playlist(playlist_id, batch)
                    if not result:
                        self.finished_signal.emit(False, f"楽曲の追加に失敗しました (バッチ {i//100 + 1})")
                        return
                
                success_count = len(track_uris)
                failed_count = len(failed_tracks)
                
                success_message = f"プレイリスト「{self.playlist_name}」を作成しました！\n\n"
                success_message += f"✓ 追加された楽曲: {success_count}曲\n"
                if failed_count > 0:
                    success_message += f"✗ 見つからなかった楽曲: {failed_count}曲\n"
                    success_message += f"見つからなかった楽曲: {', '.join(failed_tracks[:3])}"
                    if len(failed_tracks) > 3:
                        success_message += f" など{len(failed_tracks)}曲"
                
                success_message += f"\n\nSpotifyアプリでプレイリストを確認できます。"
                
                self.finished_signal.emit(True, success_message)
            else:
                self.finished_signal.emit(False, "追加できる楽曲が見つかりませんでした")
                
        except Exception as e:
            self.finished_signal.emit(False, f"エラーが発生しました: {str(e)}")


class SwipeApp(QWidget):
    """メインアプリケーションクラス"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MEET une - Swipe Demo")

        # Spotify認証オブジェクトとクライアントオブジェクトの初期化
        self.authenticator = SpotifyAuthenticator()
        self.spotify_client = SpotifyClient(self.authenticator)
        self.access_token = None
        
        # 各種マネージャーの初期化
        self.song_manager = SongManager()
        self.playlist_manager = PlaylistManager()

        # 感情ベース楽曲マネージャーの初期化
        self.emotion_song_manager = EmotionSongManager(self.spotify_client)
        
        # 認証ステータスの表示ラベル
        self.auth_status_label = QLabel("Spotify未認証")
        self.auth_status_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.auth_status_label.setStyleSheet("color: red; font-size: 12px;")

        # 認証ボタン
        self.auth_button = QPushButton("Spotifyでログイン")
        self.auth_button.clicked.connect(self.start_spotify_auth)
        self.auth_button.setStyleSheet("""
            QPushButton {
                background-color: #1DB954;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1ed760;
            }
        """)
        
        self.init_ui()
        self.connect_signals()
        self.load_current_song()

        self.notification_timer = QTimer(self)
        random_interval_seconds = random.randint(5, 30)
        self.notification_timer.setInterval(random_interval_seconds*1000)
        self.notification_timer.setSingleShot(True)
        self.notification_timer.timeout.connect(self.show_notification)
        self.notification_timer.start()

        self.token_refresh_timer = QTimer(self)
        self.token_refresh_timer.setInterval(5 * 60 * 1000)
        self.token_refresh_timer.timeout.connect(self.check_and_refresh_token)
        self.token_refresh_timer.start()

    def init_ui(self):
        # メインレイアウト（横分割）
        main_layout = QHBoxLayout()
        
        # 左側：スワイプ可能な楽曲表示エリア
        self.swipe_widget = SwipeableWidget()
        swipe_layout = QVBoxLayout()
        
        self.song_display = SongDisplayWidget()
        swipe_layout.addWidget(self.song_display)

        # 右側：プレイリストエリア
        self.playlist_widget = PlaylistWidget()
        self.playlist_widget.setMaximumWidth(300)
        
        # 認証ボタンとステータスラベル、感情選択ボタンを配置
        auth_bar_layout = QHBoxLayout()
        auth_bar_layout.addWidget(self.auth_button)
    
        # 感情選択ボタンを追加
        emotion_button = QPushButton("気分で選ぶ")
        emotion_button.clicked.connect(self.show_emotion_selector)
        emotion_button.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF5252;
            }
        """)
        auth_bar_layout.addWidget(emotion_button)
        auth_bar_layout.addWidget(self.auth_status_label)
        
        swipe_layout.addLayout(auth_bar_layout)
        self.swipe_widget.setLayout(swipe_layout)

        # メインレイアウトに追加
        main_layout.addWidget(self.swipe_widget, 2)
        main_layout.addWidget(self.playlist_widget, 1)
        
        self.setLayout(main_layout)
    
    def connect_signals(self):
        """シグナルとスロットを接続"""
        self.swipe_widget.swipe_left.connect(self.on_swipe_left)
        self.swipe_widget.swipe_right.connect(self.on_swipe_right)
        self.playlist_widget.create_spotify_playlist.connect(self.on_create_spotify_playlist)
        
        # 楽曲表示エリアのダブルクリックで詳細情報を表示（オプション）
        self.song_display.mouseDoubleClickEvent = lambda event: self.show_current_song_info()
    
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
        """Spotifyプレイリスト作成"""
        liked_songs = self.playlist_manager.get_songs()
        
        if not liked_songs:
            QMessageBox.information(self, "情報", "プレイリストが空です。まず楽曲を追加してください。")
            return
        
        # 認証チェック
        if not self.authenticator.get_access_token():
            QMessageBox.warning(self, "認証が必要", "Spotifyプレイリストを作成するには、まずSpotifyにログインしてください。")
            return
        
        # プレイリスト名の入力
        playlist_name, ok = QInputDialog.getText(
            self, 
            "プレイリスト名", 
            "作成するプレイリストの名前を入力してください:",
            text=f"MEET une プレイリスト - {datetime.now().strftime('%Y/%m/%d')}"
        )
        
        if not ok or not playlist_name.strip():
            return
        
        # 公開/非公開の選択
        dialog = QDialog(self)
        dialog.setWindowTitle("プレイリスト設定")
        dialog.setModal(True)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"プレイリスト名: {playlist_name}"))
        layout.addWidget(QLabel(f"楽曲数: {len(liked_songs)}曲"))
        
        public_checkbox = QCheckBox("公開プレイリストにする")
        public_checkbox.setChecked(False)
        layout.addWidget(public_checkbox)
        
        button_layout = QHBoxLayout()
        create_button = QPushButton("作成")
        cancel_button = QPushButton("キャンセル")
        
        create_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(create_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        is_public = public_checkbox.isChecked()
        
        # プログレスダイアログの作成
        self.progress_dialog = QProgressDialog("プレイリストを作成中...", "キャンセル", 0, 0, self)
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setValue(0)
        
        # プレイリスト作成スレッドを開始
        self.creation_thread = PlaylistCreationThread(
            self.spotify_client, 
            playlist_name, 
            liked_songs, 
            is_public
        )
        
        # スレッドのシグナルを接続
        self.creation_thread.progress_updated.connect(self.progress_dialog.setLabelText)
        self.creation_thread.finished_signal.connect(self.handle_playlist_creation_finished)
        
        # キャンセル処理
        self.progress_dialog.canceled.connect(self.creation_thread.quit)
        
        self.creation_thread.start()
        self.progress_dialog.exec()
    
    def handle_playlist_creation_finished(self, success, message):
        """プレイリスト作成完了時の処理"""
        self.on_playlist_creation_finished(success, message, self.progress_dialog)
    
    def on_playlist_creation_finished(self, success, message, progress_dialog):
        """プレイリスト作成完了時の処理"""
        progress_dialog.close()
        
        if success:
            QMessageBox.information(self, "成功", message)
            # 作成成功時に現在のプレイリストをクリア（オプション）
            reply = QMessageBox.question(
                self,
                "プレイリストをクリア",
                "プレイリストの作成が完了しました。\n現在のプレイリストをクリアしますか？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.playlist_manager.clear_playlist()
                self.playlist_widget.clear_playlist()
        else:
            QMessageBox.warning(self, "エラー", message)

    def show_notification(self):
        """BeRealのような通知を表示する"""
        print("通知がトリガーされました！")
        if not self.authenticator.get_access_token():
            QMessageBox.warning(self, "認証が必要", "Spotifyの曲を共有するには、まずSpotifyにログインしてください。")
            return

        currently_playing = self.spotify_client.get_current_playing()
        song_title = "不明な曲"
        artist_name = "不明なアーティスト"
        spotify_url = None

        if currently_playing and currently_playing.get("is_playing") and currently_playing.get("item"):
            item = currently_playing.get("item")
            song_title = item.get("name", "不明な曲")
            artist_name = ", ".join([artist["name"] for artist in item.get("artists", [])])
            spotify_url = item.get("external_urls", {}).get("spotify")

            message = f"今、聴いている曲を共有しましょう！\n\n🎵 「{song_title}」 - {artist_name}\n\nこの曲を共有しますか？"

            reply = QMessageBox.information(
                self,
                "🎵 BE REAL TIMEY! 🎵",
                message,
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Ok:
                print(f"ユーザーが「OK」（共有）を選択しました: {song_title}")
                if spotify_url:
                    QMessageBox.information(self, "共有", f"この曲のSpotify URLをクリップボードにコピーしました！\n{spotify_url}")
                    QApplication.clipboard().setText(spotify_url)
                else:
                    QMessageBox.warning(self, "共有", "この曲の共有URLが見つかりませんでした。")
            else:
                print("ユーザーが「キャンセル」を選択しました。")
        else:
            QMessageBox.information(self, "通知", "現在、Spotifyで曲が再生されていません。Spotifyアプリを開いて何か再生を開始してください。")
            print("Spotifyで再生中のアイテムがありません。")

    def start_spotify_auth(self):
        """Spotify認証プロセスを開始する"""
        auth_url = self.authenticator.get_auth_url()
        print(f"Spotify認証URL: {auth_url}")
        webbrowser.open(auth_url)

        self.auth_dialog = QDialog(self)
        self.auth_dialog.setWindowTitle("Spotify認証")
        dialog_layout = QVBoxLayout()
        dialog_layout.addWidget(QLabel("ブラウザでSpotifyにログインし、許可後、\nリダイレクトされたURLをここに貼り付けてください:"))
        self.code_input = QLineEdit()
        dialog_layout.addWidget(self.code_input)
        submit_button = QPushButton("認証コードを送信")
        submit_button.clicked.connect(self.process_auth_code_input)
        dialog_layout.addWidget(submit_button)
        self.auth_dialog.setLayout(dialog_layout)
        self.auth_dialog.exec()

    def process_auth_code_input(self):
        """ユーザーが入力した認証コードを処理する"""
        full_redirect_uri = self.code_input.text().strip()
        if not full_redirect_uri:
            QMessageBox.warning(self, "認証エラー", "URLが入力されていません。")
            return

        try:
            parsed_url = QUrl(full_redirect_uri)
            query_items = urllib.parse.parse_qs(parsed_url.query())
            auth_code = query_items.get('code', [None])[0]

            if auth_code:
                print(f"認証コードを取得しました: {auth_code[:10]}...")
                self.auth_dialog.accept()
                self.request_spotify_tokens(auth_code)
            else:
                QMessageBox.warning(self, "認証エラー", "無効なURLまたは認証コードが見つかりませんでした。")
        except Exception as e:
            QMessageBox.warning(self, "認証エラー", f"URL解析エラー: {str(e)}")

    def request_spotify_tokens(self, auth_code):
        """認証コードを使用してアクセストークンを取得する"""
        try:
            tokens = self.authenticator.get_tokens(auth_code)
            if tokens:
                print("Spotifyアクセストークンを取得しました")
                self.access_token = tokens.get('access_token')
                self.update_auth_status(True)
                QMessageBox.information(self, "認証成功", "Spotifyアカウントに正常に接続されました！")
            else:
                QMessageBox.warning(self, "認証エラー", "トークンの取得に失敗しました。")
        except Exception as e:
            QMessageBox.warning(self, "認証エラー", f"認証処理中にエラーが発生しました: {str(e)}")

    def update_auth_status(self, is_authenticated):
        """認証ステータスを更新する"""
        if is_authenticated:
            self.auth_status_label.setText("Spotify認証済み")
            self.auth_status_label.setStyleSheet("color: green; font-size: 12px;")
            self.auth_button.setText("認証済み")
            self.auth_button.setEnabled(False)
        else:
            self.auth_status_label.setText("Spotify未認証")
            self.auth_status_label.setStyleSheet("color: red; font-size: 12px;")
            self.auth_button.setText("Spotifyでログイン")
            self.auth_button.setEnabled(True)

    def check_and_refresh_token(self):
        """トークンの有効性をチェックし、必要に応じて更新する"""
        if self.authenticator.get_access_token():
            # トークンの有効性をチェック
            user_info = self.spotify_client.get_current_user()
            if not user_info:
                # トークンが無効な場合、リフレッシュを試行
                if self.authenticator.refresh_token():
                    print("トークンをリフレッシュしました")
                else:
                    print("トークンのリフレッシュに失敗しました")
                    self.update_auth_status(False)
    
    def show_emotion_selector(self):
        """感情選択ダイアログを表示"""
        emotions = self.emotion_song_manager.get_available_emotions()

        emotion, ok = QInputDialog.getItem(
            self,
            "感情選択",
            "現在の気分を選択してください:",
            emotions,
            0,
            False
        )
    
        if ok and emotion:
            self.load_emotion_songs(emotion)
    
    def show_current_song_info(self):
        """現在の楽曲の詳細情報を表示"""
        current_song = self.song_manager.get_current_song()
        if current_song and hasattr(current_song, 'spotify_uri') and current_song.spotify_uri:
            # Spotify URIがある場合、Spotifyアプリで開く
            try:
                webbrowser.open(current_song.spotify_uri)
            except:
                QMessageBox.information(self, "情報", f"楽曲: {current_song.title}\nアーティスト: {current_song.artist}")
        else:
            QMessageBox.information(self, "情報", f"楽曲: {current_song.title}\nアーティスト: {current_song.artist}")

    def load_emotion_songs(self, emotion):
        """選択された感情に基づいて楽曲を読み込み"""
        try:
            # プログレスダイアログの表示
            progress = QProgressDialog("楽曲を検索中...", "キャンセル", 0, 0, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.show()
            
            # 感情ベース楽曲を生成
            self.emotion_song_manager.set_emotion_songs(emotion, limit=20)
            
            # 楽曲が見つかった場合、song_managerに設定
            emotion_songs = self.emotion_song_manager.current_emotion_songs
            if emotion_songs:
                # 既存の楽曲リストを置き換え
                self.song_manager.songs = emotion_songs
                self.song_manager.current_index = 0
                
                # 画面を更新
                self.load_current_song()
                
                description = self.emotion_song_manager.get_emotion_description(emotion)
                QMessageBox.information(
                    self,
                    "楽曲読み込み完了",
                    f"「{emotion}」の楽曲を{len(emotion_songs)}曲読み込みました。\n\n{description}"
                )
            else:
                QMessageBox.warning(self, "エラー", "該当する楽曲が見つかりませんでした。")
            
            progress.close()
            
        except Exception as e:
            QMessageBox.warning(self, "エラー", f"楽曲の読み込み中にエラーが発生しました: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SwipeApp()
    window.show()
    sys.exit(app.exec())
