from django.db import models


class Source(models.Model):
    source_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    url = models.URLField()
    icon = models.URLField(null=True, blank=True)
    priority = models.IntegerField()

    def __str__(self):
        return self.name


class Keyword(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Story(models.Model):
    article_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    link = models.URLField()
    pubDate = models.DateTimeField()
    pubDateTZ = models.CharField(max_length=50)
    image_url = models.URLField(null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)
    language = models.CharField(max_length=50)
    duplicate = models.BooleanField(default=False)
    relevance_score = models.IntegerField()
    relevance_reason = models.TextField()

    # Relationships
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    keywords = models.ManyToManyField(Keyword)
    countries = models.ManyToManyField(Country)
    categories = models.ManyToManyField(Category)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Stories"


class SitemapURL(models.Model):
    url = models.URLField(unique=True)
    title = models.CharField(max_length=500, null=True, blank=True)
    meta_desc = models.TextField(null=True, blank=True)
    lastmod = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.url
    

class Post(models.Model):
    sitemap_url = models.ForeignKey(SitemapURL, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.story.title
    


class Remixable(models.Model):
    url = models.URLField(unique=True)
    is_video = models.BooleanField(default=False)
    html_content = models.TextField(blank=True, null=True)
    markdown_content = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    remixed_as = models.TextField(blank=True, null=True)
    remixed_image = models.FileField(upload_to='remixed_images/', null=True, blank=True)

    def __str__(self):
        return self.title or self.url


class RemixableImage(models.Model):
    remixable = models.ForeignKey(Remixable, on_delete=models.CASCADE)
    image_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.image_url
