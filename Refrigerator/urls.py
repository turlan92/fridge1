from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("fr1.urls")),  # Подключение URL-ов вашего приложения (fr1)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Добавление обработки медиа-файлов
