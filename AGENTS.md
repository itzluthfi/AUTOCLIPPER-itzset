# 🤖 AGENTS.md - AI Developer Guide for YT-Short-Clipper

## 📌 Project Overview
**YT-Short-Clipper** is a desktop application that automates the creation of short-form content (TikTok, Reels, Shorts) from long-form YouTube videos. It leverages AI (GPT-4, Whisper) for highlight detection and captioning, and Computer Vision (OpenCV) for smart cropping.

## 🏗️ Architecture & Tech Stack

### core Technology
- **Language**: Python 3.10+
- **GUI Framework**: CustomTkinter
- **Video Processing**: FFmpeg (via subprocess), OpenCV (for face detection)
- **Downloading**: yt-dlp
- **AI/ML**: 
  - **LLM**: OpenAI API (GPT-4) or compatible providers (Groq, Gemini via `ai_provider_card.py`)
  - **Transcription**: OpenAI Whisper API
  - **TTS**: OpenAI TTS (for hooks)

### High-Level Structure
1. **Frontend (GUI)**:
   - Entry point: `app.py` (Main `YTShortClipperApp` class).
   - Pages: Located in `pages/` (e.g., `browse_page.py`, `settings_page.py`).
   - Navigation: Managed by `YTShortClipperApp.show_page`.
   - Threading: Heavy tasks (downloads, processing) run in background threads to keep UI responsive.

2. **Backend (Logic)**:
   - `clipper_core.py`: **The Brain**. Contains the `AutoClipperCore` class which orchestrates the entire pipeline:
     1. Download (`download_video`)
     2. Parse Subtitles (`parse_srt`)
     3. AI Highlight Detection (`find_highlights`)
     4. Video Processing (`process_clip`: cut -> portrait -> hook -> captions)

3. **Data & Config**:
   - `config.json`: Stores user settings (API keys, preferences). Managed by `ConfigManager`.
   - `cookies.txt`: Required for YouTube authentication (handled by `COOKIES.md` guide).
   - `output/`: Generated clips and metadata (`data.json`).

## 📂 Key Directories & Files

| Path | Description |
|------|-------------|
| **`app.py`** | Main application entry point. Handles window management, global state, and navigation. |
| **`clipper_core.py`** | Core business logic. Contains all video processing and AI interaction code. |
| **`pages/`** | GUI Page classes. Each file corresponds to a screen in the app. |
| **`components/`** | Reusable UI widgets (e.g., `ai_provider_card.py` for API settings). |
| **`utils/`** | Helper utilities (`gpu_detector.py`, `dependency_manager.py`, `logger.py`). |
| **`assets/`** | Images and icons. |
| **`SYSTEM_PROMPT.md`** | Default prompt used for AI highlight detection. |
| **`build.spec`** | PyInstaller configuration for building the executable. |

## 🔄 Core Workflows

### 1. Highlight Detection Flow
`clipper_core.py` -> `find_highlights`:
1.  Reads `.srt` file from download.
2.  Constructs a prompt using `SYSTEM_PROMPT.md` + Transcript.
3.  Sends to LLM (GPT-4/Gemini/etc.).
4.  Parses JSON response containing start/end timestamps and hook text.

### 2. Portrait Conversion Flow
`clipper_core.py` -> `convert_to_portrait`:
1.  **Face Detection**: Uses OpenCV/MediaPipe to find faces in frames.
2.  **Active Speaker**: Analyzes lip movement (if MediaPipe) or simplistic face tracking (OpenCV).
3.  **Cropping**: detailed logic to calculate the 9:16 crop window, ensuring smooth transitions (simulated camera cuts).

### 3. Captioning Flow
`clipper_core.py` -> `process_clip`:
1.  Extracts audio from cut clip.
2.  Sends to Whisper API -> gets word-level timestamps.
3.  Generates `.ass` subtitle file with specific styling (Yellow highlight, specific font).
4.  Burns into video using FFmpeg.

## 🛠️ Development Setup

### specific Requirements
- **FFmpeg** and **yt-dlp** must be in PATH or configured.
- `requirements.txt` contains Python libs.

### Running Locally
```bash
pip install -r requirements.txt
python app.py
```

### Packaging
```bash
pyinstaller build.spec
```

## 📝 Coding Standards & Conventions
- **Type Hinting**: Encouraged for core logic methods (e.g., `def process(self, url: str) -> dict`).
- **Error Handling**: 
  - GUI should never crash. Catch exceptions and show `messagebox.showerror`.
  - Log errors to `error.log` using `utils.logger`.
- **Async/Threading**: strictly use `threading.Thread` for blocking I/O (network/disk) to prevent freezing the `tkinter` main loop.
- **Config**: Always access/save settings via `self.config` in `app.py` or pass config dicts to `clipper_core.py`.

## 🤖 AI Agent Tips
- When modifying `clipper_core.py`, be mindful of the huge method size. Consider breaking down `process_clip` if adding complexity.
- **Prompt Engineering**: Changes to logic often require changes to `SYSTEM_PROMPT.md`. Check that file if highlight quality degrades.
- **Dependencies**: `utils/dependency_manager.py` handles auto-downloading binaries (ffmpeg/yt-dlp) for end-users. Do not break this flow.

## 🔗 Related Documentation
- `README.md`: General user info.
- `GUIDE.md`: Detailed usage guide.
- `BUILD.md`: Detailed build instructions (PyInstaller).
