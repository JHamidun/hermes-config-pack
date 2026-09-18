---
name: memory-stats
description: "Статистика памяти (search_chats.py stats)."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [memory, stats, python]
    source: claude-code-config-pack
    origin: "command"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Статистика памяти (search_chats.py stats): сессии, сообщения, knowledge-записи, размер БД. Триггеры: «статистика памяти», «сколько в базе знаний».

# Memory Statistics

## Task

Show unified memory system statistics.

## Actions

```bash
python ~/.hermes/ccpack/tools/search_chats.py stats
```

## What it shows

- Sessions count and date range
- Messages count (user + assistant)
- Knowledge entries by type (learning, code, error, decision, discussion, question)
- Knowledge entries by source (qdrant, chromadb_v2, manual)
- Database size
