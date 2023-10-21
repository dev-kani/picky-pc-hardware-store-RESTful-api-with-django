from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from .models import Category, Brand, Product
from .serializers import CategorySerializer, BrandSerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().is_active()
    serializer_class = CategorySerializer
    # default manager
    # queryset = Category.objects.all()

    # Use this if you wish to change ModelViewSet to ViewSet
    # @extend_schema(responses=CategorySerializer)
    # def list(self, request):
    #     serializer = CategorySerializer(self.queryset, many=True)
    #     return Response(serializer.data)


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all().is_active()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ViewSet):
    queryset = Product.objects.all().is_active()
    lookup_field = 'slug'

    @extend_schema(responses=ProductSerializer)
    def retrieve(self, request, slug=None):
        # product = get_object_or_404(self.queryset.filter(pk=pk), many=True)
        serializer = ProductSerializer(self.queryset.filter(slug=slug).select_related('category', 'brand'), many=True)
        return Response(serializer.data)

    @extend_schema(responses=ProductSerializer)
    def list(self, request):
        serializer = ProductSerializer(self.queryset, many=True)
        return Response(serializer.data)

    # def retrieve(self, request, slug=None):
    #     product = self.queryset.filter(slug=slug) \
    #         .select_related('category', 'brand') \
    #         .prefetch_related('product_variant__product_image').first()
    #
    #     if product is not None:
    #         serializer = ProductSerializer(product)
    #         return Response(serializer.data)
    #     else:
    #         return Response(status=status.HTTP_404_NOT_FOUND)

    @action(
        methods=['get'],
        detail=False,
        url_path=r"category/(?P<slug>[\w-]+)",
        # url_name="all"
    )
    def list_product_by_category_slug(self, request, slug=None):
        serializer = ProductSerializer(
            self.queryset.filter(category__slug=slug), many=True
        )
        return Response(serializer.data)
