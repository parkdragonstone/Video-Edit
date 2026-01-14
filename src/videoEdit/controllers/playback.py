"""비디오 재생 관련 기능 모듈."""

import time

# 직접 실행 시와 패키지로 import 시 모두 지원
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from processors.video_processor import VideoProcessor
else:
    from ..processors.video_processor import VideoProcessor


class PlaybackController:
    """비디오 재생 제어 클래스."""
    
    def __init__(self, app):
        """초기화.
        
        Args:
            app: VideoEditApp 인스턴스
        """
        self.app = app
    
    def toggle_playback(self):
        """재생/일시정지 토글."""
        if not self.app.video_path:
            return
        
        if self.app.is_playing:
            self.pause_playback()
        else:
            self.start_playback()
    
    def start_playback(self):
        """비디오 재생 시작."""
        if not self.app.video_path or self.app.video_duration == 0:
            return
        
        self.app.is_playing = True
        if hasattr(self.app, 'play_button'):
            self.app.play_button.config(text="⏸ 일시정지")
        
        # 재생 시작 시간 기록
        self.app._playback_start_time = time.time()
        self.app._playback_start_frame_time = self.app.current_time
        
        # 재생 루프 시작
        self._play_frame()
    
    def pause_playback(self):
        """비디오 재생 일시정지."""
        self.app.is_playing = False
        if hasattr(self.app, 'play_button'):
            self.app.play_button.config(text="▶ 재생")
        
        if self.app._play_after_id is not None:
            self.app.root.after_cancel(self.app._play_after_id)
            self.app._play_after_id = None
    
    def stop_playback(self):
        """비디오 재생 중지."""
        self.pause_playback()
        self.app.current_time = 0.0
        self.app.current_frame = 0
        if hasattr(self.app, 'time_slider'):
            self.app.time_slider.set(0)
        if hasattr(self.app, 'time_label'):
            self._update_time_label()
    
    def seek_to_time(self, time_value):
        """특정 시간으로 이동."""
        if not self.app.video_path:
            return
        
        self.app.current_time = float(time_value)
        if self.app.current_time < 0:
            self.app.current_time = 0
        if self.app.current_time > self.app.video_duration:
            self.app.current_time = self.app.video_duration
        
        # 현재 프레임 계산
        if self.app.video_fps > 0:
            self.app.current_frame = int(self.app.current_time * self.app.video_fps)
            if self.app.current_frame >= self.app.total_frames:
                self.app.current_frame = self.app.total_frames - 1
        
        # 재생 중이면 시작 시간 업데이트
        if self.app.is_playing:
            self.app._playback_start_time = time.time()
            self.app._playback_start_frame_time = self.app.current_time
        
        # 프레임 업데이트
        VideoProcessor.seek_to_frame(self.app, self.app.current_time)
        self._update_time_label()
    
    def _play_frame(self):
        """비디오 프레임 재생."""
        if not self.app.is_playing or not self.app.video_path:
            return
        
        # 실제 경과 시간 계산
        elapsed_time = time.time() - self.app._playback_start_time
        target_time = self.app._playback_start_frame_time + elapsed_time
        
        # 구간 체크
        if self.app.range_unit_mode == "frame":
            target_frame = int(target_time * self.app.video_fps) if self.app.video_fps > 0 else 0
            if target_frame >= self.app.end_frame:
                # 재생이 끝나면 처음으로 돌아가서 계속 재생 (멈추지 않음)
                self.app.current_frame = self.app.start_frame
                self.app.current_time = self.app.start_frame / self.app.video_fps if self.app.video_fps > 0 else 0
                self.app._playback_start_time = time.time()
                self.app._playback_start_frame_time = self.app.current_time
                target_time = self.app.current_time
                target_frame = self.app.start_frame
            
            if target_frame < self.app.start_frame:
                target_frame = self.app.start_frame
                target_time = target_frame / self.app.video_fps if self.app.video_fps > 0 else 0
                self.app._playback_start_time = time.time()
                self.app._playback_start_frame_time = target_time
        else:
            # 시간 단위 체크
            if target_time >= self.app.end_time:
                # 재생이 끝나면 처음으로 돌아가서 계속 재생 (멈추지 않음)
                self.app.current_time = self.app.start_time
                self.app._playback_start_time = time.time()
                self.app._playback_start_frame_time = self.app.current_time
                target_time = self.app.start_time
            
            if target_time < self.app.start_time:
                target_time = self.app.start_time
                self.app._playback_start_time = time.time()
                self.app._playback_start_frame_time = target_time
        
        # 현재 시간과 프레임 업데이트
        self.app.current_time = target_time
        if self.app.video_fps > 0:
            self.app.current_frame = int(self.app.current_time * self.app.video_fps)
            if self.app.current_frame >= self.app.total_frames:
                self.app.current_frame = self.app.total_frames - 1
                self.app.current_time = self.app.current_frame / self.app.video_fps
        
        # 프레임 표시
        VideoProcessor.seek_to_frame(self.app, self.app.current_time)
        
        # UI 업데이트
        if hasattr(self.app, 'time_slider'):
            self.app.time_slider.set(self.app.current_time)
        self._update_time_label()
        
        # 다음 프레임 예약 (약 30fps로 UI 업데이트, 실제 재생 속도는 시간 기반)
        self.app._play_after_id = self.app.root.after(33, self._play_frame)
    
    def _update_time_label(self):
        """시간 및 프레임 레이블 업데이트."""
        if not hasattr(self.app, 'time_label'):
            return
        
        current_str = self._format_time(self.app.current_time)
        duration_str = self._format_time(self.app.video_duration)
        
        # 프레임 정보 추가
        current_frame_display = self.app.current_frame + 1 if self.app.current_frame >= 0 else 0
        total_frames_display = self.app.total_frames if self.app.total_frames > 0 else 0
        
        self.app.time_label.config(text=f"{current_str} / {duration_str} [{current_frame_display} / {total_frames_display}]")
    
    def _format_time(self, seconds):
        """초를 MM:SS:mm 형식으로 변환."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 100)  # 밀리초를 2자리로 (0-99)
        return f"{minutes:02d}:{secs:02d}:{millis:02d}"
