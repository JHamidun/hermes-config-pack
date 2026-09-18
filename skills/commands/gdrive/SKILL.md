---
name: gdrive
description: "Google Drive (gdrive_client.py)."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [gdrive, python]
    source: claude-code-config-pack
    origin: "command"
    argument_hint: "[ls <id|ссылка> | find <запрос> | get <id> -o <папка> | pull <id> -o <папка>]"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Google Drive (gdrive_client.py): что в папке, поиск, скачать файл/папку, залить. Триггеры: «гугл диск», «скачай с диска», «расшаренная папка». НЕ Яндекс.Диск → skill yandex.

# /gdrive

Рабочий клиент — `~/.hermes/ccpack/tools/gdrive_client.py`.

```bash
python ~/.hermes/ccpack/tools/gdrive_client.py ls <id_или_ссылка> [--recursive]
python ~/.hermes/ccpack/tools/gdrive_client.py find "вебинар"
python ~/.hermes/ccpack/tools/gdrive_client.py get <id_файла> -o ./куда/
python ~/.hermes/ccpack/tools/gdrive_client.py pull <id_папки> -o ./куда/ --ext mp4,m4a --min-mb 5
python ~/.hermes/ccpack/tools/gdrive_upload.py upload <локальная_папка> <имя_на_диске>
```

Принимает ссылку целиком — идентификатор вынимается сам. Права — из
`~/.hermes/ccpack/google_oauth_token.json` (скоуп `drive`, чтение и запись).

За подробностями — Skill `google-workspace`.

> Здесь лежал inline-код `files().list()` БЕЗ `supportsAllDrives` и
> `includeItemsFromAllDrives`. Без этих двух флагов API молча скрывает всё, что
> лежит на общих дисках: папка выглядит пустой, хотя файлы в ней есть. В клиенте
> флаги проставлены — и в списке, и при скачивании. Код удалён.
