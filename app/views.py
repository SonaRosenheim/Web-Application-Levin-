import json
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView
from django.views import View
from django.urls import reverse_lazy
from .models import Product, ProductInventory, Category, UserCart
from .forms import ProductForm
from django.http import JsonResponse

class HomePageView(TemplateView):
    template_name = 'app/home.html'

class StorePageView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'app/store.html'

class ProductPageView(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'app/product.html'

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class ProductCreateView(StaffRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'app/product_form.html'
    success_url = reverse_lazy('store')

    def form_valid(self, form):
        new_category_name = form.cleaned_data.get('new_category')
        if new_category_name:
            category, created = Category.objects.get_or_create(category_name=new_category_name)
            form.instance.category_prod = category

        new_inventory_quantity = form.cleaned_data.get('new_inventory_quantity')
        if new_inventory_quantity is not None:
            inventory = ProductInventory.objects.create(quantity=new_inventory_quantity)
            form.instance.inventory_prod = inventory

        response = super().form_valid(form)

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'message': 'Product created successfully!'}, status=200)
        return response

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'errors': form.errors}, status=400)
        return super().form_invalid(form)
    
@method_decorator(csrf_exempt, name='dispatch') 
class CreateInventoryView(View):
    def post(self, request, *args, **kwargs):
        quantity = request.POST.get('quantity')

        if not quantity or not quantity.isdigit():
            return JsonResponse({'error': 'Invalid quantity.'}, status=400)

        inventory = ProductInventory.objects.create(quantity=int(quantity))
        return JsonResponse({'id': inventory.inventory_id, 'quantity': inventory.quantity})

@method_decorator(csrf_exempt, name='dispatch')
class CreateCategoryView(View):
    def post(self, request, *args, **kwargs):
        category_name = request.POST.get('category_name')

        if not category_name:
            return JsonResponse({'error': 'Category name cannot be empty.'}, status=400)

        if Category.objects.filter(category_name=category_name).exists():
            return JsonResponse({'error': 'Category already exists.'}, status=400)

        category = Category.objects.create(category_name=category_name)
        return JsonResponse({'id': category.category_id, 'name': category.category_name})

class ProductEditView(StaffRequiredMixin, ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'app/edit_product.html'

def edit_product(request, product_id):
    product = get_object_or_404(Product, prod_id=product_id)

    if request.method == 'POST':
        try:
            product.prod_name = request.POST.get('prod_name', product.prod_name)
            product.description = request.POST.get('description', product.description)
            product.prod_price = request.POST.get('prod_price', product.prod_price)

            if 'prod_photo' in request.FILES:
                product.prod_photo = request.FILES['prod_photo']

            product.save()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
def delete_product(request, product_id):
    if request.method in ['POST', 'DELETE']:
        product = get_object_or_404(Product, prod_id=product_id)
        product.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=405)

class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'user_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        orders = user.orders.all()  
        to_pay = orders.filter(status="pending").prefetch_related("ordered_items__product")
        to_ship = orders.filter(status="processing").prefetch_related("ordered_items__product")
        to_receive = orders.filter(status="shipped").prefetch_related("ordered_items__product")
        delivered = orders.filter(status="delivered").prefetch_related("ordered_items__product")

        for order in to_pay:
            for item in order.ordered_items.all():
                item.total_price = item.quantity * item.product.prod_price

        context.update({
            "to_pay": to_pay,
            "to_ship": to_ship,
            "to_receive": to_receive,
            "delivered": delivered,
        })

        return context

@csrf_exempt
def add_to_cart(request):
    if request.method == "POST":
        data = json.loads(request.body)
        product_id = data.get("product_id")
        user = request.user

        if user.is_authenticated:
            try:
                product = Product.objects.get(pk=product_id)
                cart_item, created = UserCart.objects.get_or_create(user=user, product=product)
                if not created:
                    cart_item.quantity += 1
                cart_item.save()
                return JsonResponse({"success": True, "message": "Product added to cart."})
            except Product.DoesNotExist:
                return JsonResponse({"success": False, "message": "Product not found."})
        else:
            return JsonResponse({"success": False, "message": "User not authenticated."})
    return JsonResponse({"success": False, "message": "Invalid request method."})

@login_required
def admin_authorization(request):
    if request.method == "POST":
        admin_password = request.POST.get("admin_password")
        fixed_password = settings.ADMIN_AUTH_PASSWORD

        if admin_password == fixed_password:
            user = request.user
            user.is_staff = True
            user.is_superuser = True
            user.save()
            messages.success(request, "You are now an admin!")
            return redirect("user-profile")  
        else:
            messages.error(request, "Invalid password. Please try again.")
            return redirect("user-profile") 