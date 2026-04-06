from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from django.conf import settings
from django.urls import reverse
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from .models import Product, Order, OrderItem, UserProfile, Cart
from .cart_db import DBCart
from .forms import CheckoutForm, UserRegistrationForm, UserProfileForm
import razorpay
import re

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def validate_phone_number(phone):
    return re.match(r'^[6-9]\d{9}$', phone) is not None


def generate_unique_username(email, phone):
    base = email.split('@')[0].lower().replace(' ', '')
    base = ''.join(ch for ch in base if ch.isalnum()) or f"user{phone[-4:]}"
    candidate = base
    counter = 1

    while User.objects.filter(username=candidate).exists():
        candidate = f"{base}{counter}"
        counter += 1

    return candidate


def merge_guest_cart_to_user(request, user):
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key
    guest_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
    user_cart, _ = Cart.objects.get_or_create(user=user)

    if not guest_cart:
        return

    for guest_item in guest_cart.items.all():
        user_item = user_cart.items.filter(product=guest_item.product).first()
        if user_item:
            user_item.quantity += guest_item.quantity
            user_item.save()
            guest_item.delete()
        else:
            guest_item.cart = user_cart
            guest_item.save()

    guest_cart.delete()


def format_order_items_for_email(order):
    rows_html = ""
    rows_text = []

    for item in order.items.all():
        line_total = item.get_total()
        rows_html += f"""
            <tr>
                <td style="padding:10px;border:1px solid #e5e7eb;">{item.product.name}</td>
                <td style="padding:10px;border:1px solid #e5e7eb;text-align:center;">{item.quantity}</td>
                <td style="padding:10px;border:1px solid #e5e7eb;text-align:right;">Rs. {item.price:.2f}</td>
                <td style="padding:10px;border:1px solid #e5e7eb;text-align:right;">Rs. {line_total:.2f}</td>
            </tr>
        """
        rows_text.append(
            f"{item.product.name} | Qty: {item.quantity} | Price: Rs. {item.price:.2f} | Total: Rs. {line_total:.2f}"
        )

    return rows_html, "\n".join(rows_text)


def send_order_emails(order):
    rows_html, rows_text = format_order_items_for_email(order)
    grand_total = order.get_grand_total()

    customer_subject = f"Order Confirmation - Dr Naturals Order #{order.id}"
    customer_html = f"""
    <div style="font-family:Arial,sans-serif;max-width:700px;margin:0 auto;color:#1f2937;">
        <div style="background:#4C7840;color:white;padding:24px;border-radius:16px 16px 0 0;">
            <h2 style="margin:0;">Thank you for your order, {order.name}!</h2>
            <p style="margin:8px 0 0;">Your payment was successful and your order has been received.</p>
        </div>
        <div style="border:1px solid #e5e7eb;border-top:0;padding:24px;border-radius:0 0 16px 16px;">
            <h3 style="margin-top:0;">Order Details</h3>
            <p><strong>Order ID:</strong> #{order.id}</p>
            <p><strong>Payment Status:</strong> {order.payment_status.title()}</p>
            <p><strong>Order Status:</strong> {order.status.title()}</p>

            <h3>Customer Information</h3>
            <p><strong>Name:</strong> {order.name}</p>
            <p><strong>Email:</strong> {order.email}</p>
            <p><strong>Phone:</strong> {order.phone}</p>

            <h3>Shipping Address</h3>
            <p>{order.address}<br>{order.city}, {order.state} - {order.pincode}</p>

            <h3>Items Ordered</h3>
            <table style="width:100%;border-collapse:collapse;">
                <thead><tr><th>Product</th><th>Qty</th><th>Price</th><th>Total</th></tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
            <div style="margin-top:20px;padding:16px;background:#f8fafc;">
                <p><strong>Subtotal:</strong> Rs. {order.total_amount:.2f}</p>
                <p><strong>Delivery Charge:</strong> Rs. {order.delivery_charge:.2f}</p>
                <p style="font-size:18px;color:#4C7840;"><strong>Grand Total:</strong> Rs. {grand_total:.2f}</p>
            </div>
            <p>Regards,<br><strong>Dr Naturals</strong></p>
        </div>
    </div>
    """

    customer_text = f"Order #{order.id} confirmed. Total: Rs. {grand_total:.2f}"

    try:
        customer_email = EmailMultiAlternatives(
            subject=customer_subject,
            body=customer_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email],
        )
        customer_email.attach_alternative(customer_html, "text/html")
        customer_email.send(fail_silently=False)
    except Exception as e:
        print(f"Email error: {e}")


