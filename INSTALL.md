# Установка

Нужны: Hermes Agent 0.21+, Python 3.11+, node (только для хука-гарда).

## 1. Поставить пак

```bash
python install.py            # посмотреть план сначала: --dry-run
```

Кладёт две вещи и больше ничего не трогает:

* `~/.hermes/ccpack/` — сам пак: навыки, роли, `tools/`, `scripts/`, `config/`,
  `rules/`, `templates/`;
* `<дом Hermes>/plugins/ccpack/` — тонкий плагин на два файла.

Дом Hermes — это `$HERMES_HOME`, иначе `%LOCALAPPDATA%\hermes` на Windows и
`~/.hermes` на остальных. Повторный запуск докладывает недостающее и **не трогает
то, что уже есть**; `--repair` перезаписывает файлы пака этой версией.

Windows, если PowerShell ругается на политику запуска:

```powershell
powershell -ExecutionPolicy Bypass -File .\install-hermes.ps1
```

## 2. Включить

```bash
hermes plugins enable ccpack
hermes ccpack install      # подключает skills/ к скилл-сканеру
hermes ccpack doctor       # python, пути, подключение — по пунктам
```

Плагины у Hermes по умолчанию выключены: пока не включишь, ничего не появится.
`hermes ccpack install` дописывает `skills.external_dirs` в `config.yaml` — это и
есть шаг, после которого сотни навыков становятся слэш-командами. В живой сессии
после этого — `/reload-skills`, иначе перезапуск.

## 3. Доделать руками

Три вещи установщик сознательно не делает: они про безопасность, деньги и твой
голос.

**Гард и MCP.** В `~/.hermes/ccpack/config.snippet.yaml` лежит готовый кусок для
`config.yaml`: хук, блокирующий деструктивные команды (тот же, что в исходном
паке), и закомментированные MCP-серверы. Переноси осознанно.

**Личность.** `~/.hermes/ccpack/SOUL.example.md` → `<дом Hermes>/SOUL.md`,
переписать под себя. Это слот №1 системного промпта.

**Ключи.** В `<дом Hermes>/.env`, образец — `~/.hermes/ccpack/templates/`.
Без ключей работает всё, что не ходит наружу.

Плюс `~/.hermes/ccpack/AGENTS.md` — файл инструкций проекта. Скопируй его в
репозиторий, с которым работаешь, или оставь как справку.

## Проверить, что живое

```bash
hermes ccpack doctor
hermes ccpack status
```

В сессии: `/ccpack status` — то же самое, `/ccpack find телеграм` — найти навык
по слову, `/ccpack roles` — список ролей для `delegate_task`.

## Обновление

```bash
python install.py --repair
hermes ccpack doctor
```

`--repair` перезаписывает файлы пака, но не трогает `config.yaml`, `SOUL.md`,
`.env` и твои собственные навыки.

## Удаление

```bash
hermes ccpack uninstall        # убирает skills/ из skills.external_dirs
hermes plugins disable ccpack
rm -rf ~/.hermes/ccpack "<дом Hermes>/plugins/ccpack"
```

## Если что-то не так

**Слэш-команд нет.** Не сделан шаг 2 (`hermes ccpack install`) или сессия старше
изменения — `/reload-skills`.

**`hermes ccpack` не существует.** Плагин не включён: `hermes plugins enable ccpack`.

**Навык ругается, что нет инструмента MCP.** Сервер не объявлен в `config.yaml`
→ `mcp_servers`. Список того, что чему нужно, — в `~/.hermes/ccpack/config/`.

**Скрипт пака не находит ключ.** Ключи читаются из `<дом Hermes>/.env`. На
Windows это `%LOCALAPPDATA%\hermes\.env`, а не `~/.hermes/.env` — это два разных
места, и второе Hermes не читает.

**Совпали имена навыков.** `hermes ccpack install` печатает список имён, которые
уже есть у Hermes своими. Кто победит — решает порядок сканирования; переименуй
проигравшего в `~/.hermes/ccpack/skills/<категория>/<имя>/SKILL.md` (поле `name`
во фронтматтере, каталог можно не трогать).
