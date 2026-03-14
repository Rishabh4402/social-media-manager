# 🏗 System Architecture & Technical Details

This document provides a deep dive into the **Social Media Manager Agent**'s internal mechanics, agentic workflow, and project structure.

## 📋 Table of Contents
- [System Architecture (The How)](#-system-architecture-the-how)
- [Agentic Workflow](#-agentic-workflow)
- [Project Layout](#-project-layout)
- [GitHub Secrets](#-github-secrets)
- [GitHub Automation](#-github-automation)
- [Safety & Content Policy](#-safety--content-policy)

---

## ⚙️ System Architecture (The How)
This project is built on an **Agentic Software Design**, moving beyond simple scripts into a modular architecture where an intelligent orchestrator manages specialized "Tools" and utilizes a "Memory" state.

### 🧠 The Orchestrator
The `InstagramAgent` (located in `src/agent/core.py`) is the central brain. It maintains the high-level goal and decides which tool to call next. It doesn't know how to "talk to Instagram" or "edit video"—it only knows how to **coordinate** the tools that do.

### 🛠 The Toolset
Tools are decoupled interfaces that allow the Agent to interact with the world:
1. **Visual Tool** (`src/tools/video.py`): Interfaces with the Pixabay API to scout trending videos and uses MoviePy to programmatically edit them (adding music, optimizing for Reels).
2. **Cognitive Tool** (`src/tools/llm.py`): Interfaces with Gemini or HuggingFace to transform raw data into a narrative.
3. **Platform Tool** (`src/tools/instagram.py`): A robust wrapper for the Instagram API logic.

### 💾 The Memory Module
Located in `src/memory/history.py`, this module prevents the agent from repeating itself. It tracks every unique video and audio ID to ensure that your audience always sees fresh, unique content.

### 📜 System Instructions
Strict separation between **System Instructions** (`system_instructions/`) and dynamic **Prompts** (`prompts/`):
- **System Instructions**: Define the Agent's identity, safety guardrails, and behavioral personality.
- **Prompts**: Context-specific templates for generating a single post's content.

---

## 📁 Project Layout
| Module | Exact Implementation |
|------|---------|
| `main.py` | Minimal entrypoint to wake up the agent. |
| `src/agent/` | Core orchestration logic and decision-making. |
| `src/tools/` | Decoupled functional interfaces (LLM, Video, Instagram). |
| `src/memory/` | Persistence and state management (History Tracking). |
| `system_instructions/` | AI behavioral XML guardrails and identity. |
| `prompts/` | Dynamic templates for content generation. |
| `.github/workflows/` | Daily automation/trigger logic. |

---

## 🔑 GitHub Secrets
Add these in **Settings > Secrets and variables > Actions**:

| Secret | Description |
|--------|-------------|
| `IG_USERNAME` | Instagram email/username |
| `IG_PASSWORD` | Instagram password |
| `GEMINI_API_KEY` | Google AI Studio API key |
| `PIXABAY_API_KEY` | Pixabay API key for trending videos |
| `CONTENT_NICHE` | Content niche (e.g., "Fascinating Science Facts") |

---

## 🤖 GitHub Automation
- Runs **daily at 09:00 UTC** via GitHub Actions.
- Auto-commits `posted_history.json` after each run to track posted videos.
- Can be triggered manually from the **Actions** tab.

---

## 🛠 Low-Level Design (LLD)

### 1. Core Orchestrator (`src/agent/core.py`)
- **`InstagramAgent.run()`**: The master workflow function.
    - Logic: Calls `video_tool.create_reel()` ➔ `insta_tool.login()` ➔ `insta_tool.post_reel(path, caption)`.
    - Error Handling: Exits if content generation or login fails to prevent empty posts.

### 2. Video & Media Tool (`src/tools/video.py`)
- **`get_trending_video()`**: Searches Pixabay using `TRENDING_TOPICS`. Filters results using `HistoryManager` to ensure uniqueness.
- **`get_background_music()`**: Searches Pixabay for music-related videos. Downloads them and uses `MoviePy` to verify that an audio track actually exists.
- **`add_music_to_video()`**: 
    - Downloads a music source and overlays it onto the visual clip.
    - **Encoding**: Uses `ffmpeg_params` specifically for Instagram (`-movflags +faststart` for web streaming and `-pix_fmt yuv420p` for mobile player compatibility).
- **`create_reel()`**: The main entry point for video creation. Coordinates searching, downloading, audio-mixing, and caption generation.

### 3. LLM & Content Tool (`src/tools/llm.py`)
- **`generate_text()`**: 
    - Reads the `instagram_manager.xml` system instruction.
    - Orchestrates logic between Gemini and its HuggingFace fallback.
- **`generate_text_gemini()`**: Directly interfaces with `google.genai` to produce structured captions.
- **`overlay_text()`**: Uses `PIL (Pillow)` to draw formatted text on top of generated images for photo posts.

### 4. Instagram API Tool (`src/tools/instagram.py`)
- **`login()`**: Implements a session-caching mechanism (`ig_session.json`). It attempts to reload an existing session to avoid repeated logins and potential bot detection.
- **`post_reel()`**: Uses `clip_upload` with explicit `extra_data={"audio_muted": False}` to bypass Instagram's automated audio-stripping algorithms.

### 5. Memory Module (`src/memory/history.py`)
- **`save(video_id, audio_id)`**: Appends used IDs to `posted_history.json`.
- **`is_video_posted()`**: A high-efficiency lookup function used by the video tool to skip already-seen content.
