"""
Blog App URLs Configuration
Reference: https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.urls import path
from . import views

urlpatterns = [
    # Home and listing
    path('', views.home, name='home'),
    path('blogs/', views.blog_list, name='blog_list'),
    path('my-blogs/', views.my_blogs, name='my_blogs'),
    
    # CRUD operations
    path('create/', views.blog_create, name='blog_create'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('blog/<slug:slug>/edit/', views.blog_edit, name='blog_edit'),
    path('blog/<slug:slug>/delete/', views.blog_delete, name='blog_delete'),
    
    # Publishing
    path('blog/<slug:slug>/publish/', views.blog_publish, name='blog_publish'),
    path('blog/<slug:slug>/draft/', views.blog_draft, name='blog_draft'),
    
    # Comments
    path('blog/<slug:slug>/comment/', views.comment_create, name='comment_create'),
    # Interactions (like/dislike)
    path('blog/<slug:slug>/interact/', views.blog_interact, name='blog_interact'),
    # Comment deletion
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    
    # AI Features API
    path('api/ai/generate-blog/', views.api_generate_blog_from_idea, name='api_generate_blog'),
    path('api/ai/enhance-content/', views.api_enhance_content, name='api_enhance_content'),
    path('api/ai/translate-content/', views.api_translate_content, name='api_translate_content'),
]
