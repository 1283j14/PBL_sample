# spotify_auth.py - プレイリスト作成機能追加版
import os
import base64
import json
import requests
from datetime import datetime, timedelta
from urllib.parse import urlencode, quote


class SpotifyAuthenticator:
    """Spotify認証を処理するクラス"""
    
    def __init__(self):
        # 環境変数またはハードコードされた値
        self.CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', '1264cdded6274116ad86ae402ca3f7f1')
        self.CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', 'e48ec1cb727040c29d4b2753347a72ea')
        self.REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'https://1283j14.github.io/swipe_app.github.io/')
        
        # Spotifyエンドポイント
        self.AUTH_URL = 'https://accounts.spotify.com/authorize'
        self.TOKEN_URL = 'https://accounts.spotify.com/api/token'
        
        # トークンストレージ
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        
    def get_auth_url(self):
        """認証URLを生成"""
        scopes = [
            'user-read-private',
            'user-read-email',
            'user-read-currently-playing',
            'user-read-playback-state',
            'playlist-modify-public',
            'playlist-modify-private',
            'playlist-read-private',
            'playlist-read-collaborative'
        ]
        
        params = {
            'client_id': self.CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': self.REDIRECT_URI,
            'scope': ' '.join(scopes),
            'show_dialog': 'true'
        }
        
        return f"{self.AUTH_URL}?{urlencode(params)}"
    
    def get_tokens(self, auth_code):
        """認証コードを使用してアクセストークンを取得"""
        headers = {
            'Authorization': f'Basic {base64.b64encode(f"{self.CLIENT_ID}:{self.CLIENT_SECRET}".encode()).decode()}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.REDIRECT_URI
        }
        
        try:
            response = requests.post(self.TOKEN_URL, headers=headers, data=data)
            response.raise_for_status()
            
            tokens = response.json()
            self.access_token = tokens.get('access_token')
            self.refresh_token = tokens.get('refresh_token')
            
            # トークンの有効期限を計算
            expires_in = tokens.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            return tokens
            
        except requests.exceptions.RequestException as e:
            print(f"トークン取得エラー: {e}")
            return None
    
    def refresh_access_token(self):
        """リフレッシュトークンを使用してアクセストークンを更新"""
        if not self.refresh_token:
            return False
        
        headers = {
            'Authorization': f'Basic {base64.b64encode(f"{self.CLIENT_ID}:{self.CLIENT_SECRET}".encode()).decode()}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        
        try:
            response = requests.post(self.TOKEN_URL, headers=headers, data=data)
            response.raise_for_status()
            
            tokens = response.json()
            self.access_token = tokens.get('access_token')
            
            # 新しいリフレッシュトークンが提供された場合は更新
            if 'refresh_token' in tokens:
                self.refresh_token = tokens['refresh_token']
            
            # トークンの有効期限を更新
            expires_in = tokens.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"トークン更新エラー: {e}")
            return False
    
    def get_access_token(self):
        """有効なアクセストークンを取得（必要に応じて更新）"""
        if not self.access_token:
            return None
        
        # トークンの有効期限をチェック
        if self.token_expires_at and datetime.now() >= self.token_expires_at:
            if self.refresh_access_token():
                return self.access_token
            else:
                return None
        
        return self.access_token
    
    def is_authenticated(self):
        """認証状態を確認"""
        return self.get_access_token() is not None


