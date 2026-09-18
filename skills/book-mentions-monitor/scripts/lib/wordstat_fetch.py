#!/usr/bin/env python3
"""ШИМ. Канон живёт в skills/seo-machine-ru/scripts/wordstat_fetch.py.

Раньше здесь лежала побайтовая копия канона. Две копии расходятся молча:
Яндекс меняет ответ getTable, чинят одну копию — вторая продолжает падать
или возвращать нули, и коннектор wordstat.py тихо отдаёт пустой спрос.
Файл оставлен точкой импорта: `from lib.wordstat_fetch import fetch_one`
в connectors/wordstat.py продолжает работать, но код исполняется ровно
один — канонический.
"""
import importlib.util
import pathlib
import sys

_CANON = pathlib.Path(__file__).resolve().parents[3] / "seo-machine-ru" / "scripts" / "wordstat_fetch.py"

if not _CANON.exists():
    raise ImportError(f"Канон wordstat_fetch.py не найден: {_CANON}")

_spec = importlib.util.spec_from_file_location("seo_machine_wordstat_fetch", _CANON)
_mod = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("seo_machine_wordstat_fetch", _mod)
_spec.loader.exec_module(_mod)

# Переносим публичные имена канона сюда — чтобы работал любой импорт,
# а не только тот, что используется сегодня.
globals().update({k: v for k, v in vars(_mod).items() if not k.startswith("_")})

if __name__ == "__main__":
    _mod.main()
