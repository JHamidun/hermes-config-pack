#!/usr/bin/env python3
"""ШИМ. Канон живёт в skills/seo-machine-ru/scripts/readability_ru.py.

Раньше здесь лежала побайтовая копия канона. Две копии расходятся молча:
правку формулы Флеша-Оборневой вносят в одну, вторая продолжает считать
по-старому, и два навыка выдают разные баллы читаемости на одном тексте.
Файл оставлен точкой импорта: SKILL.md (строка 73) обещает readability_ru
в наборе lib/, поэтому `from lib.readability_ru import analyze` и запуск
CLI обязаны работать — но исполняется ровно один код, канонический.
"""
import importlib.util
import pathlib
import sys

_CANON = pathlib.Path(__file__).resolve().parents[3] / "seo-machine-ru" / "scripts" / "readability_ru.py"

if not _CANON.exists():
    raise ImportError(f"Канон readability_ru.py не найден: {_CANON}")

_spec = importlib.util.spec_from_file_location("seo_machine_readability_ru", _CANON)
_mod = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("seo_machine_readability_ru", _mod)
_spec.loader.exec_module(_mod)

# Переносим публичные имена канона сюда — чтобы работал любой импорт,
# а не только тот, что используется сегодня.
globals().update({k: v for k, v in vars(_mod).items() if not k.startswith("_")})

if __name__ == "__main__":
    _mod.main()
