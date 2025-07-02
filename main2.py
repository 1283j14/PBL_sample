# main.py
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QProgressDialog
from PyQt6.QtCore import QThread, pyqtSignal

from song_manager import SongManager
from playlist_manager import PlaylistManager
from swipeable_widget import SwipeableWidget
from song_display_widget import SongDisplayWidget
from playlist_widget import PlaylistWidget
from spotify_manager import SpotifyManager
from spotify_auth_dialog import SpotifyAuthDialog, PlaylistCreationDialog
import config


class PlaylistCreationThread(QThread):
    """プレイリスト作成処理用スレッド"""
    finished = pyqtSignal(object)  # 作成結果を送信
    error = pyqtSignal(str)  # エラー発生シグナル
    
    def __init__(self, spotify_manager, playlist_name, songs):
        super().__init__()
        self.spotify_manager = spotify_manager
        self.playlist_name = playlist_name
        self.songs = songs
    
    def run(self):
        """プレイリスト作成処理を別スレッドで実行"""
        try:
            success = self.spotify_manager.create_playlist(
                self.playlist_name, 
                self.songs, 
                f"Created by SwipeApp - {len(self.songs)} songs"
            )
            self.finished.emit(success)
        except Exception as e:
            self.error.emit(str(e))


class SwipeApp(QWidget):
    """メインアプリケーションクラス"""
    
    def __init__(self):
        super().__init__()
        self.init_managers()
        self.init_ui()
        self.connect_signals()
        self.setup_spotify()
        self.load_current_song()
    
    def init_managers(self):
        """各種マネージャーを初期化"""
        self.song_manager = SongManager()
        self.playlist_manager = PlaylistManager()
        
        # Spotify設定の検証
        is_valid, message = config.validate_spotify_config()
        if not is_valid:
            print(f"⚠️  Spotify設定エラー: {message}")
            print("config.pyファイルでSpotify API認証情報を設定してください。")
            self.spotify_manager = None
        else:
            spotify_config = config.get_spotify_config()
            self.spotify_manager = SpotifyManager(
                client_id=spotify_config['CLIENT_ID'],
                client_secret=spotify_config['CLIENT_SECRET'],
                redirect_uri=spotify_config['REDIRECT_URI']
            )
    
    def setup_spotify(self):
        """Spotify関連の設定"""
        if self.spotify_manager:
            # Spotifyマネージャーのシグナルを接続
            self.spotify_manager.auth_completed.connect(self.on_spotify_auth_completed)
            self.spotify_manager.playlist_created.connect(self.on_spotify_playlist_created)
            self.spotify_manager.error_occurred.connect(self.on_spotify_error)
    
    def init_ui(self):
        """UIを初期化"""
        # ウィンドウ設定
        app_config = config.get_app_config()
        self.setWindowTitle(app_config['WINDOW_TITLE'])
        self.resize(*app_config['WINDOW_SIZE'])
        
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
        # スワイプイベント
        self.swipe_widget.swipe_left.connect(self.on_swipe_left)
        self.swipe_widget.swipe_right.connect(self.on_swipe_right)
        
        # プレイリストウィジェットのイベント
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
        """Spotifyプレイリスト作成処理"""
        liked_songs = self.playlist_manager.get_songs()
        
        if not liked_songs:
            QMessageBox.information(self, "情報", "プレイリストが空です。まず楽曲を追加してください。")
            return
        
        if not self.spotify_manager:
            QMessageBox.warning(
                self, 
                "Spotify設定エラー", 
                "Spotify API設定が正しくありません。\n"
                "config.pyファイルでCLIENT_IDとCLIENT_SECRETを設定してください。"
            )
            return
        
        # Spotify認証状態をチェック
        if not self.spotify_manager.is_authenticated():
            self.show_spotify_auth_dialog()
        else:
            self.show_playlist_creation_dialog(liked_songs)
    
    def show_spotify_auth_dialog(self):
        """Spotify認証ダイアログを表示"""
        auth_dialog = SpotifyAuthDialog(self)
        
        if auth_dialog.exec() == QMessageBox.DialogCode.Accepted:
            # 認証成功後、プレイリスト作成ダイアログを表示
            liked_songs = self.playlist_manager.get_songs()
            self.show_playlist_creation_dialog(liked_songs)
    
    def show_playlist_creation_dialog(self, songs):
        """プレイリスト作成ダイアログを表示"""
        creation_dialog = PlaylistCreationDialog(songs, self)
        creation_dialog.exec()
    
    def on_spotify_auth_completed(self, success):
        """Spotify認証完了時の処理"""
        if success:
            print("✅ Spotify認証が完了しました")
            QMessageBox.information(
                self, 
                "認証完了", 
                "Spotifyへの認証が完了しました！\n"
                "プレイリストを作成できます。"
            )
        else:
            print("❌ Spotify認証に失敗しました")
            QMessageBox.warning(
                self, 
                "認証失敗", 
                "Spotifyへの認証に失敗しました。\n"
                "設定を確認して再度お試しください。"
            )
    
    def on_spotify_playlist_created(self, playlist_id, playlist_url):
        """Spotifyプレイリスト作成完了時の処理"""
        print(f"✅ プレイリストが作成されました: {playlist_url}")
        
        reply = QMessageBox.question(
            self,
            "プレイリスト作成完了",
            f"Spotifyプレイリストが正常に作成されました！\n"
            f"プレイリストID: {playlist_id}\n\n"
            f"Spotifyで開きますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            import webbrowser
            webbrowser.open(playlist_url)
    
    def on_spotify_error(self, error_message):
        """Spotifyエラー発生時の処理"""
        print(f"❌ Spotifyエラー: {error_message}")
        QMessageBox.critical(
            self,
            "Spotifyエラー",
            f"Spotify処理中にエラーが発生しました:\n\n{error_message}"
        )
    
    def closeEvent(self, event):
        """アプリケーション終了時の処理"""
        reply = QMessageBox.question(
            self,
            "アプリケーション終了",
            "アプリケーションを終了しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            print("アプリケーションを終了します...")
            event.accept()
        else:
            event.ignore()
    
    def show_spotify_status(self):
        """Spotify接続状態を表示"""
        if not self.spotify_manager:
            return "Spotify: 未設定"
        elif self.spotify_manager.is_authenticated():
            return "Spotify: 接続済み"
        else:
            return "Spotify: 未接続"


def main():
    """メイン実行関数"""
    app = QApplication(sys.argv)
    
    # アプリケーションのメタ情報設定
    app.setApplicationName("SwipeApp")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SwipeApp Development")
    
    # メインウィンドウ作成
    try:
        window = SwipeApp()
        window.show()
        
        print("🎵 SwipeApp - Spotify連携版が起動しました")
        print("=" * 50)
        print("操作方法:")
        print("- 右スワイプ（右にドラッグ）：次の曲へ")
        print("- 左スワイプ（左にドラッグ）：プレイリストに追加")
        print("- 「Spotifyプレイリスト作成」ボタン：Spotifyにプレイリスト作成")
        print("- ウィンドウを閉じるか、Ctrl+Cで終了")
        print("=" * 50)
        
        # Spotify設定状態の表示
        print(f"Spotify状態: {window.show_spotify_status()}")
        
        # アプリケーション実行
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ アプリケーション起動エラー: {e}")
        QMessageBox.critical(
            None,
            "起動エラー",
            f"アプリケーションの起動に失敗しました:\n{e}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
