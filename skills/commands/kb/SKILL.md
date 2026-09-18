---
name: kb
description: "Поиск по локальной KB kb.py."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [python, telegram, gmail, sql]
    source: claude-code-config-pack
    origin: "command"
    argument_hint: "\"<запрос>\" [--source tldv|spark|gmail|outlook|telegram] [--after DATE] [--speaker Name]"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Поиск по локальной KB kb.py: встречи tl;dv/Spark, письма Gmail/Outlook, Telegram; + ingest. Триггеры: «база знаний», «найди в встречах». История чатов → /search-chats.

# Knowledge Base Search

**Arguments:** текст, который пользователь написал вместе с вызовом навыка

## Task

Search the local knowledge base (meetings, emails, chats) using SQLite FTS5 with BM25 ranking.

## Actions

### Search all sources

```bash
python ~/.hermes/ccpack/tools/kb.py search "текст, который пользователь написал вместе с вызовом навыка"
```

### Search specific source

```bash
python ~/.hermes/ccpack/tools/kb.py search "текст, который пользователь написал вместе с вызовом навыка" --source tldv
```

### Search with date filter

```bash
python ~/.hermes/ccpack/tools/kb.py search "текст, который пользователь написал вместе с вызовом навыка" --after 2025-01-01
```

### Search by speaker

```bash
python ~/.hermes/ccpack/tools/kb.py search "текст, который пользователь написал вместе с вызовом навыка" --speaker "Name"
```

### Show stats

```bash
python ~/.hermes/ccpack/tools/kb.py stats
```

### Show sources

```bash
python ~/.hermes/ccpack/tools/kb.py sources
```

### Ingest new data

```bash
python ~/.hermes/ccpack/tools/kb.py ingest tldv                # tl;dv transcripts
python ~/.hermes/ccpack/tools/kb.py ingest spark                # Spark Mail transcripts
python ~/.hermes/ccpack/tools/kb.py ingest telegram <file.json> # Telegram export
python ~/.hermes/ccpack/tools/kb.py ingest gmail [days]         # Gmail emails (default: 90)
python ~/.hermes/ccpack/tools/kb.py ingest gcalendar [days]     # Google Calendar (default: 365)
python ~/.hermes/ccpack/tools/kb.py ingest outlook [days]       # Outlook/Exchange (default: 90)
```

### Show full document

```bash
python ~/.hermes/ccpack/tools/kb.py doc <id>
```

## Search tips

| Syntax | Example | Description |
|--------|---------|-------------|
| Simple words | `спринт планирование` | Match both words |
| Quoted phrase | `"example-query"` | Exact phrase match |
| Prefix | `react*` | Words starting with react |
| OR | `zoom OR meet` | Either word |

## Sources

| Source | Description | Documents |
|--------|-------------|-----------|
| tldv | tl;dv meeting transcripts | XXX |
| gmail | Gmail emails | XXX |
| spark | Spark Mail AI meeting summaries | XXX |
| gcalendar | Google Calendar events | XXX |
| telegram | Telegram chat exports | (on demand) |
| outlook | Outlook/Exchange emails | XXX |

## Examples

```
/kb example-query
/kb спринт --source tldv --after 2025-01-01
/kb "YourProduct" --source spark
/kb stats
/kb sources
```
