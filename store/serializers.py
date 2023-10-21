from rest_framework import serializers
from .models import Brand, Category, Product, ProductVariant


# ProductVariant, ProductImage, Attribute, AttributeValue


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'is_active']


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'title', 'is_active']


class ProductVariantSerializer(serializers.ModelSerializer):
    # product_image = ProductImageSerializer(many=True)
    # attribute_value = AttributeValueSerializer(many=True)

    class Meta:
        model = ProductVariant
        # exclude = ['product']
        fields = [
            'price',
            'sku',
            'stock_qty',
            'is_active',
            # 'order',
            # 'product_image',
            # 'attribute_value'
        ]

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     av_data = data.pop('attribute_value')
    #     attr_values = {}
    #     for key in av_data:
    #         attr_values.update({key['attribute']['id']: key['attribute_value']})
    #     data.update({'specification': attr_values})
    #     return data


class ProductSerializer(serializers.ModelSerializer):
    brand = serializers.CharField(source='brand.title')
    category = CategorySerializer()

    product_variant = ProductVariantSerializer(many=True)

    # attribute = serializers.SerializerMethodField()

    class Meta:
        model = Product
        # fields = '__all__'
        fields = [
            'title',
            'slug',
            'description',
            'brand',
            'is_digital',
            'is_active',
            'condition',
            'category',
            'product_variant',
            # 'attribute'
        ]

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
