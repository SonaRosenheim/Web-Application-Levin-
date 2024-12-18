from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView
from django.views import View
from django.http import JsonResponse
from django.urls import reverse_lazy
from .models import Product, ProductInventory, Category
from .forms import ProductForm
from django.http import JsonResponse

class HomePageView(TemplateView):
    template_name = 'app/home.html'

class AboutPageView(TemplateView):
    template_name = 'app/about.html'

class ContactPageView(TemplateView):
    template_name = 'app/contact_us.html'

class StorePageView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'app/store.html'

class ProductPageView(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'app/product.html'

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'app/product_form.html'
    success_url = reverse_lazy('store')

    def form_valid(self, form):
        # Handle new category creation
        new_category_name = form.cleaned_data.get('new_category')
        if new_category_name:
            category, created = Category.objects.get_or_create(category_name=new_category_name)
            form.instance.category_prod = category

        # Handle new inventory creation
        new_inventory_quantity = form.cleaned_data.get('new_inventory_quantity')
        if new_inventory_quantity is not None:
            inventory = ProductInventory.objects.create(quantity=new_inventory_quantity)
            form.instance.inventory_prod = inventory

        # Save the product
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

class ProductEditView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'app/edit_product.html'

def edit_product(request, product_id):
    product = get_object_or_404(Product, prod_id=product_id)

    if request.method == 'POST':
        try:
            # Update product fields
            product.prod_name = request.POST.get('prod_name', product.prod_name)
            product.description = request.POST.get('description', product.description)
            product.prod_price = request.POST.get('prod_price', product.prod_price)

            # Handle product image update
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