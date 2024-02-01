from django.contrib import admin
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from uuid import uuid4
from mptt.models import MPTTModel, TreeForeignKey
from cloudinary.models import CloudinaryField
from .fields import OrderField


class IsActiveQuerySet(models.QuerySet):
    def is_active(self):
        return self.filter(is_active=True)


# class Promotion(models.Model):
#     description = models.CharField(max_length=255)
#     discount = models.FloatField()


class Category(MPTTModel):
    objects = IsActiveQuerySet().as_manager()
    # Adding 'db_index=True' improves the speed of data retrieval operations 
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

    def __str__(self):
        return self.title


class AttributeValue(models.Model):
    attribute_value = models.CharField(max_length=100)
    attribute = models.ForeignKey(
        Attribute, on_delete=models.CASCADE, related_name='attribute_value')
    for_filtering = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.attribute.title}-{self.attribute_value}'

    @admin.display(ordering='attribute__title')
    def title(self):
        return f'{self.attribute.title} - {self.attribute_value}'

    # class Meta:
    #     ordering = ['attribute__title']


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
    # featured = models.BooleanField(db_index=True)
    # promotions = models.ManyToManyField(Promotion)
    product_type = models.ForeignKey(
        ProductType, on_delete=models.PROTECT, related_name='product_type'
    )
    attribute_value = models.ManyToManyField(
        AttributeValue,
        through='ProductAttributeValue',
        related_name='product_attr_value',
        blank=True
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.title

    # class Meta:
    #     ordering = ['title']


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
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(1)]
    )
    price_label = models.CharField(max_length=10, blank=True)
    # price_label = models.ForeignKey(
    #     AttributeValue,
    #     on_delete=models.CASCADE,
    #     # related_name='variant_price_labels',
    #     # limit_choices_to={'attribute__title': 'YourDesiredAttributeTitle'}
    # )
    sku = models.CharField(max_length=100)
    stock_qty = models.PositiveIntegerField()
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
        related_name='product_variant_attribute_value',
        blank=True,
    )
    # Is product type necessary here?
    # product_type = models.ForeignKey(
    #     ProductType, on_delete=models.PROTECT, related_name='product_variant_type'
    # )
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
        return f'{self.product.title} - {self.price} variant'


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
    # image = models.ImageField(upload_to='store/images', default='test.jpg')
    image = CloudinaryField('image')
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


class Customer(models.Model):
    phone_number = models.CharField(max_length=15)
    birth_date = models.DateField(null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # billing_address = models.TextField()
    # shipping_address = models.TextField()
    # orders = models.ManyToManyField('Order', related_name='customers')

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name

    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name

    class Meta:
        ordering = ['user__first_name', 'user__last_name']


class Address(models.Model):
    full_name = models.CharField(max_length=100)
    street_name = models.CharField(max_length=255)
    address_line_1 = models.CharField(max_length=50, blank=True)
    address_line_2 = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=20)
    city_or_village = models.CharField(max_length=100)
    # state_or_region = models.CharField(max_length=100)
    # country = models.CharField(max_length=100)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='address')

    def __str__(self):
        return f'{self.full_name}'

    class Meta:
        verbose_name_plural = "Addresses"


# class Cart(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid4)
#     created_at = models.DateTimeField(auto_now_add=True)


# class CartItem(models.Model):
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveSmallIntegerField(
#         validators=[MinValueValidator(1)]
#     )
#
#     class Meta:
#         unique_together = ('cart', 'product')

# created_at = models.DateTimeField(auto_now_add=True, editable=False)
# updated_at = models.DateTimeField(auto_now=True, editable=False)


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=100)
    description = models.TextField()
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    posted_at = models.DateField(auto_now_add=True)


class PaymentOption(models.Model):
    name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    placed_at = models.DateTimeField(auto_now_add=True)
    PAYMENT_STATUS = (
        ('Pending', 'Pending'),
        ('Complete', 'Complete'),
        ('Failed', 'Failed'),
    )
    payment_status = models.CharField(
        max_length=8, choices=PAYMENT_STATUS, default='Pending')
    customer = models.ForeignKey('Customer', on_delete=models.PROTECT)
    selected_address = models.ForeignKey(Address, on_delete=models.PROTECT)
    total = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        permissions = [
            ('cancel_order', 'Authorized to cancel orders')
        ]

    # total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    # is_paid = models.BooleanField(default=False)
    # products = models.ManyToManyField('Product', through='OrderItem')

    # def __str__(self):
    #     return f'Order #{self.id} by {self.customer.full_name}'


class OrderItem(models.Model):
    quantity = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    product_variant = models.CharField(max_length=50)  # Assuming variant is a string field
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
