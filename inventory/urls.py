from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.inventory_dashboard, name='inventory_dashboard'),
    path('api/dashboard/', views.inventory_dashboard_api, name='inventory_dashboard_api'),

    # User-facing inventory management
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_edit, name='product_add'),
    path('products/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('stock/receive/', views.receive_stock, name='receive_stock'),
    path('stock/receive/<int:product_id>/', views.receive_stock, name='receive_stock_product'),
    path('products/<int:product_id>/adjust-stock/', views.adjust_stock, name='adjust_stock'),

    # Supplier and PurchaseOrder routes removed

    # Analytics
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('api/analytics/sales/', views.sales_analytics_api, name='sales_analytics_api'),
    path('api/analytics/profitability/', views.profitability_analytics_api, name='profitability_analytics_api'),
    path('api/analytics/inventory/', views.inventory_analytics_api, name='inventory_analytics_api'),
    path('api/analytics/inventory/pdf/', views.analytics_inventory_pdf, name='analytics_inventory_pdf'),

    # Excel import/export routes
    path('products/export_excel/', views.export_products_excel, name='export_products_excel'),
    path('products/import_excel/', views.import_products_excel, name='import_products_excel'),
    path('products/template_excel/', views.download_products_template, name='download_products_template'),
    

]
    