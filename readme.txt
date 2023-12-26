1) Виртуальная среда питон:
создание вирт среды
python -m venv .venv
активация
.venv\Scripts\activate
деактивация
deactivate
установка зависимостей
pip install -r requirements.txt
2)докер
https://blog.ithillel.ua/ru/articles/sovety-po-startu-proekta-na-django-i-docker
3) admin 1234
4) python manage.py inspectdb > models.py создание моделей бд
5) генерация requirements 
pip freeze > requirements.txt
6) настройка vscode 
mkdir .vscode
7)  python manage.py runserver 192.168.6.168:8001