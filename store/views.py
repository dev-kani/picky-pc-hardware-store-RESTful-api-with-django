from collections import defaultdict
from django.db.models import Prefetch, Q, Min, Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import (CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin,
                                   ListModelMixin
                                   )
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, DjangoModelPermissions
from drf_spectacular.utils import extend_schema
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ViewSet, ReadOnlyModelViewSet
from pprint import pprint
from .filters import ProductFilter
from .models import (Category, Product, ProductVariant, ProductImage, ProductType, ProductTypeAttribute, Review,
                     Customer, Order, AttributeValue, PaymentOption
                     )
from .permissions import IsAdminOrReadOnly, FullDjangoModelPermissions
from .serializers import (CategorySerializer, ProductSerializer, ProductTypeAttributeSerializer, ReviewSerializer,
                          CustomerSerializer,
                          OrderSerializer, AttributeValueSerializer,
                          PaymentOptionSerializer
                          )


class CategoryViewSet(ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Category.objects.all().is_active().order_by('title')
    serializer_class = CategorySerializer


class ProductViewSet(ModelViewSet):
    # queryset = Product.objects.all().is_active()
    serializer_class = ProductSerializer
    lookup_field = 'slug'

    # filter_backends = [SearchFilter, OrderingFilter]

    permission_classes = [IsAdminOrReadOnly]

    # search_fields = ['title', 'description']
    # ordering_fields = ['product_variant__price']

    @action(
        methods=['get'],
        detail=False,
        url_path=r"category/(?P<slug>[\w-]+)",
    )
    def list_product_by_category_slug(self, request, slug=None):
        queryset = self.get_queryset().filter(category__slug=slug)
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        # queryset = Product.objects.all().is_active()

        queryset = Product.objects.prefetch_related(
            'product_variant',
            'product_variant__product_image',
            'product_variant__attribute_value__attribute',
            'attribute_value__attribute',
            # 'attribute_value',
        ).select_related('product_type').is_active()

        # category_slug = self.request.query_params.get('category_slug')
        # if category_slug:
        #     # Filter products by category_slug
        #     queryset = queryset.filter(category__slug=category_slug)

        # always use .get method when getting query params, it returns None if params doesn't exist.
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)

        # Price range filters
        if min_price is not None and max_price is not None:
            queryset = queryset.filter(product_variant__price__range=(min_price, max_price))

        for key in self.request.query_params.keys():
            if key not in ['min_price', 'max_price']:
                values = self.request.query_params.getlist(key)
                query_filter = Q(
                    attribute_value__attribute__title=key,
                    attribute_value__attribute_value__in=values
                ) | Q(
                    product_variant__attribute_value__attribute__title=key,
                    product_variant__attribute_value__attribute_value__in=values
                )
                queryset = queryset.filter(query_filter)

            # Sort the queryset after filtering
            # sort_by = self.request.query_params.get('sort_by', None)
            # if sort_by == 'title_asc':
            #     queryset = queryset.order_by('title')
            # elif sort_by == 'title_desc':
            #     queryset = queryset.order_by('-title')
            # elif sort_by == 'price_asc':
            #     queryset = queryset.annotate(
            #         min_price=Min('product_variant__price')
            #     ).order_by('min_price')
            # elif sort_by == 'price_desc':
            #     queryset = queryset.annotate(
            #         max_price=Max('product_variant__price')
            #     ).order_by('-max_price')

            # Dynamic filters according to product type
            # ----------------------- Filters ARE dynamic ----------------------- #
        if queryset:
            # product_type_id = self.request.query_params.get('product_type_id', 1)  # <---- 1 set as default
            first_product = queryset.first()
            product_type_id = first_product.product_type_id  # <---- 1 set as default

            # print(product_type_id)

            # if product_type_id:
            #     # Fetch the specific product type
            #     p_type = get_object_or_404(ProductType.objects.prefetch_related(
            #         'attribute__attribute_value',
            #
            #     ).select_related('parent'), id=product_type_id)
            #
            #     # Retrieve attributes associated with this product type
            #     product_type_attributes = p_type.attribute.all()
            #
            #     # You can further use these attributes if needed
            #     for attribute in product_type_attributes:
            #         # Do something with each attribute
            #         print(attribute.title)
            #
            #         attribute_values_for_attribute = attribute.attribute_value.all()
            #
            #         for value in attribute_values_for_attribute:
            #             print(value.attribute_value)

        # print(queryset)
        return queryset

        # ----------------------- Filters ARE dynamic ----------------------- #


