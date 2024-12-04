from django.core.management.base import BaseCommand
from core.scrapers import print_airtable_schema

class Command(BaseCommand):
    help = 'Prints the schema of the Airtable remixables table'

    def handle(self, *args, **options):
        self.stdout.write('Fetching Airtable schema...')
        print_airtable_schema() 