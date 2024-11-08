from django.core.management.base import BaseCommand
from core.tasks import get_stories, process_stories

class Command(BaseCommand):
    help = 'Get news stories'

    def handle(self, *args, **kwargs):
        process_stories(get_stories())
