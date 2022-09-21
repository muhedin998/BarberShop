from django.shortcuts import render, get_object_or_404
from .models import Post
from datetime import datetime
from django.core.paginator import Paginator, PageNotAnInteger,EmptyPage

def home(request):
    posts = Post.published.all()
    paginator = Paginator(posts,3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    now = datetime.now()
    return render(request, 'blog/index.html',{'post':posts,'now':now, 'page':page})

def post_detail(request, year, month, day, post):
    post =  get_object_or_404(Post, slug=post, status='published',
        publish__year = year,
        publish__month=month,
        publish__day = day)
    return render(request, 'blog/detail.html',{'post':post})
