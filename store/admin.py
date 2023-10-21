from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Product, Brand, ProductVariant


# ProductImage, AttributeValue, Attribute, ProductType


# class EditLinkInline(object):
#     def edit(self, instance):
#         url = reverse(
#             f'admin:{instance._meta.app_label}_{instance._meta.model_name}_change',
#             args=[instance.pk]
#         )
#         if instance.pk:
#             link = mark_safe('<a href="{u}">edit</a>'.format(u=url))
#             return link
#         else:
#             return ''


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_active']
    # prepopulated_fields = {
    #     'slug': ['title']
    # }


# class ProductImageInline(admin.TabularInline):
#     model = ProductImage


class ProductVariantInline(
    # EditLinkInline,
    admin.TabularInline):
    model = ProductVariant
    # readonly_fields = ['edit']
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductVariantInline]
    # prepopulated_fields = {
    #     'slug': ['title']
    # }


# class AttributeValueInline(admin.TabularInline):
#     model = AttributeValue.product_variant_attribute_value.through


class ProductVariantAdmin(admin.ModelAdmin):
    inlines = [
        # ProductImageInline,
        # AttributeValueInline
    ]


# class AttributeInline(admin.TabularInline):
#     model = Attribute.product_type_attribute.through


class ProductTypeAdmin(admin.ModelAdmin):
    inlines = [
        # AttributeInline
    ]


admin.site.register(ProductVariant, ProductVariantAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Brand)
# admin.site.register(Attribute)
# admin.site.register(ProductType, ProductTypeAdmin)
# admin.site.register(AttributeValue)
