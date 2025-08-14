"""Create users table

Revision ID: 001
Revises: 
Create Date: 2025-08-11 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('user_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('organization_name', sa.String(length=255), nullable=False),
        sa.Column('user_name', sa.String(length=255), nullable=False),
        sa.Column('contact_phone', sa.String(length=20), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('logo_path', sa.String(length=500), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('user_id')
    )
    
    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_organization', 'users', ['organization_name'], unique=False)
    op.create_index('idx_users_created_at', 'users', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_users_created_at', table_name='users')
    op.drop_index('idx_users_organization', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
    
    # Drop table
    op.drop_table('users')