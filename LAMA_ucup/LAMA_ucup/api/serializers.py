from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import *


class EntitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entities
        fields = '__all__'
       
class KuGraphSerializer(serializers.ModelSerializer):
    class Meta:
        model = KuGraph
        fields = '__all__'

class KuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ku
        fields = '__all__'
   

class UserSerializer(serializers.ModelSerializer):
     class Meta:
        model = User
        fields = '__all__'
      
class BrandClassifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brandclassifier
        fields = '__all__'

class ClassifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classifier
        fields = '__all__'

class ProductsSerializer(serializers.ModelSerializer):
    brand_name = serializers.SerializerMethodField()
    classifier_name = serializers.SerializerMethodField()

    class Meta:
        model = Products
        fields = ['itemid', 'name', 'brand_name', 'classifier_name'] # 'classifier', 'brand'

    def get_brand_name(self, obj):
        try:
            return obj.brand.brand_name if obj.brand else None
        except Brandclassifier.DoesNotExist:
            return None

    def get_classifier_name(self, obj):
        try:
            return obj.classifier.l3_name if obj.classifier else None
        except Classifier.DoesNotExist:
            return None

class VendorsSerializer(serializers.ModelSerializer):
     class Meta:
        model = Vendors
        fields = ['entityid', 'vendorid', 'name', 'urasticname', 'inn_kpp', 
                'directorname', 'urasticadress', 'account', 'bankname', 
                'bankbik', 'corraccount', 'dirparty' ]
    
class VendorsNameSerializer(serializers.ModelSerializer):
     class Meta:
        model = Vendors
        fields = ['entityid','vendorid', 'name']

class VendDocSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venddoc
        fields = '__all__'
      

class VendDocLinesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venddoclines
        fields = '__all__'
        
# class ProductsSerializer(serializers.ModelSerializer):
#      class Meta:
#         model = Products
#         fields = '__all__'