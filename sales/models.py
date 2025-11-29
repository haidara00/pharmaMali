from django.db import models
from inventory.models import Product

class Sale(models.Model):
    SALE_TYPES = (
        ('paid', 'Comptant'),
        ('credit', 'Crédit'),
    )

    sale_type = models.CharField(max_length=10, choices=SALE_TYPES, verbose_name="Type de vente")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant total")
    customer_name = models.CharField(max_length=200, blank=True, verbose_name="Nom du client")
    sale_date = models.DateTimeField(auto_now_add=True, verbose_name="Date de vente")

    class Meta:
        verbose_name = "Vente"
        verbose_name_plural = "Ventes"
        ordering = ['-sale_date']

    def __str__(self):
        return f"Vente #{self.id} - {self.total_amount} FCFA - {self.get_sale_type_display()}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produit")
    quantity = models.PositiveIntegerField(verbose_name="Quantité")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix unitaire")

    class Meta:
        verbose_name = "Article vendu"
        verbose_name_plural = "Articles vendus"

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    @property
    def total_price(self):
        return self.unit_price * self.quantity
