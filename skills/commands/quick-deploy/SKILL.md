---
name: quick-deploy
description: "Быстрый деплой с проверкой тестов и линтеров."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [quick, deploy, docker, python, git]
    source: claude-code-config-pack
    origin: "command"
    argument_hint: "[environment: staging/production]"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Быстрый деплой с проверкой тестов и линтеров

# Быстрый деплой в текст, который пользователь написал вместе с вызовом навыка

## Pre-deploy Checks

### 1. Проверка статуса Git
```bash
git status
git diff --stat
```
Убедись, что нет uncommitted изменений.

### 2. Запуск тестов
```bash
# Backend tests
pytest tests/ -v --cov

# Frontend tests
npm test

# Integration tests
npm run test:e2e
```

Все тесты должны пройти ✅

### 3. Lint и форматирование
```bash
# Python
black . --check
pylint src/

# JavaScript/TypeScript
npm run lint
npm run format:check
```

### 4. Build проверка
```bash
# Backend
python setup.py build

# Frontend
npm run build
```

Build должен пройти без ошибок.

## Deploy

### Staging
```bash
git push origin main
# Trigger staging deploy
```

### Production
```bash
# Создай release tag
git tag -a v$(date +%Y.%m.%d) -m "Release $(date +%Y-%m-%d)"
git push origin --tags

# Deploy to production
# [Команда деплоя зависит от твоей инфраструктуры]
```

## Post-deploy Monitoring

### Health checks
```bash
curl https://текст, который пользователь написал вместе с вызовом навыка.yourapp.com/health
```

### Проверь логи
```bash
# Если используешь k8s
kubectl logs -f deployment/app -n текст, который пользователь написал вместе с вызовом навыка

# Если используешь Docker
docker logs -f app-текст, который пользователь написал вместе с вызовом навыка
```

### Smoke tests
- Открой главную страницу
- Проверь key features
- Проверь аналитику (PostHog/другое)

## Rollback (если что-то пошло не так)

```bash
# Откат к предыдущей версии
git revert HEAD
git push

# Или
kubectl rollout undo deployment/app -n текст, который пользователь написал вместе с вызовом навыка
```

---

**Чеклист готовности к деплою:**
- [ ] Все тесты проходят
- [ ] Линтеры без ошибок
- [ ] Build успешен
- [ ] Code review прошёл
- [ ] Changelog обновлён
- [ ] Команда уведомлена
