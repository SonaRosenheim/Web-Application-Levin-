from django import forms
from .models import Product, ProductInventory, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['prod_name', 'prod_photo', 'description', 'prod_price', 'category_prod', 'inventory_prod']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['category_prod'].queryset = Category.objects.all()
        self.fields['category_prod'].empty_label = "Select Category"
        self.fields['category_prod'].widget.attrs.update({'class': 'dropdown'})
        self.fields['inventory_prod'].queryset = ProductInventory.objects.filter(
            product__isnull=True
        )
        self.fields['inventory_prod'].empty_label = "Select Product Inventory"
        self.fields['inventory_prod'].widget.attrs.update({'class': 'dropdown'})
        self.fields['prod_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Product Name'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Description'})
        self.fields['prod_price'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Price'})
        self.fields['prod_photo'].widget.attrs.update({'class': 'form-control-file'})

    new_category = forms.CharField(
        max_length=60, required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'New Category Name', 'class': 'form-control'})
    )
    new_inventory_quantity = forms.IntegerField(
        required=False, 
        widget=forms.NumberInput(attrs={'placeholder': 'New Inventory Quantity', 'class': 'form-control'})
    )