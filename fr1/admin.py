from django.contrib import admin
from .models import Fridge, RefrigeratorData

class FridgeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'location', 'image')
    list_filter = ('location',)

class RefrigeratorDataAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'fridge',
        'event_date',
        'sensor1_temp',
        'sensor2_temp',
        'humidity',         # добавил
        'air_temp',         # добавил
        'is_out_of_range',
        'door_open_duration_sec',  # добавил
        'power_lost'        # добавил
    )
    list_filter = ('event_date', 'is_out_of_range', 'power_lost')  # добавил фильтры по новым булевым полям

admin.site.register(Fridge, FridgeAdmin)
admin.site.register(RefrigeratorData, RefrigeratorDataAdmin)
