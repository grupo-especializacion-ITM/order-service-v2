"""new_migration

Revision ID: 280b728db17d
Revises: 
Create Date: 2025-03-30 20:00:57.949889

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '280b728db17d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute("CREATE SCHEMA IF NOT EXISTS order_service")

    # Create customers table
    op.create_table(
        'customers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v1()")),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('phone', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        schema='order_service'
    )

    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v1()")),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('delivery_address', postgresql.JSON(), nullable=True),
        sa.Column('total', postgresql.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ['customer_id'],
            ['order_service.customers.id'],  # 👉 referencia con schema
            name='fk_orders_customer_id_customers'
        ),
        schema='order_service'
    )

    # Create order_items table
    op.create_table(
        'order_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v1()")),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['order_id'],
            ['order_service.orders.id'],  # 👉 referencia con schema
            ondelete='CASCADE',
            name='fk_order_items_order_id_orders'
        ),
        schema='order_service'
    )

    # Create indexes
    op.create_index('ix_customers_email', 'customers', ['email'], unique=True, schema='order_service')
    op.create_index('ix_orders_customer_id', 'orders', ['customer_id'], schema='order_service')
    op.create_index('ix_orders_status', 'orders', ['status'], schema='order_service')
    op.create_index('ix_orders_created_at', 'orders', ['created_at'], schema='order_service')
    op.create_index('ix_order_items_order_id', 'order_items', ['order_id'], schema='order_service')
    op.create_index('ix_order_items_product_id', 'order_items', ['product_id'], schema='order_service')


def downgrade() -> None:
    op.drop_table('order_items', schema='order_service')
    op.drop_table('orders', schema='order_service')
    op.drop_table('customers', schema='order_service')
    op.execute("DROP SCHEMA order_service CASCADE")
