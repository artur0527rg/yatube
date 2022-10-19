# Каждый логический набор тестов — это класс, 
# который наследуется от базового класса TestCase
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Post

# Каждый класс — это набор тестов. Имя такого класса принято начинать со слова Test.
# В файле может быть множество наборов тестов, 
# не обязательно иметь один класс для всего приложения. 
class TestStringMethods(TestCase):

    # Каждый отдельный метод в наборе тестов должен начинаться со слова test
    # таких методов-тестов в наборе может быть множество.
    def test_length(self):
        # В этой строке находится собственно тест который проверяет 
        # предположение (assertion) являются ли переданные параметры 
        # эквивалентными (equal) 
        self.assertEqual(len('yatube'), 6)
    
    #ломаем тест
    def test_show_msg(self):
        # действительно ли первый аргумент — True?
        self.assertTrue(True, msg="Важная проверка на истинность")

# Финальный проект - тест
class FinalTest(TestCase):
    def setUp(self):
        # Авторизированный и неавторезированный клиенты
        self.aut_client=Client()
        self.client = Client()

        # Cоздание и вход авторезированного юзера
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.login = self.aut_client.login(username='testuser', password='12345')
    
    # Тест созадиня страницы для нового пользователя
    def test_user_profile(self):
        prof = self.aut_client.get('/testuser/')
        self.assertEqual(prof.status_code, 200, msg="Страница не была создана") 

    # Тест создания нового поста пользователем
    def test_create_post(self):
        response = self.aut_client.post('/new/', data={'text':'Wubba Lubba Dub Dub'}, follow=True)
        post = Post.objects.order_by('-pub_date')[:1]
        text = post[0].text
        self.assertEqual(text, "Wubba Lubba Dub Dub", msg ="Пользователь не может создать пост")
    
    # Тест редиректа неавторезированного пользователя
    def test_redirect(self):
        response = self.client.post('/new/')
        self.assertRedirects(response, '/')
    
    def test_new_post(self):
        # Создание тестнового поста
        post = Post.objects.create(text = "text1", author = self.user)

        # Проверка поста на главной странице
        response = self.aut_client.get('/')
        index_post = response.context['page'][0]
        self.assertEqual(index_post, post, msg="Пост не отображается на главной странице")

        # Проверка поста на странице профиля пользователя
        response = self.aut_client.get('/testuser/')
        profile_post = response.context['page'][0]
        self.assertEqual(profile_post, post, msg="Пост не отображается на странице пользователя")

        # Проверка отдельной страницы поста
        response = self.aut_client.get('/testuser/1/')
        post_post = response.context['post']
        self.assertEqual(post_post, post, msg="Посте не отображается на отдельной странице")

    def test_edit_post(self):
        # Создание тестового поста(можно было бы и не создавать, но тест не получилось бы запустить отдельно)
        post = Post.objects.create(text = "text1", author = self.user)
        # Редактирование поста
        edit = self.aut_client.post(f'/{self.user.username}/{post.pk}/edit/', data={'text':'edit text'})
        edit_post = Post.objects.get(pk=post.pk)

        # Проверка изменений
        # Проверка поста на главной странице
        response = self.aut_client.get('/')
        index_post = response.context['page'][0]
        self.assertEqual(index_post, edit_post, msg="Пост не изенился на главной странице")

        # Проверка поста на странице профиля пользователя
        response = self.aut_client.get('/testuser/')
        profile_post = response.context['page'][0]
        self.assertEqual(profile_post, edit_post, msg="Пост не изменился на странице пользователя")

        # Проверка отдельной страницы поста
        response = self.aut_client.get('/testuser/1/')
        post_post = response.context['post']
        self.assertEqual(post_post, edit_post, msg="Посте не изменился на отдельной странице")
        
    def test_page_not_found(self):
        response = self.client.get('/page_not_found/')
        self.assertEqual(response.status_code, 404, msg="page_not_found не обработан")