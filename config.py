# Spotify API設定
# Spotify Developer Dashboardで取得したCredentialsを設定してください
# https://developer.spotify.com/dashboard/

SPOTIFY_CLIENT_ID = "Y1264cdded6274116ad86ae402ca3f7f1"
SPOTIFY_CLIENT_SECRET = "e48ec1cb727040c29d4b2753347a72ea"
SPOTIFY_REDIRECT_URI = "http://kantanspotify/callback"

# 設定の確認
def validate_config():
    """設定が正しく行われているかチェック"""
    if SPOTIFY_CLIENT_ID == "YOUR_CLIENT_ID_HERE":
        return False, "SPOTIFY_CLIENT_ID が設定されていません"
    
    if SPOTIFY_CLIENT_SECRET == "YOUR_CLIENT_SECRET_HERE":
        return False, "SPOTIFY_CLIENT_SECRET が設定されていません"
    
    return True, "設定OK"

# 使用方法の説明
CONFIG_HELP = """
Spotify API設定手順:

1. Spotify Developer Dashboard にアクセス
   https://developer.spotify.com/dashboard/

2. 「Create App」をクリックしてアプリを作成

3. App settings で以下を設定:
   - Redirect URIs: http://localhost:8888/callback

4. Client ID と Client Secret をコピー

5. このファイル（config.py）の以下を編集:
   - SPOTIFY_CLIENT_ID = "取得したClient ID"
   - SPOTIFY_CLIENT_SECRET = "取得したClient Secret"

6. アプリケーションを再起動
"""
