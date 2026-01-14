"""구간 설정 관련 기능 모듈."""


class RangeController:
    """구간 설정 제어 클래스."""
    
    def __init__(self, app):
        """초기화.
        
        Args:
            app: VideoEditApp 인스턴스
        """
        self.app = app
    
    def set_start_time(self, value_str):
        """시작 시간/프레임 설정."""
        try:
            if self.app.range_unit_mode == "frame":
                frame_val = int(value_str)
                if frame_val < 0:
                    frame_val = 0
                if frame_val >= self.app.end_frame:
                    frame_val = max(0, self.app.end_frame - 1)
                self.app.start_frame = frame_val
                self.app.start_time = self.app.start_frame / self.app.video_fps if self.app.video_fps > 0 else 0
                if hasattr(self.app, 'start_time_var'):
                    self.app.start_time_var.set(str(self.app.start_frame))
                if self.app.current_frame < self.app.start_frame:
                    self.app.current_frame = self.app.start_frame
                    self.app.current_time = self.app.start_frame / self.app.video_fps if self.app.video_fps > 0 else 0
                    self.app.playback_controller.seek_to_time(self.app.current_time)
            else:
                time_val = float(value_str)
                if time_val < 0:
                    time_val = 0
                if time_val >= self.app.end_time:
                    time_val = max(0, self.app.end_time - 0.1)
                self.app.start_time = time_val
                self.app.start_frame = int(self.app.start_time * self.app.video_fps) if self.app.video_fps > 0 else 0
                if hasattr(self.app, 'start_time_var'):
                    self.app.start_time_var.set(f"{self.app.start_time:.2f}")
                if self.app.current_time < self.app.start_time:
                    self.app.playback_controller.seek_to_time(self.app.start_time)
        except ValueError:
            self._update_range_ui()
    
    def set_end_time(self, value_str):
        """종료 시간/프레임 설정."""
        try:
            if self.app.range_unit_mode == "frame":
                frame_val = int(value_str)
                if frame_val > self.app.total_frames:
                    frame_val = self.app.total_frames
                if frame_val <= self.app.start_frame:
                    frame_val = min(self.app.total_frames, self.app.start_frame + 1)
                self.app.end_frame = frame_val
                self.app.end_time = self.app.end_frame / self.app.video_fps if self.app.video_fps > 0 else 0
                if hasattr(self.app, 'end_time_var'):
                    self.app.end_time_var.set(str(self.app.end_frame))
                if self.app.current_frame >= self.app.end_frame:
                    self.app.current_frame = self.app.end_frame - 1
                    self.app.current_time = self.app.current_frame / self.app.video_fps if self.app.video_fps > 0 else 0
                    self.app.playback_controller.seek_to_time(self.app.current_time)
            else:
                time_val = float(value_str)
                if time_val > self.app.video_duration:
                    time_val = self.app.video_duration
                if time_val <= self.app.start_time:
                    time_val = min(self.app.video_duration, self.app.start_time + 0.1)
                self.app.end_time = time_val
                self.app.end_frame = int(self.app.end_time * self.app.video_fps) if self.app.video_fps > 0 else self.app.total_frames
                if hasattr(self.app, 'end_time_var'):
                    self.app.end_time_var.set(f"{self.app.end_time:.2f}")
                if self.app.current_time > self.app.end_time:
                    self.app.playback_controller.seek_to_time(self.app.end_time)
        except ValueError:
            self._update_range_ui()
    
    def set_range_unit_mode(self, mode):
        """구간 설정 단위 모드 변경."""
        self.app.range_unit_mode = mode
        self._update_range_ui()
    
    def _update_range_ui(self):
        """구간 설정 UI 업데이트."""
        if self.app.range_unit_mode == "frame":
            if hasattr(self.app, 'start_time_var'):
                self.app.start_time_var.set(str(self.app.start_frame))
            if hasattr(self.app, 'end_time_var'):
                self.app.end_time_var.set(str(self.app.end_frame))
            if hasattr(self.app, 'start_label'):
                self.app.start_label.config(text="시작 프레임:")
            if hasattr(self.app, 'end_label'):
                self.app.end_label.config(text="종료 프레임:")
        else:
            if hasattr(self.app, 'start_time_var'):
                self.app.start_time_var.set(f"{self.app.start_time:.2f}")
            if hasattr(self.app, 'end_time_var'):
                self.app.end_time_var.set(f"{self.app.end_time:.2f}")
            if hasattr(self.app, 'start_label'):
                self.app.start_label.config(text="시작 시간(초):")
            if hasattr(self.app, 'end_label'):
                self.app.end_label.config(text="종료 시간(초):")
