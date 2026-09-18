---
name: book-mentions-monitor
description: "Мониторинг упоминаний книг в СМИ и соцсетях без платной."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: marketing
    tags: [book, mentions, monitor, python, telegram, docx, xlsx, claude]
    source: claude-code-config-pack
---
## Когда применять

Мониторинг упоминаний книг в СМИ и соцсетях без платной системы мониторинга: тональность, МедиаИндекс, XLSX. Триггеры: «что пишут о книге», «упоминания автора».

# book-mentions-monitor

Свой медиамониторинг книг: воспроизводит логику и метрики промышленных систем
(объект → отчёт → 9 метрик → XLSX) из **открытых источников**, плюс добавляет
читательский слой — рецензии, отзывы магазинов, буктьюб, — которого у платных
систем обычно нет.

## Что понадобится

Ключей **не требует ни один обязательный шаг**: 4 канала из 11 работают вообще без ключей,
остальные деградируют молча и пропускаются. Полный набор:

| Переменная | Для чего | Цена |
|---|---|---|
| — | Google News RSS, LiveLib, Яндекс Suggest, RSSHub (публичный `rsshub.app`) | бесплатно |
| `SERPAPI_API_KEY` | СМИ, VK, Дзен, магазины через SerpAPI | free-план ~100 запросов/мес, дальше платно |
| `SCRAPECREATORS_API_KEY` | Instagram / TikTok / Reddit, YouTube-фолбэк | 1 кредит за запрос, платно |
| `YOUTUBE_API_KEY` (или `GOOGLE_API_KEY`) | YouTube Data API v3 | бесплатная квота 10 000 юнитов/сутки |
| `TELEGRAM_API_ID` + `TELEGRAM_API_HASH` | поиск по Telegram (Telethon) | бесплатно, my.telegram.org |
| `YANDEX_WORDSTAT_COOKIE` | спрос в Wordstat | бесплатно, но нужна кука залогиненного браузера (живёт ~2 недели) |
| `RSSHUB_BASE_URL` / `RSSHUB_SSH_HOST` | свой инстанс RSSHub вместо публичного | своё железо |

Ключи берутся из переменных окружения; можно положить их в файл `KEY=VALUE` и указать
его в `CLAUDE_CREDENTIALS_ENV` (по умолчанию ищется `$HERMES_HOME/.env`,
шаблон — `~/.hermes/ccpack/templates/$HERMES_HOME/.env.example`).

LLM-слой (тональность и дизамбигуация) идёт **по твоей подписке Claude Code**, отдельных
трат по API не создаёт — см. раздел ниже.

## Когда использовать
- Регулярный мониторинг упоминаний книги/автора в СМИ и соцсетях.
- Разовый отчёт «что пишут о книге» в привычной для PR-отдела структуре (XLSX).
- Репутационный сторож — алерт на негатив.

## Быстрый старт

```bash
cd ~/.hermes/skills/marketing/book-mentions-monitor/scripts
# 1. Скопируй конфиг книги и заполни (название, авторы, якоря, минус-слова)
#    config/ лежит УРОВНЕМ ВЫШЕ scripts/ — путь с ../ нужен и источнику, и цели
cp ../config/book.example.yaml ../config/mybook.yaml

# 2a. Автономный прогон на правилах (без LLM) — быстрый baseline:
# ОБЯЗАТЕЛЬНО: убрать классификацию прошлого сбора, иначе она приедет в отчёт (см. ниже)
mv ../out/classified.json ../out/classified.prev.json 2>/dev/null || true
python monitor.py run ../config/mybook.yaml --llm none

# 2b. С LLM-классификацией по подписке (точная дизамбигуация омонимов):
python monitor.py collect ../config/mybook.yaml          # собрать + выгрузить out/to_classify.json
#   → затем в ЭТОЙ Claude-сессии (см. ниже «LLM-слой») создать out/classified.json
python monitor.py finalize ../config/mybook.yaml         # построить XLSX + дайджест
```

Результат: `../out/<книга>.xlsx` (листы как в промышленной выгрузке) + `../out/digest.md` — то есть
`~/.hermes/skills/marketing/book-mentions-monitor/out/`, каталог рядом со `scripts/`, а не внутри него.

### ⚠️ `--llm none` НЕ игнорирует старый `out/classified.json`

Флаг до финализации не доходит: `run --llm none` зовёт `finalize(book)` без параметра
(`monitor.py:181-182`), а `finalize` безусловно подхватывает `out/classified.json`, если файл
есть (`:131-132`), и печатает «Применена LLM-классификация из classified.json». Прогон, заказанный
«на правилах», молча получает чужую классификацию.

Хуже механика склейки: `:135-136` сшивает по ПОРЯДКОВОМУ НОМЕРУ в свежем списке
(`for i, m in enumerate(rel)`) против `id` из старого файла. `id` — это позиция в том сборе,
который породил `to_classify.json`; в новом сборе состав и порядок другие, поэтому
тональность/роль/жанр/`is_target_book` садятся на ЧУЖИЕ упоминания. Отчёт выходит зелёный,
с заполненными колонками — и неверный, по XLSX это не отличить.

Правило: `out/classified.json` действителен ровно для того `out/mentions.json`, вместе с которым
он собран. Перед любым новым сбором — унеси его в сторону (`mv … classified.prev.json`), а в LLM-режиме
делай `collect` → классификацию → `finalize` без промежуточных пересборов.
Каталог `out/` — рабочая директория скрипта, а не хранилище примеров: всё в нём перезаписывается
следующим прогоном.

