"""extend documents

Revision ID: 7958fc052542
Revises: 4f683e682438
Create Date: 2026-06-09 17:31:50.063735

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7958fc052542'
down_revision: Union[str, Sequence[str], None] = '4f683e682438'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    document_status_enum = sa.Enum("uploaded","processing","ready","failed",name="documentstatus",)
    document_status_enum.create(op.get_bind(), checkfirst=True)
    op.add_column( "documents",sa.Column("storage_path", sa.String(length=500), nullable=False),)
    op.add_column("documents",sa.Column(
            "status",
            document_status_enum,
            nullable=False,
            server_default="uploaded",
        ),
    )
    op.alter_column(
        "documents",
        "status",
        server_default=None,
    )

def downgrade() -> None:
    """Downgrade schema."""
    document_status_enum = sa.Enum("uploaded","processing","ready","failed",name="documentstatus",)
    op.drop_column("documents", "status")
    op.drop_column("documents", "storage_path")

    document_status_enum.drop(op.get_bind(), checkfirst=True)