"""Create user_api_usage table

Revision ID: 003
Revises: 002
Create Date: 2025-08-15 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create user_api_usage table and related indexes/triggers."""
    
    # Create user_api_usage table
    op.create_table(
        'user_api_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('allowed_api_calls', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('performed_api_calls', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('user_created_date', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('user_expiry_date', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], name='fk_user_api_usage_user_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_user_api_usage_user_id', 'user_api_usage', ['user_id'])
    op.create_index('idx_user_api_usage_expiry', 'user_api_usage', ['user_expiry_date'])
    
    # Create function to update updated_at timestamp
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    # Create trigger to automatically update updated_at timestamp
    op.execute("""
        CREATE TRIGGER update_user_api_usage_timestamp 
            BEFORE UPDATE ON user_api_usage
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    """Drop user_api_usage table and related objects."""
    
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS update_user_api_usage_timestamp ON user_api_usage;")
    
    # Drop function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")
    
    # Drop indexes
    op.drop_index('idx_user_api_usage_expiry', table_name='user_api_usage')
    op.drop_index('idx_user_api_usage_user_id', table_name='user_api_usage')
    
    # Drop table
    op.drop_table('user_api_usage')