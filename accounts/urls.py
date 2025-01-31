from django.urls import path
from .views import SignUpCreateView, delete_account, UserCartPageView, place_order, save_mop, add_mop, save_address, add_address, delete_address, update_cart_item
from django.contrib.auth import views as auth_views
from accounts import views


urlpatterns = [
    path('signup/', SignUpCreateView.as_view(), name = "signup"), 
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('delete_account/', delete_account, name="delete_account"),
    path("save-mop/", save_mop, name="save_mop"),
    path("add_mop/", add_mop, name="add_mop"),
    path("delete_mop/<int:payment_id>/", views.delete_mop, name="delete_mop"),
    path('cart/', UserCartPageView.as_view(), name='user-cart'),
    path('save-address/', save_address, name='save_address'),
    path('add_address/', add_address, name='add_address'),
    path('delete_address/<int:address_id>/', delete_address, name='delete_address'),
    path("update-cart-item/", update_cart_item, name="update_cart_item"),
    path("place-order/", place_order, name="place_order"),
]
