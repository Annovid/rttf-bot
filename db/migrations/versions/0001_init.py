from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "user_configs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("config", sa.JSON, nullable=False),
    )


def downgrade():
    op.drop_table("user_configs")
