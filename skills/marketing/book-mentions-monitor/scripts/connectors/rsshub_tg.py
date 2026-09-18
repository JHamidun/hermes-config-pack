# -*- coding: utf-8 -*-
"""
Коннектор RSSHub — Telegram-каналы издательств.

Стратегия:
  - Дёргаем RSSHub: по умолчанию публичный https://rsshub.app (ключей не нужно,
    но он капризен под нагрузкой). Свой инстанс — переменная RSSHUB_BASE_URL;
    если он поднят на сервере и порт наружу закрыт, задай RSSHUB_SSH_HOST —
    запрос уйдёт через `ssh <host> curl`.
  - /telegram/channel/<slug> возвращает ~5-12 последних постов в RSS 2.0.
  - Фильтрация по book["anchors"] / book["queries"] — на стороне клиента,
    т.к. RSSHub для Telegram не поддерживает серверный searchQuery.
  - Каждое совпадение → make_mention(..., channel="rsshub", type="Соцсеть").
"""

import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import html
import re
import subprocess
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Optional

from lib.mention import make_mention
def _creds_path():
    """Необязательный файл вида KEY=VALUE с ключами API.

    Путь переопределяется переменной CLAUDE_CREDENTIALS_ENV. Файла может не быть
    вовсе — тогда ключи берутся из обычных переменных окружения.
    """
    import os as _os
    import pathlib as _pathlib
    return _pathlib.Path(_os.path.expanduser(
        _os.getenv("CLAUDE_CREDENTIALS_ENV", "$HERMES_HOME/.env")))

# ---------- Каналы по умолчанию ----------
# Пусто намеренно: сюда идут Telegram-каналы ТВОЕГО издательства и автора.
# Задаются в конфиге книги (`telegram_channels:`), не в коде.
DEFAULT_CHANNELS = []

# ---------- Константы ----------
import os as _os

# Публичный инстанс по умолчанию; свой — RSSHUB_BASE_URL (напр. http://127.0.0.1:1200).
RSSHUB_BASE = _os.getenv("RSSHUB_BASE_URL", "https://rsshub.app").rstrip("/")
# Если свой RSSHub закрыт от интернета — имя хоста из ~/.ssh/config, запрос пойдёт по ssh.
SSH_HOST = _os.getenv("RSSHUB_SSH_HOST", "")
SSH_TIMEOUT = 45   # секунд на один curl запрос


# ---------- Утилиты ----------
def _unescape(text: str) -> str:
    """HTML-декод + убрать теги."""
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _parse_date(rfc2822: str) -> str:
    """RFC 2822 → ISO 8601 (UTC). На ошибку — возвращаем оригинал."""
    if not rfc2822:
        return ""
    try:
        # Python 3.9+: email.utils.parsedate_to_datetime
        import email.utils
        dt = email.utils.parsedate_to_datetime(rfc2822)
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return rfc2822.strip()


def _fetch_channel_rss(channel: str) -> Optional[str]:
    """
    Получаем RSS-XML через SSH+curl.
    Возвращает строку XML или None при ошибке.
    """
    url = f"{RSSHUB_BASE}/telegram/channel/{channel}"
    if not SSH_HOST:
        # Прямой HTTP: публичный rsshub.app или свой доступный инстанс.
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={"User-Agent": "book-mentions-monitor"})
            with urllib.request.urlopen(req, timeout=SSH_TIMEOUT) as resp:
                text = resp.read().decode("utf-8", errors="replace")
        except Exception:
            return None
        if not text.strip() or "<?xml" not in text[:200]:
            return None
        return text
    cmd = [
        "ssh", "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=10",
        SSH_HOST,
        f"curl -sS --max-time {SSH_TIMEOUT} {url!r}",
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            timeout=SSH_TIMEOUT + 15,
        )
        if result.returncode != 0:
            return None
        text = result.stdout
        if not text.strip() or "<?xml" not in text[:200]:
            return None
        return text
    except Exception:
        return None


def _parse_rss(xml_text: str, channel_slug: str) -> list[dict]:
    """
    Парсим RSS-документ, возвращаем список сырых dict с полями:
    title, description, link, pubDate.
    """
    # ElementTree не любит <?xml ...?> с encoding != utf-8 в str,
    # поэтому чистим processing instruction.
    clean = re.sub(r"<\?xml[^?]*\?>", "", xml_text, count=1).strip()
    try:
        root = ET.fromstring(clean)
    except ET.ParseError:
        # Пробуем с bytes
        try:
            root = ET.fromstring(xml_text.encode("utf-8"))
        except Exception:
            return []

    items = []
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    channel_el = root.find("channel")
    if channel_el is None:
        return []

    for item in channel_el.findall("item"):
        def text(tag):
            el = item.find(tag)
            return (el.text or "") if el is not None else ""

        items.append({
            "title": _unescape(text("title")),
            "description": _unescape(text("description")),
            "link": text("link").strip(),
            "pubDate": _parse_date(text("pubDate")),
            "channel_slug": channel_slug,
        })
    return items


