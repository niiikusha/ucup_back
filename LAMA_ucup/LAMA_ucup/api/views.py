from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import generics, viewsets, status
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from django.db.models import Q
import calendar
import numpy as np
from ..models import Entities, Ku
    
class BasePagination(PageNumberPagination):
    page_size = 50  # Количество записей на странице
    page_size_query_param = 'page_size'
    max_page_size = 1000

class EntitiesListView(generics.ListAPIView):
    permission_classes = [AllowAny] 
    serializer_class = EntitiesSerializer #обрабатывает queryset
    
    def get_queryset(self):
        queryset = Entities.objects.all()
        search_query = self.request.query_params.get('search', '') 
        if search_query: 
            queryset = queryset.filter( 
                Q(entity_id__icontains=search_query) | 
                Q(name__icontains=search_query) |
                Q(urasticname__icontains=search_query) | 
                Q(directorname__icontains=search_query) | 
                Q(urasticaddress__icontains=search_query) 
            )
        return queryset
    

class BrandClassifierListView(generics.ListAPIView):
    permission_classes = [AllowAny] 
    queryset = Brandclassifier.objects.all() #данные которые будут возвращаться
    serializer_class = BrandClassifierSerializer #обрабатывает queryset
    pagination_class = BasePagination

class ClassifierListView(generics.ListAPIView):
    permission_classes = [AllowAny] 
    queryset = Classifier.objects.all() #данные которые будут возвращаться
    serializer_class = ClassifierSerializer #обрабатывает queryset
    pagination_class = BasePagination

class VendorsNameFilterView(generics.ListAPIView): #фильтрация по юр лицу
    permission_classes = [AllowAny] 
    serializer_class =  VendorsNameSerializer #обрабатывает queryset
    pagination_class = BasePagination

    def get_queryset(self):
        queryset = Vendors.objects.all()
        entity_id = self.request.query_params.get('entity_id', None)
        
        # Проверяем, предоставлен ли entityid в параметрах запроса
        if entity_id:
            # Фильтруем поставщиков на основе предоставленного entityid
            queryset = queryset.filter(entity_id=entity_id)
    
        return queryset


class VendDocListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = VendDocSerializer
    pagination_class = BasePagination

    def get_queryset(self):
        queryset = Venddoc.objects.all().order_by('vendor_id')
        entity_id = self.request.query_params.get('entity_id', None)
        vendor_id = self.request.query_params.get('vendor_id', None)
        
        # Проверяем, предоставлен ли entityid в параметрах запроса
        if entity_id is not None:
            # Фильтруем поставщиков на основе предоставленного entityid
            queryset = queryset.filter(entity_id=entity_id).order_by('vendor_id')
        if vendor_id is not None:
            queryset = queryset.filter(vendor_id=vendor_id).order_by('vendor_id')
    
        search_query = self.request.query_params.get('search', '') 

        if search_query: 
            queryset = queryset.filter( 
                Q(invoice_id__icontains=search_query) | 
                Q(invoice_number__icontains=search_query) | 
                Q(invoice_name__icontains=search_query) |
                Q(entity_id__exact=search_query) | 
                Q(entity_id__name__icontains=search_query) | 
                Q(vendor_id__exact=search_query) |
                Q(vendor_id__name__icontains=search_query) |
                Q(invoice_date__icontains=search_query) 
                )

        return queryset

class VendorsListViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny] 
    serializer_class = VendorsSerializer
    pagination_class = BasePagination
    
    def get_queryset(self):
        queryset = Vendors.objects.all().order_by('vendor_id')
        #entity_id = self.request.query_params.get('entity_id', None)
        entity_ids = self.request.query_params.getlist('entity_id', [])
        search_query = self.request.query_params.get('search', '')
        
        # Проверяем, предоставлен ли entityid в параметрах запроса
        if entity_ids:
            # Фильтруем поставщиков на основе предоставленных entity_ids
            queryset = queryset.filter(entity_id__in=entity_ids)

        if search_query:
            queryset = queryset.filter(
            Q(name__icontains=search_query) |
            Q(urasticname__icontains=search_query) |
            Q(directorname__icontains=search_query)
            )

        search_query = self.request.query_params.get('search', '') 
        try:
            queryset = queryset.filter( 
                Q(vendor_id__icontains=search_query) | 
                Q(name__icontains=search_query) | 
                Q(urasticname__icontains=search_query) | 
                Q(directorname__icontains=search_query) |
                Q(inn_kpp__icontains=search_query) |
                Q(urasticadress__icontains=search_query) |
                Q(entity_id__exact=search_query) | # если нужно только айди фильтровать, exact, т.к. он ключ
                Q(entity_id__name__icontains=search_query)  # и по id, и по name
            )
        except Exception as e:
            print(f"Error in queryset filtering: {e}")
        
        return queryset
        
    
    def list(self, request, *args, **kwargs):
        # Проверяем наличие параметра fields в запросе
        fields_param = request.query_params.get('fields', None)

        # Если параметр fields указан, создаем новый класс сериализатора с нужными полями
        if fields_param:
            fields = fields_param.split(',')
            MetaClass = type('Meta', (), {'model': Vendors, 'fields': fields})
            serializer_class = type('DynamicVendorsSerializer', (VendorsSerializer,), {'Meta': MetaClass})
        else:
            # Если параметр fields не указан, используем исходный сериализатор
            serializer_class = self.serializer_class

        # Используем новый сериализатор для текущего запроса
        self.serializer_class = serializer_class

        return super().list(request, *args, **kwargs)


class KuListView(generics.ListCreateAPIView):
    permission_classes = [AllowAny] 
    # queryset = Ku.objects.all() #данные которые будут возвращаться
    serializer_class = KuSerializer #обрабатывает queryset
    pagination_class = BasePagination

    def perform_create(self, serializer):
        # Вызвать метод save у сериализатора для создания экземпляра Ku
        instance = serializer.save()

        # Вызвать метод calculate_base для установки значения base
        #instance.calculate_base()

    def get_queryset(self):
        queryset = Ku.objects.all().order_by('ku_id')
        entity_id = self.request.query_params.get('entity_id', None)
        vendor_id = self.request.query_params.get('vendor_id', None)
        period =self.request.query_params.get('period', None)
        status =self.request.query_params.get('status', None)
        date_start =self.request.query_params.get('date_start', None)
        date_end =self.request.query_params.get('date_end', None)

        if entity_id is not None:
            # Фильтруем поставщиков на основе предоставленного entityid
            queryset = queryset.filter(entity_id=entity_id)

        if vendor_id is not None:
            queryset = queryset.filter(vendor_id=vendor_id)

        if period is not None:
            queryset = queryset.filter(period=period)

        if status is not None:
            queryset = queryset.filter(status=status)

        if date_start is not None:
            queryset = queryset.filter(date_start=date_start)

        if date_end is not None:
            queryset = queryset.filter(date_end=date_end)

        return queryset
    

class KuAPIUpdate(generics.RetrieveUpdateAPIView):
    permission_classes = [AllowAny] # (IsAuthenticated,)  
    queryset = Ku.objects.all() #данные которые будут возвращаться
    serializer_class = KuSerializer #обрабатывает queryset
    # authentication_classes = (TokenAuthentication, )

class KuDetailView(generics.RetrieveUpdateDestroyAPIView): #добавление/обновление/удаление в одном
    permission_classes = [AllowAny]
    queryset = Ku.objects.all()
    serializer_class = KuSerializer

