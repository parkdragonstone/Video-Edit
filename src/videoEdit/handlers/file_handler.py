"""파일 선택 및 경로 관리 모듈."""

import os
from pathlib import Path
from tkinter import filedialog, messagebox


class FileHandler:
    """파일 선택 및 경로 관리 클래스."""
    
    def __init__(self, app):
        """초기화.
        
        Args:
            app: VideoEditApp 인스턴스
        """
        self.app = app
    
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
            self.app.video_path = file_path
            self.app.load_video_info()
            self.update_output_path()
    
    def update_output_path(self):
        """출력 경로 자동 업데이트."""
        if self.app.video_path:
            input_path = Path(self.app.video_path)
            output_path = input_path.parent / f"{input_path.stem}_rotated{input_path.suffix}"
            self.app.output_var.set(str(output_path))
            self.app.output_path = str(output_path)
    
    def select_output_path(self):
        """출력 경로 선택 다이얼로그."""
        if not self.app.video_path:
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
            initialfile=os.path.basename(self.app.output_path) if self.app.output_path else "output.mp4"
        )
        
        if file_path:
            self.app.output_var.set(file_path)
            self.app.output_path = file_path
