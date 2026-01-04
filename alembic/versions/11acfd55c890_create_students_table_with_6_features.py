"""create students table with 6 features

Revision ID: 11acfd55c890
Revises: 
Create Date: 2026-01-04 12:03:56.383218

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '11acfd55c890'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('students',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('course', sa.String(length=255), nullable=False),
        sa.Column('attendance_rate', sa.Float(), nullable=False),
        sa.Column('homework_completion', sa.Float(), nullable=False),
        sa.Column('test_avg_score', sa.Float(), nullable=False),
        sa.Column('communication_activity', sa.Integer(), nullable=False),
        sa.Column('days_enrolled', sa.Integer(), nullable=False),
        sa.Column('missed_classes_streak', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_students_email'), 'students', ['email'], unique=True)
    op.create_index(op.f('ix_students_id'), 'students', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_students_id'), table_name='students')
    op.drop_index(op.f('ix_students_email'), table_name='students')
    op.drop_table('students')
