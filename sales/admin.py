from django.contrib import admin
from .models import Sale, SaleItem

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ('total_price',)

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'sale_type', 'total_amount', 'customer_name', 'sale_date')
    list_filter = ('sale_type', 'sale_date')
    search_fields = ('customer_name',)
    inlines = [SaleItemInline]
    readonly_fields = ('sale_date',)

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'product', 'quantity', 'unit_price', 'total_price')
    list_filter = ('sale__sale_date',)
    readonly_fields = ('total_price',)
