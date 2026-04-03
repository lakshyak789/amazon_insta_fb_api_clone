from rest_framework import serializers
import uuid
from .models import (
    Address, Category, Product, ProductImage, Inventory,
    Cart, CartItem, Wishlist, WishlistItem,
    Order, OrderItem, Payment, Review, AuditLog
)


class PriceSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    currency = serializers.CharField()


class RatingSerializer(serializers.Serializer):
    avg = serializers.DecimalField(max_digits=2, decimal_places=1)
    count = serializers.IntegerField()


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'url', 'is_primary')


class CategorySerializer(serializers.ModelSerializer):
    parent_id = serializers.UUIDField(source='parent.id', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'parent_id', 'parent_name')


class CategoryTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'children')

    def get_children(self, obj):
        children = obj.children.all()
        return CategoryTreeSerializer(children, many=True).data


class ProductCreateSerializer(serializers.ModelSerializer):
    price_cents = serializers.IntegerField()
    category_id = serializers.UUIDField(source='category.id', required=False)

    class Meta:
        model = Product
        fields = ('id', 'sku', 'title', 'slug', 'description', 'brand',
                  'price_cents', 'category_id')

    def create(self, validated_data):
        if not validated_data.get('sku'):
            validated_data['sku'] = f"SKU-{uuid.uuid4().hex[:8].upper()}"
        validated_data['currency'] = 'USD'
        return super().create(validated_data)


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'sku', 'title', 'slug', 'description', 'brand',
                  'price', 'category', 'images', 'rating')

    def get_price(self, obj):
        return {'amount': obj.price_cents, 'currency': obj.currency}

    def get_rating(self, obj):
        return {'avg': float(obj.avg_rating), 'count': obj.review_count}


class ProductListSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    category = serializers.CharField(source='category.name', read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'sku', 'title', 'slug', 'price', 'category', 'rating')

    def get_price(self, obj):
        return {'amount': obj.price_cents, 'currency': obj.currency}

    def get_rating(self, obj):
        return {'avg': float(obj.avg_rating), 'count': obj.review_count}


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('id', 'label', 'full_name', 'line1', 'line2', 'city',
                  'state', 'postal_code', 'country', 'phone', 'is_default')


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ('id', 'product_id', 'quantity', 'reserved', 'warehouse')


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'quantity', 'price')

    def get_price(self, obj):
        return {'amount': obj.price_cents, 'currency': obj.currency}


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True, source='am_items')
    totals = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'items', 'totals')

    def get_totals(self, obj):
        subtotal = sum(item.price_cents * item.quantity for item in obj.am_items.all())
        shipping = 499
        tax = int(subtotal * 0.08)
        total = subtotal + shipping + tax
        return {
            'subtotal': subtotal,
            'shipping': shipping,
            'tax': tax,
            'grandTotal': total,
            'currency': 'USD'
        }


class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = WishlistItem
        fields = ('id', 'product', 'created_at')


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('product_id', 'title', 'price', 'quantity', 'currency')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['price'] = {'amount': instance.price_cents, 'currency': instance.currency}
        return ret


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    amounts = serializers.SerializerMethodField()
    address = AddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'status', 'amounts', 'items', 'address', 'placed_at')

    def get_amounts(self, obj):
        return {
            'subtotal': obj.subtotal_cents,
            'shipping': obj.shipping_cents,
            'tax': obj.tax_cents,
            'total': obj.total_cents,
            'currency': obj.currency
        }


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('id', 'provider', 'status', 'amount_cents', 'currency', 'created_at')


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('id', 'product_id', 'user_id', 'rating', 'title', 'body',
                  'helpful_count', 'created_at')


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ('id', 'user_id', 'action', 'target_type', 'target_id', 'meta', 'created_at')


class CreateOrderSerializer(serializers.Serializer):
    addressId = serializers.UUIDField()
    paymentProvider = serializers.CharField()
