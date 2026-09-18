---
name: memory-learn
description: "Сохранить знание в память (search_chats.py learn)."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [memory, learn, python, sql]
    source: claude-code-config-pack
    origin: "command"
    argument_hint: "[категория]: <что запомнить>"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Сохранить знание в память (search_chats.py learn); без аргументов — разбор сессии. Триггеры: «запиши знание», «сохрани в базу знаний». Пайплайн 4 уровней → save-knowledge-base.

# Save to Memory

**Arguments:** текст, который пользователь написал вместе с вызовом навыка (what to remember)

## Task

Save new knowledge to long-term memory (SQLite FTS5).

## Format

```
/memory-learn [category]: [content]
```

## Categories

- `technical` - technical knowledge (code, patterns, debugging)
- `tools` - tools and usage
- `workflow` - work processes
- `preference` - user preferences
- `project` - project info

## Actions

1. **Parse arguments:**
   - If contains ":" - first part = category
   - Otherwise category = "general"

2. **Save:**
```bash
python ~/.hermes/ccpack/tools/search_chats.py learn "$CONTENT" "$CATEGORY"
```

3. **Confirm:**
   - Show what was saved
   - Category
   - Timestamp

## Examples

```
/memory-learn technical: ChromaDB crashes Extension Host on Windows
/memory-learn preference: User prefers TypeScript for frontend
/memory-learn Always use uv instead of pip for Python projects
```

## Auto-Learning Prompt

If just `/memory-learn` without arguments:
1. Analyze current session
2. Suggest what to save
3. Ask for confirmation
