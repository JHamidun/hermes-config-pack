---
name: canonical-html
description: "Канонический HTML: закрытые теги, double-quotes."
user_description: "Приводит HTML к строгому виду: закрытые теги, одинаковые кавычки, предсказуемая вложенность. Нужен, когда разметку дальше будут править инструменты — на неаккуратной они ломаются."
user_description_i18n:
  ar: "يحوّل HTML إلى صيغة صارمة وقياسية: كل الوسوم مغلقة، علامات اقتباس موحّدة، تداخل يمكن التنبؤ به. مفيد عندما ستُعدَّل الشيفرة لاحقًا بواسطة أدوات، لأن HTML غير المرتب يجعلها تتعطل."
  en: "Normalizes HTML into a strict, canonical form: every tag closed, consistent double quotes, predictable nesting. Useful when the markup will be edited by tools afterwards, since sloppy HTML makes them break."
  es: "Convierte el HTML a una forma estricta y canónica: todas las etiquetas cerradas, comillas uniformes, anidamiento predecible. Útil cuando el marcado va a ser editado después por herramientas, porque un HTML descuidado las hace fallar."
  fr: "Met le HTML dans une forme stricte et canonique : toutes les balises fermées, des guillemets uniformes, une imbrication prévisible. Utile quand le balisage sera ensuite modifié par des outils, car un HTML approximatif les fait échouer."
  ja: "HTML を厳密で正規化された形に整えます。すべてのタグを閉じ、引用符を統一し、入れ子を予測可能にします。マークアップをその後ツールで編集する場合に役立ちます。雑な HTML ではツールが壊れてしまうからです。"
  pt: "Converte o HTML para uma forma estrita e canônica: todas as tags fechadas, aspas uniformes, aninhamento previsível. Útil quando a marcação vai ser editada depois por ferramentas, porque um HTML desleixado faz com que elas quebrem."
  zh: "把 HTML 整理成严格、规范的形式：所有标签闭合、引号统一、嵌套可预测。适用于标记之后还要交给工具修改的情况，因为不规范的 HTML 会让工具出错。"
  zh-hant: "把 HTML 整理成嚴格、規範的形式：所有標籤閉合、引號統一、巢狀結構可預測。適用於標記之後還要交給工具修改的情況，因為不規範的 HTML 會讓工具出錯。"
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: prototyping-and-web-build
    tags: [canonical, html]
    source: claude-code-config-pack
---
## Когда применять

Канонический HTML: закрытые теги, double-quotes, без implied-close — для предсказуемых правок инструментами. Триггеры: «почини разметку», «закрой теги».

# Canonical HTML

Цель — чтобы любая дальнейшая инструментальная правка (find-replace, AST, форматтеры, патчи через WebSocket в `visual-edit`) работала предсказуемо.

## Правила

### 1. Закрывай каждый non-void тег явно
```html
<!-- плохо -->
<p>Привет
<p>Мир

<!-- хорошо -->
<p>Привет</p>
<p>Мир</p>
```

`<p>`, `<li>`, `<dt>`, `<dd>`, `<option>`, `<thead>`, `<tbody>`, `<tr>`, `<td>` — у всех implied-close. Закрывай все вручную.

### 2. Double-quote атрибуты
```html
<!-- плохо -->
<input type=text required>
<a href=/foo class=link>foo</a>

<!-- хорошо -->
<input type="text" required>
<a href="/foo" class="link">foo</a>
```

Boolean-атрибуты без значения — OK (`required`, `disabled`, `hidden`).

### 3. Не self-close non-void
```html
<!-- плохо -->
<div class="card" />
<span/>

<!-- хорошо -->
<div class="card"></div>
<span></span>
```

Self-closing валиден только в SVG/MathML и для void-элементов (`<br>`, `<hr>`, `<img>`, `<input>`, `<meta>`, `<link>`, `<source>`, `<area>`, `<col>`, `<embed>`, `<wbr>`).

### 4. Атрибуты в стабильном порядке
Не обязательно, но удобно. Рекомендую:
1. `id`
2. `class`
3. `data-*`
4. `aria-*`
5. role
6. остальное

### 5. Никаких `<style>`/`<script>` без `</style>`/`</script>`
Даже если пустой.

### 6. Мета-теги — full open/close не нужны (void)
```html
<meta charset="utf-8">
<link rel="stylesheet" href="...">
```

## Список void-элементов (самозакрывающихся БЕЗ слеша)

`area`, `base`, `br`, `col`, `embed`, `hr`, `img`, `input`, `link`, `meta`, `source`, `track`, `wbr`.

Всё остальное — открывать и закрывать парой.

## Почему это важно

- Регэкспы вида `</p>` начинают находить настоящие пары, а не воздух.
- AST-парсеры (cheerio, jsdom, htmlparser2) одинаково видят дерево, как браузер.
- Find-replace в редакторе не превращается в лотерею.
- `visual-edit` и `tweaks-panel` (её запись значений на диск) могут патчить файл без неожиданностей.

## Антипаттерны

- ❌ `<p>` перед `<div>` без `</p>` — браузер закроет `p` за тебя, но AST не всегда.
- ❌ `<img />` — лишний слеш. Просто `<img>`.
- ❌ Mixed quotes: `class='card' id="hero"` — выбери один стиль.
- ❌ Attribute-value в одинарных кавычках: `<a href='...'>` — работает, но непоследовательно с большинством стилей.

## Чек-перед-сдачей

```bash
npx html-validate <file>     # отловит implied-close и пр.
npx prettier --check <file>  # форматирование
```
