from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Product, Supplier, Order, StockMovement
from .serializers import ProductSerializer, SupplierSerializer, OrderSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

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
