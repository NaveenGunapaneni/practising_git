"""Create files table for file upload processing

Revision ID: 002
Revises: 001
Create Date: 2025-08-11 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create files table
    op.create_table('files',
        sa.Column('file_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('upload_date', sa.Date(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('line_count', sa.Integer(), nullable=True),
        sa.Column('storage_location', sa.String(length=500), nullable=False),
        sa.Column('input_location', sa.String(length=500), nullable=True),
        sa.Column('processed_flag', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('engagement_name', sa.String(length=255), nullable=True),
        sa.Column('browser_ip', sa.String(length=45), nullable=True),
        sa.Column('browser_location', sa.String(length=255), nullable=True),
        sa.Column('processing_time_seconds', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('file_size_mb', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('dates', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('file_id')
    )
    
    # Create foreign key constraint
    op.create_foreign_key(
        'fk_files_user_id', 
        'files', 
        'users', 
        ['user_id'], 
        ['user_id'], 
        ondelete='CASCADE'
    )
    
    # Create indexes for performance
    op.create_index('idx_files_user_id', 'files', ['user_id'], unique=False)
    op.create_index('idx_files_processed_flag', 'files', ['processed_flag'], unique=False)
    op.create_index('idx_files_upload_date', 'files', ['upload_date'], unique=False)
    op.create_index('idx_files_user_processed', 'files', ['user_id', 'processed_flag'], unique=False)
    op.create_index('idx_files_created_at', 'files', ['created_at'], unique=False)
    
    # Add file_count column to users table
    op.add_column('users', sa.Column('file_count', sa.Integer(), nullable=False, server_default=sa.text('0')))
    
    # Create function to update user file count
    op.execute("""
        CREATE OR REPLACE FUNCTION update_user_file_count()
        RETURNS TRIGGER AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                UPDATE users SET file_count = file_count + 1 WHERE user_id = NEW.user_id;
                RETURN NEW;
            ELSIF TG_OP = 'DELETE' THEN
                UPDATE users SET file_count = file_count - 1 WHERE user_id = OLD.user_id;
                RETURN OLD;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create trigger to automatically update file count
    op.execute("""
        CREATE TRIGGER trigger_update_user_file_count
            AFTER INSERT OR DELETE ON files
            FOR EACH ROW EXECUTE FUNCTION update_user_file_count();
    """)


def downgrade() -> None:
    # Drop trigger and function
    op.execute("DROP TRIGGER IF EXISTS trigger_update_user_file_count ON files;")
    op.execute("DROP FUNCTION IF EXISTS update_user_file_count();")
    
    # Remove file_count column from users table
    op.drop_column('users', 'file_count')
    
    # Drop indexes
    op.drop_index('idx_files_created_at', table_name='files')
    op.drop_index('idx_files_user_processed', table_name='files')
    op.drop_index('idx_files_upload_date', table_name='files')
    op.drop_index('idx_files_processed_flag', table_name='files')
    op.drop_index('idx_files_user_id', table_name='files')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_files_user_id', 'files', type_='foreignkey')
    
    # Drop table
    op.drop_table('files')