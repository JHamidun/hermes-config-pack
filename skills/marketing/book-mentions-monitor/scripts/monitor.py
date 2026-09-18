# -*- coding: utf-8 -*-
"""Оркестратор book-mentions-monitor.
Фазы:
  collect   — грузит коннекторы, собирает упоминания, дедуп, обогащение, охват, перепечатки.
              Сохраняет mentions.json + to_classify.json (батч для LLM). Применяет правила-fallback.
  finalize  — читает classified.json (заполненный Claude-субагентами opus/haiku), проставляет
              _is_target/_role/_genre/_tone, считает МедиаИндекс, строит XLSX + дайджест.
  run       — collect + (если --llm none) сразу finalize на правилах.

LLM-слой (--llm files): Claude в интерактивной сессии читает to_classify.json, гоняет Task opus
(дизамбигуация) + haiku (тональность) ПО ПОДПИСКЕ, пишет classified.json, затем `finalize`.
"""
# UTF-8 на выход. Консоль Windows по умолчанию cp1251/cp866/cp1252, и первый же
# не-ASCII символ (кириллица, →, ✓, эмодзи) валит процесс UnicodeEncodeError —
# нередко на --help, то есть ДО любой полезной работы. errors="replace" оставляет
# вывод читаемым, если терминал всё же не UTF-8.
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse, importlib.util, json, pathlib, re, sys, traceback

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from lib.mention import dedupe, make_mention  # noqa
from lib import enrich as E
from lib import reach as R
from lib import dedup as D
from lib import report_xlsx, report_digest


def _creds_path():
    """Необязательный файл вида KEY=VALUE с ключами API.

    Путь переопределяется переменной CLAUDE_CREDENTIALS_ENV. Файла может не быть
    вовсе — тогда ключи берутся из обычных переменных окружения.
    """
    import os as _os
    import pathlib as _pathlib
    return _pathlib.Path(_os.path.expanduser(
        _os.getenv("CLAUDE_CREDENTIALS_ENV", "$HERMES_HOME/.env")))

CRED = _creds_path()
CONN_DIR = ROOT / "connectors"
OUT = ROOT.parent / "out"   # каталог создаётся в ensure_out(), не при импорте


def ensure_out():
    """Каталог отчётов. Создаём по требованию: импорт модуля не должен
    оставлять пустой out/ в чужом дереве."""
    OUT.mkdir(parents=True, exist_ok=True)
    return OUT


def load_creds():
    """Ключи API: сначала необязательный файл KEY=VALUE, поверх — переменные окружения.

    Файла может не быть вовсе. Коннекторы, которым не хватило ключа, сами скажут,
    какая переменная нужна, и пропустятся — прогон не падает целиком.
    """
    d = {}
    if CRED.exists():
        for ln in CRED.read_text(encoding="utf-8", errors="ignore").splitlines():
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1)
                d[k.strip()] = v.strip().strip('"').strip("'")
    import os as _os
    for k in ("SERPAPI_API_KEY", "SCRAPECREATORS_API_KEY", "YOUTUBE_API_KEY",
              "YANDEX_WORDSTAT_COOKIE", "RSSHUB_BASE_URL", "RSSHUB_SSH_HOST",
              "TELEGRAM_API_ID", "TELEGRAM_API_HASH", "VK_TOKEN"):
        if _os.getenv(k):
            d[k] = _os.environ[k]
    return d


def load_book(path):
    try:
        import yaml
        return yaml.safe_load(pathlib.Path(path).read_text(encoding="utf-8"))
    except ImportError:
        raise SystemExit("Нужен pyyaml: pip install pyyaml")


def _norm_stem(s):
    return re.sub(r"^(media|social|readers|video|demand)_", "", s)


def load_connectors(book):
    wanted = book.get("channels") or []
    wanted_norm = {_norm_stem(w) for w in wanted}
    out = []
    for f in sorted(CONN_DIR.glob("*.py")):
        if f.stem.startswith("_"):
            continue
        if wanted_norm and _norm_stem(f.stem) not in wanted_norm and f.stem not in wanted:
            continue
        try:
            spec = importlib.util.spec_from_file_location(f.stem, f)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "collect"):
                out.append((f.stem, mod.collect))
        except Exception as e:
            print(f"  [skip] {f.stem}: {type(e).__name__}: {str(e)[:80]}")
    return out


# ---------- эвристики роль/жанр для --llm none ----------
def role_rule(m, book):
    tt = (m.get("title", "") or "").lower()
    title = book.get("title", "").lower()
    if title in tt or any(a.lower() in tt for a in book.get("authors", []) + book.get("anchors", [])):
        return "Главная"
    return "Эпизодическая"


def genre_rule(m):
    t = (m.get("title", "") + " " + m.get("snippet", "")).lower()
    if any(k in t for k in ["интервью", "рассказала", "поговорили", "призналась"]):
        return "Интервью"
    if any(k in t for k in ["презентация", "встреча с автор", "библионочь", "анонс", "пройдёт", "состоится"]):
        return "Анонс"
    if any(k in t for k in ["топ-100", "топ 100", "подборк", "5 книг", "10 книг", "обзор", "рейтинг", "новых книг"]):
        return "Аналитика"
    return "Новость"


