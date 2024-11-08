from core.tasks import generate_post_for_all_stories, get_stories, process_stories
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Runs the relevant page finder, post creator and post content generator'

    def handle(self, *args, **kwargs):
        process_stories(get_stories())
        generate_post_for_all_stories()