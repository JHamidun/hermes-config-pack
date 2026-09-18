#!/usr/bin/env python3
"""Install the pack into a Hermes home. Cross-platform, no dependencies.

    python install.py              # install, keeping anything you already have
    python install.py --dry-run    # print the plan, change nothing
    python install.py --repair     # overwrite pack files with this release
    python install.py --home DIR   # install the pack somewhere else

Two directories are involved, and they are deliberately different:

  <pack home>   ~/.hermes/ccpack — skills, roles, tools, scripts, config, rules.
                A plain directory in your home, the same path on every OS, which
                is why the skills can name it literally.
  <hermes home> the runtime's own home ($HERMES_HOME, else %LOCALAPPDATA%\\hermes
                on Windows and ~/.hermes elsewhere). Only the thin plugin goes
                here, because that is where Hermes looks for plugins.

Nothing outside those two places is touched, and by default nothing that already
exists is overwritten: a second run adds what is missing and leaves your edits
alone. `--repair` is the opposite and says so before it starts.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _find_build() -> Path:
    """Where the package content is, in all three shapes this script ships in:
    at the repo root next to itself, in a `ccpack/` subdirectory, or in the
    build tree of the converter workspace."""
    if (HERE / "skills").is_dir():
        return HERE
    if (HERE / "ccpack" / "skills").is_dir():
        return HERE / "ccpack"
    return HERE.parent / "build" / "ccpack"


def _find_plugin_dir() -> Path:
    return HERE / "plugin" if (HERE / "plugin" / "plugin.yaml").exists() else HERE


BUILD = _find_build()
PLUGIN_SRC = _find_plugin_dir()
PLUGIN_FILES = ["plugin.yaml", "__init__.py"]
SKIP_DIRS = {".git", ".github", "__pycache__", "node_modules", ".pytest_cache"}


def hermes_home() -> Path:
    env = os.environ.get("HERMES_HOME", "").strip()
    if env:
        return Path(env).expanduser()
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", "").strip()
        return (Path(base) if base else Path.home() / "AppData" / "Local") / "hermes"
    return Path.home() / ".hermes"


CATEGORY_RE = re.compile(r"^\s*category:\s*([A-Za-z0-9._-]+)\s*$", re.M)


def skill_category(skill_dir: Path) -> str:
    """The category bucket this skill belongs in, from its own frontmatter.

    The repository ships skills flat, because that is the only shape a Hermes
    tap can enumerate. Installed, they have to sit in category directories: the
    skills reference each other as `~/.hermes/skills/<category>/<name>/…`, and a
    flat install would break every one of those links."""
    md = skill_dir / "SKILL.md"
    if md.exists():
        try:
            head = md.read_text(encoding="utf-8", errors="replace").split("\n---", 1)[0]
            m = CATEGORY_RE.search(head)
            if m:
                return m.group(1)
        except OSError:
            pass
    return "uncategorised"


def repo_is_flat(src: Path) -> bool:
    return (src / "skills").is_dir() and any((src / "skills").glob("*/SKILL.md"))


def copy_tree(src: Path, dst: Path, *, repair: bool, dry: bool) -> tuple[int, int]:
    """Copy src over dst. Returns (written, skipped)."""
    written = skipped = 0
    flat = repo_is_flat(src)
    categories: dict[str, str] = {}
    if flat:
        for d in sorted((src / "skills").iterdir()):
            if d.is_dir() and (d / "SKILL.md").exists():
                categories[d.name] = skill_category(d)
    for p in sorted(src.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(src)
        # Installing from a git clone must not drag the repository into the pack
        # home: a first run copied 11092 files instead of 4971, the difference
        # being .git objects.
        if SKIP_DIRS & set(rel.parts):
            continue
        if flat and rel.parts[0] == "skills" and len(rel.parts) >= 2:
            cat = categories.get(rel.parts[1])
            if cat:
                rel = Path("skills", cat, *rel.parts[1:])
        target = dst / rel
        if target.exists() and not repair:
            skipped += 1
            continue
        if not dry:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)
        written += 1
    return written, skipped


def backup(path: Path, dry: bool) -> Path | None:
    if not path.exists() or not any(path.iterdir()):
        return None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = path.with_name(path.name + f".backup.{stamp}")
    if not dry:
        shutil.copytree(path, dest, dirs_exist_ok=True)
    return dest


def main() -> int:
    ap = argparse.ArgumentParser(description="Install the config pack into Hermes")
    ap.add_argument("--home", help="pack home (default: ~/.hermes/ccpack)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--repair", action="store_true",
                    help="overwrite existing pack files with this release")
    ap.add_argument("--no-backup", action="store_true")
    a = ap.parse_args()

    if not BUILD.is_dir():
        print(f"No package found at {BUILD} — run tools/convert.py first.", file=sys.stderr)
        return 1

    pack_home = Path(a.home).expanduser() if a.home else Path.home() / ".hermes" / "ccpack"
    hhome = hermes_home()
    plugin_dir = hhome / "plugins" / "ccpack"

    print(f"pack     -> {pack_home}")
    print(f"plugin   -> {plugin_dir}")
    print(f"mode     -> {'repair (overwrites pack files)' if a.repair else 'add missing only'}"
          + ("  [dry run]" if a.dry_run else ""))

    if not a.no_backup and pack_home.exists():
        b = backup(pack_home, a.dry_run)
        if b:
            print(f"backup   -> {b}")

    written, skipped = copy_tree(BUILD, pack_home, repair=a.repair, dry=a.dry_run)
    print(f"\npack files: {written} written, {skipped} left as they were")

    # The four templates are what the user fills in with their own context, and
    # ~180 places in the skills name them at the pack root. Seeding empty copies
    # there turns those into real files (a skill that reads one sees an unfilled
    # template and says so) instead of dangling paths. Never overwritten.
    seeded = 0
    for tpl in ("author-profile.md", "voice-sample.md", "business-context.md"):
        src = BUILD / "templates" / tpl
        dst = pack_home / tpl
        if src.exists() and not dst.exists():
            if not a.dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
            seeded += 1
    if seeded:
        print(f"templates seeded at the pack root: {seeded} (fill them in with your own)")

    pw = 0
    for name in PLUGIN_FILES:
        src = PLUGIN_SRC / name
        if not src.exists():
            print(f"  ! plugin file missing in the release: {name}")
            continue
        if not a.dry_run:
            plugin_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, plugin_dir / name)
        pw += 1
    # The pointer removes the guesswork: --home can put the pack anywhere, and
    # the plugin has no other way to learn where it went.
    if not a.dry_run and pw:
        (plugin_dir / "ccpack_home.txt").write_text(str(pack_home), encoding="utf-8")
    print(f"plugin files: {pw} (+ ccpack_home.txt -> {pack_home})")

    skills = sum(1 for _ in (pack_home / "skills").glob("*/*/SKILL.md")) if not a.dry_run \
        else sum(1 for _ in (BUILD / "skills").glob("*/*/SKILL.md"))
    roles = sum(1 for _ in (BUILD / "agents").glob("*/SKILL.md"))

    print(f"""
Installed: {skills} skills, {roles} agent roles.

Next, in this order:

  1. hermes plugins enable ccpack
  2. hermes ccpack install          # wires skills/ into skills.external_dirs
  3. hermes ccpack doctor           # checks python, paths, wiring

Then, by hand and on purpose (it is about safety and money):

  * merge {pack_home}/config.snippet.yaml into your config.yaml —
    the destructive-command guard and the MCP servers live there;
  * copy {pack_home}/SOUL.example.md to {hhome}/SOUL.md and rewrite it as you;
  * put your keys in {hhome}/.env (templates/ has the sample);
  * {pack_home}/AGENTS.md is the project-instruction file — copy it into a
    repository you work in, or leave it here as reference.

The pack's CLIs need Python 3.11+ and the packages in requirements.txt.""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
