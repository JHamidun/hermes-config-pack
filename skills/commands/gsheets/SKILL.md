---
name: gsheets
description: "Google Sheets (gsheets_client.py)."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [gsheets, python]
    source: claude-code-config-pack
    origin: "command"
    argument_hint: "[info <id> | read <id> [--tab лист] | write <id> --range … --values … | search <запрос>]"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Google Sheets (gsheets_client.py): прочитать/записать таблицу, найти, листы. Триггеры: «гугл таблица», «запиши в таблицу». Хаб → skill google-workspace.

# /gsheets

Рабочий код — в навыке `google-workspace`, скрипт
`~/.hermes/skills/integrations-and-apis/google-workspace/scripts/gsheets_client.py`.

```bash
python ~/.hermes/skills/integrations-and-apis/google-workspace/scripts/gsheets_client.py info <id_или_ссылка>
python ~/.hermes/skills/integrations-and-apis/google-workspace/scripts/gsheets_client.py read <id> --tab "Сводная" --limit 20
python ~/.hermes/skills/integrations-and-apis/google-workspace/scripts/gsheets_client.py search "оплаты"
python ~/.hermes/skills/integrations-and-apis/google-workspace/scripts/gsheets_client.py write <id> --range "'Лист1'!A1" --values '[["a","b"]]' --yes
```

Два пути доступа, оба рабочие: OAuth (`~/.hermes/ccpack/google_oauth_token.json`, скоуп
`drive` — Sheets API на нём проверен) и служебный ключ через флаг `--sa` — для
таблиц, расшаренных на робота, а не на человека. Запись требует `--yes`.

За подробностями — Skill `google-workspace`.

> Раньше здесь лежал inline-код (google-api + gspread). Оба пути были рабочими, но
> непроверяемыми: тела команд линтер не покрывает. Код перенесён в скрипт навыка,
> gspread-путь заменён на тот же Sheets API со служебным ключом — одна кодовая
> ветка вместо двух.
