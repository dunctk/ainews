from django.core.management.base import BaseCommand
from core.scrapers import sync_remixables_to_airtable

class Command(BaseCommand):
    help = 'Syncs Remixables with remixed content to Airtable'

    def handle(self, *args, **options):
        self.stdout.write('Starting sync to Airtable...')
        sync_remixables_to_airtable()
        self.stdout.write(self.style.SUCCESS('Successfully synced to Airtable')) 