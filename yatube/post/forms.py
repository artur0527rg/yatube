from django import forms

from .models import Post, Comment


#класс формы для добавления новой записи
class PostForm(forms.ModelForm):
    class Meta():
        # укажем модель, с которой связана создаваемая форма
        model = Post
        # укажем, какие поля должны быть видны в форме и в каком порядке
        fields = ("group", "text", 'image')


class CommentForm(forms.ModelForm):
    class Meta():
        model = Comment
        fields = ("text",)