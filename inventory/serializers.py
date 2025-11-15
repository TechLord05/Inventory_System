from rest_framework import serializers
from .models import Product, Supplier, Order, StockMovement

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ["id", "name", "email", "phone"]

class ProductSerializer(serializers.ModelSerializer):
    suppliers = SupplierSerializer(many=True, read_only=True)
    supplier_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Product
        fields = [
            "id", "name", "description", "sku",
            "quantity", "price", "category",
            "suppliers",       # read-only nested
            "supplier_ids",    # write-only list of UUIDs
            "created_at", "updated_at"
        ]

    def create(self, validated_data):
        supplier_ids = validated_data.pop("supplier_ids", [])
        product = Product.objects.create(**validated_data)

        # Assign suppliers
        if supplier_ids:
            suppliers = Supplier.objects.filter(id__in=supplier_ids)
            product.suppliers.set(suppliers)

        return product
    
    def update(self, instance, validated_data):
        supplier_ids = validated_data.pop("supplier_ids", None)

        # Update normal product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update supplier relations if supplier_ids was provided
        if supplier_ids is not None:
            suppliers = Supplier.objects.filter(id__in=supplier_ids)
            instance.suppliers.set(suppliers)

        return instance



class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    order_id = serializers.UUIDField(source='order.id', read_only=True)

    class Meta:
        model = StockMovement
        fields = ['id', 'product', 'product_name', 'order_id', 'quantity', 'type', 'created_at']


class InventoryDashboardSerializer(serializers.Serializer):
    total_products = serializers.IntegerField()
    total_stock = serializers.IntegerField()
    low_stock_products = serializers.ListField(child=serializers.DictField())
