# AI News Curator

A Django-based application that automatically curates AI-related news stories and generates relevant social media content.

## Features

- Fetches AI-related news articles from NewsData.io API
- Uses Azure OpenAI (GPT-4) to:
  - Score news articles for relevance
  - Match news stories with relevant website content
  - Generate social media posts
- Crawls and indexes website sitemaps
- Provides a web interface to view curated stories and generated posts

## Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```bash
SECRET_KEY=your_django_secret_key
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_API_KEY=your_azure_api_key
NEWSDATA_KEY=your_newsdata_api_key
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

## Key Components

### Tasks (`core/tasks.py`)

- `get_stories()`: Fetches news articles from NewsData.io
- `assign_relevance_scores()`: Uses GPT-4 to score articles for relevance
- `process_stories()`: Saves filtered stories to the database
- `sync_sitemap()`: Crawls and indexes website content
- `generate_post_content()`: Creates social media posts based on news stories
- `find_relevant_page_for_story()`: Matches news stories with website content

### Views (`core/views.py`)

- `HomeView`: Displays curated news stories
- `PostListView`: Shows generated social media posts

## Models

- `Story`: Represents a news article
- `Source`: News source information
- `Post`: Generated social media content
- `SitemapURL`: Indexed website pages
- Additional models for categorization: `Keyword`, `Country`, `Category`

## Dependencies

- Django
- OpenAI Azure
- advertools
- requests-cache
- python-dotenv
- pandas

## License

MIT
