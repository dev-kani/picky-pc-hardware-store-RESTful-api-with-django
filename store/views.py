from django.db.models import Prefetch
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from .models import Category, Product, ProductVariant, ProductImage
from .serializers import CategorySerializer, ProductSerializer, ProductCategorySerializer


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


class ProductViewSet(viewsets.ViewSet):
    queryset = Product.objects.all().is_active()
    lookup_field = 'slug'

    @extend_schema(responses=ProductSerializer)
    def retrieve(self, request, slug=None):
        serializer = ProductSerializer(
            self.queryset.filter(slug=slug)
            # .select_related('category')  # for Foreign Key relations
            .prefetch_related(Prefetch('attribute_value__attribute'))  # for reverse Foreign Key relations
            .prefetch_related(Prefetch('product_variant__product_image'))  # for reverse Foreign Key relations
            .prefetch_related(Prefetch('product_variant__attribute_value__attribute')),
            many=True)
        data = Response(serializer.data)
        return data

    @action(
        methods=['get'],
        detail=False,
        url_path=r"category/(?P<slug>[\w-]+)",
        # url_name="all"
    )
    @extend_schema(responses=ProductSerializer)
    def list_product_by_category_slug(self, request, slug=None):
        serializer = ProductCategorySerializer(
            self.queryset.filter(category__slug=slug)
            .prefetch_related(Prefetch(
                'product_variant', queryset=ProductVariant.objects.order_by('order')
            ))
            .prefetch_related(Prefetch(
                'product_variant__product_image', queryset=ProductImage.objects.filter(order=1)
            )),
            many=True
        )
        return Response(serializer.data)