def index(request):
    products = Product.objects.all()
    most_popular = list(Product.objects.filter(is_popular=True).order_by('-created_at')[:6])
    featured_products = list(Product.objects.filter(featured=True).order_by('-created_at')[:12])

    if len(featured_products) < 12:
        remaining = 12 - len(featured_products)
        extra_products = Product.objects.filter(featured=False, is_popular=False).exclude(
            id__in=[p.id for p in featured_products]
        )[:remaining]
        featured_products += list(extra_products)

    return render(request, 'index.html', {
        'most_popular': most_popular,
        'featured_products': featured_products,
        'products': products,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    product_images = product.product_images.all()
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    return render(request, 'product_detail.html', {
        'product': product,
        'product_images': product_images,
        'related_products': related_products
    })


def haircare(request):
    return render(request, 'haircare.html', {'products': Product.objects.filter(category='Hair')})


def skincare(request):
    return render(request, 'skincare.html', {'products': Product.objects.filter(category='Skin')})


def medicines(request):
    return render(request, 'medicines.html', {'products': Product.objects.filter(category='Medicines')})


def skin_analyzer(request):
    return render(request, 'skin_analyzer.html')


def add_to_cart(request, product_id):
    if request.method != 'POST':
        return redirect('index')

    cart = DBCart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    existing_item = cart.cart.items.filter(product=product).first()
    new_quantity = (existing_item.quantity + quantity) if existing_item else quantity

    if new_quantity < 2:
        error_msg = f'Minimum quantity for {product.name} is 2!'
        if is_ajax:
            return JsonResponse({'error': error_msg}, status=400)
        messages.error(request, error_msg)
        return redirect(request.META.get('HTTP_REFERER', 'index'))

    cart.add(product, quantity)

    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart!',
            'cart_count': cart.get_total_items()
        })

    messages.success(request, f'{product.name} added to cart!')
    if request.POST.get('next') == 'checkout':
        return redirect('checkout')
    return redirect(request.META.get('HTTP_REFERER', 'index'))


def cart_view(request):
    cart = DBCart(request)
    subtotal = cart.get_subtotal()
    delivery_charge = cart.get_delivery_charge()
    grand_total = subtotal + delivery_charge

    return render(request, 'cart.html', {
        'cart': cart,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'grand_total': grand_total,
    })


@require_POST
def remove_from_cart(request, product_id):
    cart = DBCart(request)
    cart.remove(get_object_or_404(Product, id=product_id))
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')


@require_POST
def update_cart_quantity(request, product_id):
    cart = DBCart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    if quantity < 2:
        messages.error(request, f'Minimum quantity for {product.name} is 2!')
        return redirect('cart')

    cart.update_quantity(product, quantity)
    messages.success(request, 'Cart updated!')
    return redirect('cart')


def checkout(request):
    cart = DBCart(request)
    if len(cart) == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('index')

    subtotal = cart.get_subtotal()
    delivery_charge = cart.get_delivery_charge()
    grand_total = subtotal + delivery_charge

    # ========== TEST MODE: FORCE ₹1 PAYMENT ==========
    # Set TEST_MODE = False when going live
    TEST_MODE = True
    if TEST_MODE:
        grand_total = 1
        delivery_charge = 0
        subtotal = 1
        messages.info(request, '🔧 TEST MODE: Payment amount is ₹1 (for testing only)')
        print(f"TEST MODE ACTIVE: Payment amount forced to ₹{grand_total}")
    # =================================================

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            print(f"Creating order with total: ₹{grand_total}")
            
            # Create order with pending status
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated and not request.user.is_staff else None,
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                alt_phone=form.cleaned_data.get('alt_phone', ''),
                address=form.cleaned_data['address'],
                landmark=form.cleaned_data.get('landmark', ''),
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                pincode=form.cleaned_data['pincode'],
                order_notes=form.cleaned_data.get('order_notes', ''),
                total_amount=subtotal,
                delivery_charge=delivery_charge,
                payment_status='pending',
                status='pending'
            )

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['price']
                )

            try:
                amount_paise = int(grand_total * 100)
                if amount_paise < 100:
                    amount_paise = 100
                
                print(f"Creating Razorpay order: ₹{grand_total} ({amount_paise} paise)")
                
                rzp_order = client.order.create({
                    'amount': amount_paise,
                    'currency': 'INR',
                    'payment_capture': 1,
                    'notes': {'order_id': order.id}
                })
                order.razorpay_order_id = rzp_order['id']
                order.save()
                
                print(f"Razorpay order created: {rzp_order['id']}")

                return render(request, 'payment.html', {
                    'order': order,
                    'razorpay_order_id': rzp_order['id'],
                    'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                    'amount': grand_total,
                    'callback_url': request.build_absolute_uri(reverse('payment_callback'))
                })
            except Exception as e:
                print(f"Payment initialization error: {e}")
                order.delete()
                messages.error(request, f'Payment error: {str(e)}')
                return redirect('cart')
        else:
            print(f"Form errors: {form.errors}")
            messages.error(request, 'Please correct the errors below.')
    else:
        initial_data = {}
        if request.user.is_authenticated and not request.user.is_staff:
            profile_instance, _ = UserProfile.objects.get_or_create(user=request.user)
            initial_data = {
                'name': f"{request.user.first_name} {request.user.last_name}".strip(),
                'email': request.user.email,
                'phone': profile_instance.phone,
                'address': profile_instance.address,
                'city': profile_instance.city,
                'state': profile_instance.state,
                'pincode': profile_instance.pincode,
            }
        form = CheckoutForm(initial=initial_data)

    return render(request, 'checkout.html', {
        'cart': cart,
        'form': form,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'grand_total': grand_total,
    })


