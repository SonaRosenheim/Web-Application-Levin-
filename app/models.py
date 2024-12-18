from django.db import models

class User(models.Model):
    user_id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    email_address = models.EmailField(max_length=60)
    password = models.CharField(max_length=30)
    phone_number = models.IntegerField(null=False)
    def __str__(self):
        return self.email_address   

class UserAddress(models.Model):
    address_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address_line1 = models.CharField(max_length=120)
    address_line2 = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=15)
    country = models.CharField(max_length=60)
    def __str__(self):
        return self.user.email_address

class UserPayment(models.Model):
    payment_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_type_choices = [
        ("CC", "Credit Card"),
        ("PP", "PayPal"),
        ("GC", "GCash"),
        ("PM", "PayMaya"),
        ("BA", "Bank Account"),
    ]
    payment_type = models.CharField(max_length=2, choices=payment_type_choices)
    acc_no = models.CharField(max_length=20)
    provider = models.CharField(max_length=50)
    expiry_date = models.DateField(null=True, blank=True)
    is_default = models.BooleanField(default=False)
    def __str__(self):
        return self.user.email_address

class Category(models.Model):
    category_id = models.BigAutoField(primary_key=True, unique=True)
    category_name = models.CharField(max_length=60)
    def __str__(self):
        return self.category_name

class ProductInventory(models.Model):
    inventory_id = models.BigAutoField(primary_key=True)
    quantity = models.IntegerField()
    def __str__(self):
        return f"Inventory ID: {self.inventory_id}, Quantity: {self.quantity}"

class Product(models.Model):
    prod_id = models.BigAutoField(primary_key=True)
    prod_photo = models.ImageField(null=True, blank=True,upload_to="media/products/")
    prod_name = models.CharField(max_length=60, unique=True )
    description = models.TextField()
    prod_price = models.DecimalField(max_digits=10, decimal_places=2)
    category_prod = models.ForeignKey(Category, on_delete=models.CASCADE)
    inventory_prod = models.OneToOneField(ProductInventory, on_delete=models.CASCADE)
    def __str__(self):
        return self.prod_name