from django.contrib import admin
from .models import Fridge, RefrigeratorData

class FridgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'image')  # Показываем имя, местоположение и изображение в списке
    list_filter = ('location',)  # Фильтровать по местоположению

class RefrigeratorDataAdmin(admin.ModelAdmin):
    list_display = ('fridge', 'event_date', 'sensor1_temp', 'sensor2_temp', 'is_out_of_range')  # Отображаем данные о температуре
    list_filter = ('event_date',)  # Фильтрация по дате

admin.site.register(Fridge, FridgeAdmin)
admin.site.register(RefrigeratorData, RefrigeratorDataAdmin)
