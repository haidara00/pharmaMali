from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class Product(models.Model):
    THERAPEUTIC_CLASSES = [
        ('analgesic', 'Analgésique'),
        ('antibiotic', 'Antibiotique'),
        ('antihypertensive', 'Antihypertenseur'),
        ('antidiabetic', 'Antidiabétique'),
        ('antiinflammatory', 'Anti-inflammatoire'),
        ('gastrointestinal', 'Traitement Gastro-intestinal'),
        ('respiratory', 'Traitement Respiratoire'),
        ('dermatological', 'Dermatologique'),
        ('vitamin', 'Vitamines et Suppléments'),
        ('other', 'Autre'),
    ]

    name = models.CharField(max_length=200, verbose_name="Nom du médicament")
    dci = models.CharField(max_length=200, blank=True, verbose_name="Dénomination Commune Internationale")
    therapeutic_class = models.CharField(
        max_length=50,
        choices=THERAPEUTIC_CLASSES,
        default='other',
        verbose_name="Classe thérapeutique"
    )
    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Prix de vente"
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Prix d'achat"
    )
    current_stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Stock actuel"
    )
    minimum_stock_level = models.IntegerField(
        default=5,
        validators=[MinValueValidator(0)],
        verbose_name="Stock minimum d'alerte"
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    barcode = models.CharField(
        max_length=50,
        blank=True,
        null=True,  # Add this
        unique=True,
        verbose_name="Code-barres",
        help_text="Code-barres EAN-13 ou autre format"
    )

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - Stock: {self.current_stock}"

    @property
    def profit_margin(self):
        if self.cost_price > 0:
            return ((self.selling_price - self.cost_price) / self.cost_price) * 100
        return 0

    @property
    def stock_status(self):
        if self.current_stock == 0:
            return 'out_of_stock'
        elif self.current_stock <= self.minimum_stock_level:
            return 'low_stock'
        else:
            return 'in_stock'

    @property
    def total_value(self):
        return self.current_stock * self.cost_price

    # Display method for admin
    def get_stock_status_display(self):
        status = self.stock_status
        if status == 'out_of_stock':
            return 'Rupture de stock'
        elif status == 'low_stock':
            return 'Stock faible'
        else:
            return 'En stock'

class Supplier(models.Model):
    PAYMENT_TERMS = [
        ('cash', 'Comptant'),
        ('7_days', '7 jours'),
        ('15_days', '15 jours'),
        ('30_days', '30 jours'),
        ('60_days', '60 jours'),
    ]

    name = models.CharField(max_length=200, verbose_name="Nom du fournisseur")
    contact_person = models.CharField(max_length=200, blank=True, verbose_name="Personne à contacter")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Email")
    address = models.TextField(blank=True, verbose_name="Adresse")
    payment_terms = models.CharField(max_length=20, choices=PAYMENT_TERMS, default='30_days', verbose_name="Conditions de paiement")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_orders(self):
        return self.purchase_orders.count()

    @property
    def total_spent(self):
        from django.db.models import Sum
        total = self.purchase_orders.aggregate(Sum('total_amount'))['total_amount__sum']
        return total or 0



class ProductBatch(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='batches')
    batch_number = models.CharField(max_length=100, verbose_name="Numéro de lot")
    expiry_date = models.DateField(verbose_name="Date d'expiration")
    quantity = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="Quantité dans le lot"
    )
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Prix d'achat du lot"
    )
    date_received = models.DateField(auto_now_add=True, verbose_name="Date de réception")
    supplier = models.ForeignKey(  # Change from CharField to ForeignKey
            Supplier,
            on_delete=models.SET_NULL,
            null=True,
            blank=True,
            related_name='batches',
            verbose_name="Fournisseur"
        )
    supplier_name = models.CharField(max_length=200, blank=True, verbose_name="Fournisseur ancien")

    class Meta:
        verbose_name = "Lot de produit"
        verbose_name_plural = "Lots de produits"
        ordering = ['expiry_date']

    def __str__(self):
        return f"{self.product.name} - Lot: {self.batch_number}"

    @property
    def days_until_expiry(self):
        today = timezone.now().date()
        delta = self.expiry_date - today
        return delta.days

    @property
    def expiry_status(self):
        days = self.days_until_expiry
        if days < 0:
            return 'expired'
        elif days <= 30:
            return 'critical'
        elif days <= 90:
            return 'warning'
        else:
            return 'good'

    # Display method for admin
    def get_expiry_status_display(self):
        status = self.expiry_status
        if status == 'expired':
            return 'Expiré'
        elif status == 'critical':
            return 'Critique'
        elif status == 'warning':
            return 'Avertissement'
        else:
            return 'Bon'

class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('sale', 'Vente'),
        ('receipt', 'Réception'),
        ('adjustment', 'Ajustement'),
        ('return', 'Retour'),
        ('damage', 'Produit endommagé'),
        ('expiry', 'Produit expiré'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField(verbose_name="Quantité")
    previous_stock = models.IntegerField(verbose_name="Stock précédent")
    new_stock = models.IntegerField(verbose_name="Nouveau stock")
    reference = models.CharField(max_length=100, blank=True, verbose_name="Référence")  # Sale ID, Batch ID, etc.
    reason = models.TextField(blank=True, verbose_name="Raison")
    created_by = models.CharField(max_length=100, default="Système", verbose_name="Effectué par")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} - {self.get_movement_type_display()} - {self.quantity} unités"


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('ordered', 'Commandé'),
        ('received', 'Reçu'),
        ('cancelled', 'Annulé'),
    ]

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders')
    order_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro de commande")
    order_date = models.DateField(auto_now_add=True, verbose_name="Date de commande")
    expected_delivery = models.DateField(null=True, blank=True, verbose_name="Livraison prévue")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Montant total")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_by = models.CharField(max_length=100, default="Système", verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bon de commande"
        verbose_name_plural = "Bons de commande"
        ordering = ['-order_date']

    def __str__(self):
        return f"BC #{self.order_number} - {self.supplier.name}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number: BC-YYYYMMDD-XXXX
            from datetime import datetime
            date_part = datetime.now().strftime('%Y%m%d')
            last_order = PurchaseOrder.objects.filter(order_number__startswith=f'BC-{date_part}').order_by('order_number').last()
            if last_order:
                last_num = int(last_order.order_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.order_number = f"BC-{date_part}-{new_num:04d}"

        # Calculate total amount from items
        if self.id:
            self.total_amount = sum(item.total_price for item in self.items.all())

        super().save(*args, **kwargs)

class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produit")
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Quantité commandée")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix unitaire")
    received_quantity = models.IntegerField(default=0, verbose_name="Quantité reçue")

    class Meta:
        verbose_name = "Article de commande"
        verbose_name_plural = "Articles de commande"

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    @property
    def pending_quantity(self):
        return self.quantity - self.received_quantity
