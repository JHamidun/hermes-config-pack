---
name: youtube-upload
description: "Upload a video to YouTube with metadata."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [youtube, upload, python, video]
    source: claude-code-config-pack
    origin: "command"
    argument_hint: "path/to/video.mp4 --title 'Title' [--private]"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Upload a video to YouTube with metadata

Upload a video to YouTube via the YouTube Data API v3.

**Usage:**
- `/youtube-upload final.mp4 --title "DeepSeek обошёл GPT-5" --private`
- `/youtube-upload video.mp4 --title "Title" --tags "ai,tech" --thumbnail thumb.png`

Аргументы: `текст, который пользователь написал вместе с вызовом навыка`

**Prerequisites (одноразово):**
1. Google Cloud Console → включи **YouTube Data API v3** → OAuth client type *Desktop app* →
   скачай JSON и положи в `~/.hermes/ccpack/.youtube-client-secrets.json`.
2. `pip install google-api-python-client google-auth-oauthlib`
3. Первый запуск сам откроет браузер и сохранит токен в `~/.hermes/ccpack/.youtube-oauth-token.json`.

Готового скилла-обёртки в паке нет — команда работает напрямую по API. Разбери `текст, который пользователь написал вместе с вызовом навыка`
(путь к файлу + флаги) и выполни:

```python
import os, sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube",
          # captions().insert() без force-ssl отвечает 403 — субтитры не зальются.
          # Меняешь скоуп — удали ~/.hermes/ccpack/.youtube-oauth-token.json, иначе
          # подхватится старый токен с прежними правами и ошибка не уйдёт.
          "https://www.googleapis.com/auth/youtube.force-ssl"]
TOKEN   = Path(os.environ.get("CCPACK_HOME", Path.home() / ".hermes" / "ccpack")) / ".youtube-oauth-token.json"
SECRETS = Path(os.environ.get("CCPACK_HOME", Path.home() / ".hermes" / "ccpack")) / ".youtube-client-secrets.json"

# --- параметры из текст, который пользователь написал вместе с вызовом навыка ---
video     = "final.mp4"
title     = "TITLE"
desc      = ""
tags      = []            # --tags "ai,tech" -> ["ai","tech"]
privacy   = "private"     # private | unlisted | public
thumbnail = None          # --thumbnail thumb.png

if TOKEN.exists():
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
else:
    if not SECRETS.exists():
        sys.exit(f"нет {SECRETS} — заведи OAuth client (Desktop app) в Google Cloud Console")
    creds = InstalledAppFlow.from_client_secrets_file(str(SECRETS), SCOPES).run_local_server(port=0)
    TOKEN.write_text(creds.to_json(), encoding="utf-8")

yt = build("youtube", "v3", credentials=creds)
req = yt.videos().insert(
    part="snippet,status",
    body={"snippet": {"title": title, "description": desc, "tags": tags},
          "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}},
    media_body=MediaFileUpload(video, chunksize=-1, resumable=True),
)
resp = None
while resp is None:                       # resumable upload: цикл обязателен
    status, resp = req.next_chunk()
    if status:
        print(f"{int(status.progress() * 100)}%")
vid = resp["id"]
print(f"https://youtube.com/watch?v={vid}")

if thumbnail and os.path.exists(thumbnail):   # требует верифицированного канала
    yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(thumbnail)).execute()
```

**Гочи:**
- Заливай сначала `private`, посмотри результат, потом переключай видимость:
  `yt.videos().update(part='status', body={'id': vid, 'status': {...'privacyStatus':'public'}})` —
  в `status` передавай **весь** объект из `videos().list(part='status')`, иначе снесёшь остальные поля.
- Дневная квота API — 10 000 единиц, одна заливка ≈ 1600. То есть ~6 видео в сутки на проект.
- Shorts определяются автоматически: вертикаль ≤ 3 минут. Отдельного флага нет.
- Субтитры отдельным вызовом `captions().insert(part='snippet', body=..., media_body=srt)`.
