from .models import Cart, CartItem
from django.conf import settings

class DBCart:
    def __init__(self, request):
        self.request = request
        self.user = request.user if request.user.is_authenticated else None
        self.session_key = request.session.session_key
        if not self.session_key and not self.user:
            request.session.create()
            self.session_key = request.session.session_key
        self.cart = self._get_cart()
    
    def _get_cart(self):
        if self.user:
            cart, _ = Cart.objects.get_or_create(user=self.user)
            if self.session_key:
                session_cart = Cart.objects.filter(session_key=self.session_key).first()
                if session_cart and session_cart != cart:
                    for item in session_cart.items.all():
                        target = cart.items.filter(product=item.product).first()
                        if target:
                            target.quantity += item.quantity
                            target.save()
                        else:
                            item.cart = cart
                            item.save()
                    session_cart.delete()
            return cart
        return Cart.objects.get_or_create(session_key=self.session_key)[0]
    
    def add(self, product, quantity=1):
        item, created = self.cart.items.get_or_create(product=product, defaults={'quantity': quantity})
        if not created:
            item.quantity += quantity
            item.save()
    
    def remove(self, product):
        self.cart.items.filter(product=product).delete()
    
    def update_quantity(self, product, quantity):
        if quantity <= 0:
            self.remove(product)
        else:
            item, _ = self.cart.items.get_or_create(product=product, defaults={'quantity': quantity})
            if item.quantity != quantity:
                item.quantity = quantity
                item.save()
    
    def __iter__(self):
        for item in self.cart.items.all():
            yield {
                'product': item.product, 
                'quantity': item.quantity, 
                'price': item.product.price, 
                'total_price': item.get_total_price(), 
                'id': item.product.id
            }
    
    def __len__(self):
        return self.cart.get_total_items()
    
    def get_subtotal(self):
        return self.cart.get_total_price()
    
    def get_delivery_charge(self):
        # Check if force free delivery is enabled
        if getattr(settings, 'FORCE_FREE_DELIVERY', False):
            return 0
        
        free_shipping_threshold = getattr(settings, 'FREE_SHIPPING_THRESHOLD', 800)
        delivery_charge = getattr(settings, 'DELIVERY_CHARGE', 75)
        
        return 0 if self.get_subtotal() >= free_shipping_threshold else delivery_charge
    
    def get_grand_total(self):
        return self.get_subtotal() + self.get_delivery_charge()
    
    def get_total_items(self):
        return self.cart.get_total_items()
    
    def clear(self):
        self.cart.items.all().delete()