from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('haircare/', views.haircare, name='haircare'),
    path('skincare/', views.skincare, name='skincare'),
    path('medicines/', views.medicines, name='medicines'),
    path('skin-analyzer/', views.skin_analyzer, name='skin_analyzer'),

    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:product_id>/', views.update_cart_quantity, name='update_cart_quantity'),

    path('checkout/', views.checkout, name='checkout'),
    path('payment-callback/', views.payment_callback, name='payment_callback'),
    path('thank-you/<int:order_id>/', views.thank_you, name='thank_you'),

    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
]
