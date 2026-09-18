# -*- coding: utf-8 -*-
"""
Telegram connector for book-mentions-monitor.
Uses tg_client.py (Telethon) via subprocess — no direct import needed.
Search strategy:
  1. search-global "<query>" — global search across all Telegram chats
  2. search "<author>" — personal dialogs search
Dedup by (channel + first 60 chars of snippet).
"""

import sys
import io
import pathlib

# Ensure stdout/stderr handle Unicode correctly on Windows
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from lib.mention import make_mention

import subprocess
import re
import os
from pathlib import Path
from datetime import datetime
def _creds_path():
    """Необязательный файл вида KEY=VALUE с ключами API.

    Путь переопределяется переменной CLAUDE_CREDENTIALS_ENV. Файла может не быть
    вовсе — тогда ключи берутся из обычных переменных окружения.
    """
    import os as _os
    import pathlib as _pathlib
    return _pathlib.Path(_os.path.expanduser(
        _os.getenv("CLAUDE_CREDENTIALS_ENV", "$HERMES_HOME/.env")))

# tg_client.py лежит в самом конфиге — путь одинаков у любого, кто поставил пак.
# Раньше здесь был личный корень кода автора, которого у ученика нет.
TG_CLIENT = str(Path(__file__).resolve().parents[3] / "tools" / "tg_client.py")


def _parse_env(env_path: str) -> dict:
    """Parse KEY=VALUE env file into dict."""
    result = {}
    try:
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                result[k.strip()] = v.strip()
    except Exception:
        pass
    return result


def _run_tg(cmd_args: list, timeout: int = 60) -> str:
    """Run tg_client.py with given args, return stdout text."""
    env = os.environ.copy()
    full_cmd = [sys.executable, TG_CLIENT] + cmd_args
    try:
        proc = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=env,
        )
        return proc.stdout or ""
    except subprocess.TimeoutExpired:
        return ""
    except Exception:
        return ""


def _parse_search_output(output: str) -> list[dict]:
    """
    Parse tg_client search / search-global output.

    search format:
        [YYYY-MM-DD HH:MM] [Channel/Chat] Sender: text...

    search-global format (from cmd_search_global):
        Global search 'q': N results
          [datetime] peer_id.channel_id=XXXXX: text...
    or the newer format (from cmd_search):
        [YYYY-MM-DD HH:MM] [Chat Name] sender: text...
    """
    records = []

    # Patterns
    # Full pattern: [date] [chat_name] sender: text
    pat_full = re.compile(
        r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\]\s+\[([^\]]+)\]\s+(.*?)\s*:\s*(.*)",
        re.DOTALL,
    )
    # search-global compact: [datetime_obj_str] peer: text
    pat_global = re.compile(
        r"^\s+\[([^\]]+)\]\s+([\w.=\-]+)\s*:\s*(.*)",
        re.DOTALL,
    )

    lines = output.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        i += 1
        if not line or line.startswith("===") or line.startswith("Global search") or line.startswith("---"):
            continue

        # Try full format first
        m = pat_full.match(line)
        if m:
            date_str, chat_name, sender, text = m.group(1), m.group(2), m.group(3), m.group(4)
            # Accumulate continuation lines (blank-line-terminated)
            while i < len(lines):
                next_line = lines[i].rstrip()
                if next_line == "":
                    i += 1
                    break
                # If next line starts a new record, stop
                if pat_full.match(next_line) or pat_global.match(next_line):
                    break
                text += " " + next_line
                i += 1
            records.append({
                "date": date_str,
                "chat": chat_name,
                "sender": sender.strip(),
                "text": text.strip()[:800],
            })
            continue

        # Try global compact format
        m2 = pat_global.match(line)
        if m2:
            date_str, peer, text = m2.group(1), m2.group(2), m2.group(3)
            records.append({
                "date": str(date_str)[:16],
                "chat": peer,
                "sender": "",
                "text": text.strip()[:800],
            })
            continue

    return records


def _get_views_for_message(chat: str, msg_ids: list[int]) -> dict[int, dict]:
    """
    Try to get views/forwards/replies for a list of message IDs in a channel.
    Returns {msg_id: {views, forwards, replies}} or empty on failure.
    Only works for channels (not private chats).
    """
    if not msg_ids or not chat:
        return {}
    ids_str = ",".join(str(x) for x in msg_ids[:10])  # limit batch
    output = _run_tg(["msg-views", chat, ids_str], timeout=30)
    result = {}
    lines = [l.strip() for l in output.splitlines() if l.strip()]
    for idx, line in enumerate(lines):
        if idx >= len(msg_ids):
            break
        m = re.search(r"Views:\s*(\d+)", line)
        f = re.search(r"Forwards:\s*(\d+)", line)
        r = re.search(r"Replies:\s*(\d+)", line)
        result[msg_ids[idx]] = {
            "views": int(m.group(1)) if m else None,
            "forwards": int(f.group(1)) if f else None,
            "replies": int(r.group(1)) if r else None,
        }
    return result


