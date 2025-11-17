"""
Blog App Forms for CRUD operations.
Reference: https://docs.djangoproject.com/en/5.2/topics/forms/
"""
from django import forms
from .models import BlogPost, Comment
from django.utils.text import slugify


class BlogPostForm(forms.ModelForm):
    """
    Form for creating and editing blog posts.
    Reference: https://docs.djangoproject.com/en/5.2/topics/forms/modelforms/
    """
    class Meta:
        model = BlogPost
        fields = ['title', 'slug', 'excerpt', 'content', 'featured_image', 'category']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Blog post title',
                'maxlength': 200
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL-friendly slug (auto-generated)',
                'readonly': 'readonly'
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief excerpt for preview',
                'maxlength': 500
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 12,
                'placeholder': 'Write your blog content here... (supports HTML)',
                'style': 'font-family: monospace;'
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Separate categories/tags with commas (e.g., python, django, web)'
            })
        }

    def clean_title(self):
        """
        Validate title is not empty and not too short.
        """
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError('Title cannot be empty.')
        if len(title) < 5:
            raise forms.ValidationError('Title must be at least 5 characters long.')
        return title

    def clean_content(self):
        """
        Validate content has minimum length.
        """
        content = self.cleaned_data.get('content', '').strip()
        if not content:
            raise forms.ValidationError('Content cannot be empty.')
        if len(content) < 50:
            raise forms.ValidationError('Content must be at least 50 characters long.')
        return content

    def clean_excerpt(self):
        """
        Validate excerpt if provided.
        """
        excerpt = self.cleaned_data.get('excerpt', '').strip()
        if excerpt and len(excerpt) < 10:
            raise forms.ValidationError('Excerpt must be at least 10 characters long.')
        return excerpt

    def save(self, commit=True):
        """
        Override save to auto-generate slug from title if not provided.
        Reference: https://docs.djangoproject.com/en/5.2/ref/models/fields/#slugfield
        """
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = slugify(instance.title)
        
        # Ensure unique slug
        original_slug = instance.slug
        queryset = BlogPost.objects.filter(slug=instance.slug)
        if instance.pk:
            queryset = queryset.exclude(pk=instance.pk)
        
        counter = 1
        while queryset.exists():
            instance.slug = f"{original_slug}-{counter}"
            queryset = BlogPost.objects.filter(slug=instance.slug)
            if instance.pk:
                queryset = queryset.exclude(pk=instance.pk)
            counter += 1
        
        if commit:
            instance.save()
        return instance


class CommentForm(forms.ModelForm):
    """
    Form for adding comments to blog posts.
    """
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your comment here...',
                'maxlength': 1000
            })
        }

    def clean_content(self):
        """
        Validate comment content.
        """
        content = self.cleaned_data.get('content', '').strip()
        if not content:
            raise forms.ValidationError('Comment cannot be empty.')
        if len(content) < 5:
            raise forms.ValidationError('Comment must be at least 5 characters long.')
        if len(content) > 1000:
            raise forms.ValidationError('Comment must not exceed 1000 characters.')
        return content


class AIBlogGenerationForm(forms.Form):
    """
    Form for AI blog generation from ideas
    """
    idea = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Describe your blog idea or topic...',
            'maxlength': 500
        }),
        help_text='Describe the blog idea or topic you want to write about'
    )
    length = forms.ChoiceField(
        choices=[
            ('short', 'Short (500 words)'),
            ('medium', 'Medium (1000 words)'),
            ('long', 'Long (2000+ words)')
        ],
        initial='medium',
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text='Choose the desired blog length'
    )


class AIContentEnhancementForm(forms.Form):
    """
    Form for enhancing blog content with AI
    """
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'Paste your blog content here...',
        }),
        help_text='The blog content to enhance'
    )
    style = forms.ChoiceField(
        choices=[
            ('professional', 'Professional'),
            ('funny', 'Funny & Casual'),
            ('casual', 'Casual & Friendly'),
            ('academic', 'Academic & Formal'),
            ('engaging', 'Engaging & Captivating')
        ],
        initial='professional',
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text='Choose the writing style for enhancement'
    )


class AITranslationForm(forms.Form):
    """
    Form for translating blog content to other languages
    """
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'Paste your blog content here...',
        }),
        help_text='The blog content to translate'
    )
    language = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Spanish, French, German, Hindi, Arabic, Chinese, Japanese...',
        }),
        help_text='Enter the target language'
    )
