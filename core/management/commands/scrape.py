from django.core.management.base import BaseCommand
from core.scrapers import crawl_llm_examples
from core.tasks import generate_posts_for_all_remixables

class Command(BaseCommand):
    help = 'Run the crawl_llm_examples function from scrapers.py'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-crawl',
            action='store_true',
            help='Skip the crawling step and only generate posts',
        )

    def handle(self, *args, **kwargs):
        if not kwargs['skip_crawl']:
            self.stdout.write(self.style.SUCCESS('Starting the crawl_llm_examples function...'))
            crawl_llm_examples()
            self.stdout.write(self.style.SUCCESS('Finished running the crawl_llm_examples function.'))
        else:
            self.stdout.write(self.style.SUCCESS('Skipping crawl step...'))

        self.stdout.write(self.style.SUCCESS('Starting the generate_posts_for_all_remixables function...'))
        generate_posts_for_all_remixables()
        self.stdout.write(self.style.SUCCESS('Finished running the generate_posts_for_all_remixables function.'))
