from django.db import transaction
from django.db.models import Avg
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .models import (Category, Product, ProductVariant, ProductImage, Attribute,
                     AttributeValue, ProductType, Review, Customer,
                     Order, OrderItem, Address, PaymentOption
                     )
from .signals import order_created


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        # fields = ['id', 'title', 'slug', 'is_active']
        fields = '__all__'


class ProductImageSerializer(ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alternative_text', 'order']

        # fields = '__all__'

        # def get_image(self, obj):
        #     # Generate URL using Cloudinary URL builder with desired options
        #     return CloudinaryURL(
        #         public_id=obj.image.public_id,
        #         format=obj.image.format,
        #         transformation={'width': 200, 'height': 150, 'crop': 'fit'},  # adjust options as needed
        #     )


# class ProductTypeSerializer(ModelSerializer):
#     class Meta:
#         model = ProductType
#         fields = '__all__'


class AttributeSerializer(ModelSerializer):
    class Meta:
        model = Attribute
        fields = '__all__'


class AttributeValueSerializer(ModelSerializer):
    attribute = AttributeSerializer(many=False)

    class Meta:
        model = AttributeValue
        # fields = ['attribute', 'attribute_value']
        fields = '__all__'


# class FilteringAttributeValueSerializer(ModelSerializer):
#     attribute = AttributeSerializer(many=False)
#
#     class Meta:
#         model = AttributeValue
#         fields = ['id', 'attribute', 'attribute_value']


class ReviewSerializer(ModelSerializer):
    # average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Review
        # fields = ['id', 'name', 'description', 'rating', 'average_rating']
        fields = ['id', 'name', 'description', 'rating']

    def create(self, validated_data):
        product = self.context['product']
        validated_data['product'] = product
        return Review.objects.create(**validated_data)

    # def get_average_rating(self, obj):
    #     product = obj.product
    #     # Calculate average rating for the current product
    #     return Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']


class ProductVariantSerializer(ModelSerializer):
    product_image = ProductImageSerializer(many=True)
    attribute_value = AttributeValueSerializer(many=True)

    class Meta:
        model = ProductVariant
        # exclude = ['product']
        fields = [
            'id',
            'order',
            'price',
            'price_label',
            'sku',
            'stock_qty',
            'is_active',
            'product_image',
            'attribute_value'
        ]

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     av_data = data.pop('attribute_value')
    #     attr_values = {}
    #     for key in av_data:
    #         attr_values.update({key['attribute']['title']: key['attribute_value']})
    #     data.update({'specification': attr_values})
    #     return data


class ProductSerializer(ModelSerializer):
    # category = CategorySerializer()
    product_variant = ProductVariantSerializer(many=True)
    attribute_value = AttributeValueSerializer(many=True)
    reviews = ReviewSerializer(many=True)
    average_rating = serializers.SerializerMethodField()

    # product_type = ProductTypeSerializer()

    # attribute = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'slug',
            'product_id',
            'description',
            'is_digital',
            'is_active',
            # 'condition',
            'product_type',
            # 'category',
            'average_rating',
            'reviews',
            'product_variant',
            'attribute_value',
            # 'attribute'
        ]

    def get_average_rating(self, obj):
        return Review.objects.filter(product=obj).aggregate(Avg('rating'))['rating__avg']

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     av_data = data.pop('attribute_value')
    #     attr_values = {}
    #     for key in av_data:
    #         attr_values.update({key['attribute']['title']: key['attribute_value']})
    #     data.update({'top_attribute': attr_values})
    #     return data

    # def get_attribute(self, obj):
    #     attribute = Attribute.objects.filter(product_type_attribute__product__id=obj.id)
    #     return AttributeSerializer(attribute, many=True).data

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     av_data = data.pop('attribute')
    #     attr_values = {}
    #     for key in av_data:
    #         attr_values.update({key['id']: key['title']})
    #     data.update({'type_specification': attr_values})
    #     return data


# class ProductVariantCategorySerializer(ModelSerializer):
#     product_image = ProductImageSerializer(many=True)
#
#     class Meta:
#         model = ProductVariant
#         fields = ['price', 'product_image']


# class ProductCategorySerializer(ModelSerializer):
#     # product_variant = ProductVariantCategorySerializer(many=True)
#
#     class Meta:
#         model = Product
#         # fields = '__all__'
#         fields = [
#             'title',
#             'slug',
#             'product_id',
#             'created_at',
#             'product_variant'
#         ]

# def to_representation(self, instance):
#     data = super().to_representation(instance)
#     x = data.pop('product_variant')
#     if x:
#         price = x[0]['price']
#         image = x[0]['product_image']
#         data.update({'price': price})
#         data.update({'image': image})
#     return data


class ProductTypeAttributeSerializer(ModelSerializer):
    attributes = AttributeSerializer(many=True, source='attribute.all')

    class Meta:
        model = ProductType
        # fields = ['id', 'title', 'attributes']
        fields = '__all__'


# class ReviewSerializer(ModelSerializer):
#     class Meta:
#         model = Review
#         fields = ['id', 'name', 'description', 'rating']
#
#     def create(self, validated_data):
#         product = self.context['product']
#         validated_data['product'] = product
#         return Review.objects.create(**validated_data)


class SimpleProductVariantSerializer(ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = [
            'id',
            # 'order',
            'price',
            # 'sku',
            # 'stock_qty',
            # 'is_active',
            # 'product_image',
            # 'attribute_value'
        ]


class SimpleProductSerializer(ModelSerializer):
    product_variant = SimpleProductVariantSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'product_variant',
        ]


