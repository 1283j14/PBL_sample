# emotion_song_manager.py
import random
from typing import List, Dict, Optional
from song import Song


class EmotionSongManager:
    """感情に基づいたおすすめ楽曲を管理するクラス"""
    
    def __init__(self, spotify_client):
        self.spotify_client = spotify_client
        self.emotion_mappings = self._initialize_emotion_mappings()
        self.current_emotion_songs = []
        self.current_index = 0
    
    def _initialize_emotion_mappings(self) -> Dict[str, Dict]:
        """感情と音楽特徴量のマッピングを初期化"""
        return {
            "幸せ": {
                "target_valence": 0.8,      # 明るさ
                "target_energy": 0.7,       # エネルギー
                "target_danceability": 0.7,  # ダンサビリティ
                "target_tempo": 120,         # テンポ
                "genres": ["pop", "dance", "funk", "disco", "happy"],
                "description": "明るく元気な楽曲"
            },
            "悲しい": {
                "target_valence": 0.2,
                "target_energy": 0.3,
                "target_danceability": 0.3,
                "target_tempo": 80,
                "genres": ["blues", "sad", "acoustic", "singer-songwriter"],
                "description": "しっとりと落ち着いた楽曲"
            },
            "リラックス": {
                "target_valence": 0.5,
                "target_energy": 0.3,
                "target_danceability": 0.4,
                "target_tempo": 90,
                "genres": ["chill", "ambient", "lo-fi", "jazz", "acoustic"],
                "description": "リラックスできる穏やかな楽曲"
            },
            "興奮": {
                "target_valence": 0.7,
                "target_energy": 0.9,
                "target_danceability": 0.8,
                "target_tempo": 140,
                "genres": ["rock", "electronic", "dance", "pop", "energetic"],
                "description": "エネルギッシュで刺激的な楽曲"
            },
            "怒り": {
                "target_valence": 0.3,
                "target_energy": 0.8,
                "target_danceability": 0.5,
                "target_tempo": 130,
                "genres": ["metal", "rock", "punk", "aggressive"],
                "description": "激しくパワフルな楽曲"
            },
            "恋愛": {
                "target_valence": 0.6,
                "target_energy": 0.5,
                "target_danceability": 0.6,
                "target_tempo": 100,
                "genres": ["r-n-b", "soul", "pop", "romantic"],
                "description": "ロマンチックな楽曲"
            },
            "やる気": {
                "target_valence": 0.8,
                "target_energy": 0.8,
                "target_danceability": 0.7,
                "target_tempo": 125,
                "genres": ["pop", "rock", "electronic", "motivational"],
                "description": "モチベーションを上げる楽曲"
            },
            "懐かしい": {
                "target_valence": 0.5,
                "target_energy": 0.5,
                "target_danceability": 0.5,
                "target_tempo": 110,
                "genres": ["classic-rock", "oldies", "retro", "vintage"],
                "description": "懐かしさを感じる楽曲"
            },
            "集中": {
                "target_valence": 0.4,
                "target_energy": 0.6,
                "target_danceability": 0.3,
                "target_tempo": 100,
                "genres": ["classical", "instrumental", "ambient", "study"],
                "description": "集中力を高める楽曲"
            },
            "パーティー": {
                "target_valence": 0.9,
                "target_energy": 0.9,
                "target_danceability": 0.9,
                "target_tempo": 128,
                "genres": ["dance", "pop", "electronic", "party"],
                "description": "パーティーにぴったりな楽曲"
            }
        }
    
    def get_available_emotions(self) -> List[str]:
        """利用可能な感情の一覧を取得"""
        return list(self.emotion_mappings.keys())
    
    def get_emotion_description(self, emotion: str) -> str:
        """感情の説明を取得"""
        return self.emotion_mappings.get(emotion, {}).get("description", "")
    
    def generate_songs_for_emotion(self, emotion: str, limit: int = 10) -> List[Song]:
        """指定された感情に基づいて楽曲を生成"""
        if not self.spotify_client.is_authenticated():
            return self._get_fallback_songs(emotion, limit)
        
        if emotion not in self.emotion_mappings:
            return []
        
        emotion_config = self.emotion_mappings[emotion]
        
        # 複数の手法で楽曲を取得
        songs = []
        
        # 1. ユーザーのトップトラックベースの推薦
        top_tracks_songs = self._get_songs_from_user_top_tracks(emotion_config, limit // 3)
        songs.extend(top_tracks_songs)
        
        # 2. ジャンルベースの推薦
        genre_songs = self._get_songs_from_genres(emotion_config, limit // 3)
        songs.extend(genre_songs)
        
        # 3. 一般的な検索ベースの推薦
        search_songs = self._get_songs_from_search(emotion, limit // 3)
        songs.extend(search_songs)
        
        # 重複を除去し、指定された数に調整
        unique_songs = []
        seen_ids = set()
        
        for song in songs:
            if song.spotify_id not in seen_ids:
                unique_songs.append(song)
                seen_ids.add(song.spotify_id)
                if len(unique_songs) >= limit:
                    break
        
        # 足りない場合は追加で取得
        if len(unique_songs) < limit:
            additional_songs = self._get_additional_songs(emotion_config, limit - len(unique_songs), seen_ids)
            unique_songs.extend(additional_songs)
        
        return unique_songs[:limit]
    
    def _get_songs_from_user_top_tracks(self, emotion_config: Dict, limit: int) -> List[Song]:
        """ユーザーのトップトラックを基にした推薦"""
        try:
            # ユーザーのトップトラックを取得
            top_tracks = self.spotify_client.get_user_top_tracks(limit=5)
            if not top_tracks or not top_tracks.get('items'):
                return []
            
            # トップトラックのIDを取得
            seed_tracks = [track['id'] for track in top_tracks['items'][:2]]
            
            # 推薦を取得
            recommendations = self.spotify_client.get_recommendations(
                seed_tracks=seed_tracks,
                limit=limit,
                **self._get_audio_features_params(emotion_config)
            )
            
            if recommendations and recommendations.get('tracks'):
                return [self._create_song_from_track(track) for track in recommendations['tracks']]
            
        except Exception as e:
            print(f"ユーザートップトラックベース推薦でエラー: {e}")
        
        return []
    
    def _get_songs_from_genres(self, emotion_config: Dict, limit: int) -> List[Song]:
        """ジャンルベースの推薦"""
        try:
            genres = emotion_config.get('genres', [])
            if not genres:
                return []
            
            # ランダムにジャンルを選択
            selected_genres = random.sample(genres, min(2, len(genres)))
            
            recommendations = self.spotify_client.get_recommendations(
                seed_genres=selected_genres,
                limit=limit,
                **self._get_audio_features_params(emotion_config)
            )
            
            if recommendations and recommendations.get('tracks'):
                return [self._create_song_from_track(track) for track in recommendations['tracks']]
            
        except Exception as e:
            print(f"ジャンルベース推薦でエラー: {e}")
        
        return []
    
    def _get_songs_from_search(self, emotion: str, limit: int) -> List[Song]:
        """検索ベースの推薦"""
        try:
            # 感情に関連するキーワードで検索
            search_queries = self._get_search_queries_for_emotion(emotion)
            songs = []
            
            for query in search_queries:
                search_results = self.spotify_client.search_tracks(query, limit=limit//len(search_queries))
                if search_results and search_results.get('tracks', {}).get('items'):
                    for track in search_results['tracks']['items']:
                        songs.append(self._create_song_from_track(track))
                        if len(songs) >= limit:
                            break
                if len(songs) >= limit:
                    break
            
            return songs
            
        except Exception as e:
            print(f"検索ベース推薦でエラー: {e}")
        
        return []
    
    def _get_additional_songs(self, emotion_config: Dict, limit: int, seen_ids: set) -> List[Song]:
        """追加の楽曲を取得"""
        try:
            # より広い範囲で推薦を取得
            recommendations = self.spotify_client.get_recommendations(
                seed_genres=emotion_config.get('genres', [])[:1],
                limit=limit * 2,  # 多めに取得して重複を除去
                **self._get_audio_features_params(emotion_config, relaxed=True)
            )
            
            additional_songs = []
            if recommendations and recommendations.get('tracks'):
                for track in recommendations['tracks']:
                    if track['id'] not in seen_ids:
                        additional_songs.append(self._create_song_from_track(track))
                        if len(additional_songs) >= limit:
                            break
            
            return additional_songs
            
        except Exception as e:
            print(f"追加楽曲取得でエラー: {e}")
        
        return []
    
    def _get_audio_features_params(self, emotion_config: Dict, relaxed: bool = False) -> Dict:
        """音楽特徴量パラメータを取得"""
        params = {}
        
        # 緩い設定の場合は範囲を広げる
        tolerance = 0.3 if relaxed else 0.2
        
        for key, value in emotion_config.items():
            if key.startswith('target_'):
                param_name = key.replace('target_', '')
                if param_name in ['valence', 'energy', 'danceability']:
                    params[f'target_{param_name}'] = value
                    params[f'min_{param_name}'] = max(0, value - tolerance)
                    params[f'max_{param_name}'] = min(1, value + tolerance)
                elif param_name == 'tempo':
                    params[f'target_{param_name}'] = value
                    params[f'min_{param_name}'] = max(50, value - 20)
                    params[f'max_{param_name}'] = min(200, value + 20)
        
        return params
    
    def _get_search_queries_for_emotion(self, emotion: str) -> List[str]:
        """感情に基づく検索クエリを生成"""
        emotion_queries = {
            "幸せ": ["happy songs", "feel good music", "uplifting tracks"],
            "悲しい": ["sad songs", "melancholy music", "heartbreak songs"],
            "リラックス": ["chill music", "relaxing songs", "calm tracks"],
            "興奮": ["energetic music", "pump up songs", "high energy"],
            "怒り": ["angry music", "aggressive songs", "intense tracks"],
            "恋愛": ["love songs", "romantic music", "relationship songs"],
            "やる気": ["motivational songs", "workout music", "inspiring tracks"],
            "懐かしい": ["nostalgic songs", "throwback music", "classic hits"],
            "集中": ["focus music", "study songs", "concentration tracks"],
            "パーティー": ["party music", "dance hits", "celebration songs"]
        }
        
        return emotion_queries.get(emotion, [f"{emotion} music"])
    
    def _create_song_from_track(self, track: Dict) -> Song:
        """SpotifyトラックデータからSongオブジェクトを作成"""
        title = track.get('name', 'Unknown')
        artist = ', '.join([artist['name'] for artist in track.get('artists', [])])
        
        # 画像URLを取得（複数サイズがある場合は中程度のサイズを選択）
        image_url = "https://via.placeholder.com/250x250/666/white?text=No+Image"
        if track.get('album', {}).get('images'):
            images = track['album']['images']
            if images:
                # 中程度のサイズを選択（通常は300x300程度）
                image_url = images[1]['url'] if len(images) > 1 else images[0]['url']
        
        return Song(
            title=title,
            artist=artist,
            image_url=image_url,
            spotify_id=track.get('id'),
            preview_url=track.get('preview_url'),
            spotify_uri=track.get('uri')
        )
    
    def _get_fallback_songs(self, emotion: str, limit: int) -> List[Song]:
        """Spotify APIが使用できない場合のフォールバック楽曲"""
        fallback_songs = {
            "幸せ": [
                Song("Happy", "Pharrell Williams", "https://via.placeholder.com/250x250/FFD700/black?text=Happy"),
                Song("Good as Hell", "Lizzo", "https://via.placeholder.com/250x250/FF69B4/white?text=Good+as+Hell"),
                Song("Uptown Funk", "Mark Ronson ft. Bruno Mars", "https://via.placeholder.com/250x250/FF4500/white?text=Uptown+Funk"),
            ],
            "悲しい": [
                Song("Someone Like You", "Adele", "https://via.placeholder.com/250x250/4682B4/white?text=Someone+Like+You"),
                Song("Hurt", "Johnny Cash", "https://via.placeholder.com/250x250/2F4F4F/white?text=Hurt"),
                Song("Mad World", "Gary Jules", "https://via.placeholder.com/250x250/696969/white?text=Mad+World"),
            ],
            "リラックス": [
                Song("Weightless", "Marconi Union", "https://via.placeholder.com/250x250/87CEEB/white?text=Weightless"),
                Song("Clair de Lune", "Claude Debussy", "https://via.placeholder.com/250x250/E6E6FA/black?text=Clair+de+Lune"),
                Song("Aqueous Transmission", "Incubus", "https://via.placeholder.com/250x250/40E0D0/white?text=Aqueous"),
            ],
            # 他の感情のフォールバック楽曲も追加...
        }
        
        emotion_songs = fallback_songs.get(emotion, [])
        return emotion_songs[:limit]
    
    def set_emotion_songs(self, emotion: str, limit: int = 10):
        """指定された感情の楽曲を設定"""
        self.current_emotion_songs = self.generate_songs_for_emotion(emotion, limit)
        self.current_index = 0
    
    def get_current_song(self) -> Optional[Song]:
        """現在の楽曲を取得"""
        if self.current_index < len(self.current_emotion_songs):
            return self.current_emotion_songs[self.current_index]
        return None
    
    def next_song(self) -> Optional[Song]:
        """次の楽曲に移動"""
        self.current_index += 1
        return self.get_current_song()
    
    def has_next_song(self) -> bool:
        """次の楽曲があるかチェック"""
        return self.current_index < len(self.current_emotion_songs)
    
    def reset(self):
        """楽曲インデックスをリセット"""
        self.current_index = 0
    
    def get_song_count(self) -> int:
        """現在の楽曲数を取得"""
        return len(self.current_emotion_songs)
    
    def get_remaining_count(self) -> int:
        """残りの楽曲数を取得"""
        return len(self.current_emotion_songs) - self.current_index
    
    def shuffle_songs(self):
        """楽曲リストをシャッフル"""
        if self.current_emotion_songs:
            random.shuffle(self.current_emotion_songs)
            self.current_index = 0
