import os
import sys

# Добавляем путь к вашему проекту, чтобы Python знал, где его искать
sys.path.append('/home/turlan91/fridge')  # Укажите правильный путь к вашему проекту

# Укажите путь до вашего виртуального окружения
virtualenv_path = '/home/turlan91/fridge/myenv'  # Путь до вашего виртуального окружения
activate_this = os.path.join(virtualenv_path, 'bin/activate')
if os.path.exists(activate_this):
    exec(open(activate_this).read(), dict(__file__=activate_this))
else:
    print("Virtualenv activation file not found!")

# Устанавливаем переменную окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Refrigerator.settings')

# Импортируем WSGI-приложение Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
