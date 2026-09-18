---
name: parallel-dev
description: "Параллельная разработка фичи используя git worktrees."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [parallel, dev, git]
    source: claude-code-config-pack
    origin: "command"
    argument_hint: "[название фичи]"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Параллельная разработка фичи используя git worktrees

# Параллельная разработка: текст, который пользователь написал вместе с вызовом навыка

Создай 3 параллельные имплементации используя git worktrees:

## Фаза 1: Подготовка
1. Создай worktrees для каждого подхода:
   - `git worktree add ../feature-performance feature/текст, который пользователь написал вместе с вызовом навыка-performance`
   - `git worktree add ../feature-ux feature/текст, который пользователь написал вместе с вызовом навыка-ux`
   - `git worktree add ../feature-maintainable feature/текст, который пользователь написал вместе с вызовом навыка-maintainable`

## Фаза 2: Параллельная разработка
2. Назначь специализированных агентов:
   - @software-architect: Подход A (performance-focused) в worktree feature-performance
   - @frontend-dev: Подход B (UX-focused) в worktree feature-ux
   - @backend-dev: Подход C (maintainability-focused) в worktree feature-maintainable

3. Каждый агент работает независимо в своём worktree

## Фаза 3: Сравнение и выбор
4. Сравни результаты всех подходов:
   - Производительность (benchmarks)
   - User experience (простота использования)
   - Поддерживаемость кода (читаемость, тестирование)

5. Выбери лучший подход или объедини лучшие части

## Фаза 4: Очистка
6. Удали неиспользованные worktrees:
   - `git worktree remove ../feature-performance`
   - `git worktree remove ../feature-ux`
   - `git worktree remove ../feature-maintainable`

Каждый agent сохраняет результаты в `docs/features/текст, который пользователь написал вместе с вызовом навыка/[agent-name].md`
