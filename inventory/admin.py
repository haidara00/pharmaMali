from django.contrib import admin
from .models import Product, ProductBatch, StockMovement

# Minimal registration - keep admin focused on core models
admin.site.register(Product)
admin.site.register(ProductBatch)
admin.site.register(StockMovement)
