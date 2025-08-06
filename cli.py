#!/usr/bin/env python3
"""
Simple CLI tool for database migrations using Alembic.

This script provides two main commands:
- migrate: Create a new migration
- upgrade: Upgrade database to head
"""

import sys
from pathlib import Path

import click
from alembic import command
from alembic.config import Config


def get_alembic_config():
    """Get Alembic configuration."""
    script_dir = Path(__file__).parent.absolute()
    alembic_cfg_path = script_dir / "alembic.ini"

    if not alembic_cfg_path.exists():
        click.echo(f"Error: alembic.ini not found at {alembic_cfg_path}", err=True)
        sys.exit(1)

    return Config(str(alembic_cfg_path))


@click.group()
def cli():
    """Simple database migration tool for ContactForm project."""


@cli.command()
@click.option(
    "--message", "-m",
    required=True,
    help="Message describing the migration"
)
def migrate(message):
    """Create a new migration with auto-generated changes.

    Example:
        python cli.py migrate -m "Add user table"
    """
    try:
        config = get_alembic_config()
        command.revision(config, message=message, autogenerate=True)
        click.echo(f"✓ Created new migration: {message}")
    except Exception as e:
        click.echo(f"Error creating migration: {e}", err=True)
        sys.exit(1)


@cli.command()
def upgrade():
    """Upgrade database to the latest migration (head).

    Example:
        python cli.py upgrade
    """
    try:
        config = get_alembic_config()
        command.upgrade(config, "head")
        click.echo("✓ Database upgraded to latest migration")
    except Exception as e:
        click.echo(f"Error upgrading database: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
