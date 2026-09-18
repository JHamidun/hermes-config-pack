---
name: analyze
description: "Анализ codebase health с метриками и рекомендациями."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [analyze, python, sql]
    source: claude-code-config-pack
    origin: "command"
    argument_hint: "[путь к проекту или директории]"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Анализ codebase health с метриками и рекомендациями

# 📊 Analyze: текст, который пользователь написал вместе с вызовом навыка

Проанализируй **текст, который пользователь написал вместе с вызовом навыка** и дай recommendations

## Checks:

### Code Quality
- Lines of code
- Cyclomatic complexity
- Code duplication
- Documentation coverage
- Type hints coverage (Python)
- ESLint issues (JS/TS)

### Architecture
- File structure
- Dependencies
- Circular imports
- Unused files
- Missing tests

### Security
- Known vulnerabilities (npm audit, safety)
- Hardcoded secrets
- SQL injection risks
- XSS vulnerabilities

### Performance
- N+1 queries
- Inefficient loops
- Memory leaks potential
- Bundle size (frontend)

### Best Practices
- Error handling
- Logging strategy
- Configuration management
- Environment variables

## Output:
- Health score (0-100)
- Critical issues
- Recommendations
- Quick wins

**Запускай анализ! 📊**
