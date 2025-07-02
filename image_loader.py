import requests
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class ImageLoader:
    """画像読み込み処理クラス"""
    @staticmethod
    def load_pixmap_from_url(url, size=(300, 300), timeout=10):
        """URLから画像を読み込んでQPixmapを返す"""
        try:
            print(f"画像を読み込み中: {url}")
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            
            pixmap = QPixmap()
            if pixmap.loadFromData(response.content):
                scaled_pixmap = pixmap.scaled(
                    size[0], size[1], 
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                print("画像読み込み成功")
                return scaled_pixmap
            else:
                raise Exception("画像データの読み込みに失敗")
                
        except Exception as e:
            print(f"画像読み込みエラー: {e}")
            return None
