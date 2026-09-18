---
name: outlook
description: "Рабочая почта компании (you@company.example) через."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [outlook, python, sql]
    source: claude-code-config-pack
    origin: "command"
    argument_hint: "[inbox | unread | search <запрос> | read <номер|EntryID> | folders | send --to … --subject …]"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Рабочая почта компании (you@company.example) через локальный Outlook по COM — пароль не нужен. Триггеры: «рабочая почта», «exchange». Личная → /gmail.

# /outlook

Рабочий путь — локальный Outlook через COM, скрипт
`~/.hermes/skills/integrations-and-apis/google-workspace/scripts/outlook_local.py`. Приложение стоит на
машине, учётная запись настроена, пароль не нужен. Проверено на рабочем ящике.

```bash
python ~/.hermes/skills/integrations-and-apis/google-workspace/scripts/outlook_local.py inbox --limit 10
python ~/.hermes/skills/integrations-and-apis/google-workspace/scripts/outlook_local.py unread
python ~/.hermes/skills/integrations-and-apis/google-workspace/scripts/outlook_local.py search "конференция" --days 60
python ~/.hermes/skills/integrations-and-apis/google-workspace/scripts/outlook_local.py search "лендинг" --field body
python ~/.hermes/skills/integrations-and-apis/google-workspace/scripts/outlook_local.py read 2 --full
python ~/.hermes/skills/integrations-and-apis/google-workspace/scripts/outlook_local.py folders
python ~/.hermes/skills/integrations-and-apis/google-workspace/scripts/outlook_local.py send --to кому@x.ru --subject "Тема" --body "Текст" --yes
```

Отправка требует `--yes` — без него письмо собирается и показывается, но не уходит.

За граблями (DASL-поиск, поиск по имени вместо адреса) — Skill `google-workspace`.

> **Сетевой путь `exchangelib` на mail.company.example НЕ РАБОТАЕТ — не пробовать.**
> Падает `RecursionError` в urllib3 ещё до авторизации, воспроизводится стабильно,
> пароль ни при чём. Здесь лежало 150 строк такого кода — удалены.
>
> Оттуда же был удалён пример поиска `items.Restrict("[Subject] like '%счёт%'")`:
> Outlook отвергает его («Условие неверно»). Рабочий вариант — DASL
> `@SQL="urn:schemas:httpmail:subject" like '%…%'`, он зашит в скрипт.