class SpotifyClient:
    """Spotify Web APIクライアント"""
    
    def __init__(self, authenticator):
        self.authenticator = authenticator
        self.BASE_URL = 'https://api.spotify.com/v1'
    
    def _get_headers(self):
        """APIリクエスト用のヘッダーを取得"""
        token = self.authenticator.get_access_token()
        if not token:
            return None
        
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method, endpoint, **kwargs):
        """APIリクエストを実行"""
        headers = self._get_headers()
        if not headers:
            return None
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"APIリクエストエラー: {e}")
            return None
    
    def get_current_user(self):
        """現在のユーザー情報を取得"""
        return self._make_request('GET', 'me')
    
    def get_current_playing(self):
        """現在再生中の曲情報を取得"""
        return self._make_request('GET', 'me/player/currently-playing')
    
    def search_tracks(self, query, limit=20):
        """楽曲を検索"""
        params = {
            'q': query,
            'type': 'track',
            'limit': limit
        }
        return self._make_request('GET', 'search', params=params)
    
    def create_playlist(self, user_id, name, description="", public=True):
        """プレイリストを作成"""
        data = {
            'name': name,
            'description': description,
            'public': public
        }
        return self._make_request('POST', f'users/{user_id}/playlists', json=data)
    
    def add_tracks_to_playlist(self, playlist_id, track_uris):
        """プレイリストに楽曲を追加"""
        if not track_uris:
            return False
        
        # URIが文字列のリストかどうかチェック
        if isinstance(track_uris, str):
            track_uris = [track_uris]
        
        # spotify:track: プレフィックスがない場合は追加
        formatted_uris = []
        for uri in track_uris:
            if uri.startswith('spotify:track:'):
                formatted_uris.append(uri)
            else:
                formatted_uris.append(f'spotify:track:{uri}')
        
        data = {
            'uris': formatted_uris
        }
        
        result = self._make_request('POST', f'playlists/{playlist_id}/tracks', json=data)
        return result is not None
    
    def get_playlist(self, playlist_id):
        """プレイリスト情報を取得"""
        return self._make_request('GET', f'playlists/{playlist_id}')
    
    def get_user_playlists(self, limit=20, offset=0):
        """ユーザーのプレイリストを取得"""
        params = {
            'limit': limit,
            'offset': offset
        }
        return self._make_request('GET', 'me/playlists', params=params)
    
    def remove_tracks_from_playlist(self, playlist_id, track_uris):
        """プレイリストから楽曲を削除"""
        if not track_uris:
            return False
        
        # URIが文字列のリストかどうかチェック
        if isinstance(track_uris, str):
            track_uris = [track_uris]
        
        # spotify:track: プレフィックスがない場合は追加
        formatted_uris = []
        for uri in track_uris:
            if uri.startswith('spotify:track:'):
                formatted_uris.append({'uri': uri})
            else:
                formatted_uris.append({'uri': f'spotify:track:{uri}'})
        
        data = {
            'tracks': formatted_uris
        }
        
        result = self._make_request('DELETE', f'playlists/{playlist_id}/tracks', json=data)
        return result is not None
    
    def get_track_by_id(self, track_id):
        """トラックIDから楽曲情報を取得"""
        return self._make_request('GET', f'tracks/{track_id}')
    
    def get_tracks_by_ids(self, track_ids):
        """複数のトラックIDから楽曲情報を取得"""
        if not track_ids:
            return None
        
        # 最大50件まで一度に取得可能
        if len(track_ids) > 50:
            track_ids = track_ids[:50]
        
        params = {
            'ids': ','.join(track_ids)
        }
        return self._make_request('GET', 'tracks', params=params)
    
    def get_user_top_tracks(self, limit=20, time_range='medium_term'):
        """ユーザーのトップトラックを取得"""
        params = {
            'limit': limit,
            'time_range': time_range  # short_term, medium_term, long_term
        }
        return self._make_request('GET', 'me/top/tracks', params=params)
    
    def get_user_top_artists(self, limit=20, time_range='medium_term'):
        """ユーザーのトップアーティストを取得"""
        params = {
            'limit': limit,
            'time_range': time_range  # short_term, medium_term, long_term
        }
        return self._make_request('GET', 'me/top/artists', params=params)
    
    def get_recommendations(self, seed_tracks=None, seed_artists=None, seed_genres=None, limit=20, **kwargs):
        """推奨楽曲を取得"""
        params = {
            'limit': limit
        }
        
        # シード値の設定（最大5つまで）
        if seed_tracks:
            params['seed_tracks'] = ','.join(seed_tracks[:5])
        if seed_artists:
            params['seed_artists'] = ','.join(seed_artists[:5])
        if seed_genres:
            params['seed_genres'] = ','.join(seed_genres[:5])
        
        # 追加パラメータ（target_*, min_*, max_*）
        for key, value in kwargs.items():
            if key.startswith(('target_', 'min_', 'max_')):
                params[key] = value
        
        return self._make_request('GET', 'recommendations', params=params)
    
    def get_available_genre_seeds(self):
        """利用可能なジャンルシードを取得"""
        return self._make_request('GET', 'recommendations/available-genre-seeds')
    
    def refresh_token(self):
        """トークンを手動で更新"""
        return self.authenticator.refresh_access_token()
    
    def is_authenticated(self):
        """認証状態を確認"""
        return self.authenticator.is_authenticated()


