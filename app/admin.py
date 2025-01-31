from django.contrib import admin
from .models import UserAddress, UserPayment, Product, ProductInventory, Category, UserCart, UserPaymentDetails, UserOrderDetails, UserOrderedItems

admin.site.register(UserAddress)
admin.site.register(UserPayment)
admin.site.register(UserCart)
admin.site.register(Product)
admin.site.register(ProductInventory)
admin.site.register(Category)
admin.site.register(UserPaymentDetails)
admin.site.register(UserOrderDetails)
admin.site.register(UserOrderedItems)