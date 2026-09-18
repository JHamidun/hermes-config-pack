---
name: changelog
description: "Автоматическая генерация changelog из git commits и PRs."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [changelog, git]
    source: claude-code-config-pack
    origin: "command"
    argument_hint: "[version number, e.g., v2.1.0]"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Автоматическая генерация changelog из git commits и PRs

# 📝 Changelog Generator: текст, который пользователь написал вместе с вызовом навыка

Создай changelog для версии: **текст, который пользователь написал вместе с вызовом навыка**

## Process:

### 1. Git Analysis
Fetch commits since last release, group by type (Conventional Commits)

### 2. GitHub Integration
Fetch PR details, closed issues

### 3. Format CHANGELOG.md
Based on Keep a Changelog format

### 4. Generate Release Notes
Create GitHub Release

### 5. Distribution
- Commit changelog
- Create git tag
- Notify team

