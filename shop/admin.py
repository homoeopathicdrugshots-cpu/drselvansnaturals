from django.contrib import admin
from django.utils.html import format_html
from .models import Product, ProductImage, Order, OrderItem, UserProfile, Cart, CartItem


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ['image', 'caption', 'is_main', 'order']


class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'quantity_label', 'original_price', 'price', 'discount_percent',
        'stock', 'featured', 'is_popular', 'image_preview', 'created_at'
    ]
    list_filter = ['category', 'featured', 'is_popular', 'created_at']
    search_fields = ['name', 'description', 'short_desc', 'benefits', 'dosage', 'usage']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['quantity_label', 'original_price', 'price', 'discount_percent', 'stock', 'featured', 'is_popular']
    list_per_page = 20
    inlines = [ProductImageInline]

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name', 'slug', 'category', 'quantity_label',
                'original_price', 'price', 'discount_percent',
                'short_desc', 'description'
            )
        }),
        ('Product Content', {
            'fields': ('benefits', 'dosage', 'usage'),
            'description': 'Benefits: comma separated. Dosage for medicines. Usage for skincare, haircare and bodycare.'
        }),
        ('Images', {
            'fields': ('image',),
            'classes': ('wide',)
        }),
        ('Visibility', {
            'fields': ('featured', 'is_popular', 'stock', 'tags'),
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:8px;object-fit:cover;" />',
                obj.image.url
            )
        return "No Image"
    image_preview.short_description = 'Image'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['price', 'get_total']

    def get_total(self, obj):
        return obj.price * obj.quantity
    get_total.short_description = 'Total'


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'phone', 'city', 'pincode',
        'total_amount', 'delivery_charge', 'grand_total',
        'payment_status', 'status', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'created_at', 'state', 'city']
    search_fields = ['name', 'email', 'phone', 'address', 'razorpay_order_id', 'razorpay_payment_id']
    readonly_fields = ['razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'created_at']
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('Customer', {
            'fields': ('user', 'name', 'email', 'phone', 'alt_phone'),
        }),
        ('Shipping Address', {
            'fields': ('address', 'landmark', 'city', 'state', 'pincode'),
        }),
        ('Order', {
            'fields': ('status', 'payment_status', 'order_notes', 'created_at'),
        }),
        ('Totals', {
            'fields': ('total_amount', 'delivery_charge'),
        }),
        ('Razorpay', {
            'fields': ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature'),
        }),
    )

    @admin.display(description='Grand Total')
    def grand_total(self, obj):
        try:
            return obj.total_amount + obj.delivery_charge
        except Exception:
            return obj.get_grand_total()


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['get_total_price']

    def get_total_price(self, obj):
        return f"₹{obj.get_total_price()}"
    get_total_price.short_description = 'Total'


class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'get_total_items', 'get_total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'session_key']
    inlines = [CartItemInline]
    readonly_fields = ['get_total_items', 'get_total_price', 'created_at']

    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Items'

    def get_total_price(self, obj):
        return f"₹{obj.get_total_price()}"
    get_total_price.short_description = 'Total'


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'state', 'created_at']
    list_filter = ['city', 'state']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at']


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_preview', 'is_main', 'order', 'created_at']
    list_filter = ['is_main', 'product__category']
    search_fields = ['product__name', 'caption']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:8px;object-fit:cover;" />',
                obj.image.url
            )
        return "No Image"
    image_preview.short_description = 'Preview'


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem)
