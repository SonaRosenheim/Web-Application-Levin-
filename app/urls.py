from . import views
from django.urls import path, include
from .views import HomePageView, StorePageView, ProductPageView, ProductCreateView, CreateInventoryView, CreateCategoryView, ProductEditView, UserProfileView, add_to_cart, admin_authorization
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('store/', StorePageView.as_view(), name='store'),
    path('product/<int:pk>/', ProductPageView.as_view(), name='product-detail'),
    path('product/create/', ProductCreateView.as_view(), name='product-create'),
    path('create-inventory/', CreateInventoryView.as_view(), name='create_inventory'),
    path('create-category/', CreateCategoryView.as_view(), name='create_category'),
    path('product/edit', ProductEditView.as_view(), name='product-edit'),
    path('product/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('user-profile/', UserProfileView.as_view(), name='user-profile'),
    path("add-to-cart/", add_to_cart, name="add_to_cart"),
    path('admin-authorization/', admin_authorization, name='admin-authorization'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
