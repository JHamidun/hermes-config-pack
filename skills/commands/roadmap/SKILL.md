---
name: roadmap
description: "Генерация product roadmap с приоритизацией."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [roadmap, xlsx, pptx]
    source: claude-code-config-pack
    origin: "command"
    argument_hint: "[Q1 2025 / 2025 / next 6 months]"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Генерация product roadmap с приоритизацией

# 🗺️ Product Roadmap: текст, который пользователь написал вместе с вызовом навыка

Создай product roadmap для периода: **текст, который пользователь написал вместе с вызовом навыка**

## Process:

### 1. Gather Context
- Fetch Linear/Jira issues
- Analyze backlog
- Review PRD and specs

### 2. Prioritization
Impact vs Effort Matrix с Priority Score

### 3. Roadmap Creation (xlsx skill)
- Timeline Gantt Chart
- Feature List с priorities
- Resource Allocation
- Metrics & Goals

### 4. Visualization (pptx skill)
- Executive Summary
- Timeline Overview
- Feature Highlights

### 5. Distribution
- Notion page
- Google Drive share
- Slack notification

