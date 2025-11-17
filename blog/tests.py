"""
Comprehensive test suite for the blog app.
Reference: https://docs.djangoproject.com/en/5.2/topics/testing/
Reference: https://pytest-django.readthedocs.io/
"""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase, Client
from blog.models import BlogPost, Comment, PostInteraction
from blog.forms import BlogPostForm, CommentForm


# ============================================================================
# FIXTURES FOR TESTING
# ============================================================================

@pytest.fixture
def client():
    """Pytest fixture for Django test client."""
    return Client()


@pytest.fixture
def test_user():
    """Create a test user."""
    user = User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='TestPass123!',
        first_name='Test',
        last_name='User'
    )
    return user


@pytest.fixture
def test_user2():
    """Create a second test user."""
    user = User.objects.create_user(
        username='testuser2',
        email='testuser2@example.com',
        password='TestPass123!',
        first_name='Another',
        last_name='User'
    )
    return user


@pytest.fixture
def test_blog_post(test_user):
    """Create a published test blog post."""
    blog = BlogPost.objects.create(
        author=test_user,
        title='Test Blog Post',
        slug='test-blog-post',
        content='This is test content for the blog post.',
        excerpt='This is a test excerpt.',
        status='published',
        category='Testing'
    )
    return blog


@pytest.fixture
def test_draft_blog(test_user):
    """Create a draft blog post."""
    blog = BlogPost.objects.create(
        author=test_user,
        title='Draft Blog Post',
        slug='draft-blog-post',
        content='This is draft content.',
        excerpt='This is a draft excerpt.',
        status='draft',
        category='Testing'
    )
    return blog


@pytest.fixture
def test_comment(test_user, test_user2, test_blog_post):
    """Create a test comment."""
    comment = Comment.objects.create(
        post=test_blog_post,
        author=test_user2,
        content='This is a test comment.'
    )
    return comment


# ============================================================================
# MODEL TESTS
# ============================================================================

class TestBlogPostModel(TestCase):
    """Test BlogPost model functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.blog = BlogPost.objects.create(
            author=self.user,
            title='Test Blog',
            content='Test content',
            excerpt='Test excerpt',
            status='published'
        )

    def test_blog_creation(self):
        """Test creating a blog post."""
        self.assertEqual(self.blog.title, 'Test Blog')
        self.assertEqual(self.blog.author, self.user)
        self.assertEqual(self.blog.status, 'published')

    def test_slug_auto_generation(self):
        """Test that slug is auto-generated from title."""
        self.assertEqual(self.blog.slug, 'test-blog')

    def test_blog_string_representation(self):
        """Test string representation of blog."""
        self.assertEqual(str(self.blog), 'Test Blog')

    def test_blog_absolute_url(self):
        """Test get_absolute_url method."""
        url = self.blog.get_absolute_url()
        self.assertIn('test-blog', url)

    def test_default_counts(self):
        """Test default counter values."""
        self.assertEqual(self.blog.likes_count, 0)
        self.assertEqual(self.blog.dislikes_count, 0)
        self.assertEqual(self.blog.comments_count, 0)
        self.assertEqual(self.blog.views_count, 0)

    def test_blog_ordering(self):
        """Test blogs are ordered by creation date descending."""
        blog2 = BlogPost.objects.create(
            author=self.user,
            title='Another Blog',
            content='Content',
            excerpt='Excerpt',
            status='published'
        )
        blogs = list(BlogPost.objects.filter(author=self.user))
        # Both blogs should be ordered by most recent first
        self.assertEqual(len(blogs), 2)
        # In the Meta class, ordering is ['-created_at'], so most recent comes first
        self.assertTrue(blogs[0].created_at >= blogs[1].created_at)


class TestCommentModel(TestCase):
    """Test Comment model functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.blog = BlogPost.objects.create(
            author=self.user,
            title='Test Blog',
            content='Content',
            excerpt='Excerpt',
            status='published'
        )
        self.comment = Comment.objects.create(
            post=self.blog,
            author=self.user,
            content='Test comment'
        )

    def test_comment_creation(self):
        """Test creating a comment."""
        self.assertEqual(self.comment.post, self.blog)
        self.assertEqual(self.comment.author, self.user)
        self.assertEqual(self.comment.content, 'Test comment')

    def test_comment_string_representation(self):
        """Test string representation of comment."""
        self.assertIn(self.user.username, str(self.comment))
        self.assertIn(self.blog.title, str(self.comment))

    def test_comment_is_approved_default(self):
        """Test that comments are approved by default."""
        self.assertTrue(self.comment.is_approved)

    def test_get_replies(self):
        """Test getting approved replies to a comment."""
        reply = Comment.objects.create(
            post=self.blog,
            author=self.user,
            content='Reply to comment',
            parent=self.comment,
            is_approved=True
        )
        replies = self.comment.get_replies()
        self.assertIn(reply, replies)

    def test_unapproved_replies_excluded(self):
        """Test that unapproved replies are not returned."""
        Comment.objects.create(
            post=self.blog,
            author=self.user,
            content='Unapproved reply',
            parent=self.comment,
            is_approved=False
        )
        replies = self.comment.get_replies()
        self.assertEqual(replies.count(), 0)


