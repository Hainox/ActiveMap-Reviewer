# Spec: v2_rebuild_20260626

## Goal

Переписать ActiveMap Reviewer с нуля (v2.0.0), сохранив все функции v1.2.0 и добавив улучшения.

## Acceptance Criteria

### Phase 1: Foundation

- [ ] `reviewer.py` использует `logging` module — логи в `reviewer.log` рядом с .exe
- [ ] `auth_ready.wait()` при таймауте показывает ошибку пользователю
- [ ] `POST /patch/{taskId}` возвращает корректный HTTP-код при ошибке ActiveMap
- [ ] `/debug` и `/debug-task` работают только при `DEBUG=1` env var
- [ ] Все `except:` заменены на `except Exception as e:` с логированием

### Phase 2: Frontend Refactor

- [ ] `reviewer_html.html` разбит на логические секции с комментариями
- [ ] ~20 глобальных переменных заменены на `AppState` и `LightboxState` объекты
- [ ] Все `.catch(function(){})` заменены на catch с UI-уведомлением
- [ ] Кнопки решений блокируются (disabled) до получения ответа сервера

### Phase 3: Persistence

- [ ] Фильтры восстанавливаются из localStorage при запуске
- [ ] Кнопки решений (до 5) сохраняются и восстанавливаются из localStorage
- [ ] Индикатор загрузки организаций виден во время пагинированного запроса

### Phase 4: Feature Completion

- [ ] Заданий > 500: автоматическая загрузка следующей страницы (без предупреждения)
- [ ] Экспорт результатов сессии в CSV: номер задания, этап, стадия, timestamp
- [ ] История решений включает все задания, не только текущую страницу

### Phase 5: QA & Release

- [ ] Ручное тестирование по чеклисту из `conductor/docs/testing-patterns.md`
- [ ] `pyinstaller --onefile --noconsole` собирает .exe без ошибок
- [ ] .exe запускается на чистой Windows 10/11 (без Python)
- [ ] GitHub Actions создаёт Release с тегом `v2.0.0`
- [ ] `GET /version` возвращает `{"version": "2.0.0"}`

## Non-Functional

- .exe размером < 20MB, старт < 3 секунд
- Обработка 500 заданий без зависаний UI
- Все тексты на русском языке
