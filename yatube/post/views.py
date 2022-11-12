from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import HttpResponseNotFound
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required


from .models import Post, Group, Follow
from .forms import PostForm, CommentForm

# Create your views here.
@cache_page(20, key_prefix="index_page")
def index(request):
        post_list = Post.objects.order_by('-pub_date').select_related('group', 'author').prefetch_related('comments')  
        paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
        page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
        page = paginator.get_page(page_number)  # получить записи с нужным смещением
        return render(
            request,
            'index.html',
            {'page': page, 'paginator': paginator}
       )

# view-функция для страницы сообществаgi
def group_posts(request, slug):
    # функция get_object_or_404 получает по заданным критериям объект из базы данных
    # или возвращает сообщение об ошибке, если объект не найден
    group = get_object_or_404(Group, slug=slug)
    
    # Метод .filter позволяет ограничить поиск по критериям. Это аналог добавления
    post_list = Post.objects.filter(group=group).order_by("-pub_date").select_related('group', 'author').prefetch_related('comments')  
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  
    return render(
        request,
        "group.html",
        {"group": group, 'page': page, 'paginator': paginator}
    )

def new_post(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PostForm(request.POST or None, files=request.FILES or None)
            if form.is_valid():
                form.instance.author = request.user
                post = form.save()
                return redirect('index')
        else:
            form = PostForm()
        return render(request, 'post/new_post.html', context={"form":form})
    else:
        return redirect('index')

def profile(request, username):
    user = get_object_or_404(User, username=username)
    if request.user.is_authenticated:
        try:
            following = Follow.objects.get(user=request.user, author=user)
        except Follow.DoesNotExist:
            following = False
    else:
        following = False
    author_posts = Post.objects.filter(author_id=user).order_by('-pub_date').select_related('group', 'author').prefetch_related('comments')  
    paginator = Paginator(author_posts, 10)
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  
    amount_posts = len(author_posts)
    return render(
        request,
        'post/profile.html',
        {
        'user_profile': user,
        "amount_posts":amount_posts,
        'page': page,
        'paginator': paginator,
        'following':following, # Используем только для кнопки "подписаться"
    })
 
 
def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk = post_id)
    try:
        following = Follow.objects.get(user=request.user, author=user)
    except Follow.DoesNotExist:
        following = False
    author_posts = Post.objects.filter(author_id=post.author_id).order_by('-pub_date') 
    amount_posts = len(author_posts)
    form = CommentForm()    
    comments = post.comments.all()

    return render(
        request,
        'post/post.html',
        {'amount_posts':amount_posts,
        "user_profile":user,
        'post':post,
        'form': form,
        'items': comments,
        'following':following, # Используем только для кнопки "подписаться"
    })


def post_edit(request, username, post_id):
    # тут тело функции. Не забудьте проверить, 
    # что текущий пользователь — это автор записи.
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author_id = user, pk = post_id)
    if request.user == user:
        if request.method == 'POST':
            form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
            if form.is_valid():
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

def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию, 
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request, 
        "misc/404.html", 
        {"path": request.path}, 
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)

def add_comment(request, username, post_id):
     if request.user.is_authenticated:
        if request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                form.instance.author = request.user
                form.instance.post = Post.objects.get(pk=post_id)
                post = form.save()
        return redirect(f'/{username}/{post_id}/')
     else:
        return redirect('index')

@login_required()
def follow_index(request):
    # Ищим все посты, в которых автор - id в поле following.
    # Какие записи достать из модели Follow?
    # Те, в которых user = request.user
    # Тоисть берем поле following, но фильтруем по user(follower)
    post_list = (
        Post.objects
        .filter(author__following__user=request.user)
        .order_by('-pub_date')
        .select_related('group', 'author')
        .prefetch_related('comments')
    )
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(
        request,
        'follow.html',
        {'page': page, 'paginator': paginator}
    )
    
    

@login_required()
def profile_follow(request, username):
    check = User.objects.get(username=username)
    if request.user == check:
        return HttpResponseNotFound('Вы не можете подписаться сами на себя')
    else:
        author = User.objects.get(username=username)
        Follow.objects.create(user=request.user, author=author)
        return redirect('profile', username)

@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    obj = Follow.objects.get(user=request.user, author=author)
    obj.delete()
    return redirect('profile', username)