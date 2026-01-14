"""UI 설정 관련 기능 모듈."""

import tkinter as tk
from tkinter import ttk

# 직접 실행 시와 패키지로 import 시 모두 지원
if __name__ == "__main__":
    from video_processor import VideoProcessor
else:
    from .video_processor import VideoProcessor


class UIManager:
    """UI 설정 및 관리 클래스."""
    
    def __init__(self, app):
        """초기화.
        
        Args:
            app: VideoEditApp 인스턴스
        """
        self.app = app
        
    def setup_scrollable_ui(self):
        """스크롤 가능한 UI 설정."""
        # 메인 Canvas와 Scrollbar 생성
        main_frame = ttk.Frame(self.app.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas 생성
        self.app.canvas = tk.Canvas(main_frame)
        self.app.scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.app.canvas.yview)
        self.app.scrollable_frame = ttk.Frame(self.app.canvas)
        
        def on_frame_configure(event):
            # 스크롤 영역 업데이트
            self.app.canvas.configure(scrollregion=self.app.canvas.bbox("all"))
            # 컨텐츠를 중앙에 배치
            self._center_content()
        
        def on_canvas_configure(event):
            # Canvas 크기 변경 시 컨텐츠 중앙 정렬
            self._center_content()
        
        self.app.scrollable_frame.bind("<Configure>", on_frame_configure)
        self.app.canvas.bind("<Configure>", on_canvas_configure)
        
        self.app.canvas_window = self.app.canvas.create_window((0, 0), window=self.app.scrollable_frame, anchor="n")
        self.app.canvas.configure(yscrollcommand=self.app.scrollbar.set)
        
        self.app.canvas.pack(side="left", fill="both", expand=True)
        self.app.scrollbar.pack(side="right", fill="y")
        
        # 마우스 휠 바인딩 - 창 내부 어디에 마우스가 있든 스크롤 작동
        self._bind_mousewheel(self.app.root)
        self._bind_mousewheel(main_frame)
        self._bind_mousewheel(self.app.canvas)
        self._bind_mousewheel(self.app.scrollable_frame)
        
        # 스크롤 가능한 프레임에 UI 설정
        self.setup_ui()
    
    def _center_content(self):
        """컨텐츠를 좌우 중앙에 배치 (위쪽 정렬)"""
        # Canvas의 현재 너비 가져오기
        canvas_width = self.app.canvas.winfo_width()
        if canvas_width <= 1:  # 아직 렌더링되지 않은 경우
            return
        
        # 컨텐츠의 너비 계산
        self.app.scrollable_frame.update_idletasks()
        content_width = self.app.scrollable_frame.winfo_reqwidth()
        
        # 최대 너비 설정 (더 넓은 화면에서도 적절한 너비 유지)
        max_width = 750
        if content_width < max_width:
            content_width = max_width
        
        # 좌우 중앙 정렬을 위한 x 좌표 계산
        x = (canvas_width - content_width) // 2
        if x < 0:
            x = 0
        
        # 컨텐츠 너비 설정 및 위치 업데이트 (y는 항상 0으로 위쪽 정렬)
        self.app.canvas.itemconfig(self.app.canvas_window, width=content_width)
        self.app.canvas.coords(self.app.canvas_window, x, 0)
    
    def _bind_mousewheel(self, widget):
        """위젯에 마우스 휠 이벤트 바인딩"""
        widget.bind("<MouseWheel>", self._on_mousewheel)
        widget.bind("<Button-4>", self._on_mousewheel)  # Linux
        widget.bind("<Button-5>", self._on_mousewheel)  # Linux
    
    def _bind_mousewheel_to_children(self, parent):
        """자식 위젯들에도 마우스 휠 이벤트 바인딩"""
        for child in parent.winfo_children():
            self._bind_mousewheel(child)
            # 재귀적으로 자식의 자식에도 바인딩
            if child.winfo_children():
                self._bind_mousewheel_to_children(child)
    
    def _on_mousewheel(self, event):
        """마우스 휠 이벤트 처리"""
        # 재생 컨트롤 영역에 마우스가 있는지 확인하고 프레임 이동 처리
        try:
            if (hasattr(self.app, 'playback_frame') and self.app.playback_frame and 
                hasattr(self.app, 'video_path') and self.app.video_path and 
                hasattr(self.app, 'video_fps') and self.app.video_fps > 0):
                
                # 마우스 위치 확인
                mouse_x = event.x_root
                mouse_y = event.y_root
                
                playback_frame = self.app.playback_frame
                playback_x = playback_frame.winfo_rootx()
                playback_y = playback_frame.winfo_rooty()
                playback_width = playback_frame.winfo_width()
                playback_height = playback_frame.winfo_height()
                
                # 재생 컨트롤 프레임 내부인지 확인
                if (playback_x <= mouse_x <= playback_x + playback_width and 
                    playback_y <= mouse_y <= playback_y + playback_height):
                    
                    # 재생 컨트롤 영역이면 프레임 이동 처리
                    # 스크롤 방향 확인
                    frame_delta = -1 if (event.delta > 0 or event.num == 4) else 1
                    
                    # 현재 프레임에서 이동
                    new_frame = self.app.current_frame + frame_delta
                    new_frame = max(0, min(new_frame, self.app.total_frames - 1))
                    
                    # 시간 계산 및 이동
                    new_time = new_frame / self.app.video_fps if self.app.video_fps > 0 else 0
                    
                    # 프레임 업데이트 (즉시 처리)
                    self.app.current_frame = new_frame
                    self.app.current_time = new_time
                    
                    # 재생 중이면 시작 시간 업데이트
                    if self.app.is_playing:
                        import time
                        self.app._playback_start_time = time.time()
                        self.app._playback_start_frame_time = new_time
                    
                    # 프레임 표시 및 UI 업데이트
                    from .processors.video_processor import VideoProcessor
                    VideoProcessor.seek_to_frame(self.app, new_time)
                    if hasattr(self.app, 'time_slider'):
                        self.app.time_slider.set(new_time)
                    self.app.playback_controller._update_time_label()
                    
                    # 이벤트 전파 중지
                    return
        except Exception as e:
            print(f"마우스 휠 처리 오류: {e}")
        
        # 재생 컨트롤 영역이 아니면 일반 스크롤 처리
        # Windows와 MacOS
        if event.delta:
            self.app.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        # Linux
        elif event.num == 4:
            self.app.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.app.canvas.yview_scroll(1, "units")
    
    def setup_ui(self):
        """UI 컴포넌트 생성."""
        # 중앙 정렬을 위한 최대 너비 설정
        max_content_width = 900
        
        # 파일 선택 프레임
        file_frame = ttk.Frame(self.app.scrollable_frame, padding="10")
        file_frame.pack(fill=tk.X, padx=10)
        
        ttk.Button(file_frame, text="비디오 파일 선택", command=self.app.select_video).pack(side=tk.LEFT, padx=5)
        self.app.file_label = ttk.Label(file_frame, text="선택된 파일 없음", foreground="gray")
        self.app.file_label.pack(side=tk.LEFT, padx=10)

        # 힌트 색상 변경 대상으로 등록
        self.app.drag_drop_handler.set_hint_widgets([self.app.file_label])
        
        # 비디오 정보 프레임
        info_frame = ttk.LabelFrame(self.app.scrollable_frame, text="비디오 정보", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.app.info_text = tk.Text(info_frame, height=4, wrap=tk.WORD, state=tk.DISABLED)
        self.app.info_text.pack(fill=tk.X)
        
        # 비디오 미리보기 프레임
        preview_frame = ttk.LabelFrame(self.app.scrollable_frame, text="비디오 미리보기", padding="10")
        preview_frame.pack(fill=tk.X, padx=10, pady=5)
        preview_frame.configure(height=460)
        preview_frame.pack_propagate(False)

        self.app.preview_canvas = tk.Canvas(preview_frame, bg="black", highlightthickness=0)
        self.app.preview_canvas.pack(fill=tk.BOTH, expand=True)
        self.app.preview_canvas.bind("<Configure>", lambda _e: self.app._schedule_preview_redraw())
        self.app._draw_preview_placeholder()

        # 재생 컨트롤 프레임
        playback_frame = ttk.Frame(preview_frame)
        playback_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 재생 컨트롤 프레임 참조 저장 (마우스 휠 이벤트에서 사용)
        self.app.playback_frame = playback_frame
        
        # 재생 컨트롤 프레임이 포커스를 받을 수 있도록 설정
        playback_frame.configure(takefocus=True)
        
        # 재생 버튼
        self.app.play_button = ttk.Button(playback_frame, text="▶ 재생", command=self.app.toggle_playback, state=tk.DISABLED)
        self.app.play_button.pack(side=tk.LEFT, padx=5)
        
        # 시간 및 프레임 레이블 (통합)
        self.app.time_label = ttk.Label(playback_frame, text="00:00:00 / 00:00:00 [0 / 0]")
        self.app.time_label.pack(side=tk.LEFT, padx=10)
        
        # 재생 위치 슬라이더
        slider_frame = ttk.Frame(playback_frame)
        slider_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.app.time_slider = ttk.Scale(slider_frame, from_=0, to=100, orient=tk.HORIZONTAL)
        self.app.time_slider.pack(fill=tk.X, expand=True)
        
        # 슬라이더 이벤트 바인딩 (드래그 중에는 재생 중지하지 않음)
        def on_slider_change(event=None):
            if hasattr(self.app, 'time_slider'):
                value = self.app.time_slider.get()
                self.app.seek_to_time(value)
        
        # 마우스 휠로 프레임 단위 이동 (최적화된 버전)
        def on_slider_wheel(event):
            if not self.app.video_path or self.app.video_fps <= 0:
                return "break"
            
            # 스크롤 방향 확인
            frame_delta = -1 if (event.delta > 0 or event.num == 4) else 1
            
            # 현재 프레임에서 이동
            new_frame = self.app.current_frame + frame_delta
            new_frame = max(0, min(new_frame, self.app.total_frames - 1))
            
            # 시간 계산 및 이동
            new_time = new_frame / self.app.video_fps if self.app.video_fps > 0 else 0
            
            # 프레임 업데이트 (즉시 처리)
            self.app.current_frame = new_frame
            self.app.current_time = new_time
            
            # 재생 중이면 시작 시간 업데이트
            if self.app.is_playing:
                import time
                self.app._playback_start_time = time.time()
                self.app._playback_start_frame_time = new_time
            
            # 프레임 표시 및 UI 업데이트
            from .processors.video_processor import VideoProcessor
            VideoProcessor.seek_to_frame(self.app, new_time)
            if hasattr(self.app, 'time_slider'):
                self.app.time_slider.set(new_time)
            self.app._update_time_label()
            
            # 이벤트 전파 중지
            return "break"
        
        self.app.time_slider.bind("<Button-1>", lambda e: self.app.pause_playback())
        self.app.time_slider.bind("<B1-Motion>", on_slider_change)
        self.app.time_slider.bind("<ButtonRelease-1>", on_slider_change)
        
        # 재생 컨트롤 프레임과 모든 자식 위젯에 마우스 휠 이벤트 바인딩
        # add="+" 없이 직접 바인딩하여 우선순위 높임
        playback_frame.bind("<MouseWheel>", on_slider_wheel)
        playback_frame.bind("<Button-4>", on_slider_wheel)  # Linux
        playback_frame.bind("<Button-5>", on_slider_wheel)  # Linux
        
        slider_frame.bind("<MouseWheel>", on_slider_wheel)
        slider_frame.bind("<Button-4>", on_slider_wheel)  # Linux
        slider_frame.bind("<Button-5>", on_slider_wheel)  # Linux
        
        self.app.time_slider.bind("<MouseWheel>", on_slider_wheel)
        self.app.time_slider.bind("<Button-4>", on_slider_wheel)  # Linux
        self.app.time_slider.bind("<Button-5>", on_slider_wheel)  # Linux
        
        # 재생 버튼과 레이블에도 바인딩
        self.app.play_button.bind("<MouseWheel>", on_slider_wheel)
        self.app.play_button.bind("<Button-4>", on_slider_wheel)
        self.app.play_button.bind("<Button-5>", on_slider_wheel)
        
        self.app.time_label.bind("<MouseWheel>", on_slider_wheel)
        self.app.time_label.bind("<Button-4>", on_slider_wheel)
        self.app.time_label.bind("<Button-5>", on_slider_wheel)
        

        # UI 생성 이후에 drop target 확장 등록
        # (root는 init에서 이미 등록됨)
        self.app.drag_drop_handler.register_widget(file_frame)
        self.app.drag_drop_handler.register_widget(self.app.preview_canvas)
        
        # 컨트롤 프레임
        control_frame = ttk.LabelFrame(self.app.scrollable_frame, text="설정", padding="10")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 회전 버튼
        rotation_frame = ttk.Frame(control_frame)
        rotation_frame.pack(fill=tk.X, pady=5)
        ttk.Label(rotation_frame, text="회전:").pack(side=tk.LEFT, padx=5)
        ttk.Button(rotation_frame, text="90° 시계방향", command=lambda: self.app.rotate_video(90)).pack(side=tk.LEFT, padx=5)
        ttk.Button(rotation_frame, text="180°", command=lambda: self.app.rotate_video(180)).pack(side=tk.LEFT, padx=5)
        ttk.Button(rotation_frame, text="90° 반시계방향", command=lambda: self.app.rotate_video(-90)).pack(side=tk.LEFT, padx=5)
        ttk.Button(rotation_frame, text="리셋", command=lambda: self.app.rotate_video(0)).pack(side=tk.LEFT, padx=5)
        self.app.rotation_label = ttk.Label(rotation_frame, text="회전: 0°")
        self.app.rotation_label.pack(side=tk.LEFT, padx=10)
        
        # 구간 설정
        time_range_frame = ttk.LabelFrame(control_frame, text="구간 설정", padding="5")
        time_range_frame.pack(fill=tk.X, pady=5)
        
        # 단위 선택 (Radio 버튼)
        unit_frame = ttk.Frame(time_range_frame)
        unit_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(unit_frame, text="단위:").pack(side=tk.LEFT, padx=5)
        self.app.range_unit_var = tk.StringVar(value="frame")
        ttk.Radiobutton(unit_frame, text="프레임", variable=self.app.range_unit_var, 
                       value="frame", command=lambda: self.app.set_range_unit_mode("frame")).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(unit_frame, text="초", variable=self.app.range_unit_var, 
                       value="time", command=lambda: self.app.set_range_unit_mode("time")).pack(side=tk.LEFT, padx=5)
        
        range_inner_frame = ttk.Frame(time_range_frame)
        range_inner_frame.pack(fill=tk.X)
        
        self.app.start_label = ttk.Label(range_inner_frame, text="시작 프레임:")
        self.app.start_label.pack(side=tk.LEFT, padx=5)
        self.app.start_time_var = tk.StringVar(value="0")
        start_entry = ttk.Entry(range_inner_frame, textvariable=self.app.start_time_var, width=10)
        start_entry.pack(side=tk.LEFT, padx=5)
        start_entry.bind("<Return>", lambda e: self.app.set_start_time(self.app.start_time_var.get()))
        start_entry.bind("<FocusOut>", lambda e: self.app.set_start_time(self.app.start_time_var.get()))
        
        self.app.end_label = ttk.Label(range_inner_frame, text="종료 프레임:")
        self.app.end_label.pack(side=tk.LEFT, padx=5)
        self.app.end_time_var = tk.StringVar(value="0")
        end_entry = ttk.Entry(range_inner_frame, textvariable=self.app.end_time_var, width=10)
        end_entry.pack(side=tk.LEFT, padx=5)
        end_entry.bind("<Return>", lambda e: self.app.set_end_time(self.app.end_time_var.get()))
        end_entry.bind("<FocusOut>", lambda e: self.app.set_end_time(self.app.end_time_var.get()))
        
        def reset_to_full_range():
            """전체 구간으로 리셋."""
            self.app.start_time = 0.0
            self.app.end_time = self.app.video_duration
            self.app.start_frame = 0
            self.app.end_frame = self.app.total_frames
            self.app.range_controller._update_range_ui()
        
        ttk.Button(range_inner_frame, text="전체 구간", command=reset_to_full_range).pack(side=tk.LEFT, padx=5)
        
        # FPS 설정
        fps_frame = ttk.Frame(control_frame)
        fps_frame.pack(fill=tk.X, pady=5)
        ttk.Label(fps_frame, text="FPS:").pack(side=tk.LEFT, padx=5)
        self.app.fps_var = tk.StringVar()
        self.app.fps_entry = ttk.Entry(fps_frame, textvariable=self.app.fps_var, width=10)
        self.app.fps_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(fps_frame, text="(원본 FPS가 기본값)").pack(side=tk.LEFT, padx=5)
        
        # 출력 경로
        output_frame = ttk.Frame(control_frame)
        output_frame.pack(fill=tk.X, pady=5)
        ttk.Label(output_frame, text="출력 경로:").pack(side=tk.LEFT, padx=5)
        self.app.output_var = tk.StringVar()
        self.app.output_entry = ttk.Entry(output_frame, textvariable=self.app.output_var, width=50)
        self.app.output_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="찾아보기", command=self.app.select_output_path).pack(side=tk.LEFT, padx=5)
        
        # Export 버튼
        export_frame = ttk.Frame(self.app.scrollable_frame, padding="10")
        export_frame.pack(fill=tk.X)
        self.app.export_button = ttk.Button(export_frame, text="Export", command=self.app.export_video, state=tk.DISABLED)
        self.app.export_button.pack(pady=10)
        
        self.app.progress = ttk.Progressbar(export_frame, mode='indeterminate')
        self.app.progress.pack(fill=tk.X, pady=5)
        
        # UI 생성 후 모든 위젯에 마우스 휠 바인딩
        self._bind_mousewheel_to_children(self.app.scrollable_frame)
