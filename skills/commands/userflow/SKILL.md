---
name: userflow
description: "Design user flow and wireframes."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [userflow]
    source: claude-code-config-pack
    origin: "command"
    argument_hint: "[scenario description]"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Design user flow and wireframes

# User Flow: текст, который пользователь написал вместе с вызовом навыка

Ask @product-designer to create comprehensive user flow:

## 1. User Journey
- Entry points
- Step-by-step flow
- Decision points
- Exit points

## 2. Screens & States
- Main screens involved
- Loading states
- Error states
- Success states

## 3. User Actions
- What user can do at each step
- Validation rules
- Error handling

## 4. Edge Cases
- What if user goes back?
- What if network fails?
- What if data is missing?

## 5. Accessibility
- Keyboard navigation
- Screen reader support
- Mobile considerations

Create flow diagram (ASCII or description) and screen descriptions.
