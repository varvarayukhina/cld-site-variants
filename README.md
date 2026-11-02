# CLD — три варианта дизайна сайта (прототип)

Прототип нового сайта лаборатории CLD (Черкесск, lab.discript.ru). Не официальный сайт.

- `v1/` — «Поиск»: строка поиска и короткий список частых анализов.
- `v2/` — «Кнопки»: крупные кнопки по задачам.
- `v3/` — «Помощник»: сайт задаёт простые вопросы и подсказывает анализы.

Переключатель вариантов — полоса сверху, экран при переключении сохраняется.
Данные общие: `shared/cld-data.js` (цены пункта Черкесск, ул. Гутякулова, 20, на 22.10.2026).
Шрифты: Avanti CLD (лицензия у CLD есть; файлы восстановлены из брендбука 2022 — заменить оригиналами) и Montserrat (OFL).


## Актуальный вариант v4

`v4/` — основной прототип после обсуждений с лабораторией. Гид `#for-pregnant` использует общие цены выбранного пункта, доступность, карточки исследований и корзину v4.

Исходники утверждённого гида: `content/pregnancy-guide/page.html` (вёрстка/тексты), `calendar.js` (календарь и пояснения), `adapter.js` (подключение к приложению). Это исходники, не отдельная опубликованная версия сайта. Иллюстрации: `assets/img/pregnancy/`.

После правок гида выполнить:

```sh
python3 scripts/build-pregnancy-guide.py
```

Скрипт обновляет `v4/index.html` и изолированный `assets/pregnancy-guide.css`; повторная сборка идемпотентна. При сборке v4 из старой базы необходимо вызвать `integrate(html)` из этого скрипта перед записью результата, чтобы сохранить утверждённый гид.

GitHub Pages остаётся прототипом с `noindex`. SEO-публикация на рабочем домене требует отдельных индексируемых URL и подключения реальных сервисов лаборатории.

Общие заголовки/описания экранов и блоки перехода из прайса к гидам: `content/navigation/navigation.js`, стили — `assets/navigation.css`. После их изменения выполнить `python3 scripts/build-navigation.py`. Этот шаг также включён в локальную сборку v4 после сборки гида.

Women guide: `content/women-guide/` → `python3 scripts/build-women-guide.py`.
Comparisons: `content/comparisons/articles.json` and `adapter.js` → `python3 scripts/build-comparisons.py`; styles in `assets/comparisons.css`.
Children guide: `content/kids-guide/` → `python3 scripts/build-kids-guide.py`.
Rebuild order: pregnancy → women → kids → navigation → comparisons. All builders are idempotent. Contextual comparisons use the shared catalogue, selected point and cart; source references stay in the JSON for editorial verification.

Women guide uses task cards and one selected topic panel at a time. The children guide retains its original full text as a continuous article with all sections visible. Keep anchor navigation working in both guides. Full analysis lists stay visible. Shared task styles live in `content/women-guide/style.css`.
