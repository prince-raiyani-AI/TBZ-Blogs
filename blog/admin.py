"""
Blog App Admin Configuration
Reference: https://docs.djangoproject.com/en/5.2/ref/contrib/admin/
"""
from django.contrib import admin
from .models import BlogPost, Comment, PostInteraction


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """
    Admin interface for BlogPost model
    Reference: https://docs.djangoproject.com/en/5.2/ref/contrib/admin/
    """
    list_display = ['title', 'author', 'status', 'created_at', 'likes_count', 'comments_count']
    list_filter = ['status', 'created_at', 'category']
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = ['slug', 'created_at', 'updated_at', 'views_count']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Post Information', {
            'fields': ('author', 'title', 'slug', 'status')
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'featured_image')
        }),
        ('Categorization', {
            'fields': ('category',),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views_count', 'likes_count', 'dislikes_count', 'comments_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['make_published', 'make_draft']

    def make_published(self, request, queryset):
        """Bulk action to publish posts"""
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated} posts published.')
    make_published.short_description = 'Publish selected posts'

    def make_draft(self, request, queryset):
        """Bulk action to draft posts"""
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} posts moved to draft.')
    make_draft.short_description = 'Move selected posts to draft'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin interface for Comment model
    Reference: https://docs.djangoproject.com/en/5.2/ref/contrib/admin/
    """
    list_display = ['get_author', 'get_post', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['author__username', 'content', 'post__title']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Comment Information', {
            'fields': ('post', 'author', 'parent')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Status', {
            'fields': ('is_approved',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['approve_comments', 'disapprove_comments']

    def get_author(self, obj):
        """Display author username"""
        return obj.author.username
    get_author.short_description = 'Author'

    def get_post(self, obj):
        """Display post title"""
        return obj.post.title
    get_post.short_description = 'Post'

    def approve_comments(self, request, queryset):
        """Bulk action to approve comments"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} comments approved.')
    approve_comments.short_description = 'Approve selected comments'

    def disapprove_comments(self, request, queryset):
        """Bulk action to disapprove comments"""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} comments disapproved.')
    disapprove_comments.short_description = 'Disapprove selected comments'


@admin.register(PostInteraction)
class PostInteractionAdmin(admin.ModelAdmin):
    """
    Admin interface for PostInteraction model
    Reference: https://docs.djangoproject.com/en/5.2/ref/contrib/admin/
    """
    list_display = ['get_user', 'get_post', 'interaction_type', 'created_at']
    list_filter = ['interaction_type', 'created_at']
    search_fields = ['user__username', 'post__title']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Interaction Information', {
            'fields': ('post', 'user', 'interaction_type')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_user(self, obj):
        """Display user username"""
        return obj.user.username
    get_user.short_description = 'User'

    def get_post(self, obj):
        """Display post title"""
        return obj.post.title
    get_post.short_description = 'Post'

