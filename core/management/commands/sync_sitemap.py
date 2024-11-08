from django.core.management.base import BaseCommand
from core.tasks import sync_sitemap

class Command(BaseCommand):
    help = 'Syncs the sitemap'

    def handle(self, *args, **kwargs):
        sync_sitemap()
