# -*- coding: utf-8 -*-
"""Markdown-дайджест + опциональная отправка в Telegram (через tg_client.py) + алерт на негатив."""
import subprocess, sys
from collections import Counter
from pathlib import Path

# Тот же путь, что в connectors/telegram.py: конфиг, а не личный диск автора.
TG = str(Path(__file__).resolve().parents[3] / "tools" / "tg_client.py")


def make_digest(mentions, book, stats):
    rel = [m for m in mentions if m.get("_is_target")]
    tone = Counter(m.get("_tone", "Нейтрал") for m in rel)
    top = sorted(rel, key=lambda x: x.get("_mi", 0), reverse=True)[:5]
    neg = [m for m in rel if m.get("_tone") == "Негатив"]
    L = []
    L.append(f"📚 *Мониторинг: {book.get('title','')}*")
    L.append(f"Всего упоминаний: *{len(rel)}* (ориг {stats.get('orig','?')}/переп {len(rel)-stats.get('orig',0)})")
    L.append(f"СМИ {stats.get('smi',0)} · Соцсети {stats.get('soc',0)} · Видео {stats.get('vid',0)} · Читательское {stats.get('rdr',0)}")
    L.append(f"Тональность: 👍 {tone.get('Позитив',0)} · ⚪ {tone.get('Нейтрал',0)} · 👎 {tone.get('Негатив',0)}")
    L.append(f"Суммарный охват: ~{sum(m.get('_reach',0) for m in rel):,}".replace(",", " "))
    if neg:
        L.append(f"\n⚠️ *Негатив ({len(neg)}):*")
        for m in neg[:3]:
            L.append(f"• {m.get('title','')[:80]} — {m.get('source','')} {m.get('url','')}")
    L.append("\n*Топ по МедиаИндексу:*")
    for m in top:
        L.append(f"• [{m.get('_mi','')}] {m.get('title','')[:70]} — {m.get('source','')}")
    return "\n".join(L)


def send_telegram(text, chat, files=None):
    if not chat:
        return False
    try:
        cmd = [sys.executable, TG, "send", str(chat), text]
        subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=60)
        if files:
            for f in files:
                subprocess.run([sys.executable, TG, "send-file", str(chat), str(f)],
                               capture_output=True, text=True, encoding="utf-8", timeout=120)
        return True
    except Exception:
        return False


def alert_negative(mentions, book, chat):
    """Мгновенный алерт по новым негативным упоминаниям."""
    if not chat:
        return 0
    neg = [m for m in mentions if m.get("_is_target") and m.get("_tone") == "Негатив"]
    for m in neg:
        send_telegram(f"🚨 *Негатив о книге «{book.get('title','')}»*\n{m.get('title','')}\n{m.get('source','')} · {m.get('url','')}", chat)
    return len(neg)
