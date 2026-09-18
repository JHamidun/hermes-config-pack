---
name: export-png
description: "PNG-скриншоты слайдов/экранов через Playwright."
user_description: "Сохраняет слайды и экраны картинками: целиком или по выбранному фрагменту. Нужен для превью, обложек и вставки в другие документы."
user_description_i18n:
  ar: "يحفظ الشرائح والشاشات كصور PNG، كاملة أو جزءًا محددًا منها فقط. مفيد للمعاينات وصور الأغلفة والإدراج في مستندات أخرى."
  en: "Saves slides and screens as PNG images, either whole or just a selected part. Useful for previews, cover images and pasting into other documents."
  es: "Guarda diapositivas y pantallas como imágenes PNG, completas o solo un fragmento seleccionado. Útil para vistas previas, portadas e inserción en otros documentos."
  fr: "Enregistre les diapositives et les écrans sous forme d'images PNG, en entier ou seulement une partie choisie. Utile pour les aperçus, les visuels de couverture et l'insertion dans d'autres documents."
  ja: "スライドや画面を PNG 画像として保存します。全体でも、選んだ一部分だけでも構いません。プレビュー、カバー画像、他の文書への貼り付けに役立ちます。"
  pt: "Salva slides e telas como imagens PNG, inteiros ou apenas um trecho selecionado. Útil para prévias, capas e inserção em outros documentos."
  zh: "把幻灯片和界面保存为 PNG 图片，可以整页保存，也可以只截取选定的部分。适合做预览图、封面图，或插入到其他文档中。"
  zh-hant: "把投影片和畫面儲存為 PNG 圖片，可以整頁儲存，也可以只擷取選定的部分。適合做預覽圖、封面圖，或插入到其他文件中。"
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: design-and-ui
    tags: [export, png, playwright, node, pdf]
    source: claude-code-config-pack
---
## Когда применять

PNG-скриншоты слайдов/экранов через Playwright: кадр на слайд или по селектору. Триггеры: «html в png», «выгрузи слайды картинками», «социалки cover». НЕ тест UI→webapp-testing.

# Export PNG

Playwright headless. Установка та же, что для `export-pdf`:

```bash
npm i -D playwright && npx playwright install chromium
```

## Скрипт

`templates/render-png.mjs` — умеет:

- Если на странице есть `<deck-stage>` — переключает слайды через `goToSlide(i)` и снимает кадр на каждый.
- Иначе — снимает либо весь viewport, либо элементы по селектору (`--selector ".artboard"`).

```bash
# Все слайды дека
node render-png.mjs deck.html out/

# Все артборды по селектору
node render-png.mjs canvas.html out/ --selector dc-artboard --width 1200 --height 800

# Один скрин страницы
node render-png.mjs prototype.html out/screen.png
```

## Размеры

По умолчанию viewport 1920×1080, scale 2 (retina). Меняется флагами `--width`, `--height`, `--scale`.

## Подсказки

- Для деков скрипт ждёт 600ms между слайдами — этого хватает для transition. Если у тебя длиннее — `--delay 1200`.
- Для прозрачных картинок добавь `--omit-background` (установит body background в transparent перед снимком).
- Шрифты — `await document.fonts.ready` уже стоит. Если используешь Google Fonts с `display: swap`, добавь `--font-wait 1000`.

## Legacy reference

Прежняя расширенная версия скилла (дерево @2026-04-30) сохранена целиком в `references/legacy-export-png.md`. Секции там: Базовый каркас, Стандартные размеры social, Серия из шаблона, Серия слайдов как PNG, Качество vs размер файла, Прозрачный PNG, После export — оптимизация, Антипаттерны.
