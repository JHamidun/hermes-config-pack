#!/usr/bin/env python3
"""ШИМ. Канон живёт в skills/seo-machine-ru/scripts/content_scrubber.py.

Раньше здесь лежала побайтовая копия канона. Две копии расходятся молча:
правку вносят в одну, вторая продолжает работать по-старому, и одинаковый
текст даёт разные хеши — а на хешах стоит разметка «оригинал/перепечатка»
(references/metrics.md). Поэтому файл оставлен только как точка импорта:
`from lib.content_scrubber import scrub` в dedup.py и enrich.py продолжает
работать, но код исполняется ровно один — канонический.
"""
import importlib.util
import pathlib
import sys

_CANON = pathlib.Path(__file__).resolve().parents[3] / "seo-machine-ru" / "scripts" / "content_scrubber.py"

if not _CANON.exists():
    raise ImportError(f"Канон content_scrubber.py не найден: {_CANON}")

_spec = importlib.util.spec_from_file_location("seo_machine_content_scrubber", _CANON)
_mod = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("seo_machine_content_scrubber", _mod)
_spec.loader.exec_module(_mod)

# Переносим публичные имена канона сюда — чтобы работал любой импорт,
# а не только тот, что используется сегодня.
globals().update({k: v for k, v in vars(_mod).items() if not k.startswith("_")})

if __name__ == "__main__":
    _mod.main()