@csrf_exempt
def payment_callback(request):
    """Handle Razorpay payment callback"""
    print(f"=== PAYMENT CALLBACK RECEIVED ===")
    print(f"Request method: {request.method}")
    
    if request.method == 'POST':
        rzp_order_id = request.POST.get('razorpay_order_id', '')
        rzp_payment_id = request.POST.get('razorpay_payment_id', '')
        rzp_signature = request.POST.get('razorpay_signature', '')
        
        print(f"Order ID: {rzp_order_id}")
        print(f"Payment ID: {rzp_payment_id}")

        if not rzp_order_id or not rzp_payment_id:
            messages.error(request, 'Payment verification failed: Missing payment details.')
            return redirect('cart')

        try:
            order = Order.objects.get(razorpay_order_id=rzp_order_id)
            print(f"Order found: #{order.id}")
            
            # Verify payment signature
            try:
                client.utility.verify_payment_signature({
                    'razorpay_order_id': rzp_order_id,
                    'razorpay_payment_id': rzp_payment_id,
                    'razorpay_signature': rzp_signature
                })
                print("Signature verified successfully!")
            except Exception as sig_err:
                print(f"Signature error: {sig_err}")
                order.payment_status = 'failed'
                order.save()
                messages.error(request, 'Payment verification failed')
                return redirect('cart')

            # Update order
            order.razorpay_payment_id = rzp_payment_id
            order.razorpay_signature = rzp_signature
            order.payment_status = 'success'
            order.status = 'processing'
            order.save()
            print(f"Order #{order.id} updated to SUCCESS")

            # Update stock
            for item in order.items.all():
                item.product.stock -= item.quantity
                item.product.save()
                print(f"Stock updated for {item.product.name}")

            # Clear cart
            try:
                DBCart(request).clear()
                print("Cart cleared")
            except Exception as e:
                print(f"Cart clear error: {e}")

            # Send emails
            try:
                send_order_emails(order)
                print("Emails sent")
            except Exception as e:
                print(f"Email error: {e}")

            messages.success(request, f'✅ Payment successful! Order #{order.id} confirmed.')
            return redirect('thank_you', order_id=order.id)
            
        except Order.DoesNotExist:
            print(f"Order not found: {rzp_order_id}")
            messages.error(request, 'Order not found')
            return redirect('cart')
        except Exception as e:
            print(f"Error: {e}")
            messages.error(request, f'Payment error: {str(e)}')
            return redirect('cart')
    
    print("Not a POST request")
    return redirect('index')


def thank_you(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'thank_you.html', {'order': order})


@ensure_csrf_cookie
def register(request):
    if request.user.is_authenticated and not request.user.is_staff:
        return redirect('index')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']

            user = form.save(commit=False)
            user.username = generate_unique_username(email, phone)
            user.email = email
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data.get('last_name', '')
            user.is_active = True
            user.is_staff = False
            user.is_superuser = False
            user.save()

            UserProfile.objects.create(user=user, phone=phone)

            login(request, user)
            merge_guest_cart_to_user(request, user)
            messages.success(request, f'Welcome {user.first_name}!')
            return redirect('index')

        messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


@ensure_csrf_cookie
@csrf_protect
def user_login(request):
    if request.user.is_authenticated and not request.user.is_staff and not request.user.is_superuser:
        return redirect('index')

    if request.method == 'POST':
        login_input = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me')
        next_url = request.POST.get('next') or request.GET.get('next') or 'index'

        try:
            user_obj = User.objects.get(email__iexact=login_input)
            username = user_obj.username
        except User.DoesNotExist:
            username = login_input

        user = authenticate(request, username=username, password=password)

        if not user or user.is_staff or user.is_superuser:
            messages.error(request, 'Invalid email or password.')
            return render(request, 'login.html')

        login(request, user)
        merge_guest_cart_to_user(request, user)

        if not remember_me:
            request.session.set_expiry(0)

        messages.success(request, f'Welcome back, {user.first_name or user.username}!')
        return redirect(next_url)

    return render(request, 'login.html')


@require_POST
@csrf_protect
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('index')


@login_required
def profile(request):
    if request.user.is_staff or request.user.is_superuser:
        logout(request)
        messages.error(request, 'Invalid account access.')
        return redirect('login')

    profile_instance, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile_instance)

    return render(request, 'profile.html', {'form': form, 'user': request.user})