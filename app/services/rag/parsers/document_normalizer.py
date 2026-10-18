import logging
from functools import singledispatchmethod

from docling_core.types.doc import (
    DocItem,
    DoclingDocument,
    ListItem,
    SectionHeaderItem,
    TableItem,
    TextItem,
    TitleItem,
)

from app.schemas.normalized_document import (
    DocumentBlock,
    DocumentBlockType,
    ListItemBlock,
    NormalizedDocument,
    SectionHeaderBlock,
    TableBlock,
    TableCell,
    TextBlock,
)

logger = logging.getLogger(__name__)


class DocumentNormalizer:
    def normalize(self, document: DoclingDocument) -> NormalizedDocument:
        blocks: list[DocumentBlock] = []

        for item, hierarchy_level in document.iterate_items():
            block = self._normalize_item(item, hierarchy_level=hierarchy_level)

            if block is not None:
                blocks.append(block)

        origin = document.origin

        return NormalizedDocument(
            source_name=origin.filename if origin else document.name,
            mime_type=origin.mimetype if origin else None,
            blocks=blocks,
        )

    @singledispatchmethod
    def _normalize_item(self, item, *, hierarchy_level: int) -> DocumentBlock | None:
        logger.warning("Unsupported Docling item skipped: %s", type(item).__name__)
        return None

    @_normalize_item.register(TitleItem)
    def _normalize_title(self, item: TitleItem, *, hierarchy_level: int) -> TextBlock | None:
        if not item.text.strip():
            return None

        return TextBlock(
            type=DocumentBlockType.TITLE,
            text=item.text,
            hierarchy_level=hierarchy_level,
            pages=self._extract_pages(item),
        )

    @_normalize_item.register(SectionHeaderItem)
    def _normalize_section_header(
        self,
        item: SectionHeaderItem,
        *,
        hierarchy_level: int,
    ) -> SectionHeaderBlock | None:
        if not item.text.strip():
            return None

        return SectionHeaderBlock(
            type=DocumentBlockType.SECTION_HEADER,
            text=item.text,
            heading_level=item.level,
            hierarchy_level=hierarchy_level,
            pages=self._extract_pages(item),
        )

    @_normalize_item.register(ListItem)
    def _normalize_list_item(self, item: ListItem, *, hierarchy_level: int) -> ListItemBlock | None:
        if not item.text.strip():
            return None

        return ListItemBlock(
            type=DocumentBlockType.LIST_ITEM,
            text=item.text,
            enumerated=item.enumerated,
            marker=item.marker,
            hierarchy_level=hierarchy_level,
            pages=self._extract_pages(item),
        )

    @_normalize_item.register(TextItem)
    def _normalize_text(self, item: TextItem, *, hierarchy_level: int) -> TextBlock | None:
        if not item.text.strip():
            return None

        return TextBlock(
            type=DocumentBlockType.TEXT,
            text=item.text,
            semantic_role=item.label.value,
            hierarchy_level=hierarchy_level,
            pages=self._extract_pages(item),
        )

    @_normalize_item.register(TableItem)
    def _normalize_table(self, item: TableItem, *, hierarchy_level: int) -> TableBlock:
        cells = [
            TableCell(
                text=cell.text,
                row_start=cell.start_row_offset_idx,
                row_end=cell.end_row_offset_idx,
                col_start=cell.start_col_offset_idx,
                col_end=cell.end_col_offset_idx,
                row_span=cell.row_span,
                col_span=cell.col_span,
                column_header=cell.column_header,
                row_header=cell.row_header,
                row_section=cell.row_section,
            )
            for cell in item.data.table_cells
        ]

        return TableBlock(
            type=DocumentBlockType.TABLE,
            hierarchy_level=hierarchy_level,
            pages=self._extract_pages(item),
            num_rows=item.data.num_rows,
            num_cols=item.data.num_cols,
            cells=cells,
        )

    @staticmethod
    def _extract_pages(item: DocItem) -> list[int]:
        return sorted({provenance.page_no for provenance in item.prov})