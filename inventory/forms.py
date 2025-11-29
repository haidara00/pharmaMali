from django import forms
from .models import Product, ProductBatch


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'dci', 'therapeutic_class',
            'cost_price', 'selling_price',
            'current_stock', 'minimum_stock_level',
            'barcode', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du médicament'}),
            'dci': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dénomination Commune Internationale'}),
            'therapeutic_class': forms.Select(attrs={'class': 'form-control'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'current_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'minimum_stock_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Scanner ou saisir le code-barres'}),
        }


class ProductBatchForm(forms.ModelForm):
    class Meta:
        model = ProductBatch
        fields = ['product', 'batch_number', 'expiry_date', 'quantity', 'purchase_price', 'supplier']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro de lot'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du fournisseur'}),
        }