## LLM-слой (тональность/роль/жанр) — ПО ПОДПИСКЕ

⚠️ **Критично:** классификацию делают **Task-субагенты Claude Code в интерактивной сессии** — это subsidized Claude Max, 0 API-трат. НЕ запускать через `claude -p` / Agent SDK (с 15.06.2026 — отдельный платный пул). Проверь: `ANTHROPIC_API_KEY` НЕ должен быть в env.

Когда пользователь просит точный отчёт, после `collect` сделай:
1. Прочитай `out/to_classify.json` (батч кандидатов).
2. Запусти **Task `model: opus`** с промптом `scripts/classify/disambiguate_prompt.md` (подставь title/authors/anchors/exclude + items) → получи `is_target_book`/`role`/`genre`/`cite`. Opus критичен — отсекает омонимы.
3. Запусти **Task `model: haiku`** с промптом `scripts/classify/tone_prompt.md` на упоминаниях с `is_target_book=true` → `tone`.
4. Слей в массив `[{id, is_target_book, role, genre, cite, tone}]` → запиши `out/classified.json`.
5. `python monitor.py finalize ../config/mybook.yaml`.

Большие батчи (100+) — дроби и/или гоняй через `Workflow` (pipeline, opus на дизамбигуацию, haiku на тональность).

## Каналы (scripts/connectors/)
| Файл | Канал | Метод | Free |
|---|---|---|---|
| `googlenews.py` | Google News RSS | RSS, кавычки+якоря | а |
| `serpapi_connector.py` | СМИ | SerpAPI news/web/yandex | б |
| `vk.py` ⭐ | VK | SerpAPI `site:vk.com` (без токена) | а |
| `dzen.py` | Дзен | SerpAPI `site:dzen.ru` | а |
| `telegram.py` | Telegram | tg_client search-global + msg-views | а |
| `rsshub_tg.py` | TG-каналы | RSSHub (публичный или свой) | а |
| `livelib.py` ⭐ | LiveLib | рейтинг/рецензии (cp1251 JSON-LD) | а |
| `marketplace_stores.py` | магазины | SerpAPI site: (отзывы/цена) | а |
| `youtube.py` | YouTube | YouTube Data API + ScrapeCreators | б |
| `scrapecreators.py` | IG/TikTok/Reddit | ScrapeCreators API | б |
| `wordstat.py` | спрос | Wordstat internal + Suggest | б |

Включить/выключить — список `channels:` в конфиге книги.

## Метрики (набор промышленных систем мониторинга)
- **Количество** · **Оригиналы/Перепечатки** (дедуп лемма-шинглами) · **Тональность** (Поз/Нейтр/Нег) · **Роль** (Главная/Эпизодическая) · **Жанр** (Новость/Аналитика/Интервью/Анонс) · **Цитирование** · **Охват** (Tranco/Cloudflare + соц-просмотры) · **МедиаИндекс** = заметность (формула в `references/metrics.md`) · **Вовлечённость** (views/likes/reposts).
- Сверх промышленного набора: **читательские рейтинги/рецензии** (LiveLib), **отзывы магазинов**, **буктьюб**, **спрос Wordstat**.

## Структура
```
config/   book.example.yaml · media-registry.json · stopwords-ru.txt
scripts/
  monitor.py              оркестратор (collect/finalize/run)
  lib/    mention.py (контракт) · enrich.py · reach.py · dedup.py · report_xlsx.py · report_digest.py
          content_scrubber.py · readability_ru.py · wordstat_fetch.py — ШИМЫ: код живёт
          в skills/seo-machine-ru/scripts/, здесь только точка импорта (правь канон, не шим)
          keyword_analyzer_ru.py — НЕ шим, а копия, и она УЖЕ разошлась с каноном:
          в seo-machine-ru 17.08 добавили фолбэк на pymorphy2, здесь его нет. Канон —
          skills/seo-machine-ru/scripts/keyword_analyzer_ru.py: правь там, потом сверяй
          (diff обеих) и переноси сюда; расхождение молчит и меняет лемматизацию
out/      рабочая директория скрипта (mentions/to_classify/classified/xlsx/digest),
          НЕ примеры: каждый прогон перезаписывает, classified.json привязан к своему сбору
  connectors/  11 коннекторов (контракт: collect(book, creds, limit) -> list[mention])
  classify/    disambiguate_prompt.md (opus) · tone_prompt.md (haiku)
references/  channels.md · metrics.md · medialogia-structure.md · disambiguation.md · llm-billing.md · cookbook.md
```

## Зависимости
`pip install pyyaml openpyxl pymorphy3 pymorphy3-dicts-ru requests python-docx` (pymorphy3 — лемматизация, НЕ pymorphy2: на Python 3.13 мёртв).

## Регулярный мониторинг
`/loop` в интерактивной сессии (LLM по подписке) или `/schedule`. Инкрементально — `period.mode: incremental` (только новое с прошлого прогона). Подробности и рецепты — `references/cookbook.md`.

## Главный урок (см. references/disambiguation.md)
Названия книг часто **омонимичны**: у художественной прозы — экранизация, у бизнес-книги — одноимённый курс, у научпопа — государственный проект с почти тем же названием. Защита двухслойная: (1) запрос = точная фраза в кавычках + якоря; (2) opus-агент `is_target_book` отсекает омонимы. Без этого precision проваливается.
