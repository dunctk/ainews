from django.urls import path
from django.urls import include
from rest_framework.routers import DefaultRouter
from .views import HomeView, PostListView, PostViewSet

app_name = 'core'

router = DefaultRouter()
router.register(r'posts', PostViewSet)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('posts/', PostListView.as_view(), name='post_list'),
    path('api/', include(router.urls)),
]
