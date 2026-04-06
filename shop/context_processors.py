from .cart_db import DBCart

def cart_count(request):
    """Makes cart count available in all templates"""
    try:
        cart = DBCart(request)
        return {'cart_count': cart.get_total_items()}
    except Exception as e:
        return {'cart_count': 0}