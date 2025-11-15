from rest_framework import viewsets, serializers, filters
from rest_framework.permissions import IsAuthenticated
from .models import Product, Supplier, Order, StockMovement
from .serializers import ProductSerializer, SupplierSerializer, OrderSerializer, InventoryDashboardSerializer, StockMovementSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]

    filterset_fields = ['category', 'suppliers']
    # Search by name, description, SKU, category
    search_fields = ['name', 'description', 'sku', 'category']

    # Allow sorting by price, quantity, created_at
    ordering_fields = ['price', 'quantity', 'created_at']


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        order = serializer.save()
        product = order.product

        if order.type == 'incoming':
            product.quantity += order.quantity
        elif order.type == 'outgoing':
            if order.quantity > product.quantity:
                raise serializers.ValidationError("Not enough stock for this outgoing order.")
            product.quantity -= order.quantity

        product.save()

        # Log the stock movement
        StockMovement.objects.create(
            product=product,
            order=order,
            quantity=order.quantity,
            type=order.type
        )

class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockMovement.objects.all().order_by('-created_at')
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]


class InventoryDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = Product.objects.all()
        total_products = products.count()
        total_stock = sum(p.quantity for p in products)

        # Low stock threshold, e.g., 10
        low_stock_threshold = 10
        low_stock_products = [
            {"id": p.id, "name": p.name, "quantity": p.quantity}
            for p in products if p.quantity <= low_stock_threshold
        ]

        data = {
            "total_products": total_products,
            "total_stock": total_stock,
            "low_stock_products": low_stock_products
        }

        serializer = InventoryDashboardSerializer(data)
        return Response(serializer.data)