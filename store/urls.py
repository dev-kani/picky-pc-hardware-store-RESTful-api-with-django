from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('categories', views.CategoryViewSet)
router.register('products', views.ProductViewSet, basename='products')
router.register('customers', views.CustomerViewSet, basename='customers')
router.register('orders', views.OrderViewSet, basename='orders')
router.register('product-types', views.ProductTypeAttributeValueViewSet, basename='product-types')
router.register('payment-options', views.PaymentOptionViewSet, basename='payment-options')
# router.register('carts', views.CartViewSet, basename='carts')
# router.register(r'product-types/(?P<title>[\w-]+)', views.ProductTypeAttributeView, basename='product-types')

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')

# carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
# carts_router.register('items', views.CartItemViewSet, basename='cart-items')

# urlpatterns = router.urls + products_router.urls + carts_router.urls
urlpatterns = router.urls + products_router.urls
