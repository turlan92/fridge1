from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import RefrigeratorData
from .serializers import RefrigeratorDataSerializer
from django.shortcuts import render, get_object_or_404
from .models import Fridge, RefrigeratorData
from django.utils.dateparse import parse_date
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime
from .models import RefrigeratorData


def index(request):
    # Здесь можно передать данные, если они нужны для отображения
    return render(request, 'fr1/index.html')


def fridge_list(request):
    fridges = Fridge.objects.all()
    return render(request, 'fr1/fridge_list.html', {'fridges': fridges})


def fridge_detail(request, fridge_id):
    fridge = get_object_or_404(Fridge, id=fridge_id)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Фильтрация по датам, если они есть
    filters = {}
    if start_date:
        start_date = parse_date(start_date)
        filters['event_date__gte'] = datetime.combine(start_date, datetime.min.time())
    if end_date:
        end_date = parse_date(end_date)
        filters['event_date__lte'] = datetime.combine(end_date, datetime.max.time())

    # Получаем связанные данные о температуре
    records = RefrigeratorData.objects.filter(fridge=fridge, **filters)

    return render(request, 'fr1/fridge_detail.html', {
        'fridge': fridge,
        'records': records,
        'start_date': start_date,
        'end_date': end_date
    })


def daily_temperatures(request):
    # Получаем строки дат из GET параметров или текущие даты по умолчанию
    start_date_str = request.GET.get('start_date', timezone.now().strftime('%Y-%m-%d'))
    end_date_str = request.GET.get('end_date', timezone.now().strftime('%Y-%m-%d'))

    try:
        # Преобразуем строки в объекты datetime
        start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date_str, '%Y-%m-%d')
        # Делаем datetime с учетом часового пояса
        start_date_obj = timezone.make_aware(start_date_obj)
        end_date_obj = timezone.make_aware(end_date_obj.replace(hour=23, minute=59, second=59, microsecond=999999))
    except ValueError:
        # Если дата некорректна, используем текущую дату
        start_date_obj = timezone.now()
        end_date_obj = timezone.now()

    # Фильтрация данных по дате, с сортировкой по последним записям
    records = RefrigeratorData.objects.filter(
        event_date__gte=start_date_obj,
        event_date__lte=end_date_obj
    ).select_related('fridge').order_by('-event_date')  # сортировка по убыванию даты

    # Передаем данные в шаблон
    return render(request, 'fr1/daily_temperatures.html', {
        'records': records,
        'start_date': start_date_obj.date(),
        'end_date': end_date_obj.date(),
    })


def emergencies(request):
    # Получаем параметры фильтрации по датам из GET запроса
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Формируем фильтры по дате, если они переданы
    filters = {}
    if start_date:
        start_date = parse_date(start_date)
        filters['event_date__gte'] = datetime.combine(start_date, datetime.min.time())  # начало дня
    if end_date:
        end_date = parse_date(end_date)
        filters['event_date__lte'] = datetime.combine(end_date, datetime.max.time())  # конец дня

    # Фильтруем данные по аварийности и дате, с сортировкой по последним записям
    emergency_records = RefrigeratorData.objects.filter(
        is_out_of_range=True,
        **filters
    ).select_related('fridge').order_by('-event_date')  # сортировка по убыванию даты

    return render(request, 'fr1/emergencies.html', {
        'emergency_records': emergency_records,
        'start_date': start_date,
        'end_date': end_date,
    })


@api_view(['POST'])
def create_refrigerator_data(request):
    if request.method == 'POST':
        serializer = RefrigeratorDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
