"""비디오 처리 관련 기능 모듈."""

import cv2
import numpy as np
from tkinter import messagebox
from moviepy.editor import VideoFileClip


class VideoProcessor:
    """비디오 처리 관련 기능을 제공하는 클래스."""
    
    @staticmethod
    def rotate_frame_keep_full(frame_bgr, angle_deg: int):
        """프레임을 회전시키되 전체가 잘리지 않도록 처리."""
        angle = angle_deg % 360
        if angle == 0:
            return frame_bgr

        # 90도 단위는 OpenCV 내장 rotate 사용 (품질/속도 좋음)
        if angle == 90:
            return cv2.rotate(frame_bgr, cv2.ROTATE_90_CLOCKWISE)
        if angle == 180:
            return cv2.rotate(frame_bgr, cv2.ROTATE_180)
        if angle == 270:
            return cv2.rotate(frame_bgr, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # 그 외 각도: 회전 후 bounding box 크기 계산
        h, w = frame_bgr.shape[:2]
        center = (w / 2.0, h / 2.0)
        # cv2.getRotationMatrix2D는 +가 반시계방향이므로, 시계방향(+) 규칙을 위해 -angle 사용
        m = cv2.getRotationMatrix2D(center, -angle, 1.0)
        cos = abs(m[0, 0])
        sin = abs(m[0, 1])
        new_w = int(h * sin + w * cos)
        new_h = int(h * cos + w * sin)

        # 이동 보정(중앙 정렬)
        m[0, 2] += (new_w / 2.0) - center[0]
        m[1, 2] += (new_h / 2.0) - center[1]

        return cv2.warpAffine(
            frame_bgr,
            m,
            (new_w, new_h),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0),
        )

    @staticmethod
    def letterbox_bgr(frame_bgr, target_w: int, target_h: int):
        """프레임을 letterbox 방식으로 리사이즈."""
        target_w = max(int(target_w), 1)
        target_h = max(int(target_h), 1)

        h, w = frame_bgr.shape[:2]
        if w <= 0 or h <= 0:
            return cv2.resize(frame_bgr, (target_w, target_h))

        scale = min(target_w / w, target_h / h)
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        resized = cv2.resize(frame_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)

        canvas = np.zeros((target_h, target_w, 3), dtype=resized.dtype)
        x = (target_w - new_w) // 2
        y = (target_h - new_h) // 2
        canvas[y:y + new_h, x:x + new_w] = resized
        return canvas
    
    @staticmethod
    def load_video_info(video_path, app):
        """비디오 정보를 로드하고 UI에 표시."""
        try:
            # OpenCV로 비디오 정보 읽기
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                messagebox.showerror("오류", "비디오 파일을 열 수 없습니다.")
                return
            
            # 비디오 정보 추출
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            # MoviePy로도 로드 (편집용)
            app.video_clip = VideoFileClip(video_path)
            
            # 재생 관련 변수 설정
            app.video_duration = duration
            app.video_fps = fps if fps > 0 else 30.0
            app.total_frames = frame_count
            app.current_time = 0.0
            app.current_frame = 0
            import tkinter as tk
            if hasattr(app, 'time_slider'):
                app.time_slider.config(to=duration)
            if hasattr(app, 'play_button'):
                app.play_button.config(state=tk.NORMAL)
            
            # 정보 표시
            info = f"프레임 수: {frame_count:,}\n"
            info += f"FPS: {fps:.2f}\n"
            info += f"시간: {duration:.2f}초\n"
            info += f"해상도: {width}x{height}"
            
            import tkinter as tk
            app.info_text.config(state=tk.NORMAL)
            app.info_text.delete(1.0, tk.END)
            app.info_text.insert(1.0, info)
            app.info_text.config(state=tk.DISABLED)
            
            # FPS 기본값 설정
            app.fps_var.set(str(int(fps)) if fps > 0 else "30")
            
            # 파일명 표시
            import os
            app.file_label.config(text=os.path.basename(video_path), foreground="black")
            
            # 미리보기 업데이트
            app.update_preview()
            
            # Export 버튼 활성화
            app.export_button.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("오류", f"비디오를 로드하는 중 오류가 발생했습니다:\n{str(e)}")
    
    @staticmethod
    def update_preview(app):
        """현재 rotation 상태를 반영해 현재 시간의 프레임을 미리보기 Canvas에 렌더링."""
        if not app.video_path:
            app._draw_preview_placeholder()
            return
        VideoProcessor.seek_to_frame(app, app.current_time)
    
    @staticmethod
    def seek_to_frame(app, time_seconds):
        """특정 시간의 프레임을 표시."""
        try:
            if not app.video_path:
                return
            
            # OpenCV로 특정 시간의 프레임 읽기
            cap = cv2.VideoCapture(app.video_path)
            
            # 프레임 번호 계산 (현재 프레임이 설정되어 있으면 사용)
            if hasattr(app, 'current_frame') and app.current_frame >= 0:
                frame_number = app.current_frame
            else:
                fps = cap.get(cv2.CAP_PROP_FPS)
                if fps > 0:
                    frame_number = int(time_seconds * fps)
                else:
                    frame_number = 0
            
            # 프레임 범위 체크
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if frame_number >= total_frames:
                frame_number = total_frames - 1
            if frame_number < 0:
                frame_number = 0
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret or frame is None:
                return
            
            # Canvas 크기
            app.preview_canvas.update_idletasks()
            canvas_w = int(app.preview_canvas.winfo_width())
            canvas_h = int(app.preview_canvas.winfo_height())
            if canvas_w <= 2 or canvas_h <= 2:
                canvas_w, canvas_h = 800, 450
            
            # 1) 회전(전체가 잘리지 않도록 bounding box 확장)
            rotated = VideoProcessor.rotate_frame_keep_full(frame, app.rotation_angle)
            
            # 2) Canvas에 '전체가 보이도록' 맞추기 (aspect 유지 + letterbox)
            fitted = VideoProcessor.letterbox_bgr(rotated, canvas_w, canvas_h)
            
            # BGR -> RGB
            frame_rgb = cv2.cvtColor(fitted, cv2.COLOR_BGR2RGB)
            
            from PIL import Image, ImageTk
            import tkinter as tk
            image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image=image)
            
            # Canvas에 표시 (이미지 참조 유지 필요)
            app._preview_image_tk = photo
            app.preview_canvas.delete("all")
            app._preview_canvas_image_id = app.preview_canvas.create_image(
                canvas_w // 2, canvas_h // 2, image=photo, anchor=tk.CENTER
            )
            
        except Exception as e:
            print(f"프레임 이동 오류: {e}")
