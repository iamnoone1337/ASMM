from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250918_0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'owners',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_table(
        'scans',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('domain', sa.String(), nullable=False, index=True),
        sa.Column('scope', sa.JSON(), nullable=True),
        sa.Column('bruteforce', sa.Boolean(), default=False),
        sa.Column('resolution', sa.Boolean(), default=False),
        sa.Column('notify', sa.Boolean(), default=False),
        sa.Column('status', sa.String(), default='pending'),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('requested_by', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
    )
    op.create_table(
        'scan_jobs',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('scan_id', sa.String(), sa.ForeignKey('scans.id', ondelete='CASCADE'), nullable=False),
        sa.Column('connector', sa.String(), nullable=False),
        sa.Column('status', sa.String(), default='pending'),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
    )
    op.create_table(
        'assets',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('domain', sa.String(), nullable=False, index=True),
        sa.Column('subdomain', sa.String(), nullable=False),
        sa.Column('normalized', sa.String(), nullable=False, index=True),
        sa.Column('resolved', sa.Boolean(), default=False),
        sa.Column('ips', sa.JSON(), nullable=True),
        sa.Column('rrtypes', sa.JSON(), nullable=True),
        sa.Column('first_seen', sa.DateTime(), nullable=True),
        sa.Column('last_seen', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('domain','normalized', name='uq_domain_normalized'),
    )
    op.create_index('ix_assets_domain_normalized', 'assets', ['domain','normalized'])
    op.create_table(
        'asset_sources',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('asset_id', sa.String(), sa.ForeignKey('assets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('proof', sa.JSON(), nullable=True),
        sa.Column('first_seen', sa.DateTime(), nullable=True),
        sa.Column('last_seen', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_asset_sources_asset_id_source', 'asset_sources', ['asset_id','source'])

def downgrade():
    op.drop_index('ix_asset_sources_asset_id_source', table_name='asset_sources')
    op.drop_table('asset_sources')
    op.drop_index('ix_assets_domain_normalized', table_name='assets')
    op.drop_table('assets')
    op.drop_table('scan_jobs')
    op.drop_table('scans')
    op.drop_table('owners')