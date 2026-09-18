---
name: weekly-synthesis
description: "Generate weekly synthesis report from git log."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [weekly, synthesis, python, git, claude]
    source: claude-code-config-pack
    origin: "command"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Generate weekly synthesis report from git log, vector memory, and subagent logs. Use with /weekly-synthesis or "итоги недели".

# Weekly Synthesis Report

Generate a comprehensive weekly summary from multiple data sources.

## Data Collection

### 1. Git Activity (last 7 days)
```bash
git log --since="7 days ago" --oneline --all --no-merges
```
Extract: commits count, files changed, main areas of work.

### 2. Vector Memory (last 7 days)
```bash
python ~/.hermes/ccpack/tools/vector_memory.py search "session" --limit 20
```
Extract: key decisions, errors fixed, tools discovered.

### 3. Subagent Logs (optional — the pack does not create this log itself)
```bash
powershell -c "if (Test-Path $env:USERPROFILE\.claude\logs\subagents.log) { Get-Content $env:USERPROFILE\.claude\logs\subagents.log | Select-Object -Last 50 } else { 'no subagent log - skipping' }"
```
Extract (if present): which agents were used, frequency, patterns.

### 4. Session Files
```bash
powershell -c "Get-ChildItem $env:USERPROFILE\.claude\projects\ -Recurse -Filter '*.jsonl' | Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-7) } | Select-Object Name, Length, LastWriteTime"
```

## Report Format

```markdown
# Weekly Synthesis: [date range]

## Highlights
- [Top 3 achievements]

## Git Activity
- Commits: N
- Key areas: [list]
- Notable changes: [list]

## Decisions Made
- [From vector memory]

## Errors Fixed
- [From vector memory]

## Agents Used
- [From subagent logs with frequency]

## Patterns & Insights
- [What repeated? What can be improved?]

## Next Week Focus
- [Based on trends and unfinished work]
```

## Process

1. Run all data collection commands
2. Analyze and cross-reference findings
3. Generate the report in the format above
4. Save key insights to vector memory:
```bash
python ~/.hermes/ccpack/tools/vector_memory.py learn "Weekly synthesis [date]: [key insight]" "meta"
```
5. Output the report to the user
