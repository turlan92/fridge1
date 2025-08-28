from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_date
from django.utils import timezone
from datetime import datetime
import requests
from .models import RefrigeratorData
import socket
import errno


from .models import Fridge
from .serializers import RefrigeratorDataSerializer

def fridge_list(request):
    fridges = Fridge.objects.all()
    return render(request, 'fr1/fridge_list.html', {'fridges': fridges})

def daily_temperatures(request):
    start_date_str = request.GET.get('start_date', timezone.now().strftime('%Y-%m-%d'))
    end_date_str = request.GET.get('end_date', timezone.now().strftime('%Y-%m-%d'))

    try:
        start_date_obj = timezone.make_aware(datetime.strptime(start_date_str, '%Y-%m-%d'))
        end_date_obj = timezone.make_aware(datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59))
    except ValueError:
        start_date_obj = timezone.now()
        end_date_obj = timezone.now()

    records = RefrigeratorData.objects.filter(
        event_date__range=(start_date_obj, end_date_obj)
    ).select_related('fridge').order_by('-event_date')[:100]

    return render(request, 'fr1/daily_temperatures.html', {
        'records': records,
        'start_date': start_date_obj.date(),
        'end_date': end_date_obj.date()
    })


def emergencies(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None

    filters = {}
    if start_date:
        filters['event_date__gte'] = datetime.combine(start_date, datetime.min.time())
    if end_date:
        filters['event_date__lte'] = datetime.combine(end_date, datetime.max.time())

    emergency_records = RefrigeratorData.objects.filter(is_out_of_range=True, **filters)
    emergency_records = emergency_records.select_related('fridge').order_by('-event_date')[:100]

    return render(request, 'fr1/emergencies.html', {
        'emergency_records': emergency_records,
        'start_date': start_date,
        'end_date': end_date
    })


TELEGRAM_BOT_TOKEN = "8031748926:AAGnjGN5qneH5w-aFg54SHCNRjBvQTJ0bXQ"
TELEGRAM_CHAT_ID = "-1003045548424"

@api_view(['POST'])
def create_refrigerator_data(request):
    serializer = RefrigeratorDataSerializer(data=request.data)

    if serializer.is_valid():
        fridge = get_object_or_404(Fridge, id=request.data.get('fridge'))
        record = serializer.save(fridge=fridge)

        # ✅ Отправка в Telegram только при True
        if record.is_out_of_range:
            message = (
                f"🚨 Аварийная температура в {fridge.name}!\n"
                f"🌡 Датчик 1: {record.sensor1_temp}°C\n"
                f"🌡 Датчик 2: {record.sensor2_temp}°C"
            )
            send_telegram_message(message)

        return Response({'message': 'Данные успешно сохранены!'}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Тест
send_telegram_message("Привет, канал!")
@api_view(['POST'])
def create_refrigerator_data(request):
    """Принимает данные, сохраняет их и отправляет уведомление при аварийной температуре"""
    serializer = RefrigeratorDataSerializer(data=request.data)

    if serializer.is_valid():
        fridge = get_object_or_404(Fridge, id=request.data.get('fridge'))
        record = serializer.save(fridge=fridge)

        # Проверяем аварийную температуру
        if getattr(record, "is_out_of_range", False):
            message = (
                f"🚨 Аварийная температура в {fridge.name}!\n"
                f"🌡 Датчик 1: {record.sensor1_temp}°C\n"
                f"🌡 Датчик 2: {record.sensor2_temp}°C"
            )
            send_telegram_message(message)

        try:
            return Response({'message': 'Данные успешно сохранены!'}, status=status.HTTP_201_CREATED)
        except socket.error as e:
            if e.errno != errno.EPIPE:
                raise  # Пробрасываем, если это не Broken pipe

    try:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except socket.error as e:
        if e.errno != errno.EPIPE:
            raise
