# inventory/urls.py
from rest_framework import routers
from django.urls import path, include
from .views import ProductViewSet, SupplierViewSet, OrderViewSet, StockMovementViewSet

router = routers.DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'stock-movements', StockMovementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
