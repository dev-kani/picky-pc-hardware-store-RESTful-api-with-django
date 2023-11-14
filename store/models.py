from django.core.exceptions import ValidationError
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from .fields import OrderField


class IsActiveQuerySet(models.QuerySet):
    def is_active(self):
        return self.filter(is_active=True)


class Category(MPTTModel):
    objects = IsActiveQuerySet().as_manager()
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    is_active = models.BooleanField(default=False)
    parent = TreeForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)

    class MPTTMeta:
        order_insertion_by = ['title']

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Categories"


class Attribute(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class AttributeValue(models.Model):
    attribute_value = models.CharField(max_length=100)
    attribute = models.ForeignKey(
        Attribute, on_delete=models.CASCADE, related_name='attribute_value')

    def __str__(self):
        return f'{self.attribute.title}-{self.attribute_value}'


class ProductType(models.Model):
    title = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self', on_delete=models.PROTECT, null=True, blank=True)
    attribute = models.ManyToManyField(
        Attribute,
        through='ProductTypeAttribute',
        related_name='product_type_attribute'
    )

    def __str__(self):
        return self.title


# Customized auto generated link table
class ProductTypeAttribute(models.Model):
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.CASCADE,
        related_name='product_type_attribute_pt'
    )
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        related_name='product_type_attribute_a'
    )

    class Meta:
        unique_together = ('product_type', 'attribute')


class Product(models.Model):
    objects = IsActiveQuerySet().as_manager()
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255)
    product_id = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    is_digital = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    product_type = models.ForeignKey(
        ProductType, on_delete=models.PROTECT, related_name='product_type'
    )
    attribute_value = models.ManyToManyField(
        'AttributeValue',
        through='ProductAttributeValue',
        related_name='product_attr_value'
    )
    CONDITION_CHOICES = (
        ('New', 'New'),
        ('Used', 'Used'),
    )
    condition = models.CharField(
        max_length=4, choices=CONDITION_CHOICES, default='New')
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.title


# Customized auto generated link table
class ProductAttributeValue(models.Model):
    attribute_value = models.ForeignKey(
        AttributeValue, on_delete=models.CASCADE, related_name='product_value_av')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='product_value_pv')

    class Meta:
        unique_together = ('attribute_value', 'product')


class ProductVariant(models.Model):
    objects = IsActiveQuerySet().as_manager()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    sku = models.CharField(max_length=100)
    stock_qty = models.IntegerField()
    is_active = models.BooleanField(default=False)
    weight = models.FloatField()
    order = OrderField(unique_for_field='product', blank=True)
    CONDITION_CHOICES = (
        ('New', 'New'),
        ('Used', 'Used'),
    )
    condition = models.CharField(
        max_length=4, choices=CONDITION_CHOICES, default='New')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='product_variant')
    attribute_value = models.ManyToManyField(
        AttributeValue,
        through='ProductVariantAttributeValue',
        related_name='product_variant_attribute_value'
    )
    product_type = models.ForeignKey(
        ProductType, on_delete=models.PROTECT, related_name='product_variant_type'
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def clean(self):
        qs = ProductVariant.objects.filter(product=self.product)
        for obj in qs:
            if self.id != obj.id and self.order == obj.order:
                raise ValidationError('Duplicate value in ORDER.')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(ProductVariant, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.sku)


# Customized auto generated link table
class ProductVariantAttributeValue(models.Model):
    attribute_value = models.ForeignKey(
        AttributeValue, on_delete=models.CASCADE, related_name='product_attribute_value_av')
    product_variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name='product_attribute_value_pv')

    class Meta:
        unique_together = ('attribute_value', 'product_variant')

    def clean(self):
        qs = (
            ProductVariantAttributeValue.objects.filter(
                attribute_value=self.attribute_value
            ).filter(product_variant=self.product_variant).exists()
        )

        if not qs:
            iqs = Attribute.objects.filter(
                attribute_value__product_variant_attribute_value=self.product_variant
            ).values_list('pk', flat=True)

        if self.attribute_value.attribute.id in list(iqs):
            raise ValidationError('Duplicate attribute exists')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(ProductVariantAttributeValue, self).save(*args, **kwargs)


class ProductImage(models.Model):
    alternative_text = models.CharField(max_length=100)
    url = models.ImageField(upload_to=None, default='test.jpg')
    product_variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name='product_image'
    )
    order = OrderField(unique_for_field='product_variant', blank=True)

    def clean(self):
        qs = ProductImage.objects.filter(product_variant=self.product_variant)
        for obj in qs:
            if self.id != obj.id and self.order == obj.order:
                raise ValidationError('Duplicate value in ORDER.')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(ProductImage, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.product_variant.sku}_img'
