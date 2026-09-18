---
name: daily
description: "Generate daily standup summary."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [daily, git]
    source: claude-code-config-pack
    origin: "command"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Generate daily standup summary

# Daily Standup Summary

Generate concise daily report:

## ✅ Completed Yesterday
- What was finished
- PRs merged
- Issues closed

## 🔄 In Progress Today
- Current work
- Focus areas
- Expected completion

## 🚧 Blockers
- Issues or dependencies
- Need help with
- Waiting on

Check recent git commits, open files, and project status.
Keep it brief and actionable.
