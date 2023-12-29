from rest_framework import generics
from django_filters import rest_framework as filters
from .models import Product, Attribute, ProductTypeAttribute, AttributeValue


class ProductFilter(filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            'category': ('exact',),
            'product_variant__price': ('exact', 'gte', 'lte',),
            # 'attribute_value__attribute__attribute_value': ('exact',),
        }
