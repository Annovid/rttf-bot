from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create players table
    op.create_table(
        'players',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=False),
        sa.Column('name', sa.String, default=''),
    )

    # Create tournaments table
    op.create_table(
        'tournaments',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=False),
        sa.Column('tournament_date', sa.Date, nullable=False),
        sa.Column('info_json', sa.String, nullable=True),
        sa.Column('next_update_dtm', sa.Integer, nullable=True),
    )

    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column(
            'user_id',
            sa.Integer,
            sa.ForeignKey('user_configs.id'),
            primary_key=True,
        ),
        sa.Column(
            'player_id',
            sa.Integer,
            sa.ForeignKey('players.id'),
            primary_key=True,
        ),
    )

    # Create player_tournament table
    op.create_table(
        'player_tournament',
        sa.Column(
            'player_id',
            sa.Integer,
            sa.ForeignKey('players.id'),
            primary_key=True,
        ),
        sa.Column(
            'tournament_id',
            sa.Integer,
            sa.ForeignKey('tournaments.id'),
            primary_key=True,
        ),
        sa.Column('results_json', sa.String, nullable=True),
    )


def downgrade() -> None:
    # Drop player_tournament table
    op.drop_table('player_tournament')

    # Drop subscriptions table
    op.drop_table('subscriptions')

    # Drop tournaments table
    op.drop_table('tournaments')

    # Drop players table
    op.drop_table('players')