class ReviewViewSet(ModelViewSet):
    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    # This queryset is for getting the all reviews of the product specified in product_slug
    def get_queryset(self):
        product_slug = self.kwargs.get('product_slug')
        product = get_object_or_404(Product.objects.all(), slug=product_slug)
        return Review.objects.filter(product=product)

    def get_serializer_context(self):
        product_slug = self.kwargs.get('product_slug')
        product = get_object_or_404(Product.objects.all(), slug=product_slug)
        return {'product': product}


# class CartViewSet(CreateModelMixin,
#                   RetrieveModelMixin,
#                   DestroyModelMixin,
#                   GenericViewSet):
#     queryset = Cart.objects.prefetch_related(
#         'cart_items__product',
#         'cart_items__product__product_variant',
#     ).all()
#     serializer_class = CartSerializer


# class CartItemViewSet(ModelViewSet):
#     http_method_names = ['get', 'post', 'patch', 'delete']
#
#     def get_serializer_class(self):
#         if self.request.method == 'POST':
#             return AddCartItemSerializer
#         elif self.request.method == 'PATCH':
#             return UpdateCartItemSerializer
#         return CartItemSerializer
#
#     def get_serializer_context(self):
#         return {'cart_id': self.kwargs['cart_pk']}
#
#     def get_queryset(self):
#         return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']) \
#             .select_related('product').prefetch_related('product__product_variant')


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.prefetch_related(
        'address',
    ).all()
    serializer_class = CustomerSerializer

    permission_classes = [FullDjangoModelPermissions]

    # @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])
    # def history(self, request, pk):
    #     return Response('ok')

    # Overriding the permission ONLY to Authenticated user
    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer = Customer.objects.get(user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    # http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    # def get_permissions(self):
    #     if self.request.method in ['PATCH', 'DELETE']:
    #         return [IsAdminUser()]
    #     return [IsAuthenticated()]

    # def create(self, request, *args, **kwargs):
    #     serializer = CreateOrderSerializer(
    #         data=request.data,
    #         context={'user_id': self.request.user.id})
    #     serializer.is_valid(raise_exception=True)
    #     order = serializer.save()
    #     serializer = OrderSerializer(order)
    #     return Response(serializer.data)

    # def get_serializer_class(self):
    #     if self.request.method == 'POST':
    #         return CreateOrderSerializer
    #     elif self.request.method == 'PATCH':
    #         return UpdateOrderSerializer
    #     return OrderSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.all().order_by('-placed_at')

        customer_id = Customer.objects.only('id').get(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id).order_by('-placed_at')


class ProductTypeAttributeValueViewSet(ViewSet):
    # serializer_class = FilteringAttributeValueSerializer

    def list(self, request):
        product_type_id = self.request.GET.get('product_type_id', None)
        if product_type_id:
            try:
                product_type = get_object_or_404(
                    ProductType.objects.prefetch_related('attribute__attribute_value'),
                    id=product_type_id
                )

                # Filter attribute values where 'for_filtering=True' using Django's ORM
                attribute_values = product_type.attribute.filter(
                    attribute_value__for_filtering=True
                ).values_list('title', 'attribute_value__attribute_value')

                # Organize attribute values under their respective attribute titles using defaultdict
                attribute_value_dict = defaultdict(list)
                for title, value in attribute_values:
                    attribute_value_dict[title].append(value)

                return JsonResponse(attribute_value_dict)  # Return JSON response
            except ProductType.DoesNotExist:
                return JsonResponse({'error': 'Product type not found'}, status=404)
        else:
            return JsonResponse({'error': 'Product type ID not provided in query parameters'}, status=400)

        # else:
        # Handle the case where the product_type_id is not provided
        # return AttributeValue.objects.none()  # Return an empty queryset or handle it as needed

        # if product_type_id:
        #     # Fetch the specific product type
        #     p_type = get_object_or_404(ProductType.objects.prefetch_related(
        #         'attribute__attribute_value',
        #
        #     ).select_related('parent'), id=product_type_id)
        #
        #     # Retrieve attributes associated with this product type
        #     product_type_attributes = p_type.attribute.all()
        #
        #     # You can further use these attributes if needed
        #     for attribute in product_type_attributes:
        #         # Do something with each attribute
        #         print(attribute.title)
        #
        #         attribute_values_for_attribute = attribute.attribute_value.all()
        #
        #         for value in attribute_values_for_attribute:
        #             print(value.attribute_value)


class PaymentOptionViewSet(ReadOnlyModelViewSet):
    # permission_classes = [IsAdminOrReadOnly]
    queryset = PaymentOption.objects.all().order_by('name')
    serializer_class = PaymentOptionSerializer
