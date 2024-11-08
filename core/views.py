
# Create your views here.
from django.views.generic import ListView
from .models import Post, Story

class HomeView(ListView):
    model = Story
    template_name = 'core/home.html'
    context_object_name = 'stories'
    ordering = ['-pubDate']
    paginate_by = 20

class PostListView(ListView):
    model = Post
    template_name = 'core/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']
    paginate_by = 20