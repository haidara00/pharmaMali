from django.urls import path
from . import views

urlpatterns = [
    path('', views.pos_view, name='pos'),
    path('sales-history/', views.sales_history_view, name='sales_history'),
    path('credit-ledger/', views.credit_ledger_view, name='credit_ledger'),
    path('api/products/search/', views.product_search_api, name='product_search'),
    path('api/products/barcode-search/', views.product_barcode_search_api, name='product_barcode_search'),  # New

    path('api/sales/complete/', views.complete_sale_api, name='complete_sale'),
    path('api/sales/history/', views.sales_history_api, name='sales_history_api'),
    path('api/credit/ledger/', views.credit_ledger_api, name='credit_ledger_api'),
    path('api/credit/<int:sale_id>/mark-paid/', views.mark_credit_paid_api, name='mark_credit_paid'),
]
