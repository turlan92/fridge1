from django.contrib import admin
from .models import Fridge, RefrigeratorData

# Настройка отображения модели Fridge в админке
class FridgeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'location', 'image')  # Отображаемые поля
    list_filter = ('location',)  # Фильтрация по местоположению

# Настройка отображения модели RefrigeratorData в админке
class RefrigeratorDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'fridge', 'event_date', 'sensor1_temp', 'sensor2_temp', 'is_out_of_range')  # Отображаемые поля
    list_filter = ('event_date',)  # Фильтрация по дате события

# Регистрация моделей в админке
admin.site.register(Fridge, FridgeAdmin)
admin.site.register(RefrigeratorData, RefrigeratorDataAdmin)
