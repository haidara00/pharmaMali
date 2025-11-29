from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from inventory.models import Product
from .models import Sale, SaleItem
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum
from django.db.models import Sum, Q
from inventory.models import Product, StockMovement  # Add StockMovement here


def credit_ledger_view(request):
    return render(request, 'sales/credit_ledger.html')

def credit_ledger_api(request):
    # Get customers with outstanding credit
    credit_sales = Sale.objects.filter(
        sale_type='credit'
    ).exclude(
        Q(customer_name='') | Q(customer_name__isnull=True)
    )

    # Group by customer and calculate totals
    customer_totals = {}
    for sale in credit_sales:
        customer_name = sale.customer_name
        if customer_name not in customer_totals:
            customer_totals[customer_name] = {
                'total_owed': 0,
                'sales_count': 0,
                'sales': []
            }

        customer_totals[customer_name]['total_owed'] += float(sale.total_amount)
        customer_totals[customer_name]['sales_count'] += 1
        customer_totals[customer_name]['sales'].append({
            'id': sale.id,
            'total_amount': float(sale.total_amount),
            'sale_date': sale.sale_date.strftime('%d/%m/%Y %H:%M'),
            'items': [
                {
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price)
                }
                for item in sale.items.all()
            ]
        })

    # Convert to list for template
    customers = []
    for customer_name, data in customer_totals.items():
        customers.append({
            'name': customer_name,
            'total_owed': data['total_owed'],
            'sales_count': data['sales_count'],
            'sales': data['sales']
        })

    # Sort by total owed (highest first)
    customers.sort(key=lambda x: x['total_owed'], reverse=True)

    # Calculate overall totals
    total_outstanding = sum(customer['total_owed'] for customer in customers)
    total_customers = len(customers)

    return JsonResponse({
        'customers': customers,
        'total_outstanding': total_outstanding,
        'total_customers': total_customers
    })

@csrf_exempt
def mark_credit_paid_api(request, sale_id):
    if request.method == 'POST':
        try:
            sale = Sale.objects.get(id=sale_id, sale_type='credit')
            # For now, we'll just change sale type to 'paid'
            # In a more advanced version, we might want to track payments separately
            sale.sale_type = 'paid'
            sale.save()

            return JsonResponse({
                'success': True,
                'message': f'Crédit #{sale_id} marqué comme payé!'
            })

        except Sale.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Vente crédit non trouvée'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erreur: {str(e)}'
            })

    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})


def sales_history_view(request):
    return render(request, 'sales/sales_history.html')

def sales_history_api(request):
    # Get filter parameters
    filter_type = request.GET.get('filter', 'today')

    # Calculate date range
    today = timezone.now().date()

    if filter_type == 'today':
        start_date = today
        end_date = today + timedelta(days=1)
    elif filter_type == 'week':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=7)
    elif filter_type == 'month':
        start_date = today.replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1)
    else:  # all time
        start_date = None
        end_date = None

    # Query sales
    sales = Sale.objects.all()

    if start_date and end_date:
        sales = sales.filter(sale_date__date__gte=start_date, sale_date__date__lt=end_date)

    sales = sales.select_related().prefetch_related('items__product').order_by('-sale_date')

    # Calculate totals
    total_sales = sales.count()
    total_revenue = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    # Prepare data for template
    sales_data = []
    for sale in sales:
        sales_data.append({
            'id': sale.id,
            'sale_type': sale.get_sale_type_display(),
            'total_amount': float(sale.total_amount),
            'customer_name': sale.customer_name,
            'sale_date': sale.sale_date.strftime('%d/%m/%Y %H:%M'),
            'items': [
                {
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                    'total_price': float(item.total_price)
                }
                for item in sale.items.all()
            ]
        })

    return JsonResponse({
        'sales': sales_data,
        'total_sales': total_sales,
        'total_revenue': float(total_revenue),
        'filter_type': filter_type,
        'date_range': {
            'start': start_date.strftime('%d/%m/%Y') if start_date else 'Tous',
            'end': end_date.strftime('%d/%m/%Y') if end_date else 'Tous'
        }
    })

def pos_view(request):
    return render(request, 'sales/pos.html')

def product_search_api(request):
    query = request.GET.get('q', '').strip()

    if query:
        # Search by name OR barcode
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(barcode__icontains=query),
            is_active=True
        )[:10]
        results = [
            {
                'id': product.id,
                'name': product.name,
                'dci': product.dci,
                'price': float(product.selling_price),
                'current_stock': product.current_stock,
                'minimum_stock_level': product.minimum_stock_level,
                'barcode': product.barcode,
            }
            for product in products
        ]
    else:
        results = []
    return JsonResponse(results, safe=False)
@csrf_exempt
def complete_sale_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sale_type = data.get('sale_type')
            customer_name = data.get('customer_name', '')
            cart_items = data.get('cart', [])

            # Calculate total
            total_amount = sum(item['price'] * item['quantity'] for item in cart_items)

            # Create sale
            sale = Sale.objects.create(
                sale_type=sale_type,
                total_amount=total_amount,
                customer_name=customer_name if sale_type == 'credit' else ''
            )

            # Create sale items AND update stock
            for item in cart_items:
                product = Product.objects.get(id=item['id'])
                previous_stock = product.current_stock

                # Check if enough stock is available
                if previous_stock < item['quantity']:
                    sale.delete()
                    return JsonResponse({
                        'success': False,
                        'message': f'Stock insuffisant pour {product.name}. Stock disponible: {previous_stock}'
                    })

                # Create sale item
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=item['quantity'],
                    unit_price=item['price']
                )

                # DEDUCT STOCK from product
                product.current_stock -= item['quantity']
                product.save()

                # LOG STOCK MOVEMENT
                StockMovement.objects.create(
                    product=product,
                    movement_type='sale',
                    quantity=-item['quantity'],  # Negative for sales
                    previous_stock=previous_stock,
                    new_stock=product.current_stock,
                    reference=f"Vente #{sale.id}",
                    reason=f"Vente au {sale.get_sale_type_display().lower()}",
                    created_by="Système POS"
                )

            return JsonResponse({
                'success': True,
                'sale_id': sale.id,
                'message': f"Vente #{sale.id} enregistrée avec succès! Stock mis à jour."
            })

        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Produit non trouvé dans la base de données'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f"Erreur: {str(e)}"
            })

    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})
def product_barcode_search_api(request):
    barcode = request.GET.get('barcode', '').strip()

    if barcode:
        try:
            product = Product.objects.get(barcode=barcode, is_active=True)
            result = {
                'id': product.id,
                'name': product.name,
                'dci': product.dci,
                'price': float(product.selling_price),
                'current_stock': product.current_stock,
                'minimum_stock_level': product.minimum_stock_level,
                'barcode': product.barcode,
            }
            return JsonResponse({'success': True, 'product': result})
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Produit non trouvé pour ce code-barres'})
        except Product.MultipleObjectsReturned:
            return JsonResponse({'success': False, 'message': 'Plusieurs produits avec le même code-barres'})

    return JsonResponse({'success': False, 'message': 'Code-barres vide'})
