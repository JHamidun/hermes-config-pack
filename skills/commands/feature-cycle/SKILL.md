---
name: feature-cycle
description: "Полный цикл разработки фичи с параллельными агентами."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [feature, cycle]
    source: claude-code-config-pack
    origin: "command"
    argument_hint: "[описание фичи]"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Полный цикл разработки фичи с параллельными агентами

# Цикл разработки фичи: текст, который пользователь написал вместе с вызовом навыка

## Phase 1: Discovery (Parallel)
Запускаем параллельно:
- @business-analyst: User research, market analysis, competitive analysis
- @product-designer: User flows, wireframes, прототипы

Каждый работает в своём Task одновременно.

## Phase 2: Planning (Sequential)
После завершения Phase 1:
- @system-analyst читает результаты Phase 1 → Technical feasibility analysis
- @software-architect читает результаты → Architecture design, tech stack выбор

## Phase 3: Implementation (Parallel)
Все работают параллельно в изолированных файлах:
- @frontend-dev: UI components, state management
- @backend-dev: API endpoints, database schema
- @integration-dev: Third-party services integration
- @qa-specialist: Test suites (unit, integration, E2E)

## Phase 4: Quality Assurance (Sequential)
Последовательная проверка всех результатов Phase 3:
- @qa-specialist: Manual testing, exploratory testing
- @security-engineer: Security review, vulnerability scanning
- Финальный code review

## Phase 5: Deployment
- @devops-engineer: CI/CD pipeline, deployment, monitoring setup

## Структура документации
Каждый agent сохраняет output в:
`docs/features/[feature-name]/[agent-name].md`

## Метрики успеха
- Time to market: сколько времени от идеи до production
- Quality score: coverage, security issues, performance
- Team efficiency: параллельная работа vs последовательная
