from core.tasks import generate_post_for_all_stories, get_stories, process_stories, sync_sitemap
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Runs the relevant page finder, post creator and post content generator'

    def handle(self, *args, **kwargs):
        # First sync the sitemap
        self.stdout.write('Syncing sitemap...')
        sync_sitemap()
        
        # Then process stories and generate posts
        self.stdout.write('Processing stories...')
        process_stories(get_stories())
        generate_post_for_all_stories()