# class CartItemSerializer(ModelSerializer):
#     product = SimpleProductSerializer()
#     total_price = serializers.SerializerMethodField()
#
#     def get_total_price(self, cart_item: CartItem):
#         # this is for now
#         product_variant = cart_item.product.product_variant.first()
#         if product_variant:
#             return cart_item.quantity * product_variant.price
#         return 0
#
#     class Meta:
#         model = CartItem
#         fields = ['id', 'product', 'quantity', 'total_price']


# class CartSerializer(ModelSerializer):
#     id = serializers.UUIDField(read_only=True)
#     cart_items = CartItemSerializer(many=True, read_only=True)
#
#     # total_price = serializers.SerializerMethodField()
#     #
#     # def get_total_price(self, cart):
#     #     cart_items = cart.cart_items.all()
#     #     total = sum([cart_item.total_price for cart_item in cart_items])
#     #     return total
#
#     class Meta:
#         model = Cart
#         fields = [
#             'id',
#             'cart_items',
#             # 'total_price'
#         ]


# class AddCartItemSerializer(ModelSerializer):
#     product_id = serializers.IntegerField()
#
#     def validate_product_id(self, value):
#         if not Product.objects.filter(pk=value).exists():
#             raise serializers.ValidationError('No product with given ID was found')
#         return value
#
#     def save(self, **kwargs):
#         cart_id = self.context['cart_id']
#         product_id = self.validated_data['product_id']
#         quantity = self.validated_data['quantity']
#
#         try:
#             cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
#             cart_item.quantity += quantity
#             cart_item.save()
#             self.instance = cart_item
#         except CartItem.DoesNotExist:
#             self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
#
#         return self.instance
#
#     class Meta:
#         model = CartItem
#         fields = ['id', 'product_id', 'quantity']


# class UpdateCartItemSerializer(ModelSerializer):
#     class Meta:
#         model = CartItem
#         fields = ['quantity']


class AddressSerializer(ModelSerializer):
    class Meta:
        model = Address
        # fields = '__all__'
        fields = [
            'id',
            'full_name',
            'street_name',
            'address_line_1',
            'address_line_2',
            'postal_code',
            'city_or_village'
        ]

    # This method is called when the serializer is preparing to represent the data.
    # 'instance' represents the instance of the model being serialized.
    def to_representation(self, instance):
        # First, get the default representation of the data by calling the superclass method.
        data = super().to_representation(instance)

        # 'data' now contains the default representation of the serialized instance.
        # We'll modify this representation to filter out empty string values from the data.

        # Using a dictionary comprehension to create a new dictionary:
        # For each key-value pair in 'data', include the key-value pair in the new dictionary
        # only if the value is not an empty string ('' represents an empty string).
        return {key: value for key, value in data.items() if value != ''}


class CustomerSerializer(ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    address = AddressSerializer(many=True)

    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone_number', 'birth_date', 'address']
        # fields = '__all__'


# class OrderItemSerializer(ModelSerializer):
#     product = SimpleProductSerializer()
#
#     class Meta:
#         model = OrderItem
#         fields = ['id', 'product', 'price', 'quantity']
#
#
# class OrderSerializer(ModelSerializer):
#     # order_items = OrderItemSerializer(many=True)
#
#     class Meta:
#         model = Order
#         # fields = ['id', 'customer', 'placed_at', 'payment_status', 'order_items']
#         fields = '__all__'


# class UpdateOrderSerializer(ModelSerializer):
#     class Meta:
#         model = Order
#         fields = ['payment_status']


# class CreateOrderSerializer(serializers.Serializer):
#     cart_id = serializers.UUIDField()
#
#     # def validate_cart_id(self, cart_id):
#     #     if not Cart.objects.filter(pk=cart_id).exists():
#     #         raise serializers.ValidationError('No cart with the given ID was found.')
#     #     if CartItem.objects.filter(cart_id=cart_id).count() == 0:
#     #         raise serializers.ValidationError('The cart is empty.')
#     #     return cart_id
#
#     def save(self, **kwargs):
#         with transaction.atomic():
#             cart_id = self.validated_data['cart_id']
#             customer = Customer.objects.get(user_id=self.context['user_id'])
#             cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id)
#
#             order = Order.objects.create(customer=customer)
#
#             # Converting cart items to order items.
#             order_items = [
#                 OrderItem(
#                     order=order,
#                     product=item.product,
#                     unit_price=item.product.unit_price,
#                     quantity=item.quantity
#                 ) for item in cart_items
#             ]
#             OrderItem.objects.bulk_create(order_items)
#
#             Cart.objects.filter(pk=cart_id).delete()
#
#             order_created.send_robust(self.__class__, order=order)
#
#             return order


class PaymentOptionSerializer(ModelSerializer):
    class Meta:
        model = PaymentOption
        # fields = ['id', 'title', 'slug', 'is_active']
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'quantity', 'price', 'sku', 'title', 'product_variant']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'placed_at', 'payment_status', 'customer', 'selected_address', 'total', 'order_items']

    class OrderSerializer(serializers.ModelSerializer):
        order_items = OrderItemSerializer(many=True)

        class Meta:
            model = Order
            fields = ['id', 'placed_at', 'payment_status', 'customer', 'selected_address', 'total', 'order_items']

        # def create(self, validated_data):
        #     # Extracting the nested data for order items
        #     order_items_data = validated_data.pop('order_items')
        #
        #     # Creating the order object using the validated data received
        #     order = Order.objects.create(**validated_data)
        #
        #     # Creating associated order items for the newly created order
        #     for order_item_data in order_items_data:
        #         # Creating individual order items linked to the order
        #         OrderItem.objects.create(order=order, **order_item_data)
        #
        #     return order
