from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command('makemigrations')
        call_command('migrate')
        # call_command('loaddata', 'tests/fixtures/admin.json')
        call_command('loaddata', 'tests/fixtures/category.json')
        # call_command('loaddata', 'tests/fixtures/product.json')
