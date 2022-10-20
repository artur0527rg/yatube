"""yatube URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.flatpages import views
from django.conf.urls import handler404, handler500
from django.conf import settings
from django.conf.urls.static import static

handler404 = "post.views.page_not_found"  # noqa
handler500 = "post.views.server_error" # noqa


urlpatterns = [
    # админка в перую очередь
    path('admin_login/', admin.site.urls),

     # flatpages
    path('about/', include('django.contrib.flatpages.urls')),

    #  регистрация и авторизация
    path("auth/", include("Users.urls")),

    #  если нужного шаблона для /auth не нашлось в файле users.urls — 
    #  ищем совпадения в файле django.contrib.auth.urls
    path("auth/", include("django.contrib.auth.urls")),

]

# новые пути, имитируем злого SEO)
urlpatterns += [
    path('rasskaz-o-tom-kakie-my-horoshie/', views.flatpage, {'url': '/about-us/'}, name='about'),
    path('about-us/', views.flatpage, {'url': '/about-us/'}, name='about'),
    path('about-author/', views.flatpage, {'url': '/about-us/'}, name='about'),
    path('about-spec/', views.flatpage, {'url': '/about-spec/'}, name='spec'),
]

# Костыль. В новых уроках для about создают отдельное приложение,
# но так как я делал по старым, то структуру оставлю такой.
urlpatterns +=[
    #  обработчик для главной страницы ищем в urls.py приложения posts
    path("", include("post.urls")),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(settings.STATIC_URL,
    document_root=settings.STATIC_ROOT
    )