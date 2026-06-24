import aiofiles

from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from sqlalchemy import inspect, select
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import MCP_SERVER_NAME
from app.db.engine import async_session, engine
from app.db.models.document import Document


mcp = FastMCP(MCP_SERVER_NAME)


def serialize_document(document: Document) -> dict[str, Any]:
    return {
        "id": document.id,
        "filename": document.filename,
        "storage_path": document.storage_path,
        "content_type": document.content_type,
        "status": document.status.value if document.status else None,
        "created_at": document.created_at.isoformat() if document.created_at else None,
    }


@mcp.tool()
async def list_documents(limit: int = 20) -> list[dict[str, Any]]:
    """
    How LLM uses this:
    1) the model can understand what document are in system.
    2) it can that call get_documents() or read_document_text() by ID.
    """

    limit = max(1, min(limit, 100))

    try:
        async with async_session() as session:
            stmt = (select(Document).order_by(Document.created_at.desc()).limit(limit))
            result = await session.execute(stmt)
            documents = result.scalars().all()

            return [serialize_document(document) for document in documents]

    except SQLAlchemyError as error:
        return [{"error": f"Database error: {str(error)}"}]

@mcp.tool()
async def get_document(document_id: int) -> dict[str, Any]:

    if document_id < 1:
        return {"error": "Document id must be positive"}

    try:
        async with async_session() as session:
            document = await session.get(Document, document_id)

            if document is None:
                return {"error": "Document not found"}

            return serialize_document(document)

    except SQLAlchemyError as error:
        return {"error": f"Database error: {str(error)}"}

@mcp.tool()
async def read_document_text(document_id: int, max_chars: int = 4000) -> dict[str, Any]:
    """
    Reads a real file from disk using storage_path from the database.
    """

    if document_id < 1:
        return {"error": "Document id must be positive"}

    max_chars = max(100, min(max_chars, 20_000))

    try:
        async with async_session() as session:
            document = await session.get(Document, document_id)

            if document is None:
                return {"error": "Document not found"}

            file_path = Path(document.storage_path)

            if not file_path.exists():
                return {
                    "error": f"File {document.storage_path} does not exist.",
                    "document": serialize_document(document)
                }

            if not file_path.is_file():
                return {
                    "error": "Storage path is not a file",
                    "document": serialize_document(document),
                }

            async with aiofiles.open(file_path, mode='r', encoding='utf-8', errors="ignore") as file:
                text = await file.read(max_chars + 1)

                return {
                    "document": serialize_document(document),
                    "text": text[:max_chars],
                    "truncated": len(text) > max_chars,
                    "read_chars": min(len(text), max_chars),
                    "file_size_bytes": file_path.stat().st_size
                }

    except OSError as error:
        return {"error": f"File read error: {str(error)}"}

    except UnicodeDecodeError as error:
        return {"error": f"File decode error: {str(error)}"}

    except SQLAlchemyError as error:
        return {"error": f"Database error: {str(error)}"}

@mcp.tool()
async def search_documents(query: str, limit: int = 20) -> list[dict[str, Any]]:
    """
    Search documents by metadata: file name and content_type.
    """

    query = query.strip()

    if not query:
        return [{"error": "query must not be empty"}]

    limit = max(1, min(limit, 100))

    try:
        async with async_session() as session:
            search_pattern = f"%{query}%"

            stmt = (select(Document).where(
                    Document.filename.ilike(search_pattern)
                    | Document.content_type.ilike(search_pattern)).order_by(Document.created_at.desc()).limit(limit))

            result = await session.execute(stmt)
            documents = result.scalars().all()

            return [serialize_document(document) for document in documents]

    except SQLAlchemyError as error:
        return [{"error": f"Database error: {str(error)}"}]

@mcp.tool()
async def list_database_tables() -> list[str]:
    """
    Returns a list of tables in database.

    How LLM uses this:
    1) LLM can understand the structure of database tables.
    2) this is useful for dev-assistant scenarios.
    3) tool works read-only.
    """

    try:
        async with engine.connect() as connection:
            tables = await connection.run_sync(lambda sync_connection: inspect(sync_connection).get_table_names())

            return tables

    except SQLAlchemyError as error:
        return [f"Database error: {str(error)}"]

@mcp.tool()
async def describe_documents_table() -> list[dict[str, Any]]:
    """
    Returns structure of documents table.
    """

    try:
        async with engine.connect() as connection:
            columns = await connection.run_sync(lambda sync_connection: inspect(sync_connection).get_columns("documents"))

            return [
                {
                    "name": column["name"],
                    "type": str(column["type"]),
                    "nullable": column["nullable"],
                    "default": str(column["default"]),
                } for column in columns
            ]


    except SQLAlchemyError as error:
        return [{"error": f"Database error: {str(error)}"}]

if __name__ == "__main__":
    mcp.run()
















