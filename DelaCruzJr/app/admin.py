from django.contrib import admin
from .models import User, UserAddress, UserPayment, Product, ProductInventory, Category

admin.site.register(User)
admin.site.register(UserAddress)
admin.site.register(UserPayment)
admin.site.register(Product)
admin.site.register(ProductInventory)
admin.site.register(Category)