def _build_keywords(book: dict) -> list[str]:
    """
    Строим список ключевых слов для client-side фильтрации.
    Порядок: title (без стоп-слов), anchors, первые слова queries.
    Всё в нижний регистр.
    """
    keywords: list[str] = []

    # Главное: anchors
    for a in book.get("anchors", []):
        if a.strip():
            keywords.append(a.strip().lower())

    # Название книги (короткое, без кавычек)
    title = book.get("title", "").strip()
    if title and len(title) > 4:
        keywords.append(title.lower())

    # Авторы
    for author in book.get("authors", []):
        if author.strip():
            # берём только фамилию (первое слово)
            surname = author.strip().split()[0].lower()
            if len(surname) > 3:
                keywords.append(surname)

    # queries: берём ключевые части в кавычках или полностью
    for q in book.get("queries", []):
        q = q.strip().strip('"').lower()
        if q and q not in keywords:
            keywords.append(q)

    return list(dict.fromkeys(keywords))  # уникальные, порядок сохранён


def _build_exclude(book: dict) -> list[str]:
    return [e.strip().lower() for e in book.get("exclude", []) if e.strip()]


def _matches(item: dict, keywords: list[str], exclude: list[str]) -> bool:
    """True если пост релевантен книге."""
    haystack = (item["title"] + " " + item["description"]).lower()

    # Исключения — сначала
    for ex in exclude:
        if ex in haystack:
            return False

    # Хотя бы одно ключевое слово
    for kw in keywords:
        if kw in haystack:
            return True

    return False


def _item_to_mention(item: dict) -> dict:
    """Конвертируем отфильтрованный RSS-item → make_mention."""
    channel_slug = item["channel_slug"]
    # Название канала для source
    # Человекочитаемые имена каналов (slug -> имя), если хочешь красивый source
    # вместо @slug. Заполняется под свои каналы, пусто — используется @slug.
    channel_names: dict = {}
    source = channel_names.get(channel_slug, f"@{channel_slug}")

    # snippet = первые 400 символов description
    snippet = item["description"][:400]

    return make_mention(
        channel="rsshub",
        type="Соцсеть",
        source=source,
        url=item["link"],
        title=item["title"],
        snippet=snippet,
        date=item["pubDate"],
        author=source,
        lang="ru",
        views=None,
        likes=None,
        reposts=None,
        comments=None,
        rating=None,
        rating_count=None,
        raw=item,
    )


# ---------- Публичный API ----------
def collect(book: dict, creds: dict, limit: int = 50) -> list[dict]:
    """
    Обходит каналы из book["telegram_channels"] через RSSHub.
    Фильтрует посты по book["anchors"] / book["queries"] / book["title"].
    Возвращает list[dict] в формате make_mention().
    """
    keywords = _build_keywords(book)
    exclude = _build_exclude(book)

    # Дополнительные каналы можно передать через creds["RSSHUB_TG_CHANNELS"]
    channels = list(book.get("telegram_channels") or DEFAULT_CHANNELS)
    extra = (creds or {}).get("RSSHUB_TG_CHANNELS", "")
    if extra:
        for slug in extra.split(","):
            slug = slug.strip()
            if slug and slug not in channels:
                channels.append(slug)

    results: list[dict] = []

    for slug in channels:
        if len(results) >= limit:
            break
        try:
            xml_text = _fetch_channel_rss(slug)
            if not xml_text:
                continue
            items = _parse_rss(xml_text, slug)
            for item in items:
                if len(results) >= limit:
                    break
                if _matches(item, keywords, exclude):
                    results.append(_item_to_mention(item))
        except Exception:
            # Не падаем на одном канале — идём дальше
            continue

    return results


# ---------- Smoke-тест ----------
if __name__ == "__main__":
    import os
    # Windows: переключаем stdout/stderr на UTF-8, чтобы не падать на Кириллице и эмодзи
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    # --- Читаем creds из master.env ---
    creds: dict = {}
    env_path = _creds_path()
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, _, v = line.partition("=")
                creds[k.strip()] = v.strip()

    # --- Тест-книга ---
    book = {
        "title": "Мастер и Маргарита",
        "authors": ["Михаил Булгаков"],
        "publisher": "",
        "anchors": ["Булгаков", "Воланд"],
        "exclude": [
            "сериал",
            "спектакль",
            "экранизация",
            "опера",
        ],
        "queries": [
            '"Мастер и Маргарита"',
            "Булгаков Мастер и Маргарита издание",
        ],
    }

    print("=== rsshub_tg smoke-test ===")
    print(f"Каналы: {DEFAULT_CHANNELS}")
    print(f"Ключевые слова: {_build_keywords(book)}")
    print()

    mentions = collect(book, creds, limit=50)

    print(f"Упоминаний найдено: {len(mentions)}")
    print()

    for m in mentions[:2]:
        print("--- Пример ---")
        print(f"  channel : {m['channel']}")
        print(f"  source  : {m['source']}")
        print(f"  type    : {m['type']}")
        print(f"  url     : {m['url']}")
        print(f"  title   : {m['title'][:80]}")
        print(f"  snippet : {m['snippet'][:120]}")
        print(f"  date    : {m['date']}")
        print()

    if not mentions:
        print("(0 упоминаний — книга свежая или ещё не попала в ленту каналов)")
        print("Smoke-тест пройден: каналы опрошены без ошибок.")
