# Conductor Index

> ActiveMap Reviewer v2.0 — инструмент Префектуры САО для проверки заданий ЖКХ

## Project Documentation

- [Product Definition](./product.md) — Проблема, пользователи, функции, ограничения
- [Product Guidelines](./product-guidelines.md) — Цвета, типографика, tone of voice, UI-правила
- [Tech Stack](./tech-stack.md) — Python stdlib, vanilla JS, PyInstaller, GitHub Actions
- [Workflow](./workflow.md) — Процесс разработки, TDD, commit-стратегия

## Codebase Documentation

- [Naming Conventions](./docs/naming-conventions.md) — Python PEP-8, JS camelCase, DOM kebab-case
- [Architecture](./docs/architecture.md) — HTTP proxy, screen flow, state management, v1→v2
- [Testing Patterns](./docs/testing-patterns.md) — Error handling, logging, manual checklist
- [API Conventions](./docs/api-conventions.md) — Internal routes, ActiveMap proxy, PATCH format

## Code Style Guides

- [Python](./code_styleguides/python.md)
- [JavaScript](./code_styleguides/javascript.md)
- [HTML/CSS](./code_styleguides/html-css.md)

## Tracks

- [Tracks Registry](./tracks.md) — Все треки разработки
- [Tracks Directory](./tracks/) — Папки треков с планами и артефактами

## Quick Reference

| | |
|--|--|
| **Стек** | Python 3.11 + vanilla JS + HTML, stdlib only |
| **Сборка** | PyInstaller → `ActiveMapReviewer.exe` |
| **Целевая ОС** | Windows 10/11 |
| **Порт** | localhost:8765 |
| **API** | ActiveMap REST, sao.geofsm.ru, apiVersion=2.0 |
| **Цвет акцента** | #c8a96a (золотой) |
| **Топбар** | #1a1a2e (тёмный) |
