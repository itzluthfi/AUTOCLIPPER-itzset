# YT-Short-Clipper

[![Discord](https://img.shields.io/badge/Join-Discord-5865F2?logo=discord&logoColor=white)](https://s.id/ytsdiscord)
[![GitHub Stars](https://img.shields.io/github/stars/jipraks/yt-short-clipper?style=social)](https://github.com/jipraks/yt-short-clipper)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS-lightgrey)]()

🎬 **Automated YouTube to Short-Form Content Pipeline**

Transform long-form YouTube videos (podcasts, interviews, vlogs) into engaging short-form content for TikTok, Instagram Reels, and YouTube Shorts — powered by AI.

---

## 🚀 Getting Started

### For Users (Non-Technical)

Download the desktop app for your platform:

| Platform | Download | Notes |
|----------|----------|-------|
| **Windows** | [Latest Release (.exe)](https://github.com/jipraks/yt-short-clipper/releases) | Windows 10+ |
| **macOS** | [Latest Release (.dmg)](https://github.com/jipraks/yt-short-clipper/releases) | macOS Catalina+, Apple Silicon & Intel |

Then follow the complete setup guide:

- 📖 **[English Guide](GUIDE.md)** - Complete setup guide with screenshots
- 📖 **[Panduan Indonesia](PANDUAN.md)** - Panduan lengkap dengan screenshot

**What you'll learn:**
1. How to download and run the app
2. Setup required libraries (yt-dlp, FFmpeg, Deno)
3. Setup YouTube cookies for video access
4. Configure AI API (multiple providers supported)
5. Start processing videos

### For Developers

If you want to contribute or run from source:

1. See [Installation](#-installation-for-development) below for development setup
2. See [Contributing](#-contributing) for contribution guidelines
3. See [Building from Source](#-building-from-source) for packaging the app

## ✨ Features

- **🎥 Auto Download** - Downloads YouTube videos with subtitles using yt-dlp
- **🔍 AI Highlight Detection** - Uses GPT-4 to identify the most engaging segments (60-120 seconds)
- **✂️ Smart Clipping** - Automatically cuts video at optimal timestamps
- **📱 Portrait Conversion** - Converts landscape (16:9) to portrait (9:16) with intelligent speaker tracking
- **🎯 Face Detection** - Two modes available:
  - **OpenCV (Fast)** - Crops to largest face, faster processing
  - **MediaPipe (Smart)** - Tracks active speaker via lip movement detection, more accurate but 2-3x slower
- **🪝 Hook Generation** - Creates attention-grabbing intro scenes with AI-generated text and TTS voiceover
- **📝 Auto Captions** - Adds CapCut-style word-by-word highlighted captions using Whisper
- **🖼️ Watermark Support** - Add custom watermark with adjustable position, size, and opacity
- **📊 SEO Metadata** - Generates optimized titles and descriptions for each clip
- **🖥️ Cross-Platform** - Runs on Windows and macOS (Apple Silicon + Intel)
- **⚡ GPU Acceleration** - NVENC (NVIDIA), AMF (AMD), QSV (Intel), VideoToolbox (macOS)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        YT-Short-Clipper                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐    ┌──────────────┐    ┌─────────────┐           │
│  │ YouTube  │───▶│  Downloader  │───▶│  Subtitle   │           │
│  │   URL    │    │   (yt-dlp)   │    │   Parser    │           │
│  └──────────┘    └──────────────┘    └─────────────┘           │
│                                              │                  │
│                                              ▼                  │
│                                    ┌─────────────────┐         │
│                                    │ Highlight Finder │         │
│                                    │    (GPT-4)       │         │
│                                    └─────────────────┘         │
│                                              │                  │
│                                              ▼                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Video Processing                       │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐  │  │
│  │  │   Clipper  │─▶│  Portrait  │─▶│  Hook Generator    │  │  │
│  │  │  (FFmpeg)  │  │ Converter  │  │  (TTS + Overlay)   │  │  │
│  │  └────────────┘  │ OpenCV /   │  └────────────────────┘  │  │
│  │                   │ MediaPipe  │             │            │  │
│  │                   └────────────┘             ▼            │  │
│  │                                    ┌────────────────┐     │  │
│  │                                    │Caption Generator│    │  │
│  │                                    │   (Whisper)     │    │  │
│  │                                    └────────────────┘     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                              │                  │
│                                              ▼                  │
│                                    ┌─────────────────┐         │
│                                    │  Output Clips   │         │
│                                    │  + Metadata      │         │
│                                    └─────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Requirements (For Development)

### System Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Runtime |
| FFmpeg | 4.4+ | Video processing |
| yt-dlp | Latest | YouTube downloading |
| Deno | 2.x | Required by yt-dlp for some extractors |

### Python Dependencies

See [requirements.txt](requirements.txt) for the full list. Key dependencies:

```
customtkinter>=5.2.0
openai>=1.0.0
opencv-python>=4.8.0
numpy>=1.24.0
Pillow>=10.0.0
mediapipe>=0.10.0
requests>=2.31.0
yt-dlp>=2026.3.17
google-generativeai>=0.7.0
google-api-python-client>=2.100.0
google-auth-oauthlib>=1.1.0
```

> **Note:** The app uses OpenAI Whisper API instead of local Whisper model.

### API Keys

The app supports **10+ AI providers** including:
- **YT Clip AI** (Recommended) - [https://ai.ytclip.org](https://ai.ytclip.org)
- **OpenAI** - GPT-4, Whisper, TTS
- **Google Gemini** - Free tier available
- **Groq** - Fastest + free
- **Anthropic Claude** - High quality
- And more...

See [GUIDE.md](GUIDE.md) or [PANDUAN.md](PANDUAN.md) for detailed API setup instructions.

---

## 🚀 Installation (For Development)

> **Note:** This section is for developers who want to run the app from source code. If you're a regular user, please follow the [User Guide](GUIDE.md) or [Panduan Indonesia](PANDUAN.md) instead.

### 1. Clone the Repository

```bash
git clone https://github.com/jipraks/yt-short-clipper.git
cd yt-short-clipper
```

### 2. Install System Dependencies

**Windows (using Chocolatey):**
```powershell
choco install ffmpeg yt-dlp
```

**macOS (using Homebrew):**
```bash
brew install ffmpeg yt-dlp
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
pip install yt-dlp
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
python app.py
```

The app will create a `config.json` file on first run where you can save your AI API keys and other settings.

---

## 📁 Project Structure

```
yt-short-clipper/
├── app.py                      # Main GUI application (entry point)
├── clipper_core.py             # Core processing logic (download, AI, video)
├── version.py                  # Version info and update URL
├── youtube_uploader.py         # YouTube upload functionality
├── tiktok_uploader.py          # TikTok upload functionality
├── requirements.txt            # Python dependencies
├── build.spec                  # PyInstaller build config (Windows)
├── build_macos.spec            # PyInstaller build config (macOS)
├── build_web.spec              # PyInstaller build config (Web version)
├── components/                 # Reusable UI widgets
│   ├── ai_provider_card.py     # AI provider configuration card
│   ├── page_layout.py          # Page layout components
│   └── progress_step.py        # Progress step indicator
├── config/                     # Configuration management
│   ├── ai_provider_config.py   # AI provider definitions
│   └── config_manager.py       # Config file read/write
├── dialogs/                    # Modal dialogs
│   ├── model_selector.py       # AI model search/select dialog
│   ├── repliz_upload.py        # Repliz upload dialog
│   ├── terms_of_service.py     # ToS dialog
│   ├── tiktok_upload.py        # TikTok upload dialog
│   └── youtube_upload.py       # YouTube upload dialog
├── pages/                      # GUI pages
│   ├── browse_page.py          # Browse output clips
│   ├── clipping_page.py        # Clipping progress
│   ├── contact_page.py         # Contact/feedback
│   ├── highlight_selection_page.py  # Select highlights to process
│   ├── processing_page.py      # Processing progress
│   ├── results_page.py         # Results display
│   ├── session_browser_page.py # Browse previous sessions
│   ├── settings_page.py        # Settings hub
│   ├── status_pages.py         # API & Library status pages
│   └── settings/               # Settings sub-pages
│       ├── ai_api_settings.py  # AI API configuration
│       ├── ai_providers/       # Per-provider settings
│       ├── output_settings.py  # Output directory settings
│       ├── performance_settings.py  # GPU & performance
│       ├── watermark_settings.py    # Watermark configuration
│       └── ...
├── utils/                      # Utility modules
│   ├── dependency_manager.py   # Auto-download FFmpeg, Deno
│   ├── gpu_detector.py         # GPU detection & encoder selection
│   ├── helpers.py              # Path helpers, platform detection
│   └── logger.py               # Logging utilities
├── assets/                     # App icons and images
│   ├── icon.png                # App icon (PNG)
│   ├── icon.ico                # App icon (Windows)
│   └── icon.icns               # App icon (macOS)
└── web/                        # Web UI (experimental)
    ├── index.html
    ├── app.js
    ├── css/
    └── components/
```

### Output Structure

```
output/
└── 20240115-143001/            # Session folder (timestamp-based)
    ├── master.mp4              # Final clip
    └── data.json               # Metadata
```

### data.json Structure

Each clip folder contains a `data.json` file with metadata:

```json
{
  "title": "🔥 Momen Kocak Saat Pembully Datang Minta Maaf",
  "hook_text": "Mantan pembully TIARA datang ke rumah minta endorse salad buah",
  "start_time": "00:15:23,000",
  "end_time": "00:17:05,000",
  "duration_seconds": 102.0,
  "has_hook": true,
  "has_captions": true,
  "youtube_title": "🔥 Momen Kocak Saat Pembully Datang Minta Maaf",
  "youtube_description": "Siapa sangka mantan pembully malah datang minta endorse! 😂 #podcast #viral #fyp",
  "youtube_tags": ["shorts", "viral", "podcast"]
}
```

---

## ⚙️ Configuration

All settings can be configured through the GUI Settings page (⚙️ button in the app).

For complete setup instructions with screenshots, see:
- [English Guide](GUIDE.md)
- [Panduan Indonesia](PANDUAN.md)

### Highlight Detection Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `num_clips` | 5 | Number of clips to generate |
| `min_duration` | 60s | Minimum clip duration |
| `max_duration` | 120s | Maximum clip duration |
| `target_duration` | 90s | Ideal clip duration |
| `temperature` | 1.0 | AI creativity (0.0-2.0) |

### Portrait Conversion Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `output_resolution` | 1080x1920 | Output video resolution |
| `min_frames_before_switch` | 210 | Frames before speaker switch (~7s at 30fps) |
| `switch_threshold` | 3.0 | Movement multiplier to trigger switch |

### Caption Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `language` | id | Transcription language |
| `chunk_size` | 4 | Words per caption line |

### Hook Generation Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `tts_voice` | nova | OpenAI TTS voice (nova/shimmer/alloy) |
| `tts_speed` | 1.0 | Speech speed |
| `max_words` | 15 | Maximum words in hook text |
| `tts_model` | tts-1 | TTS model (tts-1 or tts-1-hd) |

---

## 🔧 How It Works

### 1. Video Download
- Uses yt-dlp to download video in best quality (max 1080p)
- Automatically fetches auto-generated subtitles
- Extracts video metadata (title, description, channel)

### 2. Highlight Detection
- Parses SRT subtitle file with timestamps
- Sends transcript to GPT-4 with specific criteria:
  - Punchlines and funny moments
  - Interesting insights
  - Emotional/dramatic moments
  - Memorable quotes
  - Complete story arcs
- Validates duration (60-120 seconds)
- Generates hook text for each highlight

### 3. Portrait Conversion
- **OpenCV mode:** Uses Haar Cascade for face detection, crops to largest face
- **MediaPipe mode:** Tracks lip movement to identify active speaker
- Implements "camera cut" style switching (not smooth panning)
- Stabilizes crop position within each "shot"
- Maintains 9:16 aspect ratio at 1080x1920

### 4. Hook Generation
- Extracts first frame from clip
- Generates TTS audio using OpenAI's voice API
- Creates intro scene with:
  - Blurred/dimmed first frame background
  - Centered hook text with yellow highlight
  - AI voiceover reading the hook
- Concatenates hook with main clip

### 5. Caption Generation
- Transcribes audio using OpenAI Whisper API
- Creates ASS subtitle file with:
  - Word-by-word timing
  - Yellow highlight on current word
  - Black outline and semi-transparent background
- Burns captions into video using FFmpeg

---

## 🎨 Caption Styling

The captions use CapCut-style formatting:

```
Font: Arial Black (platform-dependent fallback)
Size: 65px
Color: White (#FFFFFF)
Highlight: Yellow (#00FFFF)
Outline: 4px Black
Shadow: 2px
Position: Lower third (400px from bottom)
```

---

## 💰 API Usage & Costs

Estimated OpenAI API costs per video (5 clips):

| Feature | Model | Est. Cost |
|---------|-------|-----------|
| Highlight Detection | GPT-4.1 | ~$0.05-0.15 |
| TTS Voiceover | TTS-1 | ~$0.01/clip |
| Captions | Whisper API | ~$0.01/clip |

**Total estimate:** ~$0.10-0.25 per video (5 clips)

The desktop app shows real-time token usage and cost estimation during processing.

---

## 🔨 Building from Source

### Windows

```bash
pip install -r requirements.txt
pip install pyinstaller

pyinstaller build.spec
# Output: dist/YTShortClipper.exe
```

### macOS

Requires Python 3.10+ and `create-dmg` (`brew install create-dmg`).

```bash
pip install -r requirements.txt
pip install pyinstaller

# Build .app bundle
python -m PyInstaller build_macos.spec --clean --noconfirm

# Create DMG (optional)
create-dmg \
    --volname "YTShortClipper" \
    --volicon "assets/icon.icns" \
    --window-size 600 400 \
    --icon "YTShortClipper.app" 150 185 \
    --app-drop-link 450 185 \
    "dist/YTShortClipper.dmg" \
    "dist/YTShortClipper.app"
```

**macOS notes:**
- User data is stored in `~/Library/Application Support/YTShortClipper/` (persists across app updates)
- FFmpeg is auto-downloaded from [evermeet.cx](https://evermeet.cx/ffmpeg/) (x86_64, runs on Apple Silicon via Rosetta 2)
- GPU acceleration uses VideoToolbox (hardware encoding on all Macs)
- ffplay is not available on macOS; video preview requires system player

---

## 🤝 Contributing

Contributions are welcome! We greatly appreciate contributions from anyone.

### Quick Start for Contributors

```bash
# 1. Fork this repo (click the Fork button on GitHub)

# 2. Clone your fork
git clone https://github.com/YOUR-USERNAME/yt-short-clipper.git
cd yt-short-clipper

# 3. Add upstream remote
git remote add upstream https://github.com/jipraks/yt-short-clipper.git

# 4. Create a new branch
git checkout -b feature/your-new-feature

# 5. Make changes, then commit
git add .
git commit -m "feat: description of changes"

# 6. Push to your fork
git push origin feature/your-new-feature

# 7. Create a Pull Request on GitHub
```

### How to Contribute

| Type | Description |
|-------|-----------|
| 🐛 **Bug Report** | Report bugs in the [Issues](../../issues) tab |
| 💡 **Feature Request** | Request new features in [Issues](../../issues) |
| 📖 **Documentation** | Improve docs, fix typos, add examples |
| 🔧 **Code** | Fix bugs, add features, improve performance |

📚 **Complete guide available in [CONTRIBUTING.md](CONTRIBUTING.md)** - includes Git tutorial for beginners!

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

- This tool is for personal/educational use only
- Respect YouTube's Terms of Service
- Ensure you have rights to use the content you're processing
- The AI-generated content should be reviewed before publishing

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloading
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [OpenCV](https://opencv.org/) - Computer vision
- [MediaPipe](https://mediapipe.dev/) - Face & lip tracking
- [FFmpeg](https://ffmpeg.org/) - Video processing
- [OpenAI API](https://openai.com/) - GPT-4 and TTS

---

## 👨‍💻 Credits

Made with ☕ by **Aji Prakoso** for content creators

| | |
|---|---|
| 🎓 | [n8n & Automation eCourse](https://classroom.jipraks.com) |
| 📸 | [@jipraks on Instagram](https://instagram.com/jipraks) |
| 🎬 | [Aji Prakoso on YouTube](https://youtube.com/@jipraks) |
| 🌐 | [About Aji Prakoso](https://www.jipraks.com) |
