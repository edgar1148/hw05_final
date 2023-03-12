from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, Follow, User
from .constants import POSTS_PER_PAGE
from .utils import get_page_context


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.order_by('-pub_date')
    page_obj = get_page_context(request, posts, count_post=POSTS_PER_PAGE)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


@cache_page(20)
def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    page_obj = get_page_context(request, post_list, count_post=POSTS_PER_PAGE)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.order_by('-pub_date')
    posts_count = Post.objects.filter(author=author).count()
    page_obj = get_page_context(request, posts, count_post=POSTS_PER_PAGE)
    following = request.user.is_authenticated
    if following:
        following = author.following.filter(user=request.user).exists()
    context = {
        'author': author,
        'posts': posts,
        'posts_count': posts_count,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    form = CommentForm()
    context = {
        'post': post,
        'requser': request.user,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        create_post = form.save(commit=False)
        create_post.author = request.user
        create_post.save()
        return redirect('posts:profile', create_post.author)
    context = {'form': form}
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {'form': form, 'post': post, 'is_edit': True}
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(
        author__following__user=request.user)
    page_obj = get_page_context(request, posts, count_post=POSTS_PER_PAGE)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    follow = get_object_or_404(
        Follow,
        user=request.user,
        author__username=username
    )
    follow.delete()
    return redirect('posts:profile', username)