def collect(book):
    creds = load_creds()
    conns = load_connectors(book)
    print(f"Коннекторы: {[c[0] for c in conns]}")
    mentions = []
    for name, fn in conns:
        try:
            res = fn(book, creds, 50) or []
            print(f"  {name}: {len(res)}")
            mentions += res
        except Exception:
            print(f"  {name}: ERROR\n{traceback.format_exc().splitlines()[-1]}")
    # дедуп → обогащение → охват → перепечатки
    mentions = dedupe(mentions)
    reg = E.load_registry()
    E.enrich_all(mentions, book, reg)
    R.enrich_reach(mentions, creds)
    rel = [m for m in mentions if m.get("_relevant")]
    D.mark_reprints(rel)
    # правила-fallback (для --llm none и как дефолт до LLM)
    for m in rel:
        m["_role"] = role_rule(m, book)
        m["_genre"] = genre_rule(m)
        m["_tone"] = E.tone_rule(m)
        m["_is_target"] = True  # relevance прошёл; opus уточнит в LLM-режиме
        m["_mi"] = E.media_index(m, 1 if m.get("_reprint_of") else 0)
    ensure_out()
    (OUT / "mentions.json").write_text(json.dumps(mentions, ensure_ascii=False, indent=1), encoding="utf-8")
    # батч для LLM-классификации (компактный)
    batch = [{"id": i, "title": m.get("title", ""), "snippet": m.get("snippet", "")[:300],
              "source": m.get("source", ""), "url": m.get("url", "")} for i, m in enumerate(rel)]
    (OUT / "to_classify.json").write_text(json.dumps(batch, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nСобрано уник.: {len(mentions)} | релевантных: {len(rel)}")
    print(f"→ {OUT/'mentions.json'} и {OUT/'to_classify.json'} (для LLM)")
    return mentions, rel


def finalize(book, classified_path=None):
    ensure_out()
    mentions = json.loads((OUT / "mentions.json").read_text(encoding="utf-8"))
    rel = [m for m in mentions if m.get("_relevant")]
    cp = pathlib.Path(classified_path) if classified_path else (OUT / "classified.json")
    if cp.exists():
        cls = json.loads(cp.read_text(encoding="utf-8"))
        by_id = {c["id"]: c for c in cls}
        for i, m in enumerate(rel):
            c = by_id.get(i, {})
            if "is_target_book" in c:
                m["_is_target"] = bool(c["is_target_book"])
            if c.get("role"):
                m["_role"] = c["role"]
            if c.get("genre"):
                m["_genre"] = c["genre"]
            if c.get("cite"):
                m["_cite"] = c["cite"]
            if c.get("tone"):
                m["_tone"] = c["tone"]
            m["_mi"] = E.media_index(m, 1 if m.get("_reprint_of") else 0)
        print(f"Применена LLM-классификация из {cp.name}")
    else:
        print("classified.json нет — финализирую на правилах (--llm none эквивалент)")
    stop = (ROOT.parent / "config" / "stopwords-ru.txt").read_text(encoding="utf-8").split() if (ROOT.parent / "config" / "stopwords-ru.txt").exists() else []
    out_xlsx = OUT / (re.sub(r"[^\w]+", "_", book.get("title", "report"))[:40] + ".xlsx")
    stats = report_xlsx.build([m for m in rel], book, out_xlsx, stopwords=stop)
    digest = report_digest.make_digest(rel, book, stats)
    (OUT / "digest.md").write_text(digest, encoding="utf-8")
    print(f"\nОтчёт: {out_xlsx}\nЛисты: {stats['sheets']}")
    print(f"Дайджест: {OUT/'digest.md'}")
    # рассылка/алерт
    dg = book.get("digest", {})
    if dg.get("telegram_chat"):
        report_digest.send_telegram(digest, dg["telegram_chat"], files=[out_xlsx])
        if dg.get("alert_on_negative"):
            report_digest.alert_negative(rel, book, dg["telegram_chat"])
    return stats, digest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=["collect", "finalize", "run"])
    ap.add_argument("book")
    ap.add_argument("--llm", choices=["none", "files"], default="none")
    ap.add_argument("--classified", default=None)
    a = ap.parse_args()
    book = load_book(a.book)
    if a.phase == "collect":
        collect(book)
    elif a.phase == "finalize":
        finalize(book, a.classified)
    else:  # run
        collect(book)
        if a.llm == "none":
            finalize(book)
        else:
            print("\n[LLM-режим] Теперь в Claude-сессии: прочитай out/to_classify.json,")
            print("запусти Task opus (disambiguate_prompt.md) + haiku (tone_prompt.md),")
            print("сохрани out/classified.json, затем: python monitor.py finalize <book>")


if __name__ == "__main__":
    main()
