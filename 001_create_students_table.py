"""create students table

Revision ID: 001
Revises: 
Create Date: 2024-01-01
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'students',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('Фамилия', sa.String(length=100), nullable=False),
        sa.Column('Имя', sa.String(length=100), nullable=False),
        sa.Column('Факультет', sa.String(length=50), nullable=False),
        sa.Column('Курс', sa.String(length=100), nullable=False),
        sa.Column('Оценка', sa.Integer(), nullable=False),
    )
    op.create_index(op.f('ix_students_Фамилия'), 'students', ['Фамилия'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_students_Фамилия'), table_name='students')
    op.drop_table('students')