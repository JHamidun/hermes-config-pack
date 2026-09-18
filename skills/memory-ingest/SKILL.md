---
name: memory-ingest
description: "Индексация сессий Claude Code в chats.db (search_chats.py."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [memory, ingest, python, sql, claude]
    source: claude-code-config-pack
    origin: "command"
    argument_hint: "[--force]"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Индексация сессий Claude Code в chats.db (search_chats.py index, --force ре-индекс). Триггеры: «проиндексируй чаты», «обнови индекс чатов». Поиск → /search-chats.

# Ingest Chat History

**Arguments:** текст, который пользователь написал вместе с вызовом навыка (optional: --force)

## Task

Index all Claude Code chat sessions into SQLite FTS5 database for search.

## Actions

1. **Incremental index (fast, skips already indexed):**

```bash
python ~/.hermes/ccpack/tools/search_chats.py index
```

2. **Force full re-index:**

```bash
python ~/.hermes/ccpack/tools/search_chats.py index --force
```

3. **Check stats after:**

```bash
python ~/.hermes/ccpack/tools/search_chats.py stats
```

## Info

- Chats are stored in `~/.hermes/sessions/` as JSONL files
- Archived chats in `~/.hermes/sessions/*/archive/`
- Both active and archived sessions are indexed
- Incremental: only new/modified files are re-indexed
- Database: `~/.hermes/ccpack/chats.db` (SQLite FTS5)

## After indexing

- `/search-chats query` to search chats
- `/memory-search query` to search knowledge base
