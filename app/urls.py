from . import views
from django.urls import path
from .views import HomePageView, AboutPageView, StorePageView, ContactPageView, ProductPageView, ProductCreateView, CreateInventoryView, CreateCategoryView, ProductEditView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('about/', AboutPageView.as_view(), name='about'),
    path('store/', StorePageView.as_view(), name='store'),
    path('contact-us/', ContactPageView.as_view(), name='contact-us'),
    path('product/<int:pk>/', ProductPageView.as_view(), name='product-detail'),
    path('product/create/', ProductCreateView.as_view(), name='product-create'),
    path('create-inventory/', CreateInventoryView.as_view(), name='create_inventory'),
    path('create-category/', CreateCategoryView.as_view(), name='create_category'),
    path('product/edit', ProductEditView.as_view(), name='product-edit'),
    path('product/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
