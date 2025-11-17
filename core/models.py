"""
Core App Models - AI Features and Sentiment Analysis
Reference: https://docs.djangoproject.com/en/5.2/topics/db/models/
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from blog.models import Comment, BlogPost


class AIPrompt(models.Model):
    """
    Model to store AI prompt history and generated content
    Used for tracking blog generation, enhancement, and translation
    Reference: https://docs.djangoproject.com/en/5.2/topics/db/models/
    """
    CONTENT_TYPE_CHOICES = (
        ('blog_generation', 'Blog Generation'),
        ('content_enhancement', 'Content Enhancement'),
        ('translation', 'Translation'),
        ('image_description', 'Image Description'),
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ai_prompts',
        help_text="User who created the prompt"
    )
    blog_post = models.ForeignKey(
        BlogPost,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_prompts',
        help_text="Associated blog post (if any)"
    )
    prompt_text = models.TextField(
        help_text="Original user prompt/idea"
    )
    generated_content = models.TextField(
        help_text="AI-generated content"
    )
    content_type = models.CharField(
        max_length=50,
        choices=CONTENT_TYPE_CHOICES,
        help_text="Type of AI generation"
    )
    ai_model_used = models.CharField(
        max_length=100,
        default='openai-gpt-3.5',
        help_text="Which AI model was used"
    )
    enhancement_level = models.CharField(
        max_length=50,
        default='professional',
        blank=True,
        help_text="Enhancement style (funny, professional, formal, etc.)"
    )
    target_language = models.CharField(
        max_length=50,
        blank=True,
        help_text="Target language for translation"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Generation timestamp"
    )
    usage_tokens = models.IntegerField(
        default=0,
        help_text="Tokens used for API call"
    )

    def __str__(self):
        """Return prompt preview"""
        return f"AI {self.content_type} by {self.author.username} - {self.created_at.strftime('%Y-%m-%d')}"

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "AI Prompts"
        indexes = [
            models.Index(fields=['author', 'content_type']),
            models.Index(fields=['-created_at']),
        ]


class CommentSentiment(models.Model):
    """
    Model to store sentiment analysis results for comments
    Reference: https://docs.djangoproject.com/en/5.2/topics/db/models/
    Reference: TextBlob - https://textblob.readthedocs.io/
    """
    SENTIMENT_CHOICES = (
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
    )

    SENTIMENT_TYPE_CHOICES = (
        ('improvement', 'Improvement Suggestion'),
        ('appreciation', 'Appreciation'),
        ('feedback', 'Detailed Feedback'),
        ('question', 'Question'),
        ('criticism', 'Criticism'),
        ('other', 'Other'),
    )

    comment = models.OneToOneField(
        Comment,
        on_delete=models.CASCADE,
        related_name='sentiment',
        help_text="Associated comment"
    )
    sentiment = models.CharField(
        max_length=20,
        choices=SENTIMENT_CHOICES,
        help_text="Overall sentiment"
    )
    confidence_score = models.FloatField(
        help_text="Confidence score (0-1)"
    )
    sentiment_type = models.CharField(
        max_length=50,
        choices=SENTIMENT_TYPE_CHOICES,
        default='other',
        help_text="Type of sentiment content"
    )
    polarity = models.FloatField(
        default=0.0,
        help_text="Polarity score (-1 to 1)"
    )
    subjectivity = models.FloatField(
        default=0.0,
        help_text="Subjectivity score (0 to 1)"
    )
    analyzed_at = models.DateTimeField(
        default=timezone.now,
        help_text="Analysis timestamp"
    )
    analysis_model = models.CharField(
        max_length=100,
        default='textblob',
        help_text="Which analysis model was used"
    )

    def __str__(self):
        """Return sentiment info"""
        return f"{self.sentiment.upper()} - {self.comment.author.username} on {self.comment.post.title}"

    class Meta:
        verbose_name_plural = "Comment Sentiments"
        ordering = ['-analyzed_at']
        indexes = [
            models.Index(fields=['sentiment']),
            models.Index(fields=['sentiment_type']),
        ]


class ImageSuggestion(models.Model):
    """
    Model to store image suggestions for blog posts
    Reference: https://docs.djangoproject.com/en/5.2/topics/db/models/
    """
    IMAGE_SOURCE_CHOICES = (
        ('unsplash', 'Unsplash'),
        ('pixabay', 'Pixabay'),
        ('pexels', 'Pexels'),
        ('user_upload', 'User Upload'),
    )

    blog_post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='image_suggestions',
        help_text="Blog post"
    )
    image_url = models.URLField(
        help_text="URL of the suggested image"
    )
    title = models.CharField(
        max_length=200,
        help_text="Image title"
    )
    description = models.TextField(
        blank=True,
        help_text="Image description"
    )
    source = models.CharField(
        max_length=50,
        choices=IMAGE_SOURCE_CHOICES,
        help_text="Where image came from"
    )
    relevance_score = models.FloatField(
        default=0.0,
        help_text="How relevant to blog (0-1)"
    )
    suggested_at = models.DateTimeField(
        default=timezone.now,
        help_text="Suggestion timestamp"
    )
    is_selected = models.BooleanField(
        default=False,
        help_text="Was this image used"
    )

    def __str__(self):
        """Return suggestion info"""
        return f"Image for '{self.blog_post.title}' from {self.source}"

    class Meta:
        verbose_name_plural = "Image Suggestions"
        ordering = ['-relevance_score', '-suggested_at']