# 使用例とヘルパー関数
class SpotifyPlaylistManager:
    """プレイリスト管理用のヘルパークラス"""
    
    def __init__(self, spotify_client):
        self.client = spotify_client
    
    def create_playlist_from_songs(self, playlist_name, songs, description="", public=False):
        """楽曲リストからプレイリストを作成"""
        if not self.client.is_authenticated():
            return False, "認証が必要です"
        
        # ユーザー情報を取得
        user_info = self.client.get_current_user()
        if not user_info:
            return False, "ユーザー情報の取得に失敗しました"
        
        # プレイリストを作成
        playlist_info = self.client.create_playlist(
            user_info['id'], 
            playlist_name, 
            description, 
            public
        )
        
        if not playlist_info:
            return False, "プレイリストの作成に失敗しました"
        
        # 楽曲を検索してURIを取得
        track_uris = []
        failed_tracks = []
        
        for song in songs:
            # 楽曲名とアーティスト名で検索
            search_query = f"{song.title} {song.artist}"
            search_results = self.client.search_tracks(search_query, limit=1)
            
            if search_results and search_results.get('tracks', {}).get('items'):
                track = search_results['tracks']['items'][0]
                track_uris.append(track['uri'])
            else:
                failed_tracks.append(str(song))
        
        # 見つかった楽曲をプレイリストに追加
        if track_uris:
            success = self.client.add_tracks_to_playlist(playlist_info['id'], track_uris)
            if success:
                return True, f"プレイリスト '{playlist_name}' を作成しました。{len(track_uris)}曲を追加しました。"
            else:
                return False, "楽曲の追加に失敗しました"
        else:
            return False, "追加できる楽曲が見つかりませんでした"
    
    def get_playlist_tracks(self, playlist_id):
        """プレイリストの楽曲を取得"""
        playlist = self.client.get_playlist(playlist_id)
        if playlist and 'tracks' in playlist:
            return playlist['tracks']['items']
        return []
    
    def duplicate_playlist(self, source_playlist_id, new_name):
        """プレイリストを複製"""
        # 元のプレイリストの楽曲を取得
        tracks = self.get_playlist_tracks(source_playlist_id)
        track_uris = [track['track']['uri'] for track in tracks if track['track']]
        
        # ユーザー情報を取得
        user_info = self.client.get_current_user()
        if not user_info:
            return False, "ユーザー情報の取得に失敗しました"
        
        # 新しいプレイリストを作成
        new_playlist = self.client.create_playlist(
            user_info['id'], 
            new_name, 
            f"複製元: {source_playlist_id}"
        )
        
        if not new_playlist:
            return False, "プレイリストの作成に失敗しました"
        
        # 楽曲を追加
        if track_uris:
            success = self.client.add_tracks_to_playlist(new_playlist['id'], track_uris)
            if success:
                return True, f"プレイリスト '{new_name}' を作成しました。{len(track_uris)}曲を複製しました。"
            else:
                return False, "楽曲の複製に失敗しました"
        
        return True, f"空のプレイリスト '{new_name}' を作成しました。"


# 設定ファイルの例
def create_config_template():
    """設定ファイルのテンプレートを作成"""
    config_template = {
        "spotify": {
            "client_id": "your_client_id_here",
            "client_secret": "your_client_secret_here",
            "redirect_uri": "http://localhost:8888/callback"
        }
    }
    
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config_template, f, indent=2, ensure_ascii=False)
    
    print("config.json テンプレートを作成しました。")
    print("Spotify Developer Dashboardで取得した値を設定してください。")


if __name__ == "__main__":
    # 設定ファイルのテンプレートを作成
    create_config_template()