class TestPostInteractionModel(TestCase):
    """Test PostInteraction model functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.blog = BlogPost.objects.create(
            author=self.user,
            title='Test Blog',
            content='Content',
            excerpt='Excerpt',
            status='published'
        )

    def test_create_like_interaction(self):
        """Test creating a like interaction."""
        interaction = PostInteraction.objects.create(
            post=self.blog,
            user=self.user,
            interaction_type='like'
        )
        self.assertEqual(interaction.interaction_type, 'like')
        self.assertEqual(interaction.post, self.blog)
        self.assertEqual(interaction.user, self.user)

    def test_create_dislike_interaction(self):
        """Test creating a dislike interaction."""
        interaction = PostInteraction.objects.create(
            post=self.blog,
            user=self.user,
            interaction_type='dislike'
        )
        self.assertEqual(interaction.interaction_type, 'dislike')

    def test_unique_together_constraint(self):
        """Test that a user can't like the same post twice."""
        PostInteraction.objects.create(
            post=self.blog,
            user=self.user,
            interaction_type='like'
        )
        with self.assertRaises(Exception):
            PostInteraction.objects.create(
                post=self.blog,
                user=self.user,
                interaction_type='like'
            )

    def test_interaction_string_representation(self):
        """Test string representation of interaction."""
        interaction = PostInteraction.objects.create(
            post=self.blog,
            user=self.user,
            interaction_type='like'
        )
        self.assertIn(self.user.username, str(interaction))
        self.assertIn(self.blog.title, str(interaction))


# ============================================================================
# VIEW TESTS
# ============================================================================

