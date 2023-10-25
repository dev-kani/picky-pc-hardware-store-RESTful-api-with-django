from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductViewSet)

urlpatterns = router.urls

# urlpatterns = [
#     path('api/', include(router.urls)),
#     path(
#         'api/products/<int:pk>/category/<str:category>/all/',
#         views.list_product_by_category,
#         name='list_product_by_category',
#     ),
# ]
