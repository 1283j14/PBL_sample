from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal


class SwipeableWidget(QWidget):
    """スワイプ操作を検出するウィジェット"""
    
    # シグナル定義
    swipe_left = pyqtSignal()   # 左スワイプシグナル
    swipe_right = pyqtSignal()  # 右スワイプシグナル
    
    def __init__(self):
        super().__init__()
        self.drag_start_position = None
        self.is_dragging = False
        self.swipe_threshold = 100  # スワイプと判定する最小距離
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.position().toPoint()
            self.is_dragging = True

    def mouseMoveEvent(self, event):
        if not self.is_dragging or self.drag_start_position is None:
            return
            
        # ドラッグ中の視覚的フィードバック
        current_pos = event.position().toPoint()
        distance = current_pos.x() - self.drag_start_position.x()
        
        if abs(distance) > 20:
            if distance > 0:
                self.setStyleSheet("background-color: rgba(76, 175, 80, 0.1);")  # 右スワイプ（緑）
            else:
                self.setStyleSheet("background-color: rgba(255, 152, 0, 0.1);")  # 左スワイプ（オレンジ）
        else:
            self.setStyleSheet("")

    def mouseReleaseEvent(self, event):
        if not self.is_dragging or self.drag_start_position is None:
            return
            
        current_pos = event.position().toPoint()
        distance = current_pos.x() - self.drag_start_position.x()
        
        # スワイプ判定とシグナル送信
        if abs(distance) > self.swipe_threshold:
            if distance > 0:
                self.swipe_right.emit()
            else:
                self.swipe_left.emit()
        
        # リセット
        self.is_dragging = False
        self.drag_start_position = None
        self.setStyleSheet("")