class TestBlogViews(TestCase):
    """Test blog app views."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='TestPass123!'
        )
        self.blog = BlogPost.objects.create(
            author=self.user,
            title='Published Blog',
            slug='published-blog',
            content='Published content',
            excerpt='Published excerpt',
            status='published'
        )
        self.draft = BlogPost.objects.create(
            author=self.user,
            title='Draft Blog',
            slug='draft-blog',
            content='Draft content',
            excerpt='Draft excerpt',
            status='draft'
        )

    def test_home_page_view(self):
        """Test home page displays published blogs."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        # 'blogs' is a Page object from paginator
        blogs_list = list(response.context['blogs'].object_list)
        self.assertIn(self.blog, blogs_list)
        self.assertNotIn(self.draft, blogs_list)

    def test_blog_detail_view(self):
        """Test blog detail view."""
        response = self.client.get(reverse('blog_detail', kwargs={'slug': self.blog.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['blog'], self.blog)

    def test_blog_detail_draft_not_accessible_to_others(self):
        """Test draft blog not accessible to non-authors."""
        response = self.client.get(reverse('blog_detail', kwargs={'slug': self.draft.slug}))
        self.assertEqual(response.status_code, 404)

    def test_blog_detail_draft_accessible_to_author(self):
        """Test draft blog accessible to author."""
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(reverse('blog_detail', kwargs={'slug': self.draft.slug}))
        self.assertEqual(response.status_code, 200)

    def test_my_blogs_view_requires_login(self):
        """Test my blogs view requires authentication."""
        response = self.client.get(reverse('my_blogs'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_my_blogs_view_shows_user_blogs(self):
        """Test my blogs view shows user's blogs."""
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(reverse('my_blogs'))
        self.assertEqual(response.status_code, 200)
        blogs_list = list(response.context['blogs'].object_list)
        self.assertIn(self.blog, blogs_list)
        self.assertIn(self.draft, blogs_list)


# ============================================================================
# INTERACTION TESTS (Like/Dislike)
# ============================================================================

class TestBlogInteractionView(TestCase):
    """Test blog interaction (like/dislike) functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='TestPass123!'
        )
        self.blog = BlogPost.objects.create(
            author=self.user,
            title='Test Blog',
            slug='test-blog',
            content='Test content',
            excerpt='Test excerpt',
            status='published'
        )

    def test_like_blog_post(self):
        """Test liking a blog post."""
        self.client.login(username='testuser2', password='TestPass123!')
        response = self.client.post(
            reverse('blog_interact', kwargs={'slug': self.blog.slug}),
            {'action': 'like'}
        )
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.likes_count, 1)
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_dislike_blog_post(self):
        """Test disliking a blog post."""
        self.client.login(username='testuser2', password='TestPass123!')
        response = self.client.post(
            reverse('blog_interact', kwargs={'slug': self.blog.slug}),
            {'action': 'dislike'}
        )
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.dislikes_count, 1)

    def test_remove_like(self):
        """Test removing a like."""
        PostInteraction.objects.create(
            post=self.blog,
            user=self.user2,
            interaction_type='like'
        )
        self.blog.likes_count = 1
        self.blog.save()

        self.client.login(username='testuser2', password='TestPass123!')
        response = self.client.post(
            reverse('blog_interact', kwargs={'slug': self.blog.slug}),
            {'action': 'like'}
        )
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.likes_count, 0)

    def test_switch_from_like_to_dislike(self):
        """Test switching from like to dislike."""
        PostInteraction.objects.create(
            post=self.blog,
            user=self.user2,
            interaction_type='like'
        )
        self.blog.likes_count = 1
        self.blog.save()

        self.client.login(username='testuser2', password='TestPass123!')
        response = self.client.post(
            reverse('blog_interact', kwargs={'slug': self.blog.slug}),
            {'action': 'dislike'}
        )
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.likes_count, 0)
        self.assertEqual(self.blog.dislikes_count, 1)

    def test_like_requires_login(self):
        """Test liking requires login."""
        response = self.client.post(
            reverse('blog_interact', kwargs={'slug': self.blog.slug}),
            {'action': 'like'}
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_invalid_interaction_action(self):
        """Test invalid interaction action."""
        self.client.login(username='testuser2', password='TestPass123!')
        response = self.client.post(
            reverse('blog_interact', kwargs={'slug': self.blog.slug}),
            {'action': 'invalid'}
        )
        self.assertEqual(response.status_code, 302)


# ============================================================================
# COMMENT TESTS
# ============================================================================

class TestCommentView(TestCase):
    """Test comment creation and management."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='TestPass123!'
        )
        self.blog = BlogPost.objects.create(
            author=self.user,
            title='Test Blog',
            slug='test-blog',
            content='Test content',
            excerpt='Test excerpt',
            status='published'
        )

    def test_add_comment(self):
        """Test adding a comment to a blog post."""
        self.client.login(username='testuser2', password='TestPass123!')
        response = self.client.post(
            reverse('blog_detail', kwargs={'slug': self.blog.slug}),
            {'content': 'Great post!'}
        )
        self.assertEqual(Comment.objects.filter(post=self.blog).count(), 1)
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.comments_count, 1)

    def test_comment_requires_login(self):
        """Test adding comment requires login."""
        response = self.client.post(
            reverse('blog_detail', kwargs={'slug': self.blog.slug}),
            {'content': 'Great post!'}
        )
        self.assertEqual(Comment.objects.filter(post=self.blog).count(), 0)


class TestCommentDeleteView(TestCase):
    """Test comment deletion functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='TestPass123!'
        )
        self.blog = BlogPost.objects.create(
            author=self.user,
            title='Test Blog',
            slug='test-blog',
            content='Test content',
            excerpt='Test excerpt',
            status='published'
        )
        self.comment = Comment.objects.create(
            post=self.blog,
            author=self.user2,
            content='Test comment'
        )
        self.blog.comments_count = 1
        self.blog.save()

    def test_author_can_delete_own_comment(self):
        """Test comment author can delete their own comment."""
        self.client.login(username='testuser2', password='TestPass123!')
        response = self.client.post(
            reverse('comment_delete', kwargs={'pk': self.comment.pk})
        )
        self.assertEqual(Comment.objects.filter(pk=self.comment.pk).count(), 0)
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.comments_count, 0)

    def test_post_author_can_delete_comment(self):
        """Test post author can delete comments on their post."""
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post(
            reverse('comment_delete', kwargs={'pk': self.comment.pk})
        )
        self.assertEqual(Comment.objects.filter(pk=self.comment.pk).count(), 0)
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.comments_count, 0)

    def test_other_users_cannot_delete_comment(self):
        """Test other users cannot delete comments."""
        user3 = User.objects.create_user(
            username='testuser3',
            email='test3@example.com',
            password='TestPass123!'
        )
        self.client.login(username='testuser3', password='TestPass123!')
        response = self.client.post(
            reverse('comment_delete', kwargs={'pk': self.comment.pk})
        )
        self.assertEqual(Comment.objects.filter(pk=self.comment.pk).count(), 1)

    def test_delete_requires_login(self):
        """Test comment deletion requires login."""
        response = self.client.post(
            reverse('comment_delete', kwargs={'pk': self.comment.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertEqual(Comment.objects.filter(pk=self.comment.pk).count(), 1)


# ============================================================================
# FORM TESTS
# ============================================================================

class TestBlogPostForm(TestCase):
    """Test BlogPostForm validation."""

    def test_valid_form(self):
        """Test form with valid data."""
        form_data = {
            'title': 'Test Blog',
            'content': 'Test content',
            'excerpt': 'Test excerpt',
            'category': 'Testing',
            'status': 'published'
        }
        form = BlogPostForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_missing_title(self):
        """Test form without title."""
        form_data = {
            'content': 'Test content',
            'excerpt': 'Test excerpt',
            'status': 'published'
        }
        form = BlogPostForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_missing_content(self):
        """Test form without content."""
        form_data = {
            'title': 'Test Blog',
            'excerpt': 'Test excerpt',
            'status': 'published'
        }
        form = BlogPostForm(data=form_data)
        self.assertFalse(form.is_valid())


class TestCommentForm(TestCase):
    """Test CommentForm validation."""

    def test_valid_comment_form(self):
        """Test form with valid data."""
        form_data = {'content': 'Great post!'}
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_empty_comment_form(self):
        """Test form without content."""
        form_data = {'content': ''}
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())
