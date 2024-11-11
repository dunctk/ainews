from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import requests
import requests_cache
import json
import logging
from django.utils.dateparse import parse_datetime
import advertools
from .models import Post, Source, Keyword, Country, Category, Story, SitemapURL

logger = logging.getLogger(__name__)
load_dotenv()

requests_cache.install_cache('news_api_cache', expire_after=3600)

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment="gpt-4o-mini",
    api_version="2024-08-01-preview",
    api_key=os.getenv("AZURE_OPENAI_API_KEY")
)

def prompt_openai(prompt, json_schema):
    
    json_schema = { }
    # Define the prompt for GPT-4
    prompt = f"""
    Do things

    Use the following JSON schema:
    ```
    {json_schema}
    ```
    """

    # Call the GPT-4 API on Azure
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a html to json extractor."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        n=1,
        stop=None,
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    # Parse the response
    result = response.choices[0].message.content
    try:
        data = json.loads(result)
    except json.JSONDecodeError:
        print('error:', result)
        return

    return data


def assign_relevance_score(title: str, description: str) -> dict:
    """
    Assign a relevance score to a news story based on its title and description.
    """
    audience = """
    Corporate executives with a focus on AI, and AI enthusiasts.
    They are interested in genuine AI innovations, not corporate mergers or deals (for example, 'GS Group, Notion to team up on AI capabilities '), or general PR like 'How China plans to rule the world in AI'
    """
    json_format = {
        "score": 0,
        "reason": ""
    }
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        messages=[
            {"role": "system", "content": f"You are a helpful assistant that assigns a relevance score to a news story based on its title and description. Output in the following JSON format: {json_format}"},
            {"role": "user", "content": f"""Assign a relevance score between 0 and 100 to the following news
              story based on its title and description for an audience of {audience}: 
              Title: {title}\nDescription: {description}"""}
        ],
        response_format={"type": "json_object"},
        max_tokens=500,
        temperature=0.3
    )

    try:
        score = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {e}")
        return
    
    return score


def get_stories():
    NEWSAPI_KEY = os.getenv("NEWSDATA_KEY")
    r = requests.get(f"https://newsdata.io/api/1/news?apikey={NEWSAPI_KEY}&q=artificial%20intelligence&language=en")

    return r.json()


def assign_relevance_scores(stories: list, threshold: int = 70):
    """
    Assign a relevance score to each story in the list, and filter out the ones below the threshold.
    """
    stories_with_scores = []
    for story in stories:
        score = assign_relevance_score(story['title'], story['description'])
        story['relevance_score'] = score['score']
        story['relevance_reason'] = score['reason']
        if score['score'] >= threshold:
            stories_with_scores.append(story)

    return stories_with_scores


def process_stories(stories: list):
    """
    Process the stories and save them to the database.
    """

    processed_stories = []
    stories_with_scores = assign_relevance_scores(stories['results'])
    
    for story_data in stories_with_scores:
        try:
            # Get or create Source
            source_defaults = {
                'name': story_data['source_name'],
                'url': story_data['source_url'],
                'icon': story_data['source_icon'],
                'priority': story_data['source_priority']
            }
            source, _ = Source.objects.get_or_create(
                source_id=story_data['source_id'],
                defaults=source_defaults
            )

            # Create Story
            story_defaults = {
                'title': story_data['title'],
                'description': story_data['description'],
                'link': story_data['link'],
                'pubDate': parse_datetime(story_data['pubDate']),
                'pubDateTZ': story_data['pubDateTZ'],
                'image_url': story_data['image_url'],
                'video_url': story_data['video_url'],
                'language': story_data['language'],
                'duplicate': story_data['duplicate'],
                'source': source,
                'relevance_score': story_data['relevance_score'],
                'relevance_reason': story_data['relevance_reason'],
            }
            
            story, created = Story.objects.get_or_create(
                article_id=story_data['article_id'],
                defaults=story_defaults
            )
            
            if created:
                # Process Keywords
                if story_data.get('keywords'):
                    keywords = [k.strip() for k in story_data['keywords']]
                    for keyword in keywords:
                        keyword_obj, _ = Keyword.objects.get_or_create(name=keyword)
                        story.keywords.add(keyword_obj)

                # Process Countries
                if story_data.get('country'):
                    for country in story_data['country']:
                        country_obj, _ = Country.objects.get_or_create(name=country)
                        story.countries.add(country_obj)

                # Process Categories
                if story_data.get('category'):
                    for category in story_data['category']:
                        category_obj, _ = Category.objects.get_or_create(name=category)
                        story.categories.add(category_obj)

                processed_stories.append(story)
                
        except Exception as e:
            logger.error(f"Error processing story {story_data.get('article_id')}: {str(e)}")
            continue

    logger.info(f"Processed {len(processed_stories)} new stories")
    return processed_stories


