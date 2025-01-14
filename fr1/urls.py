from django.urls import path
from . import views

urlpatterns = [
    path('', views.fridge_list, name='fridge_list'),  # Список холодильников
    path('fridges/<int:fridge_id>/', views.fridge_detail, name='fridge_detail'),  # Детали холодильника
    path('daily-temperatures/', views.daily_temperatures, name='daily_temperatures'),  # Температуры за день
    path('emergencies/', views.emergencies, name='emergencies'),  # Аварийные ситуации
    path('api/refrigerator_data/', views.create_refrigerator_data),
]
