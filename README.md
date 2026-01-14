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
conda create -n videoEdit python=3.12 -y
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

## 파일 구조

```
VideoEdit/
├── src/
│   └── videoEdit/
│       ├── __init__.py          # 패키지 초기화
│       ├── main.py              # 메인 애플리케이션 클래스 및 진입점
│       ├── ui.py                # UI 설정 및 관리
│       ├── controllers/         # 컨트롤러 모듈
│       │   ├── __init__.py
│       │   ├── playback.py     # 비디오 재생 제어
│       │   ├── export.py        # 비디오 내보내기 제어
│       │   └── range_controller.py  # 구간 설정 제어
│       ├── handlers/            # 핸들러 모듈
│       │   ├── __init__.py
│       │   ├── drag_drop.py     # 드래그 앤 드롭 처리
│       │   └── file_handler.py  # 파일 선택 및 경로 관리
│       └── processors/          # 프로세서 모듈
│           ├── __init__.py
│           └── video_processor.py  # 비디오 처리 (회전, 프레임 처리 등)
├── pyproject.toml               # 프로젝트 설정 및 의존성
├── README.md                    # 프로젝트 문서
└── LICENSE                      # 라이선스
```

### 모듈 설명

- **main.py**: 메인 애플리케이션 클래스(`VideoEditApp`)와 진입점(`main()` 함수)
- **ui.py**: UI 컴포넌트 생성 및 레이아웃 관리
- **controllers/**: 기능별 제어 로직
  - `playback.py`: 비디오 재생, 일시정지, 시크 등 재생 관련 기능
  - `export.py`: 비디오 내보내기 및 완료 처리
  - `range_controller.py`: 구간 설정 (시작/종료 시간 또는 프레임)
- **handlers/**: 이벤트 및 파일 처리
  - `drag_drop.py`: 드래그 앤 드롭 이벤트 처리
  - `file_handler.py`: 파일 선택 다이얼로그 및 경로 관리
- **processors/**: 비디오 처리 로직
  - `video_processor.py`: 프레임 회전, 리사이즈, 비디오 정보 로드 등

## 사용 방법

1. **비디오 파일 선택**: "비디오 파일 선택" 버튼을 클릭하거나 파일을 드래그 앤 드롭하여 비디오 파일을 선택합니다.
2. **비디오 재생**: 재생 버튼을 클릭하여 비디오를 재생/일시정지할 수 있습니다.
   - 재생바에서 마우스 휠을 사용하여 프레임 단위로 이동할 수 있습니다.
   - 재생이 끝나면 자동으로 처음부터 반복 재생됩니다.
3. **비디오 정보 확인**: 선택한 비디오의 프레임 수, FPS, 시간, 해상도 정보가 표시됩니다.
4. **회전 설정**:
   - 90° 시계방향: 비디오를 시계방향으로 90도 회전
   - 180°: 비디오를 180도 회전
   - 90° 반시계방향: 비디오를 반시계방향으로 90도 회전
   - 리셋: 회전을 초기화
5. **구간 설정**: 
   - 프레임 또는 초 단위로 시작/종료 구간을 설정할 수 있습니다 (기본값: 전체 구간)
   - Radio 버튼으로 단위를 선택할 수 있습니다 (기본값: 프레임)
6. **FPS 설정**: 원하는 FPS 값을 입력합니다 (기본값은 원본 비디오의 FPS)
7. **출력 경로 설정**: 출력 파일의 경로를 설정합니다 (기본값은 원본 파일과 같은 경로에 `_rotated` 접미사 추가)
8. **Export**: "Export" 버튼을 클릭하여 처리된 비디오를 저장합니다.

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
