---
name: specs
description: "Create technical specifications."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [specs]
    source: claude-code-config-pack
    origin: "command"
    argument_hint: "[feature name]"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Create technical specifications

# Technical Specifications: текст, который пользователь написал вместе с вызовом навыка

Ask @system-analyst and @software-architect to create detailed tech specs:

## 1. System Architecture
- Components involved
- Data flow diagrams
- Integration points

## 2. API Design
- Endpoints needed
- Request/response formats
- Authentication requirements

## 3. Data Models
- Database schema changes
- Relationships
- Migrations needed

## 4. Technical Requirements
- Performance requirements
- Scalability considerations
- Security requirements

## 5. Implementation Plan
- Development phases
- Testing strategy
- Deployment approach

## 6. Risks & Mitigation
- Technical risks
- Mitigation strategies
- Alternative approaches

Output as detailed Markdown artifact.
