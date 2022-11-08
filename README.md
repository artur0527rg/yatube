# yatube
Социальная сеть блогеров
 
Мой учебный для Яндекс Практикума

git clone https://github.com/artur0527rg/yatube.git

cd yatube/

python -m venv venv

source venv/Scripts/activate

pip install -r requirements.txt

cd yatube/

python manage.py migrate

python manage.py runserver
