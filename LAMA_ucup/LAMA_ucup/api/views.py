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
from ..models import Entities, Ku
    
class BasePagination(PageNumberPagination):
    page_size = 50  # Количество записей на странице
    page_size_query_param = 'page_size'
    max_page_size = 1000

class EntitiesListView(generics.ListAPIView):
    permission_classes = [AllowAny] 
    queryset = Entities.objects.all() #данные которые будут возвращаться
    serializer_class = EntitiesSerializer #обрабатывает queryset

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
        
        return queryset

class VendorsListViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny] 
    serializer_class = VendorsSerializer
    pagination_class = BasePagination
    
    def get_queryset(self):
        queryset = Vendors.objects.all().order_by('vendor_id')
        entity_id = self.request.query_params.get('entity_id', None)
        
        # Проверяем, предоставлен ли entityid в параметрах запроса
        if entity_id:
            # Фильтруем поставщиков на основе предоставленного entityid
            queryset = queryset.filter(entity_id=entity_id)
    
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
    queryset = Ku.objects.all() #данные которые будут возвращаться
    serializer_class = KuSerializer #обрабатывает queryset
    pagination_class = BasePagination

    def perform_create(self, serializer):
        # Вызвать метод save у сериализатора для создания экземпляра Ku
        instance = serializer.save()

        # Вызвать метод calculate_base для установки значения base
        instance.calculate_base()

    def get_queryset(self):
        queryset = Ku.objects.all()
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
    
    # def get_queryset(self):   
    #     # Получаем выбранную сущность из данных запроса
    #     selected_entity_id = self.request.data.get('entity_id')

    #     # Фильтруем вендоров на основе выбранной сущности
    #     if selected_entity_id:
    #         return Ku.objects.filter(entity__id=selected_entity_id)
    #     else:
    #         return Ku.objects.all()

class KuAPIUpdate(generics.RetrieveUpdateAPIView):
    permission_classes = [AllowAny] # (IsAuthenticated,)  
    queryset = Ku.objects.all() #данные которые будут возвращаться
    serializer_class = KuSerializer #обрабатывает queryset
    # authentication_classes = (TokenAuthentication, )

class KuDetailView(generics.RetrieveUpdateDestroyAPIView): #добавление/обновление/удаление в одном
    permission_classes = [AllowAny]
    queryset = Ku.objects.all()
    serializer_class = KuSerializer

class GraphListView(generics.ListCreateAPIView): 
    permission_classes = [AllowAny]
    serializer_class = KuGraphSerializer
    #pagination_class = BasePagination

    def get_queryset(self):
        queryset = KuGraph.objects.all()
        vendor_id = self.request.query_params.get('vendor_id', None)
        ku = self.request.query_params.get('ku', None)
        period =self.request.query_params.get('period', None)
        status =self.request.query_params.get('status', None)
        date_start =self.request.query_params.get('date_start', None)
        date_end =self.request.query_params.get('date_end', None)

        if vendor_id is not None:
            queryset = queryset.filter(vendor_id=vendor_id)

        if ku is not None:
            queryset = queryset.filter(ku=ku)

        if period is not None:
            queryset = queryset.filter(period=period)

        if status is not None:
            queryset = queryset.filter(status=status)

        if date_start is not None:
            queryset = queryset.filter(date_start=date_start)

        if date_end is not None:
            queryset = queryset.filter(date_end=date_end)

        return queryset

class GraphDetailView(generics.CreateAPIView): #добавление
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
    graph_data = JSONParser().parse(request)
    serializer_class = KuGraphSerializer(data=graph_data)
    if serializer_class.is_valid():
        serializer_class.save()
        return JsonResponse(serializer_class.data, status=status.HTTP_201_CREATED)
    return JsonResponse(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['POST']) #добавление графика платежей
# @permission_classes([AllowAny])
# def create_graph(request):
#     ku_data = request.data.get('ku_instance', {})
#     graph_data = request.data

#     ku_graph_serializer = KuGraphSerializer(data=graph_data)
#     if ku_graph_serializer.is_valid():
#         ku_graph = ku_graph_serializer.save()
#         return Response({'graph_id': ku_graph.graph_id}, status=status.HTTP_201_CREATED)
#     else:
#         return Response(ku_graph_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    