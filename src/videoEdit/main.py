"""Main GUI application for video rotation and export."""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import os
import threading
import sys

# 직접 실행 시 경로 추가
if __name__ == "__main__":
    # 현재 파일의 디렉토리를 sys.path에 추가
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    from drag_drop import DragDropHandler
    from video_processor import VideoProcessor
    from ui import UIManager
else:
    # 패키지로 import 시 상대 import
    from .drag_drop import DragDropHandler
    from .video_processor import VideoProcessor
    from .ui import UIManager


class VideoEditApp:
    """비디오 편집 애플리케이션 메인 클래스."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Video Edit Tool")
        self.root.geometry("940x700")
        
        self.video_path = None
        self.video_clip = None
        self.rotation_angle = 0
        self.output_path = None

        self._preview_image_tk = None
        self._preview_canvas_image_id = None
        self._preview_redraw_after_id = None
        
        # 모듈 초기화
        self.drag_drop_handler = DragDropHandler(self)
        self.ui_manager = UIManager(self)
        
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
        file_path = filedialog.askopenfilename(
            title="비디오 파일 선택",
            filetypes=[
                ("비디오 파일", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"),
                ("모든 파일", "*.*")
            ]
        )
        
        if file_path:
            self.video_path = file_path
            self.load_video_info()
            self.update_output_path()
            
    def load_video_info(self):
        """비디오 정보 로드."""
        VideoProcessor.load_video_info(self.video_path, self)
            
    def update_preview(self):
        """미리보기 업데이트."""
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
        if self.video_path:
            input_path = Path(self.video_path)
            output_path = input_path.parent / f"{input_path.stem}_rotated{input_path.suffix}"
            self.output_var.set(str(output_path))
            self.output_path = str(output_path)
            
    def select_output_path(self):
        """출력 경로 선택 다이얼로그."""
        if not self.video_path:
            messagebox.showwarning("경고", "먼저 비디오 파일을 선택해주세요.")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="출력 파일 저장",
            defaultextension=".mp4",
            filetypes=[
                ("MP4 파일", "*.mp4"),
                ("AVI 파일", "*.avi"),
                ("모든 파일", "*.*")
            ],
            initialfile=os.path.basename(self.output_path) if self.output_path else "output.mp4"
        )
        
        if file_path:
            self.output_var.set(file_path)
            self.output_path = file_path
            
    def export_video(self):
        """비디오 내보내기."""
        if not self.video_path or not self.video_clip:
            messagebox.showerror("오류", "비디오 파일을 먼저 선택해주세요.")
            return
            
        output_path = self.output_var.get()
        if not output_path:
            messagebox.showerror("오류", "출력 경로를 설정해주세요.")
            return
            
        try:
            fps = float(self.fps_var.get())
            if fps <= 0:
                raise ValueError("FPS는 0보다 커야 합니다.")
        except ValueError as e:
            messagebox.showerror("오류", f"올바른 FPS 값을 입력해주세요.\n{str(e)}")
            return
            
        # Export 버튼 비활성화 및 진행바 시작
        self.export_button.config(state=tk.DISABLED)
        self.progress.start()
        
        # 별도 스레드에서 export 실행
        thread = threading.Thread(target=self._export_video_thread, args=(output_path, fps))
        thread.daemon = True
        thread.start()
        
    def _export_video_thread(self, output_path, fps):
        """비디오 내보내기 스레드."""
        try:
            # 비디오 클립 복사
            clip = self.video_clip.copy()
            
            if self.rotation_angle != 0:
                clip = clip.rotate(-self.rotation_angle)
            
            # FPS 설정
            if fps != self.video_clip.fps:
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
            
            self.root.after(0, self._export_complete, True, "비디오가 성공적으로 export되었습니다!")
            
        except Exception as e:
            self.root.after(0, self._export_complete, False, f"Export 중 오류가 발생했습니다:\n{str(e)}")
            
    def _export_complete(self, success, message):
        """내보내기 완료 처리."""
        self.progress.stop()
        self.export_button.config(state=tk.NORMAL)
        
        if success:
            messagebox.showinfo("완료", message)
        else:
            messagebox.showerror("오류", message)


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
