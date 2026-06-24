import asyncio
import json

from app.mcp.server import (
    list_documents,
    get_document,
    read_document_text,
    search_documents,
    list_database_tables,
    describe_documents_table,
)


def print_result(title: str, data) -> None:
    print(f"\n===== {title} =====")
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))


async def main() -> None:
    documents = await list_documents()
    print_result("list_documents", documents)

    document = await get_document(document_id=1)
    print_result("get_document", document)

    text = await read_document_text(document_id=1, max_chars=4000)
    print_result("read_document_text", text)

    search_result = await search_documents(query="test")
    print_result("search_documents", search_result)

    tables = await list_database_tables()
    print_result("list_database_tables", tables)

    documents_table = await describe_documents_table()
    print_result("describe_documents_table", documents_table)


if __name__ == "__main__":
    asyncio.run(main())