"""드래그 앤 드롭 기능 모듈."""

import os
from tkinter import messagebox


class DragDropHandler:
    """드래그 앤 드롭 이벤트를 처리하는 클래스."""
    
    def __init__(self, app):
        """초기화.
        
        Args:
            app: VideoEditApp 인스턴스
        """
        self.app = app
        self._dnd_enabled = False
        self._dnd_files = None
        self._drop_hint_widgets = []
        
    def setup_drag_drop(self):
        """드래그 앤 드롭 기능 설정."""
        try:
            from tkinterdnd2 import DND_FILES
            self._dnd_files = DND_FILES
            self._dnd_enabled = self._register_drag_drop(self.app.root)
        except Exception:
            self._dnd_enabled = False
    
    def _register_drag_drop(self, widget):
        """특정 위젯을 드롭 타겟으로 등록."""
        if self._dnd_files is None:
            return False
        if not hasattr(widget, 'drop_target_register') or not hasattr(widget, 'dnd_bind'):
            return False

        try:
            widget.drop_target_register(self._dnd_files)
            widget.dnd_bind('<<Drop>>', self._on_drop)
            # (지원되는 경우) 드래그 진입/이탈 이벤트
            try:
                widget.dnd_bind('<<DropEnter>>', lambda _e: self._set_drop_hint(True))
                widget.dnd_bind('<<DropLeave>>', lambda _e: self._set_drop_hint(False))
            except Exception:
                pass
            return True
        except Exception:
            return False

    def _set_drop_hint(self, active: bool):
        """드래그 중일 때 UI 힌트를 주기."""
        for w in self._drop_hint_widgets:
            try:
                from tkinter import ttk
                if isinstance(w, ttk.Label):
                    w.configure(foreground=("#1f6feb" if active else "gray"))
            except Exception:
                pass

        # 비디오가 아직 없다면 preview 안내 문구도 같이 갱신
        if not self.app.video_path:
            hint_text = "여기로 비디오 파일을 드래그하세요" if active else "비디오를 선택하거나 드래그하세요요"
            self.app._draw_preview_placeholder(hint_text)
    
    def _clean_file_path(self, path: str) -> str:
        """파일 경로에서 중괄호와 따옴표 제거"""
        cleaned = path
        if cleaned.startswith('{') and cleaned.endswith('}'):
            cleaned = cleaned[1:-1]
        if (cleaned.startswith('"') and cleaned.endswith('"')) or \
           (cleaned.startswith("'") and cleaned.endswith("'")):
            cleaned = cleaned[1:-1]
        return cleaned
    
    def _on_drop(self, event):
        """드래그 앤 드롭 이벤트 처리"""
        try:
            # 드롭된 파일 경로 가져오기
            data = event.data
            
            # 파일 경로 리스트로 변환
            try:
                # tkinterdnd2의 경우
                if hasattr(self.app.root, 'tk') and hasattr(self.app.root.tk, 'splitlist'):
                    files = self.app.root.tk.splitlist(data)
                else:
                    # 직접 처리
                    files = [data]
            except:
                # 문자열로 직접 처리
                files = [str(data)]
            
            if files:
                # 여러 개가 들어오면 첫 번째 '비디오 확장자'를 우선 사용
                candidates = [f.strip() for f in files if f]
                file_path = None
                video_exts = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')
                for c in candidates:
                    cc = self._clean_file_path(c)
                    if cc.lower().endswith(video_exts):
                        file_path = cc
                        break
                if file_path is None:
                    file_path = self._clean_file_path(candidates[0])
                
                # 비디오 파일 확장자 확인
                if file_path.lower().endswith(video_exts):
                    if os.path.exists(file_path):
                        self.app.video_path = file_path
                        self.app.load_video_info()
                        self.app.update_output_path()
                        self._set_drop_hint(False)
                    else:
                        messagebox.showerror("오류", f"파일을 찾을 수 없습니다:\n{file_path}")
                else:
                    messagebox.showwarning("경고", "비디오 파일만 업로드할 수 있습니다.")
        except Exception as e:
            import traceback
            error_msg = f"파일을 로드하는 중 오류가 발생했습니다:\n{str(e)}\n\n{traceback.format_exc()}"
            messagebox.showerror("오류", error_msg)
    
    def register_widget(self, widget):
        """위젯을 드롭 타겟으로 등록."""
        return self._register_drag_drop(widget)
    
    def set_hint_widgets(self, widgets):
        """힌트 표시 대상 위젯 설정."""
        self._drop_hint_widgets = widgets
