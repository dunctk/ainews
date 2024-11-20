from django.views.generic import ListView
from .models import Post, Story
from rest_framework import viewsets
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination

# First, create a serializer for your Post model
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'  # This will include all model fields
        # Or specify only the fields that exist in your model, for example:
        # fields = ['id', 'body', 'created']  # adjust these based on your actual model fields

# Add the ViewSet
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    pagination_class = PageNumberPagination
    page_size = 20

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


