from rest_framework import serializers
from .models import Category, Product, ProductVariant, ProductImage, Attribute, AttributeValue


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug', 'is_active']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        exclude = ['id', 'product_variant']
        # fields = '__all__'


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = '__all__'


class AttributeValueSerializer(serializers.ModelSerializer):
    attribute = AttributeSerializer(many=False)

    class Meta:
        model = AttributeValue
        fields = ['attribute', 'attribute_value']


class ProductVariantSerializer(serializers.ModelSerializer):
    product_image = ProductImageSerializer(many=True)
    attribute_value = AttributeValueSerializer(many=True)

    class Meta:
        model = ProductVariant
        # exclude = ['product']
        fields = [
            'order',
            'price',
            'sku',
            'stock_qty',
            'is_active',
            'product_image',
            'attribute_value'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        av_data = data.pop('attribute_value')
        attr_values = {}
        for key in av_data:
            attr_values.update({key['attribute']['title']: key['attribute_value']})
        data.update({'specification': attr_values})
        return data


class ProductSerializer(serializers.ModelSerializer):
    # category = CategorySerializer()
    product_variant = ProductVariantSerializer(many=True)
    attribute_value = AttributeValueSerializer(many=True)

    # attribute = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'title',
            'slug',
            'product_id',
            'description',
            'is_digital',
            'is_active',
            'condition',
            # 'category',
            'attribute_value',
            'product_variant',
            # 'attribute'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        av_data = data.pop('attribute_value')
        attr_values = {}
        for key in av_data:
            attr_values.update({key['attribute']['title']: key['attribute_value']})
        data.update({'attribute': attr_values})
        return data

    # def get_attribute(self, obj):
    #     attribute = Attribute.objects.filter(product_type_attribute__product__id=obj.id)
    #     return AttributeSerializer(attribute, many=True).data
    #
    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     av_data = data.pop('attribute')
    #     attr_values = {}
    #     for key in av_data:
    #         attr_values.update({key['id']: key['title']})
    #     data.update({'type_specification': attr_values})
    #     return data


class ProductVariantCategorySerializer(serializers.ModelSerializer):
    product_image = ProductImageSerializer(many=True)

    class Meta:
        model = ProductVariant
        fields = ['price', 'product_image']


class ProductCategorySerializer(serializers.ModelSerializer):
    product_variant = ProductVariantCategorySerializer(many=True)

    class Meta:
        model = Product
        fields = [
            'title',
            'slug',
            'product_id',
            'created_at',
            'product_variant'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        x = data.pop('product_variant')
        if x:
            price = x[0]['price']
            image = x[0]['product_image']
            data.update({'price': price})
            data.update({'image': image})
        return data
