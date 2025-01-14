from django.db import models

class Fridge(models.Model):
    name = models.CharField(max_length=100)  # Название холодильника
    location = models.CharField(max_length=255, blank=True, null=True)  # Местоположение холодильника (опционально)
    image = models.ImageField(upload_to='fridges/', null=True, blank=True)  # Поле для изображения

    def __str__(self):
        return self.name

class RefrigeratorData(models.Model):
    fridge = models.ForeignKey(Fridge, on_delete=models.CASCADE, related_name='temperature_records')  # Связь с холодильником
    sensor1_temp = models.FloatField()  # Температура с датчика 1
    sensor2_temp = models.FloatField()  # Температура с датчика 2
    is_out_of_range = models.BooleanField()  # Булевое значение аварийности
    event_date = models.DateTimeField()  # Дата и время события

    def __str__(self):
        return f"{self.fridge.name} ({self.event_date})"
