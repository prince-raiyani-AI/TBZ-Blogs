"""
Core App Admin Configuration
Reference: https://docs.djangoproject.com/en/5.2/ref/contrib/admin/
"""
from django.contrib import admin
from .models import AIPrompt, CommentSentiment, ImageSuggestion


@admin.register(AIPrompt)
class AIPromptAdmin(admin.ModelAdmin):
    """
    Admin interface for AIPrompt model
    Reference: https://docs.djangoproject.com/en/5.2/ref/contrib/admin/
    """
    list_display = ['get_author', 'content_type', 'ai_model_used', 'usage_tokens', 'created_at']
    list_filter = ['content_type', 'ai_model_used', 'created_at']
    search_fields = ['author__username', 'prompt_text', 'generated_content']
    readonly_fields = ['created_at', 'usage_tokens']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Prompt Information', {
            'fields': ('author', 'blog_post', 'content_type')
        }),
        ('Content', {
            'fields': ('prompt_text', 'generated_content'),
            'classes': ('wide',)
        }),
        ('Configuration', {
            'fields': ('ai_model_used', 'enhancement_level', 'target_language'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'usage_tokens'),
            'classes': ('collapse',)
        }),
    )

    def get_author(self, obj):
        """Display author username"""
        return obj.author.username
    get_author.short_description = 'Author'


@admin.register(CommentSentiment)
class CommentSentimentAdmin(admin.ModelAdmin):
    """
    Admin interface for CommentSentiment model
    Reference: https://docs.djangoproject.com/en/5.2/ref/contrib/admin/
    """
    list_display = ['get_comment_author', 'sentiment', 'sentiment_type', 'confidence_score', 'analyzed_at']
    list_filter = ['sentiment', 'sentiment_type', 'analysis_model', 'analyzed_at']
    search_fields = ['comment__author__username', 'comment__content', 'comment__post__title']
    readonly_fields = ['analyzed_at', 'get_comment_content']
    date_hierarchy = 'analyzed_at'

    fieldsets = (
        ('Comment Information', {
            'fields': ('comment', 'get_comment_content')
        }),
        ('Sentiment Analysis', {
            'fields': ('sentiment', 'sentiment_type', 'confidence_score', 'analysis_model')
        }),
        ('Scores', {
            'fields': ('polarity', 'subjectivity'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('analyzed_at',),
            'classes': ('collapse',)
        }),
    )

    def get_comment_author(self, obj):
        """Display comment author"""
        return obj.comment.author.username
    get_comment_author.short_description = 'Author'

    def get_comment_content(self, obj):
        """Display comment content"""
        return obj.comment.content
    get_comment_content.short_description = 'Comment'


@admin.register(ImageSuggestion)
class ImageSuggestionAdmin(admin.ModelAdmin):
    """
    Admin interface for ImageSuggestion model
    Reference: https://docs.djangoproject.com/en/5.2/ref/contrib/admin/
    """
    list_display = ['get_post_title', 'source', 'relevance_score', 'is_selected', 'suggested_at']
    list_filter = ['source', 'is_selected', 'suggested_at']
    search_fields = ['blog_post__title', 'title', 'description']
    readonly_fields = ['suggested_at']
    date_hierarchy = 'suggested_at'

    fieldsets = (
        ('Image Information', {
            'fields': ('blog_post', 'title', 'image_url')
        }),
        ('Details', {
            'fields': ('description', 'source', 'relevance_score')
        }),
        ('Status', {
            'fields': ('is_selected',)
        }),
        ('Timestamp', {
            'fields': ('suggested_at',),
            'classes': ('collapse',)
        }),
    )

    def get_post_title(self, obj):
        """Display blog post title"""
        return obj.blog_post.title
    get_post_title.short_description = 'Blog Post'

