"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2025-08-31
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('api_key', sa.String(), nullable=True, unique=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    op.create_table(
        'regulators',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('country', sa.String(), nullable=True),
        sa.Column('sector', sa.String(), nullable=True),
        sa.Column('website', sa.String(), nullable=True),
    )

    op.create_table(
        'vendors',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('website', sa.String(), nullable=True),
        sa.Column('contact_email', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
    )

    op.create_table(
        'compliance_standards',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('version', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('regulator_id', sa.Integer(), sa.ForeignKey('regulators.id'), nullable=True),
    )
    op.create_index('ix_standards_name', 'compliance_standards', ['name'], unique=True)

    op.create_table(
        'controls',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('standard_id', sa.Integer(), sa.ForeignKey('compliance_standards.id'), nullable=False),
        sa.Column('control_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('implementation_guidance', sa.String(), nullable=True),
        sa.Column('is_mandatory', sa.Boolean(), nullable=True),
    )

    op.create_table(
        'assessments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('control_id', sa.Integer(), sa.ForeignKey('controls.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('evidence', sa.String(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('assessed_at', sa.DateTime(), nullable=True),
        sa.Column('next_review_date', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('ts', sa.DateTime(), nullable=True, index=True),
        sa.Column('user_email', sa.String(), nullable=True),
        sa.Column('method', sa.String(), nullable=False),
        sa.Column('path', sa.String(), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('ip', sa.String(), nullable=True),
    )

    op.create_table(
        'evidence',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('control_id', sa.Integer(), sa.ForeignKey('controls.id'), nullable=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=True),
        sa.Column('original_filename', sa.String(), nullable=True),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('path', sa.String(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=True),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('sha256', sa.String(), nullable=True),
        sa.Column('storage', sa.String(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_evidence_control', 'evidence', ['control_id'])

    op.create_table(
        'vendor_regulator',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('vendor_id', sa.Integer(), sa.ForeignKey('vendors.id'), nullable=False),
        sa.Column('regulator_id', sa.Integer(), sa.ForeignKey('regulators.id'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
    )

    op.create_table(
        'vendor_tenant',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('vendor_id', sa.Integer(), sa.ForeignKey('vendors.id'), nullable=False),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
    )

    op.create_table(
        'connectors',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('vendor_id', sa.Integer(), sa.ForeignKey('vendors.id'), nullable=True),
        sa.Column('regulator_id', sa.Integer(), sa.ForeignKey('regulators.id'), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('connectors')
    op.drop_table('vendor_tenant')
    op.drop_table('vendor_regulator')
    op.drop_index('ix_evidence_control', table_name='evidence')
    op.drop_table('evidence')
    op.drop_table('audit_logs')
    op.drop_table('assessments')
    op.drop_table('controls')
    op.drop_index('ix_standards_name', table_name='compliance_standards')
    op.drop_table('compliance_standards')
    op.drop_table('vendors')
    op.drop_table('regulators')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
    op.drop_table('tenants')

