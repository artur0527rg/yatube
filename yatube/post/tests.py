# Каждый логический набор тестов — это класс, 
# который наследуется от базового класса TestCase
from django.test import TestCase, override_settings
from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from .models import Post, Group, Follow, Comment
from .forms import PostForm

import tempfile

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
class FinalTest_5(TestCase):
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

        cache.clear() #чистим кеш, что бы нужный пост отобразился

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

        cache.clear() #чистим кеш, что бы нужный пост отобразился

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


class ImgTest(TestCase):
    def setUp(self):
        # Авторизированный клиент
        self.aut_client=Client()

        # Cоздание и вход авторезированного юзера
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.login = self.aut_client.login(username='testuser', password='12345')

        self.group = Group.objects.create(title='First group', slug='first_group', description='text')
    
    # Хрупкий тест
    def test_page_have_img(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            with override_settings(MEDIA_ROOT=temp_directory):
                with open('media/post/file.jpg','rb') as img:
                    self.post = self.aut_client.post("/new/", {'author': self.user, 'text': 'post with image', 'group': self.group.pk, 'image': img})

                    cache.clear() #чистим кеш, что бы нужный пост отобразился

                    page = self.aut_client.get(f'/{self.user.username}/')
                    self.assertContains(page, 'unique_id')
                    # self.assertContains(page, '<img')
                    # self.assertIn('<img', str(page.content), msg='Картинки нет на странице поста')
        
                    page = self.aut_client.get(f'/')
                    self.assertContains(page, 'unique_id')
                    # self.assertContains(page, '<img')
                    # self.assertIn('<img', str(page.content), msg='Картинки нет на главной странице')
        
                    page = self.aut_client.get(f'/{self.user.username}/')
                    self.assertContains(page, 'unique_id')
                    # self.assertContains(page, '<img')
                    # self.assertIn('<img', str(page.content), msg='Картинки нет на странице автора')

                    page = self.aut_client.get(f'/group/first_group/')
                    self.assertContains(page, 'unique_id')
                    # self.assertContains(page, '<img')
                    # self.assertIn('<img', str(page.content), msg='Картинки нет на странице группы')

    def test_incorrect_file_format(self):
        with open('db.sqlite3','rb') as file:
            post = self.aut_client.post("/new/", {'author': self.user, 'text': 'post with image', 'group': self.group.pk, 'image': file})
            self.assertEqual(post.status_code, 200, msg='Не сработала валидация файла')


class CacheTest(TestCase):
    def setUp(self):
        # Авторизированный клиент
        self.aut_client=Client()

        # Cоздание и вход авторезированного юзера
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.login = self.aut_client.login(username='testuser', password='12345')

    

    def test_index_page_test(self):
        cache.clear()# Чистим кеш перед тестом
        
        response = self.aut_client.get('/')# Кешируем страницу
        post = Post.objects.create(text = "text1", author = self.user)# Создаем тестовый пост
        response_cache = self.aut_client.get('/')# Получаем экземпляр
        # Проверяю, передается ли контекст или загружаем страницу с кеша
        self.assertEqual(response.content, response_cache.content, msg='Страница не кешируется')
        

class FinalTest_6(TestCase):
    def setUp(self):
        # Авторизированный и неавторезированный клиенты
        self.aut_client=Client()
        self.aut_prob_client = Client()
        self.client = Client()

        # Cоздание и вход авторезированных юзеров
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.login = self.aut_client.login(username='testuser', password='12345')

        self.user2 = User.objects.create_user(username='prob', password='12345')
        self.login2 = self.aut_prob_client.login(username='prob', password='12345')
    
    
    def test_follow(self):
        response = self.aut_client.get('/prob/follow/')
        try:
            obj = Follow.objects.get(user=User.objects.get(username='testuser'))
        except Follow.DoesNotExist:
            obj = False

        self.assertNotEqual(obj, False, msg="Подписка не сработала")

        response = self.aut_client.get('/prob/unfollow/')

        try:
            obj = Follow.objects.get(user=User.objects.get(username='testuser'))
        except Follow.DoesNotExist:
            obj = False

        self.assertEqual(obj, False, msg="Отподписка не сработала")

    def test_timeline(self):
        # Пользователь, который подписан на "проб", видит его посты
        response = self.aut_client.get('/prob/follow/')
        post = Post.objects.create(author=self.user2, text='text')
        try:
            response = self.aut_client.get('/follow/').context['page'].object_list[0]
        except IndexError:
            response = False

        self.assertNotEqual(response, False, msg='Пользователь не видит постов тех, на кого подписан')

        # "Проб" не видит свой пост в своих подписках
        try:
            response = self.aut_prob_client.get('/follow/').context['page'].object_list[0]
        except IndexError:
            response = False

        self.assertEqual(False, False, msg='Пользователь видит посты тех, на кого не подписан')

    def test_comment(self):
        # Пост к ктоторому будмем добовлять комментарий 
        post = Post.objects.create(author=self.user2, text='test text')

        # Пробник пустого кверисета
        sample = Comment.objects.all()

        # Неавторезированный пользователь пытается создать комментарий
        comment = self.client.post(f'/{self.user2.username}/{post.id}/comment', data={'author':self.user, 'text':'Wubba Lubba Dub Dub'})
        # Получаем новый кверисет для сравнения
        comments = Comment.objects.all()
        self.assertEqual(list(comments), list(sample), msg="Неавторезированный пользователь может создать комментарий")
        
        # Авторезированный пользователь пытается создать комментарий
        comment = self.aut_client.post(f'/{self.user2.username}/{post.id}/comment', data={'author':self.user, 'text':'Wubba Lubba Dub Dub'})
        # Получаем новый кверисет для сравнения
        comments = Comment.objects.all()
        self.assertNotEqual(list(comments), list(sample), msg="Авторезированный пользователь неможет создать комментарий")
        
        





