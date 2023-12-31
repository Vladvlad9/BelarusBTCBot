"""create table

Revision ID: c8e0bf71898f
Revises: 
Create Date: 2023-07-26 11:04:05.840675

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8e0bf71898f'
down_revision = None
branch_labels = None
depends_on = None


# нужно не забыть сделать на новом сервере
# Select pg_get_serial_sequence('sales', 'sale_id');
# SELECT setval('public.sales_sale_id_seq', 549112, false);

# Select pg_get_serial_sequence('purchases', 'purchase_id');
# SELECT setval('public.purchases_purchase_id_seq', 449112, false);


def upgrade() -> None:
    op.create_table('users',
                    sa.Column('id', sa.BigInteger(), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('date_created', sa.DateTime(), nullable=True),
                    sa.Column('transaction_timer', sa.Boolean(), default=False),
                    sa.Column('captcha', sa.String(), default=False),
                    sa.Column('check_captcha', sa.Boolean(), default=False),

                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('purchases',
                    sa.Column('id', sa.BigInteger()),
                    sa.Column('purchase_id', sa.Integer(), autoincrement=True, start=549112),
                    sa.Column('user_id', sa.BigInteger()),
                    sa.Column('currency', sa.String(10)),
                    sa.Column('coin', sa.String(10)),
                    sa.Column('wallet', sa.Text()),
                    sa.Column('quantity', sa.Float()),
                    sa.Column('price_per_unit', sa.Float()),
                    sa.Column('commission', sa.String()),
                    sa.Column('date', sa.DateTime()),
                    sa.Column('status', sa.Boolean()),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),

                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('sales',
                    sa.Column('id', sa.BigInteger()),
                    sa.Column('sale_id', sa.Integer(), autoincrement=True, start_with=449112),
                    sa.Column('user_id', sa.BigInteger()),
                    sa.Column('currency', sa.String(10)),
                    sa.Column('coin', sa.String(10)),
                    sa.Column('erip', sa.String(11)),
                    sa.Column('quantity', sa.Float()),
                    sa.Column('price_per_unit', sa.Float()),
                    sa.Column('commission', sa.String()),
                    sa.Column('date', sa.DateTime()),
                    sa.Column('status', sa.Boolean()),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),

                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('transactions',
                    sa.Column('id', sa.BigInteger()),
                    sa.Column('purchase_id', sa.BigInteger()),
                    sa.Column('sale_id', sa.BigInteger()),
                    sa.Column('date', sa.DateTime()),
                    sa.Column('status', sa.Boolean()),
                    sa.ForeignKeyConstraint(['purchase_id'], ['purchases.id'], ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['sale_id'], ['sales.id'], ondelete='CASCADE'),

                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('sales')
    op.drop_table('purchases')
    op.drop_table('users')
    op.drop_table('users')
