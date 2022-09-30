from django.shortcuts import render, redirect
from django.http import HttpResponse

from .models import Post, Group
from .forms import PostForm

# Create your views here.
def index(request):
    latest = Post.objects.order_by("-pub_date")[:11]
    return render(request, "index.html", {"posts": latest})

# view-функция для страницы сообщества
def group_posts(request, slug):
    # функция get_object_or_404 получает по заданным критериям объект из базы данных 
    def get_object_or_404(group, slug):
        try:
            object = Group.objects.get(slug = slug)
            return object
        except :
            pass
    
    # или возвращает сообщение об ошибке, если объект не найден
    group = get_object_or_404(Group, slug=slug)
    
    # # Метод .filter позволяет ограничить поиск по критериям. Это аналог добавления
    # # условия WHERE group_id = {group_id}
    posts = Post.objects.filter(group=group).order_by("-pub_date")[:12]
    return render(request, "group.html", {"group": group, "posts": posts})

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