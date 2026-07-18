## MCP Server

В проект добавлен MCP-сервер для подключения LLM-клиента к данным приложения.

MCP-сервер работает как отдельный слой поверх существующего FastAPI/SQLAlchemy/PostgreSQL проекта и предоставляет набор read-only tools для работы с документами и структурой базы данных.

### Что такое MCP в этом проекте

MCP, или Model Context Protocol, используется как способ дать языковой модели ограниченный доступ к внешнему контексту приложения.

Вместо того чтобы передавать модели все данные вручную, LLM-клиент может вызвать заранее описанные tools:

* получить список документов;
* получить metadata конкретного документа;
* прочитать текст документа по `storage_path`;
* выполнить поиск по metadata документов;
* посмотреть список таблиц в БД;
* посмотреть структуру таблицы `documents`.

Примерная схема:

```text
LLM Client
  ↓
MCP Server
  ↓
Async SQLAlchemy
  ↓
PostgreSQL
  ↓
documents table
  ↓
file storage
```

### Реализованные MCP tools

#### `list_documents(limit: int = 20)`

Возвращает список последних загруженных документов из таблицы `documents`.

Используется для того, чтобы LLM могла увидеть, какие документы есть в системе, и получить их `id`.

#### `get_document(document_id: int)`

Возвращает metadata одного документа по его `id`.

Возвращаемые данные:

* `id`;
* `filename`;
* `storage_path`;
* `content_type`;
* `status`;
* `created_at`.

#### `read_document_text(document_id: int, max_chars: int = 4000)`

Читает реальный файл с диска по пути `storage_path`, который хранится в БД.

Файл читается асинхронно через `aiofiles`.

Ограничения:

* хорошо работает с текстовыми файлами: `.txt`, `.md`, `.json`, `.csv`;
* PDF/DOCX пока не парсятся как документы;
* для больших файлов используется ограничение `max_chars`, чтобы не перегружать LLM-контекст.

#### `search_documents(query: str, limit: int = 20)`

Ищет документы по metadata:

* `filename`;
* `content_type`.

Это простой metadata-search, не полноценный RAG.

#### `list_database_tables()`

Возвращает список таблиц в PostgreSQL.

Используется для dev-assistant сценариев, когда LLM нужно понять структуру базы данных.

#### `describe_documents_table()`

Возвращает структуру таблицы `documents`: названия колонок, типы, nullable и default-значения.

### Безопасность

На текущем этапе MCP tools работают в read-only режиме.

Сервер:

* не изменяет данные в БД;
* не выполняет произвольный SQL от модели;
* не удаляет документы;
* не изменяет файлы на диске;
* только читает данные из таблицы `documents`;
* читает только файл, путь к которому уже сохранён в `storage_path`.

Это снижает риск случайного изменения данных через LLM.

### Docker-запуск

Проект запускается через Docker Compose.

Основные сервисы:

* `api` — FastAPI-приложение;
* `db` — PostgreSQL/pgvector;
* `pgadmin` — интерфейс для работы с БД;
* `mcp` — MCP-сервер.

Запуск проекта:

```bash
docker compose up -d --build
```

Применение миграций:

```bash
docker compose exec api alembic upgrade head
```

Запуск MCP-сервера:

```bash
docker compose run --rm mcp
```

MCP-сервер работает в `stdio`-режиме и ожидает подключения MCP-клиента.

### Проверка MCP tools без внешнего клиента

Для локальной проверки добавлен dev-скрипт:

```bash
docker compose run --rm mcp python -m scripts.check_mcp_tools
```

Скрипт проверяет:

* получение списка документов;
* получение документа по ID;
* чтение текста файла;
* поиск документа;
* получение списка таблиц;
* получение структуры таблицы `documents`.

### Тестовый документ

Для проверки можно создать текстовый файл внутри контейнера:

```bash
docker compose exec api mkdir -p /app/uploads
docker compose exec api sh -c "echo 'This is test document for MCP server.' > /app/uploads/test.txt"
```

Добавить запись в БД:

```bash
docker compose exec db psql -U postgres -d doc_ai
```

```sql
INSERT INTO documents (filename, storage_path, content_type, status, created_at)
VALUES (
    'test.txt',
    '/app/uploads/test.txt',
    'text/plain',
    'ready',
    NOW()
);
```

После этого MCP tool `read_document_text(document_id=1)` сможет прочитать реальный файл из `/app/uploads/test.txt`.

### Текущий статус

На текущем этапе реализован MVP MCP-интеграции.

Проект уже умеет:

* запускать MCP-сервер в Docker;
* использовать существующий async SQLAlchemy engine;
* читать данные из PostgreSQL;
* читать реальные файлы из Docker volume;
* отдавать данные LLM-клиенту через MCP tools.

### Ограничения

Текущая версия не является production-ready.

Ограничения:

* нет авторизации MCP-клиента;
* нет полноценного RAG-поиска;
* нет embeddings;
* нет таблицы `document_chunks`;
* нет semantic search через pgvector;
* PDF/DOCX пока не парсятся;
* нет Git tools;
* нет аудита вызовов MCP tools.

### Возможные улучшения

Следующие шаги:

* добавить MCP tools для Git:

  * `get_git_status`;
  * `list_recent_commits`;
  * `show_commit_diff`;
* добавить таблицу `document_chunks`;
* добавить embeddings;
* добавить pgvector semantic search;
* добавить parser service для PDF/DOCX;
* добавить авторизацию и контроль доступа;
* добавить логирование вызовов tools.

### Git tools

Для работы с Git реализован отдельный набор read-only инструментов.

#### git_current_branch()

Возвращает текущую ветку Git.

#### git_status()

Возвращает статус рабочего дерева (аналог `git status --short --branch`).

#### git_log(limit)

Возвращает последние коммиты.

#### git_diff(file_path=None)

Возвращает незакоммиченные изменения.

Если указан `file_path`, diff строится только для этого файла.

#### git_staged_diff()

Возвращает изменения, добавленные в staging (`git diff --cached`).

#### git_show_commit(commit_hash)

Возвращает информацию о коммите вместе с patch.