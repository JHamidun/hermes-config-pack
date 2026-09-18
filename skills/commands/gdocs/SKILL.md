---
name: gdocs
description: "Google Docs (gdocs_client.py)."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [gdocs, python]
    source: claude-code-config-pack
    origin: "command"
    argument_hint: "[read <id|ссылка> | search <запрос> | append <id> --text <текст>]"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Google Docs (gdocs_client.py): прочитать документ, найти по названию, дописать. Триггеры: «гугл документ», «саммари документа». Хаб → skill google-workspace.

# /gdocs

Рабочий код — в навыке `google-workspace`, скрипт
`~/.hermes/skills/integrations-and-apis/google-workspace/scripts/gdocs_client.py`.

```bash
python ~/.hermes/skills/integrations-and-apis/google-workspace/scripts/gdocs_client.py read <id_или_ссылка>
python ~/.hermes/skills/integrations-and-apis/google-workspace/scripts/gdocs_client.py read <id> --limit 2000
python ~/.hermes/skills/integrations-and-apis/google-workspace/scripts/gdocs_client.py search "резюме встреч"
python ~/.hermes/skills/integrations-and-apis/google-workspace/scripts/gdocs_client.py append <id> --text "строка" --yes
```

Принимает ссылку целиком. Права берутся из `~/.hermes/ccpack/google_oauth_token.json`:
у токена единственный скоуп `drive`, и Docs API на нём работает — проверено.

За подробностями (таблицы в документах, разграничение токенов, что делать при 404)
— Skill `google-workspace`.

> Раньше здесь лежал inline-код работы с Docs API. Он был рабочим, но не проверялся
> ничем: тела команд линтер связности не покрывает. Код перенесён в скрипт навыка и
> прогнан на живом документе.