def _is_relevant(text: str, book: dict) -> bool:
    """
    Check if text contains at least one anchor term.
    Exclude if any exclude term is found.
    Case-insensitive.
    """
    text_l = text.lower()
    # Check exclude list first
    for exc in book.get("exclude", []):
        if exc.lower() in text_l:
            return False
    # Must match at least one anchor or query keyword
    anchors = book.get("anchors", [])
    title_words = book.get("title", "").lower().split()[:4]
    all_positive = anchors + [book.get("title", ""), book.get("publisher", "")]
    all_positive += book.get("authors", [])
    for term in all_positive:
        if term and len(term) >= 4 and term.lower() in text_l:
            return True
    # Fall back to first two title words if anchors empty
    if len(title_words) >= 2:
        if title_words[0] in text_l and title_words[1] in text_l:
            return True
    return False


def collect(book: dict, creds: dict, limit: int = 50) -> list[dict]:
    """
    Main entry point. Collect Telegram mentions of the book.

    book keys: title, authors, publisher, anchors, exclude, queries
    creds: ключи (переменные окружения / необязательный файл KEY=VALUE)
    limit: max mentions to return
    """
    mentions = []
    seen = set()  # dedup key: (chat, snippet[:60])

    # Build queries list
    queries = list(book.get("queries", []))
    # Add author-based queries
    title = (book.get("title") or "").strip()
    for author in book.get("authors", []):
        parts = [p for p in author.split() if len(p) >= 4]
        last_name = parts[-1] if parts else ""   # фамилия чаще последняя
        if last_name:
            if title:
                queries.append(f"{last_name} {title}")
            queries.append(last_name)

    # Deduplicate queries while preserving order
    seen_q: set = set()
    unique_queries = []
    for q in queries:
        if q.lower() not in seen_q:
            seen_q.add(q.lower())
            unique_queries.append(q)

    per_query_limit = max(20, limit // max(len(unique_queries), 1))

    for query in unique_queries:
        if len(mentions) >= limit:
            break
        try:
            # 1. search-global (public channels + personal chats indexed by TG)
            output_global = _run_tg(
                ["search-global", query, "--limit", str(per_query_limit)],
                timeout=60,
            )
            records_global = _parse_search_output(output_global)

            # 2. search (all personal dialogs)
            output_local = _run_tg(
                ["search", query, "--limit", str(per_query_limit)],
                timeout=60,
            )
            records_local = _parse_search_output(output_local)

            all_records = records_global + records_local

            for rec in all_records:
                if len(mentions) >= limit:
                    break
                text = rec.get("text", "")
                if not text or not _is_relevant(text, book):
                    continue

                chat = rec.get("chat", "unknown")
                dedup_key = (chat.lower()[:40], text[:60].lower())
                if dedup_key in seen:
                    continue
                seen.add(dedup_key)

                # Build URL: telegram.me/<channel>/<msg_id> if channel looks like username
                url = ""
                chat_clean = chat.strip("@")
                # Try to extract a message_id if present in the raw output
                # search output doesn't include msg_id directly, so URL is best-effort
                if re.match(r"^[a-zA-Z0-9_]{3,}$", chat_clean):
                    url = f"https://t.me/{chat_clean}"

                author = rec.get("sender", "") or ""
                date_str = rec.get("date", "")

                mention = make_mention(
                    channel="telegram",
                    type="Соцсеть",
                    source=chat,
                    url=url,
                    title=f"Упоминание в {chat}",
                    snippet=text[:500],
                    date=date_str,
                    author=author,
                    lang="ru",
                    views=None,
                    likes=None,
                    reposts=None,
                    comments=None,
                    rating=None,
                    rating_count=None,
                    raw=rec,
                )
                mentions.append(mention)

        except Exception as e:
            # Don't fail — return whatever we collected so far
            sys.stderr.write(f"[telegram connector] error on query '{query}': {e}\n")
            continue

    return mentions


# ============================================================
# SMOKE TEST
# ============================================================
if __name__ == "__main__":
    # Load credentials
    env_path = str(_creds_path())
    creds = _parse_env(env_path)

    test_book = {
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

    print("Running Telegram smoke test on book: «Мастер и Маргарита»")
    print(f"tg_client path: {TG_CLIENT}")
    print()

    results = collect(test_book, creds, limit=50)

    print(f"=== Smoke test result: {len(results)} mentions ===")
    print()
    for i, m in enumerate(results[:2]):
        print(f"--- Example {i+1} ---")
        print(f"  channel   : {m['channel']}")
        print(f"  type      : {m['type']}")
        print(f"  source    : {m['source']}")
        print(f"  url       : {m['url']}")
        print(f"  title     : {m['title']}")
        print(f"  date      : {m['date']}")
        print(f"  author    : {m['author']}")
        print(f"  views     : {m['views']}")
        print(f"  snippet   : {m['snippet'][:120]}")
        print()
