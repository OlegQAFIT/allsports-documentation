# Allsports Diplodoc Style Guide

Этот файл описывает единый визуальный стандарт для документации Allsports в Diplodoc.

## Цель

Сделать все статьи визуально цельными, чтобы:

1. текущие документы выглядели как единая система;

1. новые документы можно было добавлять по одному шаблону;

1. правки по стилю делались централизованно через CSS и базовый markdown-каркас.

## Базовый каркас статьи

Каждая новая статья должна содержать следующие блоки:

1. `# Заголовок статьи`

1. блок `doc-page-actions` со ссылкой на исходный `DOCX`

1. блок `doc-hero-badge`

1. блок `doc-page-intro`

1. основной контент документа

Пример последовательности:

```md
# Название документа

<div class="doc-page-actions">
  <a class="doc-download-link" href="_assets/documents/example.docx">Скачать исходный DOCX</a>
</div>

<div class="doc-hero-badge">
  <div class="doc-hero-badge__logo" aria-hidden="true"></div>
  <div class="doc-hero-badge__meta">
    <div class="doc-hero-badge__eyebrow">Руководство пользователя</div>
    <div class="doc-hero-badge__brand">Allsports Documentation</div>
  </div>
</div>

<div class="doc-page-intro">
  <p class="doc-page-lead">Короткое описание назначения документа.</p>
  <div class="doc-page-overview">
    <div class="doc-page-overview__item">
      <div class="doc-page-overview__label">Для кого</div>
      <div class="doc-page-overview__value">Основная аудитория</div>
    </div>
    <div class="doc-page-overview__item">
      <div class="doc-page-overview__label">Основные разделы</div>
      <div class="doc-page-overview__value">Ключевые сценарии и разделы</div>
    </div>
    <div class="doc-page-overview__item">
      <div class="doc-page-overview__label">Формат</div>
      <div class="doc-page-overview__value">Веб-версия + исходный DOCX</div>
    </div>
  </div>
</div>
```

## Правила по тексту

1. не переписывать смысл документа без отдельной задачи;

1. сохранять исходную логику разделов из предоставленного материала;

1. улучшать только структуру, заголовки, форматирование и визуальную подачу;

1. одинаковые сущности называть одинаково во всех статьях.

## Правила по изображениям

1. вертикальные мобильные скриншоты должны быть компактными;

1. горизонтальные изображения не должны растягиваться шире комфортного чтения;

1. все скриншоты должны иметь одинаковые отступы, скругления и тень;

1. мелкие служебные иконки не должны растягиваться общими правилами.

## Универсальные компоненты

Стили уже подготовлены в `_assets/style/custom.css`.

Основные reusable-классы:

1. `doc-page-actions`

1. `doc-download-link`

1. `doc-hero-badge`

1. `doc-page-intro`

1. `doc-page-overview`

1. `doc-home-hero`

1. `doc-home-grid`

1. `doc-home-card`

1. `doc-note`

## Чеклист перед публикацией

1. заголовок страницы корректный;

1. ссылка на исходный `DOCX` работает;

1. intro-блок заполнен;

1. названия разделов в меню соответствуют статье;

1. вертикальные и горизонтальные картинки выглядят пропорционально;

1. таблицы и блоки `Важно/Примечание` читаются в светлой и темной теме.
