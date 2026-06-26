# Track: v2_rebuild_20260626

## Overview

Полная пересборка ActiveMap Reviewer с v1.2.0 → v2.0.0.

**Goal:** Переписать `reviewer.py` и `reviewer_html.html` с нуля, устранив технический долг v1.x и добавив новые функции.

## Files

- [Spec](./spec.md) — Требования и приёмочные критерии
- [Plan](./plan.md) — Задачи с чекбоксами

## Status

Not started

## Phases

1. Foundation — Python refactor (AppState, logging, error handling)
2. Frontend Refactor — HTML структуризация, замена глобалей
3. Persistence — localStorage настройки
4. Feature Completion — Пагинация, PATCH errors, CSV-экспорт
5. QA & Release — Тестирование, .exe сборка, GitHub Release v2.0.0
