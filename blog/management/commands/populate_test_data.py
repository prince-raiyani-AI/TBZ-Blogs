"""
Management command to populate test data
Usage: python manage.py populate_test_data
Reference: https://docs.djangoproject.com/en/5.2/howto/custom-management-commands/
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from blog.models import BlogPost, Comment, PostInteraction
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Populate database with test data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate test data...'))

        # Create test users
        users = []
        usernames = ['john_doe', 'jane_smith', 'alex_wilson', 'sarah_jones', 'mike_brown']

        for username in usernames:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@tbzblogs.com',
                    'first_name': username.split('_')[0].capitalize(),
                    'last_name': username.split('_')[1].capitalize() if '_' in username else 'User',
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Created user: {username}'))
            else:
                self.stdout.write(self.style.WARNING(f'~ User already exists: {username}'))

            # Create user profile
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'bio': f'I am {username}, a passionate blogger!',
                    'follower_count': 0,
                }
            )
            users.append(user)

        # Create test blog posts
        blog_titles = [
            'Getting Started with Django REST Framework',
            'Top 10 Python Tips and Tricks',
            'Building Modern Web Applications',
            'Understanding Database Optimization',
            'Mastering Git Workflows',
            'Cloud Computing for Beginners',
            'Machine Learning Basics',
            'Web Security Best Practices',
        ]

        blog_posts = []
        for idx, title in enumerate(blog_titles):
            author = users[idx % len(users)]
            blog, created = BlogPost.objects.get_or_create(
                title=title,
                author=author,
                defaults={
                    'slug': title.lower().replace(' ', '-'),
                    'content': f'''
                    <h2>{title}</h2>
                    <p>This is a comprehensive guide about {title.lower()}.</p>
                    <p>In this blog post, we will cover the basics, intermediate concepts, and advanced techniques.</p>
                    <h3>Introduction</h3>
                    <p>Let's start by understanding the fundamentals of {title.lower()}.</p>
                    <h3>Key Concepts</h3>
                    <ul>
                        <li>Concept 1</li>
                        <li>Concept 2</li>
                        <li>Concept 3</li>
                    </ul>
                    <h3>Conclusion</h3>
                    <p>We have covered the essentials of {title.lower()}. Keep practicing and stay updated!</p>
                    ''',
                    'excerpt': f'Learn about {title.lower()} in this comprehensive guide.',
                    'status': 'published',
                    'category': 'Technology',
                    'created_at': timezone.now() - timedelta(days=idx * 2),
                    'likes_count': 0,
                    'dislikes_count': 0,
                    'comments_count': 0,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created blog: {title}'))
            else:
                self.stdout.write(self.style.WARNING(f'~ Blog already exists: {title}'))
            blog_posts.append(blog)

        # Create test comments
        for blog in blog_posts:
            for i in range(2):
                commenter = users[(blog.id + i) % len(users)]
                if commenter != blog.author:
                    comment, created = Comment.objects.get_or_create(
                        post=blog,
                        author=commenter,
                        content=f'Great article on {blog.title}! Very informative.',
                        defaults={
                            'is_approved': True,
                        }
                    )
                    if created:
                        blog.comments_count += 1
                        blog.save()

        self.stdout.write(self.style.SUCCESS('✓ Created comments'))

        # Create test interactions
        for blog in blog_posts:
            for user in users[:3]:
                if user != blog.author:
                    interaction, created = PostInteraction.objects.get_or_create(
                        post=blog,
                        user=user,
                        interaction_type='like',
                    )
                    if created:
                        blog.likes_count += 1
                        blog.save()

        self.stdout.write(self.style.SUCCESS('✓ Created interactions'))

        self.stdout.write(self.style.SUCCESS('\n✅ Test data populated successfully!'))
        self.stdout.write(self.style.SUCCESS('\nAdmin Credentials:'))
        self.stdout.write(self.style.SUCCESS('Username: admin'))
        self.stdout.write(self.style.SUCCESS('Email: admin@tbzblogs.com'))
        self.stdout.write(self.style.SUCCESS('\nTest User Credentials:'))
        for username in usernames[:2]:
            self.stdout.write(self.style.SUCCESS(f'Username: {username}'))
            self.stdout.write(self.style.SUCCESS('Password: testpass123'))
