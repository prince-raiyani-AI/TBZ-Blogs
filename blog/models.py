"""
Blog App Models
Reference: https://docs.djangoproject.com/en/5.2/topics/db/models/
Reference: https://docs.djangoproject.com/en/5.2/topics/db/models/relationships/
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify


class BlogPost(models.Model):
    """
    Main blog post model
    Reference: https://docs.djangoproject.com/en/5.2/topics/db/models/
    """
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_posts',
        help_text="Blog author"
    )
    title = models.CharField(
        max_length=200,
        help_text="Blog post title"
    )
    slug = models.SlugField(
        unique=True,
        help_text="URL-friendly title"
    )
    content = models.TextField(
        help_text="Main blog content"
    )
    excerpt = models.TextField(
        max_length=500,
        help_text="Short preview of blog"
    )
    featured_image = models.ImageField(
        upload_to='blog_images/',
        blank=True,
        null=True,
        help_text="Main blog image"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Publication date"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modification date"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Current status"
    )
    category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Blog category/tags"
    )
    likes_count = models.IntegerField(
        default=0,
        help_text="Total likes"
    )
    dislikes_count = models.IntegerField(
        default=0,
        help_text="Total dislikes"
    )
    comments_count = models.IntegerField(
        default=0,
        help_text="Total comments"
    )
    views_count = models.IntegerField(
        default=0,
        help_text="Total views"
    )

    def __str__(self):
        """Return blog title"""
        return self.title

    def get_absolute_url(self):
        """Return URL for blog detail view"""
        return reverse('blog_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        """Auto-generate slug from title"""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Blog Posts"
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['author', 'status']),
            models.Index(fields=['-created_at']),
        ]


class Comment(models.Model):
    """
    Comment model for blog post comments
    Reference: https://docs.djangoproject.com/en/5.2/topics/db/models/relationships/
    """
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="Blog post being commented on"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="Comment author"
    )
    content = models.TextField(
        help_text="Comment text"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Comment creation date"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modification"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text="Parent comment (for nested replies)"
    )
    is_approved = models.BooleanField(
        default=True,
        help_text="Is comment approved"
    )

    def __str__(self):
        """Return comment preview"""
        return f"Comment by {self.author.username} on {self.post.title}"

    def get_replies(self):
        """Get approved nested replies"""
        return self.replies.filter(is_approved=True).order_by('created_at')

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Comments"


class PostInteraction(models.Model):
    """
    Model to track likes and dislikes on blog posts
    Reference: https://docs.djangoproject.com/en/5.2/topics/db/models/
    """
    INTERACTION_CHOICES = (
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    )

    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='interactions',
        help_text="Blog post"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='post_interactions',
        help_text="User who interacted"
    )
    interaction_type = models.CharField(
        max_length=10,
        choices=INTERACTION_CHOICES,
        help_text="Type of interaction"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Interaction date"
    )

    def __str__(self):
        """Return interaction info"""
        return f"{self.user.username} {self.interaction_type}d {self.post.title}"

    class Meta:
        unique_together = ('post', 'user', 'interaction_type')
        verbose_name_plural = "Post Interactions"
        indexes = [
            models.Index(fields=['post', 'interaction_type']),
        ]