class GraphListView(generics.ListCreateAPIView, generics.DestroyAPIView): 
    permission_classes = [AllowAny]
    serializer_class = KuGraphSerializer
    #pagination_class = BasePagination
    
    def destroy(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Проходим по queryset и удаляем каждый объект
        for instance in queryset:
            self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_queryset(self):
        queryset = KuGraph.objects.all().order_by('graph_id')
        vendor_id = self.request.query_params.get('vendor_id', None)
        ku_id = self.request.query_params.get('ku_id', None)
        period =self.request.query_params.get('period', None)
        status =self.request.query_params.get('status', None)
        date_start =self.request.query_params.get('date_start', None)
        date_end =self.request.query_params.get('date_end', None)

        if vendor_id is not None:
            queryset = queryset.filter(vendor_id=vendor_id)

        if ku_id is not None:
            queryset = queryset.filter(ku_id=ku_id)

        if period is not None:
            queryset = queryset.filter(period=period)

        if status is not None:
            queryset = queryset.filter(status=status)

        if date_start is not None:
            queryset = queryset.filter(date_start=date_start)

        if date_end is not None:
            queryset = queryset.filter(date_end=date_end)

        return queryset

class GraphDetailView(generics.RetrieveUpdateDestroyAPIView): #добавление
    permission_classes = [AllowAny]
    queryset = KuGraph.objects.all()
    serializer_class = KuGraphSerializer

class ProductsListView(generics.ListAPIView):
    permission_classes = [AllowAny] 
    queryset = Products.objects.all() #данные которые будут возвращаться
    serializer_class = ProductsSerializer #обрабатывает queryset
    pagination_class = BasePagination



@api_view(['POST'])
@permission_classes([AllowAny])
def create_graph(request):
    input_data = JSONParser().parse(request)

    # Получите данные от пользователя
    ku_id = input_data.get('ku_id')
    period = input_data.get('period')
    date_start = input_data.get('date_start')
    date_end_initial = input_data.get('date_end')
    percent = input_data.get('percent')
    vendor_id = input_data.get('vendor_id')
    entity_id = input_data.get('entity_id')

    # Разбейте date_start на год, месяц и день
    year, month, day = map(int, date_start.split('-'))

    # Подготовьте данные для создания графиков
    graph_data_list = []
   
    if period == 'Месяц':
        # Получите последний день месяца
        sum_bonus = 0
        sum_calc = 0
        status_value = "Запланировано"
        date_end = f"{year}-{month:02d}-{day:02d}"
        
        while date_end < date_end_initial:
            
            # last_month_of_quarter = ((month - 1) // 3 + 1) * 3 #квартал
            # Формируйте date_end как последний день месяца
            last_day = calendar.monthrange(year, month)[1] #количество дней месяца
            last_month = 12
            date_end = f"{year}-{month:02d}-{last_day:02d}"

            if date_end > date_end_initial: #проверка последнего графика 
                date_end = date_end_initial

            next_month = month % 12 + 1
            next_month_year = year + (1 if next_month == 1 else 0) #проверка на переполнение месяцев

            # next_quarter = ((last_month_of_quarter - 1) // 3 + 1) % 4 + 1 #квартал
            # next_quarter_year = year + (1 if next_quarter == 1 else 0)
            
            
            graph_data_list.append({
                'date_start': f"{year}-{month:02d}-{day:02d}",
                'date_end': date_end,
                'date_calc': f"{next_month_year}-{next_month:02d}-01",
                'status': status_value,
                'sum_calc': sum_calc,
                'sum_bonus': sum_bonus,
                'percent': percent,
                'vendor_id': vendor_id,
                'ku_id': ku_id,
                'period': period
            })

            # Переходите к следующему месяцу
            month = next_month
            year = next_month_year
            day = 1  # Начинайте с первого дня следующего месяца

    if period == 'Год':
        # Получите последний день месяца
        sum_bonus = 0
        sum_calc = 0
        status_value = "Запланировано"
        date_end = f"{year}-{month:02d}-{day:02d}"
        
        while date_end < date_end_initial:
            
            # last_month_of_quarter = ((month - 1) // 3 + 1) * 3 #квартал
            # Формируйте date_end как последний день месяца
            last_day = calendar.monthrange(year, month)[1] #количество дней месяца
            last_month = 12
            date_end = f"{year}-{month:02d}-{last_day:02d}"

            if date_end > date_end_initial: #проверка последнего графика 
                date_end = date_end_initial

            next_month = month % 12 + 1
            next_month_year = year + (1 if next_month == 1 else 0) #проверка на переполнение месяцев

            # next_quarter = ((last_month_of_quarter - 1) // 3 + 1) % 4 + 1 #квартал
            # next_quarter_year = year + (1 if next_quarter == 1 else 0)
            
            
            graph_data_list.append({
                'date_start': f"{year}-{month:02d}-{day:02d}",
                'date_end': date_end,
                'date_calc': f"{next_month_year}-{next_month:02d}-01",
                'status': status_value,
                'sum_calc': sum_calc,
                'sum_bonus': sum_bonus,
                'percent': percent,
                'vendor_id': vendor_id,
                'ku_id': ku_id,
                'period': period
            })

            # Переходите к следующему месяцу
            month = next_month
            year = next_month_year
            day = 1  # Начинайте с первого дня следующего месяца

    for date_range in graph_data_list:
        start_date = date_range['date_start']
        end_date = date_range['date_end']
        # Рассчитать sum_calc, используя метод products_amount_sum_in_range
        sum_calc = Venddoc().products_amount_sum_in_range(start_date, end_date, vendor_id, entity_id)
        sum_bonus = sum_calc * percent / 100
        date_range['sum_calc'] = sum_calc
        date_range['sum_bonus'] = sum_bonus

    # elif period == 'Год':
    #     while year <= datetime.now().year:
    #         # Получите последний день текущего года
    #         last_day = calendar.monthrange(year, 12)[1]

    #         # Формируйте date_end как последний день года
    #         date_end = f"{year}-12-{last_day:02d}"

    #         graph_data_list.append({
    #             'date_start': f"{year}-{month:02d}-{day:02d}",
    #             'date_end': date_end,
    #             # Добавьте другие данные графика
    #         })

    #         # Переходите к следующему году
    #         year += 1
    #         month = 1  # Начинайте с января следующего года
    #         day = 1  # Начинайте с первого дня января следующего года

    # Создайте экземпляры сериализаторов и сохраните их
    serializer_instances = []
    for graph_data in graph_data_list:
        serializer_instance = KuGraphSerializer(data=graph_data)
        if serializer_instance.is_valid():
            serializer_instance.save()
            serializer_instances.append(serializer_instance)
        else:
            return JsonResponse({'error': serializer_instance.errors}, status=status.HTTP_400_BAD_REQUEST)

    # Верните успешный ответ с данными созданных объектов
    data = [serializer_instance.data for serializer_instance in serializer_instances]
    return JsonResponse(data, status=status.HTTP_201_CREATED, safe=False)


@api_view(['GET'])
def products_filter(request): 
    classifier_id = request.query_params.get('classifier_id', None)
    brand_id = request.query_params.get('brand_id', None)
    name = request.query_params.get('name', None)
    # Фильтрация по classifier_id и brand_id, name если они предоставлены в запросе
    queryset = Products.objects.all()
    if classifier_id:
        queryset = queryset.filter(classifier_id=classifier_id)
    if brand_id:
        queryset = queryset.filter(brand_id=brand_id)
    if name:
        queryset = queryset.filter(name=name)

    serializer = ProductsSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    return Response(UserSerializer(request.user).data)


@api_view(['POST'])
def user_info(request):
    data = JSONParser().parse(request)
    login = data.get('login', None)
    response_data = {}
    # try:
    #     user_processing = UserProcessing()
    #     return login
    # except Exception as ex:
    #     response_data['error'] = 'Непредвиденная ошибка: ' + ex.args[0]
    #     return JsonResponse(response_data, status=status.HTTP_409_CONFLICT)

# class ProductsListView(generics.ListAPIView):
#     permission_classes = [AllowAny] 
#     queryset = Products.objects.all() #данные которые будут возвращаться
#     serializer_class = ProductsSerializer #обрабатывает queryset
    