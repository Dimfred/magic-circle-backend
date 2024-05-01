"""init

Revision ID: 2b164321f7f1
Revises: 
Create Date: 2024-05-01 19:26:41.715889

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel



# revision identifiers, used by Alembic.
revision: str = '2b164321f7f1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('circledb',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_circledb_name'), 'circledb', ['name'], unique=True)
    op.create_table('userdb',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('password', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_userdb_username'), 'userdb', ['username'], unique=True)
    op.create_table('carddb',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('foil', sa.Boolean(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('language', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('set_code', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('set_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('rarity', sa.Enum('common', 'uncommon', 'rare', 'mythic', name='rarity'), nullable=False),
    sa.Column('condition', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('scryfall_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['userdb.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('circleuserlinkdb',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('circle_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['circle_id'], ['circledb.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['userdb.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'circle_id')
    )
    op.create_table('usersessiondb',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['userdb.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('usersessiondb')
    op.drop_table('circleuserlinkdb')
    op.drop_table('carddb')
    op.drop_index(op.f('ix_userdb_username'), table_name='userdb')
    op.drop_table('userdb')
    op.drop_index(op.f('ix_circledb_name'), table_name='circledb')
    op.drop_table('circledb')
    # ### end Alembic commands ###
