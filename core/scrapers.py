from usp.tree import sitemap_tree_for_homepage
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import requests
from core.models import Remixable, RemixableImage
from logging import getLogger
import os
from pyairtable import Api
from typing import Dict, Any

logger = getLogger(__name__)

def crawl_llm_examples():
    logger.info("Starting to crawl LLM examples")
    def get_example_url(page_url: str) -> str | None:
        try:
            response = requests.get(page_url)
            soup = BeautifulSoup(response.text, "html.parser")
            link = soup.find("a", class_="llm-link")
            
            if link is None:
                print(f"No llm-link found on {page_url}")
                return None
            
            return link.get("href") or link.text.strip()
        except Exception as e:
            print(f"Error processing {page_url}: {str(e)}")
            return None
        
    def get_llm_example_content(example_url: str) -> dict:
        try:
            html_content = requests.get(example_url).text
            soup = BeautifulSoup(html_content, "html.parser")
            title = soup.find("meta", property="og:title")["content"]
            markdown_content = md(html_content)
            
            # Extract all image URLs
            image_urls = []
            for img in soup.find_all('img'):
                src = img.get('src')
                if src and src.startswith(('http://', 'https://')):
                    image_urls.append(src)
            
            return {
                "title": title,
                "markdown_content": markdown_content,
                "image_urls": image_urls
            }
        except Exception as e:
            print(f"Error processing {example_url}: {str(e)}")
            return None
    

    sitemap = sitemap_tree_for_homepage("https://www.zenml.io/sitemap.xml")
    pages = sitemap.all_pages()
    llm_example_pages = [page for page in pages if "llmops-database" in page.url]
    for page in llm_example_pages:
        print(page.url) 
        example_url = get_example_url(page.url)
        if example_url is None:
            continue
        print(example_url, '\n')
        if 'youtube' in example_url:
            remixable, _ = Remixable.objects.get_or_create(url=example_url, defaults={"is_video": True})
        else:
            example_content = get_llm_example_content(example_url)
            if not example_content:
                continue
            image_urls = example_content.pop('image_urls', [])
            remixable, _ = Remixable.objects.get_or_create(url=example_url, defaults=example_content)
            
            # Save associated images
            for image_url in image_urls:
                RemixableImage.objects.get_or_create(
                    remixable=remixable,
                    image_url=image_url
                )
    logger.info("Finished crawling LLM examples")
    logger.info(f"{Remixable.objects.count()} remixables now in db")

def print_airtable_schema():
    AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
    BASE_ID = 'app1qC1c10uiW1DRr'
    TABLE_ID = 'tbllQR6GmaJD579oS'
    
    api = Api(AIRTABLE_API_KEY)
    table = api.table(BASE_ID, TABLE_ID)
    
    # Fetch a single record to examine the schema
    records = table.all(max_records=1)
    if records:
        print("Airtable Schema:")
        for field, value in records[0]['fields'].items():
            print(f"{field}: {type(value).__name__}")
    else:
        print("No records found in Airtable")

def sync_airtable_remixables():
    AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
    BASE_ID = 'app1qC1c10uiW1DRr'
    TABLE_ID = 'tbllQR6GmaJD579oS'
    
    api = Api(AIRTABLE_API_KEY)
    table = api.table(BASE_ID, TABLE_ID)
    
    records = table.all()
    logger.info(f"Found {len(records)} records in Airtable")
    
    for record in records:
        fields = record['fields']
        video_url = fields.get('video_url')
        remixed_as = fields.get('post')  # The 'post' field contains the remixed content
        
        if not video_url:
            continue
            
        try:
            remixable, created = Remixable.objects.get_or_create(
                url=video_url,
                defaults={
                    'remixed_as': remixed_as,
                    'title': fields.get('video_title'),
                    'is_video': True,  # These are all videos
                    'markdown_content': fields.get('transcript')  # Store transcript in markdown_content
                }
            )
            
            if not created:
                # Update fields if they've changed
                remixable.remixed_as = remixed_as
                remixable.title = fields.get('video_title')
                remixable.markdown_content = fields.get('transcript')
                remixable.save()
                
            # Handle images if present
            images = fields.get('image', [])
            if images:
                for image_url in images:
                    RemixableImage.objects.get_or_create(
                        remixable=remixable,
                        image_url=image_url
                    )
                
            logger.info(f"{'Created' if created else 'Updated'} remixable: {video_url}")
            
        except Exception as e:
            logger.error(f"Error processing record {video_url}: {str(e)}")

def sync_remixables_to_airtable():
    AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
    BASE_ID = 'app1qC1c10uiW1DRr'
    TABLE_ID = 'tbllQR6GmaJD579oS'
    
    api = Api(AIRTABLE_API_KEY)
    table = api.table(BASE_ID, TABLE_ID)
    
    # Get all remixables that have remixed_as content
    remixables = Remixable.objects.exclude(remixed_as__isnull=True).exclude(remixed_as='').exclude(markdown_content__isnull=True)
    logger.info(f"Found {remixables.count()} remixables with remixed content")
    
    for remixable in remixables:
        try:
            # Prepare the record data
            fields = {
                'video_url': remixable.url,
                'video_title': remixable.title,
                'post': remixable.remixed_as,
                'transcript': remixable.markdown_content
            }
            
            # Try to find existing record by video_url
            existing_records = table.all(formula=f"{{video_url}}='{remixable.url}'")
            
            if existing_records:
                # Update existing record
                record_id = existing_records[0]['id']
                table.update(record_id, fields)
                logger.info(f"Updated Airtable record for: {remixable.url}")
            else:
                # Create new record
                table.create(fields)
                logger.info(f"Created new Airtable record for: {remixable.url}")
                
        except Exception as e:
            logger.error(f"Error syncing remixable {remixable.url} to Airtable: {str(e)}")
    
    logger.info("Finished syncing remixables to Airtable")


