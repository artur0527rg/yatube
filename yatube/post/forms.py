from django import forms

from .models import Post


#класс формы для добавления новой записи
class PostForm(forms.ModelForm):
    class Meta():
        # укажем модель, с которой связана создаваемая форма
        model = Post
        # укажем, какие поля должны быть видны в форме и в каком порядке
        fields = ("group", "text")