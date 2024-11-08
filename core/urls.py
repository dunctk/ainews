from django.urls import path
from .views import HomeView, PostListView

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('posts/', PostListView.as_view(), name='post_list'),
]
