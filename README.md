# Video Edition Tool

비디오 파일을 회전시키고 프레임(FPS)을 설정하여 export할 수 있는 GUI 도구입니다.

## 요구사항

- **Anaconda 또는 Miniconda** (Python 3.9 이상 포함)
- Windows 지원 (macOS, Linux 는 Test 해보지 않음)

## 설치 방법

### 1. Conda 설치 확인

먼저 conda가 설치되어 있는지 확인하세요:

```bash
conda --version
```

conda가 설치되어 있지 않다면 [Anaconda](https://www.anaconda.com/download) 또는 [Miniconda](https://docs.conda.io/en/latest/miniconda.html)를 설치하세요.

### 2. Conda 환경 생성

```bash
conda create -n videoEdit python=3.12
conda activate videoEdit
```

### 3. 패키지 설치

```bash
pip install -e .
```

## 실행 방법

### 방법 1: 명령어로 실행 (권장)

패키지 설치 후 다음 명령어로 프로그램을 실행할 수 있습니다:

```bash
videoEdit
```

### 방법 2: Python 스크립트 직접 실행

```bash
python src/videoEdit/main.py
```

### 방법 3: 실행 파일(.exe)로 실행

Windows에서 실행 파일을 만들어 아이콘으로 실행할 수 있습니다:

1. **PyInstaller 설치**:
   ```bash
   pip install pyinstaller
   ```

2. **실행 파일 빌드**:
   ```bash
   # Windows 배치 파일 사용
   build.bat
   
   # 또는 Python 스크립트 직접 실행
   python build_exe.py
   ```

3. **빌드 완료 후**:
   - `dist/VideoEdit.exe` 파일이 생성됩니다
   - 이 파일을 더블클릭하여 실행할 수 있습니다
   - 바탕화면에 바로가기를 만들려면 `create_shortcut.bat`를 실행하세요

**참고**: 실행 파일 빌드에 대한 자세한 내용은 [README_BUILD.md](README_BUILD.md)를 참조하세요.

## 사용 방법

1. **비디오 파일 선택**: "비디오 파일 선택" 버튼을 클릭하여 처리할 비디오 파일을 선택합니다.
2. **비디오 정보 확인**: 선택한 비디오의 프레임 수, FPS, 시간, 해상도 정보가 표시됩니다.
3. **회전 설정**:
   - 90° 시계방향: 비디오를 시계방향으로 90도 회전
   - 180°: 비디오를 180도 회전
   - 90° 반시계방향: 비디오를 반시계방향으로 90도 회전
   - 리셋: 회전을 초기화
4. **FPS 설정**: 원하는 FPS 값을 입력합니다 (기본값은 원본 비디오의 FPS)
5. **출력 경로 설정**: 출력 파일의 경로를 설정합니다 (기본값은 원본 파일과 같은 경로)
6. **Export**: "Export" 버튼을 클릭하여 처리된 비디오를 저장합니다.

## 지원 형식

### 입력 형식

- MP4, AVI, MOV, MKV, FLV, WMV 등

## 📄 License

이 프로젝트는 [MIT License](LICENSE) 하에 배포됩니다.

## 🔗 링크

- **GitHub 저장소**: [https://github.com/parkdragonstone/Video-Edit](https://github.com/parkdragonstone/Video-Edit)
- **이슈 리포트**: [https://github.com/parkdragonstone/Video-Edit/issues](https://github.com/parkdragonstone/Video-Edit/issues)

## 개발자 정보

이 프로젝트는 비디오 파일의 회전 및 프레임 설정을 위한 간단한 GUI 도구입니다.
