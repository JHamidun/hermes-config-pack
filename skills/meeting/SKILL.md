---
name: meeting
description: "Structure meeting notes."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [meeting]
    source: claude-code-config-pack
    origin: "command"
    argument_hint: "[meeting topic]"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Structure meeting notes

# Meeting Notes: текст, который пользователь написал вместе с вызовом навыка

Structure the meeting notes with clear sections:

## 1. Meeting Info
- Date and attendees
- Duration and agenda

## 2. Key Decisions
- Decisions made
- Action items with owners
- Deadlines

## 3. Discussion Points
- Main topics discussed
- Open questions
- Blockers identified

## 4. Next Steps
- Immediate actions
- Follow-up meetings
- Documentation needed

Format as clear Markdown artifact.
