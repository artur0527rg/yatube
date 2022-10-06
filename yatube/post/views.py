from cgi import print_arguments
from itertools import count
import re
from time import process_time_ns
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import HttpResponseNotFound

from .models import Post, Group
from .forms import PostForm

# Create your views here.
def index(request):
        post_list = Post.objects.order_by('-pub_date').all()
        paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
        page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
        page = paginator.get_page(page_number)  # получить записи с нужным смещением
        return render(
            request,
            'index.html',
            {'page': page, 'paginator': paginator}
       )

# view-функция для страницы сообщества
def group_posts(request, slug):
    # функция get_object_or_404 получает по заданным критериям объект из базы данных
    # или возвращает сообщение об ошибке, если объект не найден
    group = get_object_or_404(Group, slug=slug)
    
    # Метод .filter позволяет ограничить поиск по критериям. Это аналог добавления
    post_list = Post.objects.filter(group=group).order_by("-pub_date")
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  
    return render(
        request,
        "group.html",
        {"group": group, 'page': page, 'paginator': paginator}
    )

def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid:
            form.instance.author = request.user
            post = form.save()
            return redirect('index')
    else:
        form = PostForm()
    return render(request, 'post/new_post.html', context={"form":form})

def profile(request, username):
    user = get_object_or_404(User, username=username)
    author_posts = Post.objects.filter(author_id=user).order_by('-pub_date')
    paginator = Paginator(author_posts, 10)
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  
    amount_posts = len(author_posts)
    if request.user == user:
        edit = True
    else:
        edit = False

    return render(
        request,
        'post/profile.html',
        {
        "edit":edit,
        "user_profile":user,
        "amount_posts":amount_posts,
        'page': page,
        'paginator': paginator
    })
 
 
def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    if request.user == user:
        edit = True
    else:
        edit = False
    post = get_object_or_404(Post, pk = post_id)
    author_posts = Post.objects.filter(author_id=post.author_id).order_by('-pub_date')
    amount_posts = len(author_posts)
    return render(request, 'post/post.html', {'amount_posts':amount_posts, "user_profile":user, 'post':post, 'edit':edit})


def post_edit(request, username, post_id):
    # тут тело функции. Не забудьте проверить, 
    # что текущий пользователь — это автор записи.
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author_id = user, pk = post_id)
    print(request.user, end="\n\n\n")
    if request.user == user:
        if request.method == 'POST':
            form = PostForm(request.POST)
            if form.is_valid:
                form = PostForm(request.POST, instance=post)
                form.save()
                return redirect('post', username=username, post_id=post_id)
        else:
            
            form = PostForm(instance=post)
            return render(request, 'post/new_post.html', context={"form":form, 'edit_page':True, 'post':post})
    else:
        return redirect('post', username=username, post_id=post_id)     

    # В качестве шаблона страницы редактирования укажите шаблон создания новой записи
    # который вы создали раньше (вы могли назвать шаблон иначе)
    return render(request, 'post/new_post.html', {})