---
name: deploy
description: "Universal deployment command для различных environments."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [deploy, docker, image]
    source: claude-code-config-pack
    origin: "command"
    argument_hint: "[staging / production / local]"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Universal deployment command для различных environments

# 🚢 Deploy: текст, который пользователь написал вместе с вызовом навыка

Deploy to **текст, который пользователь написал вместе с вызовом навыка** environment

## Process:

### Pre-Deploy Checks
- [ ] Tests passing
- [ ] Linting clean
- [ ] No console.log / debugger
- [ ] Env variables configured
- [ ] Database migrations ready
- [ ] Backup created

### Deployment Steps
1. Build application
2. Run tests
3. Create Docker image (if applicable)
4. Push to registry
5. Deploy to environment
6. Run migrations
7. Health check
8. Smoke tests

### Post-Deploy
- Verify deployment
- Monitor logs
- Check metrics
- Notify team

**Environment-specific:**
- **local**: docker-compose up
- **staging**: Deploy to staging server, run E2E tests
- **production**: Blue-green deployment, gradual rollout

**Deploying! 🚢**