def sync_sitemap():
    SITEMAP_URL = "https://www.clickworker.com/sitemap_index.xml/"
    print(f"Syncing sitemap from {SITEMAP_URL}")
    
    # Get sitemap data into DataFrame
    sitemap_df = advertools.sitemap_to_df(SITEMAP_URL)
    
    # Filter for URLs updated in last 90 days
    cutoff_date = datetime.now(sitemap_df['lastmod'].dtype.tz) - timedelta(days=90)
    recent_urls = sitemap_df[sitemap_df['lastmod'] >= cutoff_date]
    
    # Get just the URLs
    sitemap_urls = recent_urls['loc'].tolist()
    print(f"Found {len(sitemap_urls)} URLs updated in last 90 days")
    
    # Create temporary file for crawl output
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(suffix='.jl', delete=False).name
    
    # Crawl URLs to get title, meta description and body content
    advertools.crawl(
        sitemap_urls,
        temp_file,
        follow_links=False,  # Only crawl the specified URLs
        custom_settings={
            'USER_AGENT': 'Mozilla/5.0 (compatible; MyBot/1.0)',
            'ROBOTSTXT_OBEY': True,
            'CONCURRENT_REQUESTS': 5  # Adjust based on server capacity
        }
    )
    
    # Read crawl results
    import pandas as pd
    crawl_df = pd.read_json(temp_file, lines=True)
    
    # Clean up temp file
    import os
    os.unlink(temp_file)
    
    # Save results to database
    for _, row in crawl_df[['url', 'title', 'meta_desc', 'body_text']].iterrows():
        try:
            SitemapURL.objects.update_or_create(
                url=row['url'],
                defaults={
                    'title': row['title'],
                    'meta_desc': row['meta_desc'],
                    'content': row['body_text'],  # Store the page content
                    'lastmod': recent_urls[recent_urls['loc'] == row['url']]['lastmod'].iloc[0]
                }
            )
        except Exception as e:
            logger.error(f"Error saving URL {row['url']}: {str(e)}")
            continue
    
    return f"Processed {len(crawl_df)} URLs"


def find_relevant_page_for_story(story: Story):
    # Get all URLs and their metadata
    urls = SitemapURL.objects.all().values('id', 'title', 'meta_desc')
    
    # Convert queryset to list of dictionaries with relevant fields
    url_list = [
        {
            'id': url['id'],
            'title': url['title'],
            'description': url['meta_desc']
        }
        for url in urls
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a social media manager that matches news stories to the most relevant pages on a website."},
            {"role": "user", "content": f"Here is the news story: {story.title}\n{story.description}\n\nHere are the URLs and their metadata: {url_list}. Please return the ID of the most relevant URL in the following JSON format: {{'url_id': <id>, 'reason': <reason>}}"}
        ],
        max_tokens=2000,
        n=1,
        stop=None,
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    # Parse the response
    result = response.choices[0].message.content
    try:
        data = json.loads(result)
        sitemap_url = SitemapURL.objects.get(id=data['url_id'])
    except json.JSONDecodeError:
        print('error:', result)
        return 
    
    create_post(story, sitemap_url)

    print(f"Found relevant page: {sitemap_url.url} - {data['reason']}")
    

def generate_post_content(story: Story, sitemap_url: SitemapURL):

    style = """
    Do not use hashtags or emojis.
    Write in simple, concise language, with a conversational tone.
    If you use bullet points, just use simple -.
    The tone should be valuable, teaching, and with a non-salesy, non-promotional tone
    with a straightforward connection between the news story and the page content.
    When referencing the news article, don't say 'the article', just say 'this'.
    Add a learn more link at the end of the post, linking to the page on our website.
    This will be shared on LinkedIn, so add the plain anchor text of the link as the link text,
    for example 'Learn more: https://www.clickworker.com/...'
    Do not use the words 'evolving', 'transforming', 'disrupting' or 'revolutionizing'.
    """

    response = client.chat.completions.create(
        model="gpt4turbo",
        messages=[
            {"role": "system", "content": "You are a social media manager that generates content for a news story based on a page on a website."},
            {"role": "user", "content": f"""
            Here is the news story: {story.title}\n{story.description}\n\n
            Here is the page on the website: {sitemap_url.title}\n{sitemap_url.meta_desc}\n\n{sitemap_url.content}. 
            Write in this style: {style}"""}
        ],
        max_tokens=2000,
        n=1,
        stop=None,
        temperature=0.7,
    )

    return response.choices[0].message.content  


def create_post(story: Story, sitemap_url: SitemapURL):
    post_content = generate_post_content(story, sitemap_url)
    post = Post.objects.create(
        story=story,
        sitemap_url=sitemap_url,
        content=post_content
    )
    return post


def generate_post_for_all_stories():
    stories = Story.objects.filter(post__isnull=True)
    for story in stories:
        find_relevant_page_for_story(story)