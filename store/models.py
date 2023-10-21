from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class IsActiveQuerySet(models.QuerySet):
    def is_active(self):
        return self.filter(is_active=True)


class Category(MPTTModel):
    objects = IsActiveQuerySet().as_manager()
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=255)
    is_active = models.BooleanField(default=False)
    parent = TreeForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)

    class MPTTMeta:
        order_insertion_by = ['title']

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Categories"


class Brand(models.Model):
    objects = IsActiveQuerySet().as_manager()
    title = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Product(models.Model):
    objects = IsActiveQuerySet().as_manager()
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    is_digital = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    CONDITION_CHOICES = (
        ('New', 'New'),
        ('Used', 'Used'),
    )
    condition = models.CharField(
        max_length=4, choices=CONDITION_CHOICES, default='New')
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT)

    # product_type = models.ForeignKey(
    #     'ProductType', on_delete=models.PROTECT)

    def __str__(self):
        return self.title


class ProductVariant(models.Model):
    objects = IsActiveQuerySet().as_manager()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    sku = models.CharField(max_length=100)
    stock_qty = models.IntegerField()
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='product_variant')
    is_active = models.BooleanField(default=False)
    order = models.PositiveIntegerField()

    # order = OrderField(unique_for_field='product', blank=True)

    # attribute_value = models.ManyToManyField(
    #     AttributeValue,
    #     through='ProductVariantAttributeValue',
    #     related_name='product_variant_attribute_value'
    # )

    # def __str__(self):
    #     return str(self.order)

    def __str__(self):
        return str(self.sku)

    # def clean(self):
    #     qs = ProductVariant.objects.filter(product=self.product)
    #     for obj in qs:
    #         if self.id != obj.id and self.order == obj.order:
    #             raise ValidationError('Duplicate value in ORDER.')

    # def save(self, *args, **kwargs):
    #     self.full_clean()
    #     return super(ProductVariant, self).save(*args, **kwargs)

    # size = models.IntegerField()
    # color = models.CharField(max_length=50)
