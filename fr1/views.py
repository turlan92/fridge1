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

TELEGRAM_BOT_TOKEN = "8031748926:AAGnjGN5qneH5w-aFg54SHCNRjBvQTJ0bXQ"
TELEGRAM_CHAT_ID = "-1003045548424"  # ← вот сюда вставляем

def fridge_list(request):
    fridges = Fridge.objects.all()
    return render(request, 'fr1/fridge_list.html', {'fridges': fridges})

def send_telegram_message(message):
    """Отправляет сообщение в Telegram и логирует результат"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Ошибка: TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID не установлены!")
        return None

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}

    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result.get("ok"):
            print(f"✅ Сообщение отправлено: {message}")
        else:
            print(f"⚠️ Ошибка Telegram: {result}")
        return result
    except requests.RequestException as e:
        print(f"Ошибка отправки в Telegram: {e}")
        return None

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


def send_telegram_message(message):
    """Отправляет сообщение в Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Ошибка: TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID не установлены!")
        return None

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Проверка ошибок HTTP
        return response.json()
    except requests.RequestException as e:
        print(f"Ошибка отправки в Telegram: {e}")
        return None



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
