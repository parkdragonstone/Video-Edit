"""Main GUI application for video rotation and export."""

import tkinter as tk
import os
import sys

# 직접 실행 시 경로 추가
if __name__ == "__main__":
    # 현재 파일의 디렉토리를 sys.path에 추가
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    from handlers.drag_drop import DragDropHandler
    from processors.video_processor import VideoProcessor
    from ui import UIManager
    from controllers.playback import PlaybackController
    from controllers.export import ExportController
    from handlers.file_handler import FileHandler
    from controllers.range_controller import RangeController
else:
    # 패키지로 import 시 상대 import
    from .handlers.drag_drop import DragDropHandler
    from .processors.video_processor import VideoProcessor
    from .ui import UIManager
    from .controllers.playback import PlaybackController
    from .controllers.export import ExportController
    from .handlers.file_handler import FileHandler
    from .controllers.range_controller import RangeController


class VideoEditApp:
    """비디오 편집 애플리케이션 메인 클래스."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Video Edit Tool")
        self.root.geometry("800x700")
        
        self.video_path = None
        self.video_clip = None
        self.rotation_angle = 0
        self.output_path = None

        self._preview_image_tk = None
        self._preview_canvas_image_id = None
        self._preview_redraw_after_id = None
        
        # 비디오 재생 관련
        self.is_playing = False
        self.current_time = 0.0
        self.video_duration = 0.0
        self.video_fps = 30.0
        self.total_frames = 0
        self.current_frame = 0
        self._play_after_id = None
        self._cap = None  # OpenCV VideoCapture
        
        # 구간 설정
        self.start_time = 0.0
        self.end_time = 0.0
        self.start_frame = 0
        self.end_frame = 0
        self.range_unit_mode = "frame"  # "frame" or "time"
        
        # 모듈 초기화
        self.drag_drop_handler = DragDropHandler(self)
        self.ui_manager = UIManager(self)
        self.playback_controller = PlaybackController(self)
        self.export_controller = ExportController(self)
        self.file_handler = FileHandler(self)
        self.range_controller = RangeController(self)
        
        # 드래그 앤 드롭 설정 (가능하면 root에 먼저 등록)
        self.drag_drop_handler.setup_drag_drop()
        
        # 스크롤 가능한 프레임 설정
        self.ui_manager.setup_scrollable_ui()
    
    def _draw_preview_placeholder(self, text: str = "비디오를 선택하거나 드래그하시오"):
        """미리보기 캔버스에 안내 문구를 중앙에 표시"""
        if not hasattr(self, "preview_canvas"):
            return
        self.preview_canvas.delete("all")
        w = self.preview_canvas.winfo_width() or 800
        h = self.preview_canvas.winfo_height() or 450
        self.preview_canvas.create_text(w // 2, h // 2, text=text, fill="white")

    def _schedule_preview_redraw(self, delay_ms: int = 80):
        """캔버스 크기 변경/회전 등으로 미리보기 재렌더링이 필요할 때 디바운스"""
        if not self.video_path:
            self._draw_preview_placeholder()
            return
        if self._preview_redraw_after_id is not None:
            try:
                self.root.after_cancel(self._preview_redraw_after_id)
            except tk.TclError:
                pass
        self._preview_redraw_after_id = self.root.after(delay_ms, self.update_preview)
        
    def select_video(self):
        """비디오 파일 선택 다이얼로그."""
        self.file_handler.select_video()
            
    def load_video_info(self):
        """비디오 정보 로드."""
        # 기존 재생 중지
        self.playback_controller.stop_playback()
        from .processors.video_processor import VideoProcessor
        VideoProcessor.load_video_info(self.video_path, self)
        # 구간 초기화 (전체 구간)
        if self.video_duration > 0 and self.total_frames > 0:
            self.start_time = 0.0
            self.end_time = self.video_duration
            self.start_frame = 0
            self.end_frame = self.total_frames
            if hasattr(self, 'start_time_var'):
                if self.range_unit_mode == "frame":
                    self.start_time_var.set("0")
                else:
                    self.start_time_var.set("0.00")
            if hasattr(self, 'end_time_var'):
                if self.range_unit_mode == "frame":
                    self.end_time_var.set(str(self.total_frames))
                else:
                    self.end_time_var.set(f"{self.video_duration:.2f}")
            self.range_controller._update_range_ui()
        
        # 시간 및 프레임 정보 즉시 업데이트
        self.playback_controller._update_time_label()
            
    def update_preview(self):
        """미리보기 업데이트."""
        from .processors.video_processor import VideoProcessor
        VideoProcessor.update_preview(self)

    def rotate_video(self, angle):
        """비디오 회전 각도 설정."""
        if self.rotation_angle == 0:
            self.rotation_angle = angle
        elif angle == 0:
            self.rotation_angle = 0
        else:
            self.rotation_angle = (self.rotation_angle + angle) % 360
            
        self.rotation_label.config(text=f"회전: {self.rotation_angle}°")
        if self.video_path:
            self.update_preview()
    
    def update_output_path(self):
        """출력 경로 자동 업데이트."""
        self.file_handler.update_output_path()
    
    def select_output_path(self):
        """출력 경로 선택 다이얼로그."""
        self.file_handler.select_output_path()
    
    def export_video(self):
        """비디오 내보내기."""
        self.export_controller.export_video()
    
    def toggle_playback(self):
        """재생/일시정지 토글."""
        self.playback_controller.toggle_playback()
    
    def start_playback(self):
        """비디오 재생 시작."""
        self.playback_controller.start_playback()
    
    def pause_playback(self):
        """비디오 재생 일시정지."""
        self.playback_controller.pause_playback()
    
    def stop_playback(self):
        """비디오 재생 중지."""
        self.playback_controller.stop_playback()
    
    def seek_to_time(self, time_value):
        """특정 시간으로 이동."""
        self.playback_controller.seek_to_time(time_value)
    
    def set_start_time(self, value_str):
        """시작 시간/프레임 설정."""
        self.range_controller.set_start_time(value_str)
    
    def set_end_time(self, value_str):
        """종료 시간/프레임 설정."""
        self.range_controller.set_end_time(value_str)
    
    def set_range_unit_mode(self, mode):
        """구간 설정 단위 모드 변경."""
        self.range_controller.set_range_unit_mode(mode)
    
    def _update_range_ui(self):
        """구간 설정 UI 업데이트."""
        self.range_controller._update_range_ui()


def main():
    """애플리케이션 진입점."""
    try:
        from tkinterdnd2 import TkinterDnD
        root = TkinterDnD.Tk()
    except Exception:
        root = tk.Tk()
    
    app = VideoEditApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
