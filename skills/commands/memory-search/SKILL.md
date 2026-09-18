---
name: memory-search
description: "Поиск по памяти: заметки (memory_find.py) + чаты + знания."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [memory, search, python, telegram, sql]
    source: claude-code-config-pack
    origin: "command"
    argument_hint: "<запрос> [--type code|error|learning|decision]"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Поиск по памяти: заметки (memory_find.py) + чаты + знания (search_chats.py knowledge). Триггеры: «поищи в памяти», «найди в базе знаний». Чистый поиск чатов → /search-chats.

# Search Memory

> **Алиас `/search-chats`.** Обе команды используют один движок — `~/.hermes/ccpack/tools/search_chats.py` (SQLite FTS5, `~/.hermes/ccpack/chats.db`).
> `/memory-search` дополнительно ищет по извлечённым знаниям (knowledge base); `/search-chats` — базовый полнотекстовый поиск + управление индексом/архивом.

**Arguments:** текст, который пользователь написал вместе с вызовом навыка (search query [--type code|error|learning|decision])

## Task

Search across all chat history and accumulated knowledge using SQLite FTS5.

## Actions

1. **Search chats (full history):**

```bash
python ~/.hermes/ccpack/tools/search_chats.py search "текст, который пользователь написал вместе с вызовом навыка"
```

2. **Search knowledge base (extracted learnings, code, errors):**

```bash
python ~/.hermes/ccpack/tools/search_chats.py knowledge "текст, который пользователь написал вместе с вызовом навыка"
```

3. **Search only code snippets:**

```bash
python ~/.hermes/ccpack/tools/search_chats.py knowledge "текст, который пользователь написал вместе с вызовом навыка" --type code
```

4. **Search only errors:**

```bash
python ~/.hermes/ccpack/tools/search_chats.py knowledge "текст, который пользователь написал вместе с вызовом навыка" --type error
```

## Content Types

| Type | Description |
|------|-------------|
| `code` | Code, functions, configs |
| `error` | Errors and solutions |
| `learning` | Extracted knowledge |
| `decision` | Architectural decisions |
| `discussion` | Discussions |
| `question` | Questions |

## Examples

```
/memory-search FastAPI streaming
/memory-search telegram bot errors --type error
/memory-search ChromaDB vector --type code
```
