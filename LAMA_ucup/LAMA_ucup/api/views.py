from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser

from ..models import Entities, Ku
    
class EntitiesListView(generics.ListAPIView):
    permission_classes = [AllowAny] 
    queryset = Entities.objects.all() #данные которые будут возвращаться
    serializer_class = EntitiesSerializer #обрабатывает queryset

class BrandClassifierListView(generics.ListAPIView):
    permission_classes = [AllowAny] 
    queryset = Brandclassifier.objects.all() #данные которые будут возвращаться
    serializer_class = BrandClassifierSerializer #обрабатывает queryset

class ClassifierListView(generics.ListAPIView):
    permission_classes = [AllowAny] 
    queryset = Classifier.objects.all() #данные которые будут возвращаться
    serializer_class = ClassifierSerializer #обрабатывает queryset

class VendorsListView(generics.ListAPIView):
    permission_classes = [AllowAny] 
    queryset = Vendors.objects.all() #данные которые будут возвращаться
    serializer_class =  VendorsSerializer #обрабатывает queryset

class BasePagination(PageNumberPagination):
    page_size = 500  # Количество записей на странице
    page_size_query_param = 'page_size'
    max_page_size = 1000

class VendDocListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Venddoc.objects.all()
    serializer_class = VendDocSerializer
    pagination_class = BasePagination

class VendorsViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny] 
    queryset = Vendors.objects.all()
    serializer_class = VendorsSerializer
    pagination_class = BasePagination

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
    

class KuListView(generics.ListCreateAPIView, generics.DestroyAPIView):
    permission_classes = [AllowAny] 
    queryset = Ku.objects.all() #данные которые будут возвращаться
    serializer_class = KuSerializer #обрабатывает queryset

class KuAPIUpdate(generics.RetrieveUpdateAPIView):
    permission_classes = [AllowAny] # (IsAuthenticated,)  
    queryset = Ku.objects.all() #данные которые будут возвращаться
    serializer_class = KuSerializer #обрабатывает queryset
    # authentication_classes = (TokenAuthentication, )

class KuDetailView(generics.RetrieveUpdateDestroyAPIView): #добавление/обновление/удаление в одном
    permission_classes = [AllowAny]
    queryset = Ku.objects.all()
    serializer_class = KuSerializer

class GraphListView(generics.ListAPIView): 
    permission_classes = [AllowAny]
    queryset = KuGraph.objects.all()
    serializer_class = KuGraphSerializer

class GraphDetailView(generics.RetrieveUpdateDestroyAPIView): #добавление/обновлени/удаление в одном
    permission_classes = [AllowAny]
    queryset = KuGraph.objects.all()
    serializer_class = KuGraphSerializer

class ProductsListView(generics.ListAPIView):
    permission_classes = [AllowAny] 
    queryset = Products.objects.all() #данные которые будут возвращаться
    serializer_class = ProductsSerializer #обрабатывает queryset

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
    