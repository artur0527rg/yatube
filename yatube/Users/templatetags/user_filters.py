from hashlib import new
from django import template
# В template.Library зарегистрированы все теги и фильтры шаблонов
# добавляем к ним и наш фильтр
register = template.Library()


@register.filter 
def addclass(field, css):
        return field.as_widget(attrs={"class": css})

# синтаксис @register... , под которой описан класс addclass() - 
# это применение "декораторов", функций, обрабатывающих функции
# мы скоро про них расскажем. Не бойтесь соб@к

@register.filter
def uglify(field):
    dlin = len(field)
    new_str = ''
    for i in range(0, dlin):
        if i%2!=0:
            new_str += field[i].upper()
        if i%2==0:
            new_str += field[i].lower()
        
            
    return new_str
        