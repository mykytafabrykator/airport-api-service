import time

from django.core.management.base import BaseCommand
from django.db import connection, OperationalError


class Command(BaseCommand):
    help_info = "Wait for the database to be available"

    def handle(self, *args, **options):
        db_connection = None
        while not db_connection:
            try:
                connection.ensure_connection()
                db_connection = True
            except OperationalError:
                time.sleep(1)
