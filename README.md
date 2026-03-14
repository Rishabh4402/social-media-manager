# 🤖 Social Media Manager Agent

An automated agent that posts engaging Instagram content daily using AI and trending videos.

## 📋 Table of Contents
- [Overview](#overview)
- [How it Works](#how-it-works)
- [Trending Reels](#trending-reels)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [GitHub Secrets](#github-secrets)
- [GitHub Automation](#github-automation)
- [Safety & Content Policy](#safety-content-policy)

---

## 🚀 Overview
This agent automates the entire lifecycle of Instagram content:
1. **AI-Powered Captions**: Uses **Gemini** to generate viral captions with trending hashtags.
2. **Trending Reels**: Downloads the **most popular videos** from Pixabay (with sound) and posts them directly.
3. **Photo Posts**: Generates AI images with fact overlays for static posts.
4. **Auto-Alternating**: Posts a **Photo** on odd days and a **Reel** on even days.
5. **Zero Repeats**: Tracks every posted video to guarantee fresh content every single day.

## ⚙️ How it Works
1. **Brain**: AI generates a unique fact and viral caption with trending hashtags.
2. **Eyes**: Pixabay API finds the most popular, high-view-count videos on trending topics.
3. **Voice**: `instagrapi` logs in and uploads the content to Instagram.
4. **Memory**: A history file tracks all posted video IDs — no video is ever posted twice.

## 🎬 Trending Reels
- **80+ Trending Topics**: Spiritual, Motivational, Animation, Science, Tech & AI, Music, Nature, and India Specials.
- **Audio Included**: Pixabay videos come with cinematic sound/music.
- **Bilingual Captions**: English + Hindi (including Shayari & motivational quotes).
- **Global Hashtags**: Curated for Indian, European, and US audiences.
- **Sorted by Popularity**: Only the most-viewed videos are selected.
- **Never Repeats**: History tracking ensures every post is unique.

## 📁 Project Structure
| File | Purpose |
|------|---------|
| `main.py` | Central orchestrator — alternates between Photo and Reel |
| `content_gen.py` | AI text generation (Gemini + HuggingFace fallback) and image creation |
| `trending_reels.py` | Downloads trending Pixabay videos with sound and viral captions |
| `social_manager.py` | Instagram login and upload (photo + reel) |
| `posted_history.json` | Tracks posted video IDs to prevent duplicates |
| `requirements.txt` | Python dependencies |
| `.github/workflows/daily_post.yml` | GitHub Actions daily automation |

## 🛠 Setup Instructions

### Local Run
1. Clone the repo
2. `pip install -r requirements.txt`
3. Copy `.env.template` to `.env` and fill in your keys
4. Run: `python3 main.py`

## 🔑 GitHub Secrets
Add these in **Settings > Secrets and variables > Actions**:

| Secret | Description |
|--------|-------------|
| `IG_USERNAME` | Instagram email/username |
| `IG_PASSWORD` | Instagram password |
| `GEMINI_API_KEY` | Google AI Studio API key |
| `PIXABAY_API_KEY` | Pixabay API key for trending videos |
| `CONTENT_NICHE` | Content niche (e.g., "Fascinating Science Facts") |

## 🤖 GitHub Automation
- Runs **daily at 09:00 UTC** via GitHub Actions.
- Auto-commits `posted_history.json` after each run to track posted videos.
- Can be triggered manually from the **Actions** tab.

## 🛡 Safety & Content Policy
- All AI-generated content is filtered for **no vulgarity** and **no sensitive matters**.
- Pixabay videos are **royalty-free** and safe to use commercially.
- Trending hashtags are curated to avoid shadowbanned or inappropriate tags.

---
*Built for automated Instagram growth* 🚀
