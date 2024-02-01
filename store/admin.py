from django.contrib import admin
from django.utils.html import format_html, urlencode
from django.db.models import Count
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (Category, Product, ProductVariant, ProductImage,
                     AttributeValue, Attribute, ProductType, Customer, Order,
                     ProductAttributeValue, Address, PaymentOption, OrderItem
                     )


class EditLinkInline(object):
    def edit(self, instance):
        url = reverse(
            f'admin:{instance._meta.app_label}_{instance._meta.model_name}_change',
            args=[instance.pk]
        )
        if instance.pk:
            link = mark_safe('<a href="{u}">edit</a>'.format(u=url))
            return link
        else:
            return ''


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_active', 'products_count']
    prepopulated_fields = {
        'slug': ['title']
    }

    @admin.display(ordering='products_count')
    def products_count(self, category):
        url = reverse('admin:store_product_changelist')
        query_params = {'category__id': str(category.id)}
        url = f'{url}?{urlencode(query_params)}'
        return format_html(f'<a href="{url}">{category.products_count}</a>')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('product')
        )


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(EditLinkInline, admin.TabularInline):
    model = ProductVariant
    readonly_fields = ['edit']
    min_num = 1  # Minimum number of product variant instances
    extra = 1


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue.product_variant_attribute_value.through


class AttributeValueProductInline(admin.TabularInline):
    model = AttributeValue.product_attr_value.through


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductVariantInline,
        AttributeValueProductInline
    ]
    list_display = ['title', 'product_id']
    prepopulated_fields = {
        'slug': ['title']
    }
    search_fields = ['title__istartswith']
    list_filter = ['category', 'updated_at']
    autocomplete_fields = ['product_type']


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'price', 'sku', 'stock_qty', 'is_active', 'weight']
    inlines = [
        ProductImageInline,
        AttributeValueInline
    ]


class OrderItem(admin.TabularInline):
    model = OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'placed_at', 'customer', 'payment_status']
    inlines = [
        OrderItem
    ]


class AttributeInline(admin.TabularInline):
    model = Attribute.product_type_attribute.through


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    inlines = [
        AttributeInline
    ]
    search_fields = ['title']


class AddressInline(admin.StackedInline):
    model = Address
    extra = 1


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    inlines = [
        AddressInline
    ]
    list_display = ['id', 'first_name', 'last_name']
    list_select_related = ['user']
    ordering = ['user__first_name', 'user__last_name']


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    pass
    # list_display = ['id', 'title']
    # search_fields = ['id', 'attribute']


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    search_fields = ['attribute_value', 'attribute__title']
    list_display = ['id', 'title', 'for_filtering']
    # list_select_related = ['attribute']
    # autocomplete_fields = ['attribute_title']


# class CartItemInline(admin.StackedInline):
#     model = CartItem
#     extra = 1


# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     inlines = [CartItemInline]
#     # list_display = ['id', 'customer', 'created_at']


@admin.register(PaymentOption)
class PaymentOptionAdmin(admin.ModelAdmin):
    pass
