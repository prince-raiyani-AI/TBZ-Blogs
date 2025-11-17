"""
Accounts App Models
Reference: https://docs.djangoproject.com/en/5.2/topics/db/models/
Reference: https://docs.djangoproject.com/en/5.2/ref/contrib/auth/
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    """
    Extended user profile with additional information
    Reference: https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#extending-the-existing-user-model
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text="Link to Django User model"
    )
    bio = models.TextField(
        blank=True,
        null=True,
        max_length=500,
        help_text="User biography"
    )
    profile_image = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        help_text="User profile picture"
    )
    follower_count = models.IntegerField(
        default=0,
        help_text="Number of followers"
    )
    following_count = models.IntegerField(
        default=0,
        help_text="Number of users following"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Account creation date"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last profile update"
    )

    def __str__(self):
        """Return username"""
        return f"{self.user.username} Profile"

    class Meta:
        verbose_name_plural = "User Profiles"
        ordering = ['-created_at']

    def get_full_name(self):
        """Return user's full name"""
        return self.user.get_full_name() or self.user.username

    def get_blog_count(self):
        """Return number of published blogs"""
        return self.user.blog_posts.filter(status='published').count()
