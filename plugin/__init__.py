"""ccpack — the Claude Code config pack, ported to Hermes Agent.

The plugin is deliberately thin. The pack itself — skills, agent roles, the
Python CLIs, the reference config — lives in one place:

    ~/.hermes/ccpack/
        skills/<category>/<name>/SKILL.md    every one of these is a slash command
        agents/<name>/SKILL.md               subagent roles, skill_view only
        tools/  scripts/                     the pack's Python CLIs
        config/ rules/ templates/ docs/      references the skills read on demand

This package registers that content with Hermes:

  * `skills/` is wired into `skills.external_dirs` by `hermes ccpack install`,
    which is what turns ~420 skills into slash commands;
  * every `agents/<name>` is registered with `ctx.register_skill`, so a role
    costs nothing until `skill_view("ccpack:<name>")` asks for it;
  * `/ccpack` reports status and lists what is available;
  * `CCPACK_HOME` is exported into the process environment, so the shell
    commands inside the skills resolve whether or not the default path is used.

Why roles are registered and workflows are not: a plugin skill is resolvable
only through an explicit `skill_view` and never enters the system prompt, which
is exactly right for 74 roles that are used one at a time. Workflow skills have
to be in the index to become slash commands, so they go through external_dirs.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent


def _hermes_home() -> Path:
    return Path(os.environ.get("HERMES_HOME") or (Path.home() / ".hermes"))


def ccpack_home() -> Path:
    """Where the pack itself lives.

    Order, and why: the `CCPACK_HOME` override first; then the pointer the
    installer drops next to the plugin, which is the only source that actually
    knows (a `--home` install can put the pack anywhere); then `~/.hermes/ccpack`,
    the documented default that every skill names literally; then
    `<hermes home>/ccpack`, which differs from the former on Windows, where the
    runtime lives in %LOCALAPPDATA%; and finally the plugin directory, for a
    single-directory install.

    Guessing cost a live run: the plugin reported `skills: 0` while 413 sat in
    ~/.hermes/ccpack, because only the Windows runtime home was consulted."""
    env = os.environ.get("CCPACK_HOME")
    if env:
        return Path(env).expanduser()
    pointer = PLUGIN_ROOT / "ccpack_home.txt"
    if pointer.exists():
        try:
            p = Path(pointer.read_text(encoding="utf-8").strip()).expanduser()
            if (p / "skills").is_dir():
                return p
        except OSError:
            pass
    for candidate in (Path.home() / ".hermes" / "ccpack", _hermes_home() / "ccpack"):
        if (candidate / "skills").is_dir():
            return candidate
    return PLUGIN_ROOT


HOME = ccpack_home()
SKILLS_DIR = HOME / "skills"
AGENTS_DIR = HOME / "agents"
MANIFEST = HOME / "MANIFEST.json"


# --- introspection ----------------------------------------------------------

def _manifest() -> dict:
    try:
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _skill_count() -> int:
    if not SKILLS_DIR.is_dir():
        return 0
    return sum(1 for _ in SKILLS_DIR.glob("*/*/SKILL.md"))


def _categories() -> list[str]:
    if not SKILLS_DIR.is_dir():
        return []
    return sorted(d.name for d in SKILLS_DIR.iterdir() if d.is_dir())


def _agent_names() -> list[str]:
    if not AGENTS_DIR.is_dir():
        return []
    return sorted(d.name for d in AGENTS_DIR.iterdir() if (d / "SKILL.md").exists())


def _wired() -> bool:
    """True when skills/ is in skills.external_dirs — the difference between
    'the files are on disk' and 'the slash commands exist'."""
    try:
        from hermes_cli.config import load_config
        cfg = load_config() or {}
    except Exception:
        return False
    target = SKILLS_DIR.resolve()
    for entry in ((cfg.get("skills") or {}).get("external_dirs") or []):
        try:
            if Path(str(entry)).expanduser().resolve() == target:
                return True
        except Exception:
            continue
    return False


def _status_text() -> str:
    man = _manifest()
    version = man.get("version", "1.0.0")
    lines = [f"ccpack {version} — Claude Code config pack on Hermes",
             f"  home:        {HOME}",
             f"  skills:      {_skill_count()} in {len(_categories())} categories"
             + ("  (slash commands active)" if _wired()
                else "  ⚠ not in skills.external_dirs — run `hermes ccpack install`"),
             f"  agent roles: {len(_agent_names())} (skill_view(\"ccpack:<name>\"))"
             + (f"  ⚠ {len(ROLE_ERRORS)} не зарегистрированы" if ROLE_ERRORS else "")]
    for err in ROLE_ERRORS[:5]:
        lines.append(f"      ! {err}")
    for extra in ("tools", "scripts", "config", "rules"):
        d = HOME / extra
        n = sum(1 for _ in d.rglob("*")) if d.is_dir() else 0
        lines.append(f"  {extra + ':':<12} {n} files" if n else f"  {extra + ':':<12} missing")
    return "\n".join(lines)


def _help_text() -> str:
    cats = _categories()
    return ("ccpack — навыки, роли и CLI из конфиг-пака Claude Code.\n\n"
            f"Навыки:   {_skill_count()} штук, каждый — слэш-команда (/<имя>)\n"
            f"Категории: {', '.join(cats) if cats else '—'}\n"
            f"Роли:     skill_view(\"ccpack:<имя>\") — {len(_agent_names())} штук\n"
            f"CLI пака: python {HOME}/tools/<имя>.py\n\n"
            "/ccpack status     состояние и подключение\n"
            "/ccpack skills     список навыков по категориям\n"
            "/ccpack roles      список ролей для delegate_task\n"
            "/ccpack find X     найти навык по подстроке\n")


# --- slash command ----------------------------------------------------------

def _find(term: str) -> str:
    term = term.lower()
    hits = []
    for p in sorted(SKILLS_DIR.glob("*/*/SKILL.md")):
        name = p.parent.name
        text = ""
        try:
            text = p.read_text(encoding="utf-8")[:2000].lower()
        except OSError:
            pass
        if term in name.lower() or term in text:
            hits.append(f"  /{name:<32} {p.parent.parent.name}")
    if not hits:
        return f"Ничего не нашлось по «{term}»."
    return f"Навыки по «{term}» ({len(hits)}):\n" + "\n".join(hits[:60])


def _handle_slash(raw_args: str) -> str:
    argv = (raw_args or "").split()
    sub = argv[0].lower() if argv else "help"
    if sub in ("help", "-h", "--help"):
        return _help_text()
    if sub == "status":
        return _status_text()
    if sub == "skills":
        out = []
        for cat in _categories():
            names = sorted(p.parent.name for p in (SKILLS_DIR / cat).glob("*/SKILL.md"))
            out.append(f"{cat} ({len(names)}): " + ", ".join(f"/{n}" for n in names))
        return "\n\n".join(out) if out else "Навыков не найдено."
    if sub == "roles":
        roles = _agent_names()
        return (f"Роли для delegate_task ({len(roles)}):\n"
                + "\n".join(f'  skill_view("ccpack:{r}")' for r in roles))
    if sub == "find":
        if len(argv) < 2:
            return "Использование: /ccpack find <подстрока>"
        return _find(" ".join(argv[1:]))
    return f"Неизвестная подкоманда: {sub}\n\n{_help_text()}"


# --- CLI: hermes ccpack … ---------------------------------------------------

def _setup_cli(parser) -> None:
    sub = parser.add_subparsers(dest="ccpack_command")
    sub.add_parser("status", help="Show what is installed and whether it is wired")
    sub.add_parser("doctor", help="Diagnose the install")
    inst = sub.add_parser("install", help="Wire ccpack skills into config.yaml")
    inst.add_argument("--override", action="store_true",
                      help="Keep pack skills whose names collide with existing ones")
    sub.add_parser("uninstall", help="Remove ccpack skills from skills.external_dirs")


def _load_cfg():
    from hermes_cli.config import load_config, save_config
    return load_config() or {}, save_config


def _cli_install(override: bool = False) -> int:
    try:
        cfg, save_config = _load_cfg()
    except Exception as exc:
        print(f"Cannot load Hermes config API: {exc}")
        return 1
    if not SKILLS_DIR.is_dir():
        print(f"No skills at {SKILLS_DIR} — install the pack first "
              f"(install-hermes.ps1 / install-hermes.sh)")
        return 1
    skills_cfg = cfg.setdefault("skills", {})
    dirs = list(skills_cfg.get("external_dirs") or [])
    target = str(SKILLS_DIR.resolve())
    if any(str(Path(str(d)).expanduser().resolve()) == target for d in dirs):
        print(f"Already wired: {target}")
    else:
        dirs.append(target)
        skills_cfg["external_dirs"] = dirs
        save_config(cfg)
        print(f"Added to skills.external_dirs: {target}")

    collisions = _collisions()
    if collisions:
        print(f"\n{len(collisions)} name(s) also exist as built-in Hermes skills:")
        for name in collisions[:20]:
            print(f"  {name}")
        if len(collisions) > 20:
            print(f"  … and {len(collisions) - 20} more")
        print("Hermes resolves a duplicate name by scan order — check `/ccpack status` "
              "and rename the loser if the wrong one wins.")
    print(f"\n{_skill_count()} skills are now slash commands "
          f"(restart the session or run /reload-skills).")
    return 0


def _collisions() -> list[str]:
    """Pack skill names that already exist elsewhere in this Hermes install."""
    ours = {p.parent.name for p in SKILLS_DIR.glob("*/*/SKILL.md")}
    theirs: set[str] = set()
    try:
        from agent.skill_utils import get_all_skills_dirs
        for d in get_all_skills_dirs():
            d = Path(str(d))
            if not d.is_dir() or d.resolve() == SKILLS_DIR.resolve():
                continue
            for p in d.rglob("SKILL.md"):
                theirs.add(p.parent.name)
    except Exception:
        return []
    return sorted(ours & theirs)


def _cli_uninstall() -> int:
    try:
        cfg, save_config = _load_cfg()
    except Exception as exc:
        print(f"Cannot load Hermes config API: {exc}")
        return 1
    skills_cfg = cfg.setdefault("skills", {})
    target = str(SKILLS_DIR.resolve())
    skills_cfg["external_dirs"] = [
        d for d in (skills_cfg.get("external_dirs") or [])
        if str(Path(str(d)).expanduser().resolve()) != target]
    save_config(cfg)
    print(f"Removed from skills.external_dirs: {target}")
    return 0


def _cli_doctor() -> int:
    print(_status_text())
    problems = []
    if not _skill_count():
        problems.append(f"no skills under {SKILLS_DIR}")
    if not _agent_names():
        problems.append(f"no agent roles under {AGENTS_DIR}")
    if not _wired():
        problems.append("skills/ not in skills.external_dirs — run `hermes ccpack install`")
    if not (HOME / "tools").is_dir():
        problems.append(f"{HOME}/tools missing — the pack's CLIs will not run")
    import shutil as _sh
    if not _sh.which("python") and not _sh.which("python3"):
        problems.append("python not on PATH — the pack's CLIs need Python 3.11+")
    if problems:
        print("\nProblems:")
        for p in problems:
            print(f"  x {p}")
        return 1
    print("\n  ok — ccpack is ready")
    return 0


def _handle_cli(args) -> int:
    cmd = getattr(args, "ccpack_command", None) or "status"
    if cmd == "status":
        print(_status_text())
        return 0
    if cmd == "doctor":
        return _cli_doctor()
    if cmd == "install":
        return _cli_install(getattr(args, "override", False))
    if cmd == "uninstall":
        return _cli_uninstall()
    print(f"Unknown command: {cmd}")
    return 1


# --- session hook -----------------------------------------------------------

def _on_session_start(_payload=None):
    """Export CCPACK_HOME for the terminal tool. The skills name the literal
    path as well, so an unset variable is never fatal — this just makes
    `$CCPACK_HOME/tools/x.py` work for anyone who prefers the variable."""
    os.environ.setdefault("CCPACK_HOME", str(HOME))
    return None


# --- entry point ------------------------------------------------------------

ROLE_ERRORS: list[str] = []


def register(ctx) -> None:
    os.environ.setdefault("CCPACK_HOME", str(HOME))

    ROLE_ERRORS.clear()
    for name in _agent_names():
        # The path argument is the SKILL.md itself, as a Path: register_skill
        # checks `path.exists()`, and a plain string fails that check with an
        # AttributeError that used to be swallowed here — 74 roles silently
        # registering as zero. Failures are collected and shown in status now.
        try:
            ctx.register_skill(name, AGENTS_DIR / name / "SKILL.md")
        except Exception as exc:  # one bad role must not take the plugin down
            ROLE_ERRORS.append(f"{name}: {exc}")
            logger = getattr(ctx, "logger", None)
            if logger:
                logger.warning("ccpack: role %s not registered: %s", name, exc)

    try:
        ctx.register_command("ccpack", _handle_slash,
                             "Состояние пака, список навыков и ролей, поиск навыка")
    except Exception:
        pass
    try:
        # Signature is (name, help, setup_fn, handler_fn) — passing setup first
        # registers the command but silently no subcommands, and every
        # `hermes ccpack <sub>` dies with "unrecognized arguments".
        ctx.register_cli_command("ccpack",
                                 "Manage the Claude Code config pack on Hermes",
                                 _setup_cli, _handle_cli)
    except Exception:
        pass
    try:
        ctx.register_hook("on_session_start", _on_session_start)
    except Exception:
        pass
