from contextlib import contextmanager
from io import StringIO

from django.core import management
from django.core.management.base import BaseCommand
from django.db import connection


def reset_db():
    """
    Reset database to a blank state by removing all the tables and recreating them.
    """
    with connection.cursor() as cursor:
        cursor.execute("select tablename from pg_tables where schemaname = 'public'")
        tables = [row[0] for row in cursor.fetchall()]

        # Can't use query parameters here as they'll add single quotes which are not
        # supported by postgres
        for table in tables:
            cursor.execute('drop table "' + table + '" cascade')

    # Call migrate so that post-migrate hooks such as generating a default Site object
    # are run
    management.call_command("migrate", "--noinput", stdout=StringIO())


class Command(BaseCommand):
    help = "Reset the database and load test data"

    def add_arguments(self, parser):
        parser.add_argument(
            "-y",
            "--yes",
            action="store_true",
            dest="force_yes",
            default=False,
            help="Don't ask for confirmation.",
        )

    @contextmanager
    def print_step(self, message):
        self.stdout.write(message, ending=" ")
        self.stdout.flush()
        yield
        self.stdout.write(self.style.SUCCESS("OK"))

    def handle(self, *args, **options):
        with self.print_step("Resetting the database..."):
            reset_db()
