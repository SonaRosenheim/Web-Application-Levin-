from django.db import models
from django.contrib.auth.models import User 

class UserAddress(models.Model):
    address_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_line1 = models.CharField(max_length=120)
    address_line2 = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=15)
    country = models.CharField(max_length=60)
    def __str__(self):
        return self.user.email

class UserPayment(models.Model):
    payment_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    payment_type_choices = [
        ("CC", "Credit Card"),
        ("GC", "GCash"),
        ("PM", "PayMaya"),
    ]
    payment_type = models.CharField(max_length=2, choices=payment_type_choices)
    
    card_no = models.CharField(null=True, blank=True, max_length=16)
    expiry_date = models.DateField(null=True, blank=True)
    cvv = models.CharField(null=True, blank=True, max_length=3)
    name_on_card = models.CharField(null=True, blank=True, max_length=64)
    
    phone_number = models.CharField(null=True, blank=True, max_length=15)

    is_default = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.user.email} - {self.get_payment_type_display()}"

    def clean(self):
        """
        Validate the fields based on the payment type.
        """
        from django.core.exceptions import ValidationError
        
        if self.payment_type in ['GC', 'PM'] and not self.phone_number:
            raise ValidationError("Phone number is required for e-wallet payments.")
        
        if self.payment_type == 'CC' and not (self.card_no and self.expiry_date and self.cvv):
            raise ValidationError("All credit card details must be filled.")

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
    
class UserCart(models.Model):
    cart_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user.username}'s Cart - {self.product.prod_name} x {self.quantity}"

    @property
    def total_price(self):
        return self.product.prod_price * self.quantity
    
class UserOrderDetails(models.Model):
    order_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    address = models.ForeignKey(UserAddress, on_delete=models.CASCADE, related_name='order_addresses')
    payment = models.ForeignKey(UserPayment, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_payments')
    shipping_provider_choices = [
        ('standard', 'Standard Delivery'),
        ('express', 'Express Delivery'),
    ]
    shipping_provider = models.CharField(max_length=10, choices=shipping_provider_choices, default='standard')
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    status_choices = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='pending')

    def __str__(self):
        return f"Order {self.order_id} - {self.user.username}"

    def calculate_total(self):
        return self.subtotal + self.shipping_fee

class UserPaymentDetails(models.Model):
    payment_detail_id = models.BigAutoField(primary_key=True)
    order = models.OneToOneField(UserOrderDetails, on_delete=models.CASCADE, related_name='payment_detail')
    payment_method = models.ForeignKey(UserPayment, on_delete=models.SET_NULL, null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status_choices = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    payment_status = models.CharField(max_length=10, choices=payment_status_choices, default='pending')

    def __str__(self):
        return f"Payment for Order {self.order.order_id} - {self.payment_status}"

class UserOrderedItems(models.Model):
    ordered_item_id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(UserOrderDetails, on_delete=models.CASCADE, related_name='ordered_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order {self.order.order_id} - {self.product.prod_name} x {self.quantity}"
