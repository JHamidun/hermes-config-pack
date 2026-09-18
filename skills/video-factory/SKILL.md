---
name: video-factory
description: "Full video production pipeline."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [video, factory, audio]
    source: claude-code-config-pack
    origin: "command"
    argument_hint: "topic or 'auto' for trend-based selection"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Full video production pipeline — from trends to YouTube in one command

Launch the Video Factory agent to produce a complete video.

**Usage:**
- `/video-factory DeepSeek V4 release` — make a video about a specific topic
- `/video-factory auto` — auto-detect best trending topic
- `/video-factory auto --format short` — YouTube Short (15-25s)
- `/video-factory auto --format medium` — Medium video (60-90s)
- `/video-factory "тема" --no-avatar` — AI video only, no HeyGen avatar
- `/video-factory "тема" --no-upload` — produce video but don't upload to YouTube

**What happens:**
1. Trend Discovery (if auto) — finds viral topics across Reddit, X, TikTok, YouTube
2. Script Generation — hook-value-abrupt formula, optimized for retention
3. Visual Production — HeyGen avatar + Veo 3.1 b-roll (parallel)
4. Audio Production — ElevenLabs voiceover + music with ducking
5. Post-Production — assembly, subtitles, thumbnail
6. YouTube Upload — as Private first, then you review and approve

Topic: текст, который пользователь написал вместе с вызовом навыка

Read the Agent `video-factory` definition and execute the full pipeline for the specified topic.
