from app.core.config import Settings
from app.modules.rag.chunker.tiktoker_counter import TiktokCounter
from app.modules.rag.chunker.document_chunker import DocumentChunker
from app.schemas.chunking_config import ChunkingConfig


def create_chunker(setting: Settings) -> DocumentChunker:
    counter = TiktokCounter(encoding_name=setting.TOKENIZER_ENCODING)

    return DocumentChunker(
        token_counter=counter,
        config=ChunkingConfig()
    )




