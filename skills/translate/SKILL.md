---
name: translate
description: "Перевод через DeepL Pro: текст, formality."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: commands
    tags: [translate, python, pdf, docx, xlsx, pptx, claude]
    source: claude-code-config-pack
    origin: "command"
    argument_hint: "<text> [target_lang] [formal] | file <path> <lang> | usage"
---
> **Аргументы.** Всё, что пользователь написал в одном сообщении с вызовом
> этого навыка, — и есть его аргумент. Если аргумента нет, спроси одним
> вопросом через `clarify` и работай дальше.

## Когда применять

Перевод через DeepL Pro: текст, formality, документы docx/pptx/pdf/xlsx. Триггеры: «переведи», «перевод документа». Массовый Google-перевод → /gtranslate.

# Translate

/translate - Professional translation via DeepL Pro API

## Usage
```
/translate <text>                    - Auto-detect -> English (configurable)
/translate <text> EN                 - Translate to English
/translate <text> DE formal          - Translate to formal German
/translate file <path> <target_lang> - Translate document
/translate usage                     - Check API usage/limits
```

## Instructions for Claude

Uses DeepL Pro API. Full reference: `~/.hermes/skills/integrations-and-apis/deepl-pro/SKILL.md`

### Quick translate

```python
import deepl
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.environ.get("HERMES_HOME") or os.path.expanduser("~/.hermes"), ".env"))
translator = deepl.Translator(os.getenv('DEEPL_API_KEY'))

# Text translation
result = translator.translate_text("Hello world", target_lang="RU")
print(result.text)  # "Привет мир"

# With formality
result = translator.translate_text("How are you?", target_lang="DE", formality="more")

# Batch
results = translator.translate_text(["Hello", "Goodbye"], target_lang="FR")
for r in results:
    print(r.text)
```

### Translate document

```python
# Supports: .docx, .pptx, .pdf, .txt, .html, .xlsx
with open("report.docx", "rb") as in_file:
    with open("report_de.docx", "wb") as out_file:
        translator.translate_document(in_file, out_file, target_lang="DE")
```

### Check usage

```python
usage = translator.get_usage()
print(f"Characters: {usage.character.count}/{usage.character.limit}")
```

## Language codes

**Common:** RU, EN-US, EN-GB, DE, FR, ES, IT, PT-BR, ZH-HANS, JA, KO, TR, PL, UK

**Formality** (DE, FR, ES, RU, IT, NL, PL, PT, JA): `more`, `less`, `prefer_more`, `prefer_less`

## Important

- Use `api.deepl.com` (NOT `api-free.deepl.com`)
- DEEPL_API_KEY from `$HERMES_HOME/.env`
