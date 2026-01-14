"""비디오 내보내기 관련 기능 모듈."""

import threading
import tkinter as tk
from tkinter import messagebox


class ExportController:
    """비디오 내보내기 제어 클래스."""
    
    def __init__(self, app):
        """초기화.
        
        Args:
            app: VideoEditApp 인스턴스
        """
        self.app = app
    
    def export_video(self):
        """비디오 내보내기."""
        if not self.app.video_path or not self.app.video_clip:
            messagebox.showerror("오류", "비디오 파일을 먼저 선택해주세요.")
            return
            
        output_path = self.app.output_var.get()
        if not output_path:
            messagebox.showerror("오류", "출력 경로를 설정해주세요.")
            return
            
        try:
            fps = float(self.app.fps_var.get())
            if fps <= 0:
                raise ValueError("FPS는 0보다 커야 합니다.")
        except ValueError as e:
            messagebox.showerror("오류", f"올바른 FPS 값을 입력해주세요.\n{str(e)}")
            return
            
        # Export 버튼 비활성화 및 진행바 시작
        self.app.export_button.config(state=tk.DISABLED)
        self.app.progress.start()
        
        # 별도 스레드에서 export 실행
        thread = threading.Thread(target=self._export_video_thread, args=(output_path, fps))
        thread.daemon = True
        thread.start()
    
    def _export_video_thread(self, output_path, fps):
        """비디오 내보내기 스레드."""
        try:
            # 비디오 클립 복사
            clip = self.app.video_clip.copy()
            
            # 구간 설정 적용
            if self.app.range_unit_mode == "frame":
                if self.app.start_frame > 0 or self.app.end_frame < self.app.total_frames:
                    start_t = self.app.start_frame / self.app.video_fps if self.app.video_fps > 0 else 0
                    end_t = self.app.end_frame / self.app.video_fps if self.app.video_fps > 0 else self.app.video_duration
                    clip = clip.subclip(start_t, end_t)
            else:
                if self.app.start_time > 0 or self.app.end_time < self.app.video_duration:
                    clip = clip.subclip(self.app.start_time, self.app.end_time)
            
            if self.app.rotation_angle != 0:
                clip = clip.rotate(-self.app.rotation_angle)
            
            # FPS 설정
            if fps != self.app.video_clip.fps:
                clip = clip.set_fps(fps)
            
            # Export
            clip.write_videofile(
                output_path,
                fps=fps,
                codec='libx264',
                audio_codec='aac' if clip.audio else None,
                preset='medium',
                threads=4
            )
            clip.close()
            
            self.app.root.after(0, self._export_complete, True, "비디오가 성공적으로 export되었습니다!")
            
        except Exception as e:
            self.app.root.after(0, self._export_complete, False, f"Export 중 오류가 발생했습니다:\n{str(e)}")
    
    def _export_complete(self, success, message):
        """내보내기 완료 처리."""
        self.app.progress.stop()
        self.app.export_button.config(state=tk.NORMAL)
        
        if success:
            messagebox.showinfo("완료", message)
        else:
            messagebox.showerror("오류", message)
