from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.shortcuts import get_object_or_404

from core.pagination import StandardResultsSetPagination
from .models import (
    Address, Category, Product, ProductImage, Inventory,
    Cart, CartItem, Wishlist, WishlistItem,
    Order, OrderItem, Payment, Review, AuditLog
)
from .serializers import (
    AddressSerializer, CategorySerializer, CategoryTreeSerializer,
    ProductSerializer, ProductListSerializer, ProductCreateSerializer, ProductImageSerializer,
    InventorySerializer, CartSerializer, WishlistItemSerializer,
    OrderSerializer, PaymentSerializer, ReviewSerializer,
    AuditLogSerializer, CreateOrderSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == 'list' and not self.request.query_params.get('parent'):
            return CategoryTreeSerializer
        return CategorySerializer

    def get_queryset(self):
        queryset = Category.objects.all()
        parent_id = self.request.query_params.get('parent')
        if parent_id == 'null':
            queryset = queryset.filter(parent__isnull=True)
        return queryset

    @action(detail=False, methods=['get'])
    def tree(self, request):
        categories = Category.objects.filter(parent__isnull=True)
        return Response(CategoryTreeSerializer(categories, many=True).data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        if self.action == 'create':
            return ProductCreateSerializer
        return ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        q = self.request.query_params.get('q')
        category = self.request.query_params.get('category')
        price_min = self.request.query_params.get('price_min')
        price_max = self.request.query_params.get('price_max')
        sort = self.request.query_params.get('sort', '')

        if q:
            queryset = queryset.filter(Q(title__icontains=q) | Q(description__icontains=q))
        if category:
            queryset = queryset.filter(category__slug=category)
        if price_min:
            queryset = queryset.filter(price_cents__gte=int(price_min))
        if price_max:
            queryset = queryset.filter(price_cents__lte=int(price_max))

        if sort:
            sort_fields = sort.split(',')
            for field in sort_fields:
                if field.startswith('-'):
                    queryset = queryset.order_by(field[1:]) if queryset.query.order_by else queryset
                    queryset = queryset
                else:
                    queryset = queryset.order_by(field)
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    @action(detail=True, methods=['get'])
    def images(self, request, pk=None):
        product = self.get_object()
        images = product.images.all()
        return Response(ProductImageSerializer(images, many=True).data)

    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        product = self.get_object()
        similar = Product.objects.filter(category=product.category).exclude(id=product.id)[:10]
        return Response(ProductListSerializer(similar, many=True).data)


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminUser]


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination
    lookup_field = 'product_id'

    def get_queryset(self):
        queryset = Inventory.objects.all()
        low_stock = self.request.query_params.get('low_stock')
        if low_stock:
            queryset = queryset.filter(quantity__lte=int(low_stock))
        return queryset

    @action(detail=False, methods=['post'])
    def bulk_adjust(self, request):
        adjustments = request.data
        results = []
        for adj in adjustments:
            product_id = adj.get('productId')
            delta = adj.get('delta', 0)
            try:
                inv = Inventory.objects.get(product_id=product_id)
                inv.quantity += delta
                inv.save()
                results.append({'productId': str(product_id), 'quantity': inv.quantity})
            except Inventory.DoesNotExist:
                results.append({'productId': str(product_id), 'error': 'Not found'})
        return Response({'summary': results})


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        address = serializer.save(user=self.request.user)
        if address.is_default:
            Address.objects.filter(user=self.request.user).exclude(id=address.id).update(is_default=False)

    @action(detail=True, methods=['post'])
    def default(self, request, pk=None):
        address = self.get_object()
        address.is_default = True
        address.save()
        Address.objects.filter(user=request.user).exclude(id=address.id).update(is_default=False)
        return Response(AddressSerializer(address).data)


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def items(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('productId')
        quantity = request.data.get('quantity', 1)
        product = get_object_or_404(Product, id=product_id)

        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={'quantity': quantity, 'price_cents': product.price_cents}
        )
        if not created:
            item.quantity += quantity
            item.save()
        return Response(CartSerializer(cart).data)

    @action(detail=True, methods=['patch', 'delete'])
    def item(self, request, pk=None):
        cart = self.get_object()
        item = get_object_or_404(CartItem, id=pk, cart=cart)
        if request.method == 'PATCH':
            item.quantity = request.data.get('quantity', item.quantity)
            item.save()
        else:
            item.delete()
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def apply_coupon(self, request):
        cart = self.get_object()
        return Response(CartSerializer(cart).data)

    def destroy(self, request, *args, **kwargs):
        cart = self.get_object()
        CartItem.objects.filter(cart=cart).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        wishlist, _ = Wishlist.objects.get_or_create(user=self.request.user)
        return WishlistItem.objects.filter(wishlist=wishlist)

    def get_object(self):
        wishlist, _ = Wishlist.objects.get_or_create(user=self.request.user)
        return wishlist

    def perform_create(self, serializer):
        wishlist = self.get_object()
        product_id = self.request.data.get('productId')
        product = get_object_or_404(Product, id=product_id)
        serializer.save(wishlist=wishlist, product=product)

    @action(detail=False, methods=['get'])
    def check(self, request):
        product_id = request.query_params.get('productId')
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        in_wishlist = WishlistItem.objects.filter(wishlist=wishlist, product_id=product_id).exists()
        return Response({'inWishlist': in_wishlist})

    def destroy(self, request, *args, **kwargs):
        wishlist = self.get_object()
        WishlistItem.objects.filter(wishlist=wishlist, id=kwargs.get('pk')).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def create(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        address_id = serializer.validated_data['addressId']
        payment_provider = serializer.validated_data['paymentProvider']

        address = get_object_or_404(Address, id=address_id, user=request.user)
        cart = Cart.objects.filter(user=request.user).first()

        if not cart or not cart.am_items.exists():
            return Response({'error': {'code': 'CART_EMPTY', 'message': 'Cart is empty'}}, status=400)

        subtotal = sum(item.price_cents * item.quantity for item in cart.am_items.all())
        shipping = 500
        tax = int(subtotal * 0.08)
        total = subtotal + shipping + tax

        order = Order.objects.create(
            user=request.user,
            address=address,
            status='created',
            subtotal_cents=subtotal,
            shipping_cents=shipping,
            tax_cents=tax,
            total_cents=total
        )

        for item in cart.am_items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                title=item.product.title,
                price_cents=item.price_cents,
                quantity=item.quantity,
                currency=item.currency
            )

        Payment.objects.create(
            order=order,
            provider=payment_provider,
            status='initiated',
            amount_cents=total
        )

        cart.am_items.all().delete()

        return Response(OrderSerializer(order).data, status=201)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status in ['shipped', 'delivered']:
            return Response({'error': {'code': 'CANNOT_CANCEL', 'message': 'Cannot cancel shipped order'}}, status=400)
        order.status = 'cancelled'
        order.save()
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        order = self.get_object()
        order.status = 'shipped'
        order.save()
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def mark_delivered(self, request, pk=None):
        order = self.get_object()
        order.status = 'delivered'
        order.placed_at = timezone.now()
        order.save()
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        order = self.get_object()
        order.status = 'refunded'
        order.save()
        payment = order.payment
        payment.status = 'refunded'
        payment.save()
        return Response(PaymentSerializer(payment).data)

    @action(detail=True, methods=['get'])
    def invoice(self, request, pk=None):
        order = self.get_object()
        return Response({'id': str(order.id), 'status': order.status, 'total': order.total_cents})


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']
    pagination_class = StandardResultsSetPagination
    lookup_field = 'order_id'

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)

    def create(self, request, order_id=None):
        if order_id:
            order = get_object_or_404(Order, id=order_id)
        else:
            order_id = request.data.get('orderId')
            order = get_object_or_404(Order, id=order_id)
        provider = request.data.get('provider', 'stripe')

        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={'provider': provider, 'status': 'initiated', 'amount_cents': order.total_cents}
        )

        return Response({
            'paymentIntent': f'mock_{payment.id}',
            'provider': provider,
            'amount': payment.amount_cents
        }, status=201)

    @action(detail=True, methods=['post'], url_path='initiate')
    def initiate(self, request, order_id=None):
        order = get_object_or_404(Order, id=order_id)
        provider = request.data.get('provider', 'stripe')
        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={'provider': provider, 'status': 'initiated', 'amount_cents': order.total_cents}
        )
        return Response({
            'paymentIntent': f'mock_{payment.id}',
            'provider': provider,
            'amount': payment.amount_cents
        })

    @action(detail=True, methods=['get'], url_path='status')
    def status(self, request, order_id=None):
        order = get_object_or_404(Order, id=order_id)
        try:
            payment = order.am_payment
        except:
            return Response({'error': 'No payment found'}, status=404)
        return Response(PaymentSerializer(payment).data)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def create(self, request, product_id=None):
        product = get_object_or_404(Product, id=product_id)
        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, product=product)

        reviews = Review.objects.filter(product=product)
        avg = reviews.aggregate(avg=Sum('rating'))['avg'] / reviews.count()
        product.avg_rating = avg
        product.review_count = reviews.count()
        product.save()

        return Response(serializer.data, status=201)

    def partial_update(self, request, *args, **kwargs):
        review = self.get_object()
        if review.user != request.user:
            return Response({'error': {'code': 'FORBIDDEN', 'message': 'Not your review'}}, status=403)
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def mark_helpful(self, request, pk=None):
        review = Review.objects.get(pk=pk)
        review.helpful_count += 1
        review.save()
        return Response({'helpful_count': review.helpful_count})


class ProductReviewViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    def list(self, request, product_id=None):
        product = get_object_or_404(Product, id=product_id)
        reviews = Review.objects.filter(product=product)
        return Response(ReviewSerializer(reviews, many=True).data)

    def create(self, request, product_id=None):
        if not request.user.is_authenticated:
            return Response({'error': {'code': 'AUTH_REQUIRED'}}, status=401)
        product = get_object_or_404(Product, id=product_id)
        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, product=product)

        reviews = Review.objects.filter(product=product)
        if reviews.count() > 0:
            avg = reviews.aggregate(avg=Sum('rating'))['avg'] / reviews.count()
            product.avg_rating = avg
            product.review_count = reviews.count()
            product.save()

        return Response(serializer.data, status=201)


class AdminMetricsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        from_date = request.query_params.get('from')
        to_date = request.query_params.get('to')
        granularity = request.query_params.get('granularity', 'day')

        orders = Order.objects.all()
        if from_date:
            orders = orders.filter(created_at__gte=from_date)
        if to_date:
            orders = orders.filter(created_at__lte=to_date)

        total_sales = orders.aggregate(total=Sum('total_cents'))['total'] or 0
        total_orders = orders.count()

        return Response({
            'sales': {'total': total_sales, 'orders': total_orders},
            'granularity': granularity
        })


class AdminTopProductsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        from_date = request.query_params.get('from')
        to_date = request.query_params.get('to')
        limit = int(request.query_params.get('limit', 10))

        items = OrderItem.objects.all()
        if from_date:
            items = items.filter(order__created_at__gte=from_date)
        if to_date:
            items = items.filter(order__created_at__lte=to_date)

        top_products = items.values('product_id', 'title').annotate(
            total_sold=Sum('quantity'),
            total_revenue=Sum('price_cents')
        ).order_by('-total_sold')[:limit]

        return Response({'products': list(top_products)})


class AdminAuditLogView(APIView):
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        user_id = request.query_params.get('user')
        action = request.query_params.get('action')
        queryset = AuditLog.objects.all()

        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if action:
            queryset = queryset.filter(action=action)

        queryset = queryset.order_by('-created_at')[:100]
        return Response(AuditLogSerializer(queryset, many=True).data)


class AdminUserExportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        from core.models import User
        users = User.objects.all().values('id', 'email', 'full_name', 'is_active', 'created_at')
        return Response({'users': list(users)})


class AdminCatalogReindexView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        return Response({'status': 'queued'})
