import json
from django.forms import ValidationError
from django.http import JsonResponse
from django.views.generic import CreateView, TemplateView
from django.views.decorators.csrf import csrf_exempt
from app.models import UserAddress, UserCart, UserOrderDetails, UserOrderedItems, UserPayment, UserPaymentDetails
from .forms import CustomUserCreationForm
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages

class SignUpCreateView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login') 

    def form_valid(self, form):
        user = form.save()
        print(f'User created: {user.username}')
        login(self.request, user)
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
    
@login_required
def delete_account(request):
    user = request.user
    user.delete() 
    return redirect('login')  

class UserProfileView(TemplateView):
    template_name = 'user_profile.html' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
    
@login_required
def save_mop(request):
    """
    Save or update payment details submitted via the form.
    """
    if request.method == 'POST':
        user = request.user
        for payment in user.payments.all():
            payment_id = payment.payment_id
            payment_type = payment.payment_type

            if payment_type == "CC":
                payment.card_no = request.POST.get(f'card_no_{payment_id}', '')
                payment.expiry_date = request.POST.get(f'expiry_date_{payment_id}', None)
                payment.cvv = request.POST.get(f'cvv_{payment_id}', '')
                payment.name_on_card = request.POST.get(f'name_on_card_{payment_id}', '')

            elif payment_type in ["GC", "PM"]:
                payment.phone_number = request.POST.get(f'phone_number_{payment_id}', '')

            try:
                payment.clean() 
                payment.save()  
            except ValidationError as e:
                return render(request, 'user_profile.html', {'errors': e.messages, 'user': user})

        return redirect('user-profile')
    else:
        return redirect('user-profile')

@login_required
def add_mop(request):
    """
    Add a new payment method.
    """
    if request.method == 'POST':
        user = request.user
        payment_type = request.POST.get('payment_type')
        payment = UserPayment(user=user, payment_type=payment_type)

        if payment_type == 'CC':
            payment.card_no = request.POST.get('card_no')
            payment.expiry_date = request.POST.get('expiry_date')
            payment.cvv = request.POST.get('cvv')
            payment.name_on_card = request.POST.get('name_on_card')
        elif payment_type in ['GC', 'PM']:
            payment.phone_number = request.POST.get('phone_number')

        try:
            payment.clean()
            payment.save()
            return redirect('user-profile')
        except ValidationError as e:
            return render(request, 'user_profile.html', {'errors': e.messages, 'user': user})

    return render(request, 'user_profile.html')

@login_required
@csrf_exempt
def delete_mop(request, payment_id):
    """
    Delete a payment method using AJAX.
    """
    if request.method == 'POST':
        payment = get_object_or_404(UserPayment, pk=payment_id, user=request.user)
        payment.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required
def save_address(request):
    """
    Save or update user address details submitted via the form.
    """
    if request.method == 'POST':
        user = request.user
        for address in user.addresses.all():
            address_id = address.address_id

            address.address_line1 = request.POST.get(f'address_line1_{address_id}', '')
            address.address_line2 = request.POST.get(f'address_line2_{address_id}', '')
            address.postal_code = request.POST.get(f'postal_code_{address_id}', '')
            address.country = request.POST.get(f'country_{address_id}', '')

            address.save()
        return redirect('user-profile')
    return redirect('user-profile')

@login_required
def add_address(request):
    """
    Add a new address for the user.
    """
    if request.method == 'POST':
        user = request.user
        address = UserAddress(
            user=user,
            address_line1=request.POST.get('address_line1', ''),
            address_line2=request.POST.get('address_line2', ''),
            postal_code=request.POST.get('postal_code', ''),
            country=request.POST.get('country', '')
        )
        address.save()
        return redirect('user-profile')
    return redirect('user-profile')

@login_required
@csrf_exempt
def delete_address(request, address_id):
    """
    Delete an address using AJAX.
    """
    if request.method == 'POST':
        address = get_object_or_404(UserAddress, pk=address_id, user=request.user)
        address.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

class UserCartPageView(TemplateView):
    template_name = 'user_cart.html'

@csrf_exempt
def update_cart_item(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            cart_id = data.get("cart_id")
            action = data.get("action")

            cart_item = UserCart.objects.get(pk=cart_id)
            
            if action == "increase":
                cart_item.quantity += 1
                cart_item.save()
            elif action == "decrease":
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                else:
                    cart_item.delete()
            elif action == "remove":
                cart_item.delete()

            return JsonResponse({"success": True, "message": "Cart item updated."})
        except UserCart.DoesNotExist:
            return JsonResponse({"success": False, "message": "Cart item not found."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request method."})

def shipping_details(request):
    if not request.user.is_authenticated:
        return redirect('login')  

    user_addresses = UserAddress.objects.filter(user=request.user)
    user_payments = UserPayment.objects.filter(user=request.user)

    context = {
        'user': request.user,
        'user_addresses': user_addresses,
        'user_payments': user_payments,
    }
    return render(request, 'shipping_details.html', context)

def place_order(request):
    if request.method == "POST":
        user = request.user
        address_id = request.POST.get("address_id")
        payment_id = request.POST.get("payment_id")
        shipping_option = request.POST.get("shipping_option")

        print("Address ID:", address_id)
        print("Payment ID:", payment_id)
        print("Shipping Option:", shipping_option)

        if not address_id or not payment_id:
            messages.error(request, "Address or payment information is missing.")
            return redirect("user-cart")

        try:
            address = user.addresses.get(pk=address_id)
            payment = user.payments.get(pk=payment_id)

        except Exception as e:
            messages.error(request, f"Error fetching address or payment: {e}")
            return redirect("user-cart")

        cart_items = user.cart_items.all()
        if not cart_items.exists():
            messages.error(request, "Your cart is empty. Please add items to your cart.")
            return redirect("user-cart")

        subtotal = sum(item.total_price for item in cart_items)
        shipping_fee = 50 if shipping_option == "standard" else 100
        total = subtotal + shipping_fee

        try:
            with transaction.atomic():
                order = UserOrderDetails.objects.create(
                    user=user,
                    address=address,
                    payment=payment,
                    shipping_provider=shipping_option,
                    shipping_fee=shipping_fee,
                    subtotal=subtotal,
                    total=total,
                )
                print("Order Created:", order)

                payment_detail = UserPaymentDetails.objects.create(
                    order=order,
                    payment_method=payment,
                    payment_status="pending",
                )
                print("Payment Detail Created:", payment_detail)

                payment_response = {"success": True}
                print("Payment Response:", payment_response)

                if payment_response["success"]:
                    payment_detail.payment_status = "completed"
                    payment_detail.save()
                    print("Payment Completed")
                else:
                    raise ValueError("Payment failed. Please try again.")

                for cart_item in cart_items:
                    product = cart_item.product

                    if product.inventory_prod.quantity < cart_item.quantity:
                        raise ValueError(
                            f"Not enough stock for {product.prod_name}. Available: {product.inventory_prod.quantity}"
                        )

                    UserOrderedItems.objects.create(
                        order=order,
                        product=product,
                        quantity=cart_item.quantity,
                        price_at_purchase=product.prod_price,
                    )

                    product.inventory_prod.quantity -= cart_item.quantity
                    product.inventory_prod.save()

                cart_items.delete()

                messages.success(request, "Order placed successfully.")

        except ValueError as e:
            messages.error(request, str(e))
            print("Error:", e)
            return redirect("user-cart")
        except Exception as e:
            messages.error(request, f"Unexpected error occurred: {e}")
            print("Unexpected Error:", e)
            return redirect("user-cart")

        return redirect("user-cart")
        