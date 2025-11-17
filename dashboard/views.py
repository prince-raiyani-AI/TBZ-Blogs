from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from datetime import timedelta
from blog.models import BlogPost, Comment
from core.sentiment_service import analyze_sentiment, classify_comment_importance, get_comment_summary
import json


@login_required(login_url='login')
def analytics_dashboard(request):
    """
    Main analytics dashboard showing overall user statistics and engagement metrics.
    """
    user = request.user
    
    # Get user's blog posts
    user_blogs = BlogPost.objects.filter(author=user)
    total_blogs = user_blogs.count()
    published_blogs = user_blogs.filter(status='published').count()
    draft_blogs = user_blogs.filter(status='draft').count()
    
    # Get engagement metrics
    total_views = sum(blog.views_count for blog in user_blogs)
    total_comments = Comment.objects.filter(post__author=user).count()
    total_likes = sum(blog.likes_count for blog in user_blogs)
    
    # Calculate engagement rate
    engagement_rate = 0
    if total_blogs > 0:
        engagement_rate = round((total_views + total_comments + total_likes) / (total_blogs * 100), 2)
    
    # Get recent activity (comments in last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_comments = Comment.objects.filter(
        post__author=user,
        created_at__gte=seven_days_ago
    ).order_by('-created_at')[:10]
    
    # Analyze sentiment across all comments
    all_comments = Comment.objects.filter(post__author=user)
    sentiment_data = get_comment_summary(all_comments)
    
    # Prepare sentiment chart data
    sentiment_chart = {
        'positive': sentiment_data.get('positive_count', 0),
        'neutral': sentiment_data.get('neutral_count', 0),
        'negative': sentiment_data.get('negative_count', 0),
    }
    
    # Get top performing blogs
    top_blogs = user_blogs.annotate(
        engagement=F('views_count') + F('likes_count') + F('comments_count')
    ).order_by('-engagement')[:5]
    
    # Get importance distribution
    importance_breakdown = {
        'high': sum(1 for c in all_comments if classify_comment_importance(c.content)['importance'] == 'HIGH'),
        'medium': sum(1 for c in all_comments if classify_comment_importance(c.content)['importance'] == 'MEDIUM'),
        'low': sum(1 for c in all_comments if classify_comment_importance(c.content)['importance'] == 'LOW'),
    }
    
    context = {
        'total_blogs': total_blogs,
        'published_blogs': published_blogs,
        'draft_blogs': draft_blogs,
        'total_views': total_views,
        'total_comments': total_comments,
        'total_likes': total_likes,
        'engagement_rate': engagement_rate,
        'recent_comments': recent_comments,
        'sentiment_chart': json.dumps(sentiment_chart),
        'sentiment_data': sentiment_data,
        'top_blogs': top_blogs,
        'importance_breakdown': importance_breakdown,
    }
    
    return render(request, 'dashboard/analytics.html', context)


@login_required(login_url='login')
def blog_analytics(request, slug):
    """
    Detailed analytics for a specific blog post including comment sentiment analysis.
    """
    user = request.user
    blog = get_object_or_404(BlogPost, slug=slug)
    
    # Security check: ensure user owns this blog
    if blog.author != user:
        return redirect('analytics_dashboard')
    
    # Get blog metrics
    views = blog.views_count
    likes = blog.likes_count
    comments_count = blog.comments_count
    
    # Calculate engagement
    total_engagement = views + likes + comments_count
    engagement_rate = round(total_engagement / max(1, views) * 100, 2) if views > 0 else 0
    
    # Get all comments for this blog
    comments = Comment.objects.filter(post=blog).order_by('-created_at')
    
    # Analyze comment sentiment and importance
    comments_analysis = []
    for comment in comments:
        sentiment = analyze_sentiment(comment.content)
        importance = classify_comment_importance(comment.content)
        comments_analysis.append({
            'comment': comment,
            'sentiment': sentiment,
            'importance': importance,
        })
    
    # Get sentiment summary
    sentiment_summary = get_comment_summary(comments)
    
    # Prepare sentiment chart data
    sentiment_chart = {
        'positive': sentiment_summary.get('positive_count', 0),
        'neutral': sentiment_summary.get('neutral_count', 0),
        'negative': sentiment_summary.get('negative_count', 0),
    }
    
    # Count importance levels
    importance_breakdown = {
        'high': sum(1 for ca in comments_analysis if ca['importance']['importance'] == 'HIGH'),
        'medium': sum(1 for ca in comments_analysis if ca['importance']['importance'] == 'MEDIUM'),
        'low': sum(1 for ca in comments_analysis if ca['importance']['importance'] == 'LOW'),
    }
    
    # Get high importance comments
    high_importance_comments = [ca for ca in comments_analysis if ca['importance']['importance'] == 'HIGH']
    
    context = {
        'blog': blog,
        'views': views,
        'likes': likes,
        'comments_count': comments_count,
        'engagement_rate': engagement_rate,
        'total_engagement': total_engagement,
        'comments_analysis': comments_analysis,
        'sentiment_summary': sentiment_summary,
        'sentiment_chart': json.dumps(sentiment_chart),
        'importance_breakdown': importance_breakdown,
        'high_importance_comments': high_importance_comments,
        'total_comments': comments.count(),
    }
    
    return render(request, 'dashboard/blog_analytics.html', context)
