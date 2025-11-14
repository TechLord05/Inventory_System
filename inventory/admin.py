from django.contrib import admin
from .models import Supplier, Product, Order

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone')
    search_fields = ('name', 'email', 'phone')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sku', 'quantity', 'price', 'category')
    search_fields = ('name', 'sku', 'category')

    # def get_suppliers(self, obj):
    #     return ", ".join([supplier.name for supplier in obj.suppliers.all()])
    # get_suppliers.short_description = 'Suppliers'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'type', 'quantity', 'status', 'created_at')
    list_filter = ('type', 'status', 'created_at')
    search_fields = ('product__name',)
    date_hierarchy = 'created_at'
