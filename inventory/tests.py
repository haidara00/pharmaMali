from django.test import TestCase, Client
from django.utils import timezone
from datetime import timedelta
from .models import Product, ProductBatch


class ExpiryLogicTests(TestCase):
	def setUp(self):
		self.product = Product.objects.create(
			name='TestMed',
			selling_price=10.00,
			cost_price=5.00,
			current_stock=100,
			minimum_stock_level=5,
			is_active=True
		)

	def test_days_until_expiry_and_status(self):
		today = timezone.now().date()
		# batch expires in 10 days -> critical
		batch = ProductBatch.objects.create(
			product=self.product,
			batch_number='B1',
			expiry_date=today + timedelta(days=10),
			quantity=10,
			purchase_price=4.50
		)
		self.assertEqual(batch.days_until_expiry, 10)
		self.assertEqual(batch.expiry_status, 'critical')

		# batch expired yesterday -> expired
		expired = ProductBatch.objects.create(
			product=self.product,
			batch_number='B2',
			expiry_date=today - timedelta(days=1),
			quantity=5,
			purchase_price=4.00
		)
		self.assertEqual(expired.expiry_status, 'expired')

		# batch far in future -> good
		future = ProductBatch.objects.create(
			product=self.product,
			batch_number='B3',
			expiry_date=today + timedelta(days=365),
			quantity=20,
			purchase_price=3.50
		)
		self.assertEqual(future.expiry_status, 'good')


class AnalyticsExpiryFilteringTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.product_active = Product.objects.create(
			name='ActiveMed', selling_price=5, cost_price=2, current_stock=50, minimum_stock_level=5, is_active=True
		)
		self.product_inactive = Product.objects.create(
			name='InactiveMed', selling_price=5, cost_price=2, current_stock=0, minimum_stock_level=5, is_active=False
		)
		today = timezone.now().date()
		# Active batch with quantity -> should appear
		ProductBatch.objects.create(
			product=self.product_active,
			batch_number='A1',
			expiry_date=today + timedelta(days=20),
			quantity=5,
			purchase_price=1.0
		)
		# Active batch with zero quantity -> should NOT appear
		ProductBatch.objects.create(
			product=self.product_active,
			batch_number='A2',
			expiry_date=today + timedelta(days=10),
			quantity=0,
			purchase_price=1.0
		)
		# Inactive product batch with quantity -> should NOT appear
		ProductBatch.objects.create(
			product=self.product_inactive,
			batch_number='I1',
			expiry_date=today + timedelta(days=5),
			quantity=10,
			purchase_price=1.0
		)

	def test_inventory_analytics_expiry_alerts_filtering(self):
		resp = self.client.get('/inventory/api/analytics/inventory/')
		self.assertEqual(resp.status_code, 200)
		data = resp.json()
		alerts = data.get('expiry_alerts', [])
		# Only one alert should be present (A1)
		self.assertEqual(len(alerts), 1)
		self.assertEqual(alerts[0]['product__name'], 'ActiveMed')


class RemovedRoutesTests(TestCase):
	def setUp(self):
		self.client = Client()

	def test_supplier_and_purchase_order_routes_removed(self):
		# expect 404 or removed-notice for removed routes
		for url in ['/inventory/suppliers/', '/inventory/suppliers/add/', '/inventory/purchase-orders/']:
			resp = self.client.get(url)
			# allow redirect or 404 or a 200 removed-notice page
			self.assertIn(resp.status_code, (301, 302, 404, 200))
			if resp.status_code == 200:
				content = resp.content.decode('utf-8').lower()
				self.assertTrue('supprim' in content or 'supprimé' in content or 'supprim' in content)


class ProductViewFormTests(TestCase):
	def setUp(self):
		self.client = Client()

	def test_product_create_view(self):
		# POST to product add view
		data = {
			'name': 'NewMed',
			'dci': 'DCI1',
			'therapeutic_class': 'other',
			'cost_price': '2.50',
			'selling_price': '5.00',
			'current_stock': '0',
			'minimum_stock_level': '5',
			'barcode': '',
			'is_active': 'on'
		}
		resp = self.client.post('/inventory/products/add/', data)
		# should redirect to product list
		self.assertIn(resp.status_code, (302, 301))
		# product exists
		from .models import Product
		p = Product.objects.filter(name='NewMed').first()
		self.assertIsNotNone(p)

	def test_receive_stock_updates_product_and_creates_batch(self):
		# Create a product
		from .models import Product, ProductBatch
		product = Product.objects.create(
			name='StockMed', selling_price=3.0, cost_price=1.0,
			current_stock=0, minimum_stock_level=2, is_active=True
		)
		today = timezone.now().date()
		data = {
			'product': str(product.id),
			'batch_number': 'RX123',
			'expiry_date': (today + timedelta(days=180)).strftime('%Y-%m-%d'),
			'quantity': '15',
			'purchase_price': '1.20',
			'supplier': ''
		}
		resp = self.client.post(f'/inventory/stock/receive/{product.id}/', data)
		# should redirect to inventory dashboard
		self.assertIn(resp.status_code, (302, 301))
		# reload product and check stock increased
		product.refresh_from_db()
		self.assertEqual(product.current_stock, 15)
		# batch exists
		batch = ProductBatch.objects.filter(product=product, batch_number='RX123').first()
		self.assertIsNotNone(batch)
		self.assertEqual(batch.quantity, 15)
