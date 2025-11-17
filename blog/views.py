"""
Blog App Views for CRUD operations
Reference: https://docs.djangoproject.com/en/5.2/topics/http/views/
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import BlogPost, Comment, PostInteraction
from .forms import BlogPostForm, CommentForm
from accounts.models import UserProfile


def home(request):
    """
    Home page view showing latest blog posts with pagination.
    Reference: https://docs.djangoproject.com/en/5.2/topics/http/views/
    """
    # Get all published blog posts ordered by creation date
    blogs = BlogPost.objects.filter(status='published').order_by('-created_at')
    
    # Pagination: 6 blogs per page
    paginator = Paginator(blogs, 6)
    page = request.GET.get('page')
    
    try:
        blogs = paginator.page(page)
    except PageNotAnInteger:
        blogs = paginator.page(1)
    except EmptyPage:
        blogs = paginator.page(paginator.num_pages)
    
    context = {
        'page_title': 'Home',
        'blogs': blogs,
        'total_posts': paginator.count,
    }
    return render(request, 'blog/home.html', context)


def blog_list(request):
    """
    List all published blog posts with filtering and search.
    Reference: https://docs.djangoproject.com/en/5.2/topics/db/queries/
    """
    blogs = BlogPost.objects.filter(status='published').order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        blogs = blogs.filter(
            Q(title__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    
    # Filter by category
    category_filter = request.GET.get('category', '')
    if category_filter:
        blogs = blogs.filter(category__icontains=category_filter)
    
    # Pagination
    paginator = Paginator(blogs, 9)
    page = request.GET.get('page')
    
    try:
        blogs = paginator.page(page)
    except PageNotAnInteger:
        blogs = paginator.page(1)
    except EmptyPage:
        blogs = paginator.page(paginator.num_pages)
    
    context = {
        'page_title': 'All Blogs',
        'blogs': blogs,
        'search_query': search_query,
        'category_filter': category_filter,
        'total_posts': paginator.count,
    }
    return render(request, 'blog/blog_list.html', context)


def blog_detail(request, slug):
    """
    Display single blog post with comments and interactions.
    Authors are allowed to view their own drafts; public detail only shows published posts.
    """
    try:
        blog = BlogPost.objects.get(slug=slug, status='published')
    except BlogPost.DoesNotExist:
        # If the post isn't published, allow the author to view it when logged in.
        if request.user.is_authenticated:
            try:
                blog = BlogPost.objects.get(slug=slug, author=request.user)
            except BlogPost.DoesNotExist:
                raise Http404("No BlogPost matches the given query.")
        else:
            raise Http404("No BlogPost matches the given query.")
    
    # Increment view count each time the blog is viewed
    blog.views_count += 1
    blog.save(update_fields=['views_count'])
    
    # Get approved comments with nested structure
    comments = blog.comments.filter(is_approved=True, parent=None).order_by('-created_at')
    
    # Get user's interaction with this blog (if authenticated)
    user_interaction = None
    if request.user.is_authenticated:
        user_interaction = blog.interactions.filter(user=request.user).first()
    
    # Comment form for POST requests
    form = CommentForm()
    
    context = {
        'page_title': blog.title,
        'blog': blog,
        'comments': comments,
        'form': form,
        'user_interaction': user_interaction,
    }
    return render(request, 'blog/blog_detail.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def blog_create(request):
    """
    Create a new blog post. Only authenticated users can create.
    Reference: https://docs.djangoproject.com/en/5.2/ref/decorators/#require-http-methods
    """
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            # Create blog post with current user as author
            blog = form.save(commit=False)
            blog.author = request.user
            blog.status = 'published'  # Set as published by default
            blog.save()

            messages.success(request, f'Blog post "{blog.title}" created and published successfully!')
            # Redirect to the blog detail page so user can see the published post
            return redirect('blog_detail', slug=blog.slug)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = BlogPostForm()
    
    context = {
        'page_title': 'Create Blog Post',
        'form': form,
        'action': 'create'
    }
    return render(request, 'blog/blog_form.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def blog_edit(request, slug):
    """
    Edit an existing blog post. Only author can edit.
    """
    blog = get_object_or_404(BlogPost, slug=slug)
    
    # Check if user is the author
    if request.user != blog.author:
        messages.error(request, 'You can only edit your own blog posts.')
        return redirect('blog_detail', slug=slug)
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, f'Blog post "{blog.title}" updated successfully!')
            return redirect('blog_detail', slug=blog.slug)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = BlogPostForm(instance=blog)
    
    context = {
        'page_title': f'Edit: {blog.title}',
        'form': form,
        'blog': blog,
        'action': 'edit'
    }
    return render(request, 'blog/blog_form.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def blog_delete(request, slug):
    """
    Delete a blog post. Only author can delete.
    """
    blog = get_object_or_404(BlogPost, slug=slug)
    
    # Check if user is the author
    if request.user != blog.author:
        messages.error(request, 'You can only delete your own blog posts.')
        return redirect('blog_detail', slug=slug)
    
    if request.method == 'POST':
        blog_title = blog.title
        blog.delete()
        messages.success(request, f'Blog post "{blog_title}" deleted successfully!')
        return redirect('blog_list')
    
    context = {
        'page_title': f'Delete: {blog.title}',
        'blog': blog,
    }
    return render(request, 'blog/blog_delete.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def comment_create(request, slug):
    """
    Add a comment to a blog post.
    """
    blog = get_object_or_404(BlogPost, slug=slug, status='published')
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = blog
            comment.author = request.user
            
            # Check if this is a reply to another comment
            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent_comment = get_object_or_404(
                    Comment, 
                    id=parent_id, 
                    post=blog
                )
                comment.parent = parent_comment
            
            comment.save()
            # Increment comment count
            blog.comments_count += 1
            blog.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('blog_detail', slug=slug)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    
    return redirect('blog_detail', slug=slug)


@login_required(login_url='login')
def blog_publish(request, slug):
    """
    Publish a draft blog post. Only author can publish.
    """
    blog = get_object_or_404(BlogPost, slug=slug)
    
    # Check if user is the author
    if request.user != blog.author:
        messages.error(request, 'You can only publish your own blog posts.')
        return redirect('blog_detail', slug=slug)
    
    if blog.status == 'draft':
        blog.status = 'published'
        blog.save()
        messages.success(request, f'Blog post "{blog.title}" published successfully!')
    else:
        messages.info(request, 'This blog post is already published.')
    
    return redirect('blog_detail', slug=slug)


@login_required(login_url='login')
def blog_draft(request, slug):
    """
    Move a published blog post back to draft. Only author can do this.
    """
    blog = get_object_or_404(BlogPost, slug=slug)
    
    # Check if user is the author
    if request.user != blog.author:
        messages.error(request, 'You can only modify your own blog posts.')
        return redirect('blog_detail', slug=slug)
    
    if blog.status == 'published':
        blog.status = 'draft'
        blog.save()
        messages.success(request, f'Blog post "{blog.title}" moved to draft.')
    
    return redirect('blog_detail', slug=slug)


@login_required(login_url='login')
def my_blogs(request):
    """
    Display all blog posts by the current user.
    """
    blogs = BlogPost.objects.filter(author=request.user).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter in ['published', 'draft']:
        blogs = blogs.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(blogs, 6)
    page = request.GET.get('page')
    
    try:
        blogs = paginator.page(page)
    except PageNotAnInteger:
        blogs = paginator.page(1)
    except EmptyPage:
        blogs = paginator.page(paginator.num_pages)
    
    context = {
        'page_title': 'My Blogs',
        'blogs': blogs,
        'status_filter': status_filter,
        'total_posts': paginator.count,
    }
    return render(request, 'blog/my_blogs.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def blog_interact(request, slug):
    """
    Handle like/dislike interactions for a blog post.
    Toggle interaction: if user clicks same interaction again it is removed; switching removes opposite interaction.
    """
    blog = get_object_or_404(BlogPost, slug=slug, status='published')

    if not request.user.is_authenticated:
        messages.info(request, 'Please login to interact with posts.')
        return redirect('login')

    action = request.POST.get('action')
    if action not in ('like', 'dislike'):
        messages.error(request, 'Invalid action.')
        return redirect('blog_detail', slug=slug)

    user = request.user
    existing_like = PostInteraction.objects.filter(post=blog, user=user, interaction_type='like').first()
    existing_dislike = PostInteraction.objects.filter(post=blog, user=user, interaction_type='dislike').first()

    if action == 'like':
        if existing_like:
            # remove like
            existing_like.delete()
            blog.likes_count = max(0, blog.likes_count - 1)
            messages.info(request, 'Like removed.')
        else:
            # remove dislike if present
            if existing_dislike:
                existing_dislike.delete()
                blog.dislikes_count = max(0, blog.dislikes_count - 1)
            # add like
            PostInteraction.objects.create(post=blog, user=user, interaction_type='like')
            blog.likes_count += 1
            messages.success(request, 'You liked this post.')
    else:  # dislike
        if existing_dislike:
            existing_dislike.delete()
            blog.dislikes_count = max(0, blog.dislikes_count - 1)
            messages.info(request, 'Dislike removed.')
        else:
            if existing_like:
                existing_like.delete()
                blog.likes_count = max(0, blog.likes_count - 1)
            PostInteraction.objects.create(post=blog, user=user, interaction_type='dislike')
            blog.dislikes_count += 1
            messages.success(request, 'You disliked this post.')

    blog.save()
    return redirect('blog_detail', slug=slug)


@login_required(login_url='login')
@require_http_methods(["POST"])
def comment_delete(request, pk):
    """
    Delete a comment. Allowed for comment author or post author.
    """
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post

    if request.user == comment.author or request.user == post.author:
        comment.delete()
        post.comments_count = max(0, post.comments_count - 1)
        post.save()
        messages.success(request, 'Comment deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this comment.')

    return redirect('blog_detail', slug=post.slug)


# AI-Powered Features API Endpoints

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from core.ai_service import ai_service


@login_required(login_url='login')
@require_http_methods(["POST"])
@login_required(login_url='login')
@require_http_methods(["POST"])
def api_generate_blog_from_idea(request):
    """
    API endpoint to generate a blog from an idea using AI
    """
    try:
        data = json.loads(request.body)
        idea = data.get('idea', '').strip()
        length = data.get('length', 'medium')
        
        if not idea:
            return JsonResponse({'error': 'Idea is required'}, status=400)
        
        if not ai_service.is_available():
            return JsonResponse({'error': 'AI service is not available'}, status=503)
        
        result = ai_service.generate_blog_from_idea(idea, length)
        
        if 'error' in result:
            return JsonResponse({'error': result['error']}, status=400)
        
        return JsonResponse(result)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required(login_url='login')
@require_http_methods(["POST"])
def api_enhance_content(request):
    """
    API endpoint to enhance blog content using AI
    """
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        style = data.get('style', 'professional')
        
        if not content:
            return JsonResponse({'error': 'Content is required'}, status=400)
        
        if not ai_service.is_available():
            return JsonResponse({'error': 'AI service is not available'}, status=503)
        
        result = ai_service.enhance_content(content, style)
        
        if 'error' in result:
            return JsonResponse({'error': result['error']}, status=400)
        
        return JsonResponse(result)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required(login_url='login')
@require_http_methods(["POST"])
@login_required(login_url='login')
@require_http_methods(["POST"])
def api_translate_content(request):
    """
    API endpoint to translate blog content using AI
    """
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        language = data.get('language', '').strip()
        
        if not content:
            return JsonResponse({'error': 'Content is required'}, status=400)
        
        if not language:
            return JsonResponse({'error': 'Target language is required'}, status=400)
        
        if not ai_service.is_available():
            return JsonResponse({'error': 'AI service is not available'}, status=503)
        
        result = ai_service.translate_content(content, language)
        
        if 'error' in result:
            return JsonResponse({'error': result['error']}, status=400)
        
        return JsonResponse(result)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

