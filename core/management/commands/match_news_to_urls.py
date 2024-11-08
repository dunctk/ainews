from django.core.management.base import BaseCommand
from core.models import Story
from core.tasks import find_relevant_page_for_story

class Command(BaseCommand):
    help = 'Finds the relevant page for a story'

    def handle(self, *args, **kwargs):
        story = Story.objects.get(id=1)
        find_relevant_page_for_story(story)
