from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator

from django.shortcuts import get_object_or_404

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