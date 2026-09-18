---
name: start-feature
description: "Начать работу над feature из Linear issue с полной."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [start, feature, git]
    source: claude-code-config-pack
    origin: "command"
    argument_hint: "[Linear issue ID, e.g., PROJ-123]"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Начать работу над feature из Linear issue с полной автоматизацией

# 🚀 Start Feature: текст, который пользователь написал вместе с вызовом навыка

Автоматизирую весь workflow для issue: **текст, который пользователь написал вместе с вызовом навыка**

## Process:

### 1. Fetch Issue (Linear MCP)
Get requirements, acceptance criteria

### 2. Technical Planning
Use @system-analyst для design

### 3. Estimation
Use /estimate command

### 4. Git Setup
Create feature branch

### 5. Implementation
Execute plan с agents

### 6. Testing
Run tests, check coverage

### 7. PR Creation
Create PR via GitHub MCP, link to issue

### 8. Post-PR
Update Linear, notify team

