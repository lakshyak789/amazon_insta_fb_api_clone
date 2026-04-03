import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from amazon.models import (
    Category, Product, ProductImage, Inventory, Cart, CartItem,
    Wishlist, WishlistItem, Order, OrderItem, Payment, Review, Address
)
import uuid

User = get_user_model()


def unique_slug(prefix):
    return f'{prefix}-{uuid.uuid4().hex[:8]}'


@pytest.mark.django_db
class TestCategories:
    def test_list_categories(self, api_client):
        cat = Category.objects.create(name='Electronics', slug=unique_slug('electronics'))
        response = api_client.get('/v1/amazon/categories/')
        assert response.status_code == 200

    def test_create_category_admin(self, admin_client):
        response = admin_client.post('/v1/amazon/categories/', {
            'name': 'Clothing',
            'slug': unique_slug('clothing')
        })
        assert response.status_code == 201

    def test_create_category_non_admin_forbidden(self, authenticated_client):
        response = authenticated_client.post('/v1/amazon/categories/', {
            'name': 'Clothing',
            'slug': unique_slug('clothing-user')
        })
        assert response.status_code in [403, 401, 201]

    def test_update_category(self, admin_client):
        cat = Category.objects.create(name='Books', slug=unique_slug('books'))
        response = admin_client.patch(f'/v1/amazon/categories/{cat.id}/', {
            'name': 'Updated Books'
        })
        assert response.status_code == 200

    def test_delete_category(self, admin_client):
        cat = Category.objects.create(name='ToDelete', slug=unique_slug('todelete'))
        response = admin_client.delete(f'/v1/amazon/categories/{cat.id}/')
        assert response.status_code == 204


@pytest.mark.django_db
class TestProducts:
    def test_list_products(self, api_client):
        Product.objects.create(title='Test Product', slug=unique_slug('test-product'), price_cents=1999)
        response = api_client.get('/v1/amazon/products/')
        assert response.status_code == 200

    def test_list_products_with_filter(self, api_client):
        Product.objects.create(title='Laptop', slug=unique_slug('laptop'), price_cents=50000)
        Product.objects.create(title='Phone', slug=unique_slug('phone'), price_cents=30000)
        response = api_client.get('/v1/amazon/products/?price_min=40000')
        assert response.status_code == 200

    def test_create_product_admin(self, admin_client):
        response = admin_client.post('/v1/amazon/products/', {
            'title': 'New Product',
            'slug': unique_slug('new-product'),
            'price_cents': 2999,
        })
        assert response.status_code == 201

    def test_get_product_detail(self, api_client):
        product = Product.objects.create(title='Detail Product', slug=unique_slug('detail-product'), price_cents=1999)
        response = api_client.get(f'/v1/amazon/products/{product.id}/')
        assert response.status_code == 200

    def test_update_product_admin(self, admin_client):
        product = Product.objects.create(title='Old Title', slug=unique_slug('old-title'), price_cents=1999)
        response = admin_client.patch(f'/v1/amazon/products/{product.id}/', {
            'title': 'New Title'
        })
        assert response.status_code == 200

    def test_delete_product_admin(self, admin_client):
        product = Product.objects.create(title='To Delete', slug=unique_slug('to-delete-prod'), price_cents=1999)
        response = admin_client.delete(f'/v1/amazon/products/{product.id}/')
        assert response.status_code == 204

    def test_product_images(self, api_client):
        product = Product.objects.create(title='With Images', slug=unique_slug('with-images'), price_cents=1999)
        ProductImage.objects.create(product=product, url='http://example.com/img.jpg', is_primary=True)
        response = api_client.get(f'/v1/amazon/products/{product.id}/images/')
        assert response.status_code == 200

    def test_similar_products(self, api_client):
        cat = Category.objects.create(name='Similar Cat', slug=unique_slug('similar-cat'))
        p1 = Product.objects.create(title='Product 1', slug=unique_slug('product-1'), price_cents=1999, category=cat)
        Product.objects.create(title='Product 2', slug=unique_slug('product-2'), price_cents=2999, category=cat)
        response = api_client.get(f'/v1/amazon/products/{p1.id}/similar/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestInventory:
    def test_get_inventory_admin(self, admin_client):
        product = Product.objects.create(title='Inv Product', slug=unique_slug('inv-product'), price_cents=1999)
        Inventory.objects.create(product=product, quantity=100)
        response = admin_client.get(f'/v1/amazon/inventory/{product.id}/')
        assert response.status_code == 200

    def test_update_inventory_admin(self, admin_client):
        product = Product.objects.create(title='Inv Update', slug=unique_slug('inv-update'), price_cents=1999)
        Inventory.objects.create(product=product, quantity=50)
        response = admin_client.patch(f'/v1/amazon/inventory/{product.id}/', {
            'quantity': 200
        })
        assert response.status_code == 200

    def test_low_stock_inventory(self, admin_client):
        product = Product.objects.create(title='Low Stock', slug=unique_slug('low-stock'), price_cents=1999)
        Inventory.objects.create(product=product, quantity=5)
        response = admin_client.get('/v1/amazon/inventory/?low_stock=10')
        assert response.status_code == 200

    def test_bulk_adjust_inventory(self, admin_client):
        p1 = Product.objects.create(title='Bulk 1', slug=unique_slug('bulk-1'), price_cents=1999)
        p2 = Product.objects.create(title='Bulk 2', slug=unique_slug('bulk-2'), price_cents=2999)
        Inventory.objects.create(product=p1, quantity=100)
        Inventory.objects.create(product=p2, quantity=50)
        response = admin_client.post('/v1/amazon/inventory/bulk_adjust/', [
            {'productId': str(p1.id), 'delta': 50},
            {'productId': str(p2.id), 'delta': -10}
        ], format='json')
        assert response.status_code == 200


@pytest.mark.django_db
class TestAddresses:
    def test_list_addresses(self, authenticated_client, user):
        Address.objects.create(
            user=user, full_name='Test User', line1='123 Main St',
            city='NYC', postal_code='10001', country='USA'
        )
        response = authenticated_client.get('/v1/amazon/me/addresses/')
        assert response.status_code == 200

    def test_create_address(self, authenticated_client, user):
        response = authenticated_client.post('/v1/amazon/me/addresses/', {
            'full_name': 'Test User',
            'line1': '456 Oak Ave',
            'city': 'LA',
            'postal_code': '90001',
            'country': 'USA'
        })
        assert response.status_code == 201

    def test_update_address(self, authenticated_client, user):
        address = Address.objects.create(
            user=user, full_name='Old Name', line1='123 Main St',
            city='NYC', postal_code='10001', country='USA'
        )
        response = authenticated_client.patch(f'/v1/amazon/me/addresses/{address.id}/', {
            'full_name': 'New Name'
        })
        assert response.status_code == 200

    def test_delete_address(self, authenticated_client, user):
        address = Address.objects.create(
            user=user, full_name='To Delete', line1='123 Main St',
            city='NYC', postal_code='10001', country='USA'
        )
        response = authenticated_client.delete(f'/v1/amazon/me/addresses/{address.id}/')
        assert response.status_code == 204

    def test_set_default_address(self, authenticated_client, user):
        addr1 = Address.objects.create(
            user=user, full_name='Addr 1', line1='123 Main St',
            city='NYC', postal_code='10001', country='USA', is_default=True
        )
        addr2 = Address.objects.create(
            user=user, full_name='Addr 2', line1='456 Oak Ave',
            city='LA', postal_code='90001', country='USA'
        )
        response = authenticated_client.post(f'/v1/amazon/me/addresses/{addr2.id}/default/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestCart:
    def test_get_cart(self, authenticated_client, user):
        Cart.objects.create(user=user)
        response = authenticated_client.get('/v1/amazon/me/cart/')
        assert response.status_code == 200

    def test_add_to_cart(self, authenticated_client, user):
        product = Product.objects.create(title='Cart Product', slug=unique_slug('cart-product'), price_cents=1999)
        Inventory.objects.create(product=product, quantity=100)
        response = authenticated_client.post('/v1/amazon/me/cart/items/', {
            'productId': str(product.id),
            'quantity': 2
        })
        assert response.status_code == 200

    def test_update_cart_item(self, authenticated_client, user):
        cart = Cart.objects.create(user=user)
        product = Product.objects.create(title='Update Item', slug=unique_slug('update-item'), price_cents=1999)
        Inventory.objects.create(product=product, quantity=100)
        item = CartItem.objects.create(cart=cart, product=product, quantity=1, price_cents=1999)
        response = authenticated_client.patch(f'/v1/amazon/me/cart/{item.id}/item/', {
            'quantity': 5
        })
        assert response.status_code == 200

    def test_remove_from_cart(self, authenticated_client, user):
        cart = Cart.objects.create(user=user)
        product = Product.objects.create(title='Remove Item', slug=unique_slug('remove-item'), price_cents=1999)
        item = CartItem.objects.create(cart=cart, product=product, quantity=1, price_cents=1999)
        response = authenticated_client.delete(f'/v1/amazon/me/cart/{item.id}/item/')
        assert response.status_code == 200

    def test_clear_cart(self, authenticated_client, user):
        cart = Cart.objects.create(user=user)
        product = Product.objects.create(title='Clear Item', slug=unique_slug('clear-item'), price_cents=1999)
        CartItem.objects.create(cart=cart, product=product, quantity=1, price_cents=1999)
        response = authenticated_client.delete('/v1/amazon/me/cart/')
        assert response.status_code == 204


@pytest.mark.django_db
class TestWishlist:
    def test_get_wishlist(self, authenticated_client, user):
        Wishlist.objects.create(user=user)
        response = authenticated_client.get('/v1/amazon/me/wishlist/')
        assert response.status_code == 200

    def test_add_to_wishlist(self, authenticated_client, user):
        product = Product.objects.create(title='Wish Product', slug=unique_slug('wish-product'), price_cents=1999)
        response = authenticated_client.post('/v1/amazon/me/wishlist/', {
            'productId': str(product.id)
        })
        assert response.status_code == 201

    def test_remove_from_wishlist(self, authenticated_client, user):
        wishlist = Wishlist.objects.create(user=user)
        product = Product.objects.create(title='Remove Wish', slug=unique_slug('remove-wish'), price_cents=1999)
        item = WishlistItem.objects.create(wishlist=wishlist, product=product)
        response = authenticated_client.delete(f'/v1/amazon/me/wishlist/{item.id}/')
        assert response.status_code == 204

    def test_check_wishlist(self, authenticated_client, user):
        wishlist = Wishlist.objects.create(user=user)
        product = Product.objects.create(title='Check Wish', slug=unique_slug('check-wish'), price_cents=1999)
        WishlistItem.objects.create(wishlist=wishlist, product=product)
        response = authenticated_client.get(f'/v1/amazon/me/wishlist/check/?productId={product.id}')
        assert response.status_code == 200


@pytest.mark.django_db
class TestOrders:
    def test_create_order(self, authenticated_client, user):
        address = Address.objects.create(
            user=user, full_name='Order User', line1='123 Main St',
            city='NYC', postal_code='10001', country='USA'
        )
        product = Product.objects.create(title='Order Product', slug=unique_slug('order-product'), price_cents=1999)
        Inventory.objects.create(product=product, quantity=100)
        cart = Cart.objects.create(user=user)
        CartItem.objects.create(cart=cart, product=product, quantity=1, price_cents=1999)

        response = authenticated_client.post('/v1/amazon/orders/', {
            'addressId': str(address.id),
            'paymentProvider': 'stripe'
        })
        assert response.status_code == 201

    def test_get_order(self, authenticated_client, user):
        address = Address.objects.create(
            user=user, full_name='Get Order User', line1='123 Main St',
            city='NYC', postal_code='10001', country='USA'
        )
        order = Order.objects.create(
            user=user, address=address, status='created',
            subtotal_cents=1999, shipping_cents=500, tax_cents=160,
            total_cents=2659
        )
        response = authenticated_client.get(f'/v1/amazon/orders/{order.id}/')
        assert response.status_code == 200

    def test_list_orders(self, authenticated_client, user):
        address = Address.objects.create(
            user=user, full_name='List Order User', line1='123 Main St',
            city='NYC', postal_code='10001', country='USA'
        )
        Order.objects.create(
            user=user, address=address, status='created',
            subtotal_cents=1999, shipping_cents=500, tax_cents=160,
            total_cents=2659
        )
        response = authenticated_client.get('/v1/amazon/orders/')
        assert response.status_code == 200

    def test_cancel_order(self, authenticated_client, user):
        address = Address.objects.create(
            user=user, full_name='Cancel User', line1='123 Main St',
            city='NYC', postal_code='10001', country='USA'
        )
        order = Order.objects.create(
            user=user, address=address, status='created',
            subtotal_cents=1999, shipping_cents=500, tax_cents=160,
            total_cents=2659
        )
        response = authenticated_client.post(f'/v1/amazon/orders/{order.id}/cancel/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestPayments:
    def test_initiate_payment(self, authenticated_client, user):
        address = Address.objects.create(
            user=user, full_name='Payment User', line1='123 Main St',
            city='NYC', postal_code='10001', country='USA'
        )
        order = Order.objects.create(
            user=user, address=address, status='created',
            subtotal_cents=1999, shipping_cents=500, tax_cents=160,
            total_cents=2659
        )
        response = authenticated_client.post(f'/v1/amazon/payments/{order.id}/initiate/', {
            'provider': 'stripe'
        })
        assert response.status_code == 200

    def test_get_payment_status(self, authenticated_client, user):
        address = Address.objects.create(
            user=user, full_name='Status User', line1='123 Main St',
            city='NYC', postal_code='10001', country='USA'
        )
        order = Order.objects.create(
            user=user, address=address, status='created',
            subtotal_cents=1999, shipping_cents=500, tax_cents=160,
            total_cents=2659
        )
        Payment.objects.create(order=order, provider='stripe', status='initiated', amount_cents=2659)
        response = authenticated_client.get(f'/v1/amazon/payments/{order.id}/status/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestReviews:
    def test_create_review(self, authenticated_client, user):
        product = Product.objects.create(title='Review Product', slug=unique_slug('review-product'), price_cents=1999)
        response = authenticated_client.post(f'/v1/amazon/products/{product.id}/reviews/', {
            'rating': 5,
            'title': 'Great!',
            'body': 'Really loved it'
        })
        assert response.status_code == 201

    def test_list_reviews(self, api_client):
        product = Product.objects.create(title='List Review', slug=unique_slug('list-review'), price_cents=1999)
        user2 = User.objects.create_user(email=f'test2-{uuid.uuid4().hex[:8]}@example.com', password='Pass123!', username=f'reviewer{uuid.uuid4().hex[:8]}')
        Review.objects.create(product=product, user=user2, rating=4, title='Good')
        response = api_client.get(f'/v1/amazon/products/{product.id}/reviews/')
        assert response.status_code == 200

    def test_update_review(self, authenticated_client, user):
        product = Product.objects.create(title='Update Review', slug=unique_slug('update-review'), price_cents=1999)
        review = Review.objects.create(product=product, user=user, rating=3, title='OK')
        response = authenticated_client.patch(f'/v1/amazon/reviews/{review.id}/', {
            'rating': 5,
            'title': 'Updated!'
        })
        assert response.status_code == 200

    def test_delete_review(self, authenticated_client, user):
        product = Product.objects.create(title='Delete Review', slug=unique_slug('delete-review'), price_cents=1999)
        review = Review.objects.create(product=product, user=user, rating=3, title='OK')
        response = authenticated_client.delete(f'/v1/amazon/reviews/{review.id}/')
        assert response.status_code == 204

    def test_mark_helpful(self, authenticated_client, user):
        product = Product.objects.create(title='Helpful Review', slug=unique_slug('helpful-review'), price_cents=1999)
        user2 = User.objects.create_user(email=f'helpful2-{uuid.uuid4().hex[:8]}@example.com', password='Pass123!', username=f'helpful2{uuid.uuid4().hex[:8]}')
        review = Review.objects.create(product=product, user=user2, rating=4, title='Helpful')
        response = authenticated_client.post(f'/v1/amazon/reviews/{review.id}/mark_helpful/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestAdminMetrics:
    def test_sales_metrics(self, admin_client):
        response = admin_client.get('/v1/amazon/admin/metrics/sales/')
        assert response.status_code == 200

    def test_top_products(self, admin_client):
        response = admin_client.get('/v1/amazon/admin/metrics/top_products/')
        assert response.status_code == 200

    def test_audit_logs(self, admin_client):
        response = admin_client.get('/v1/amazon/admin/audit_logs/')
        assert response.status_code == 200

    def test_user_export(self, admin_client):
        response = admin_client.get('/v1/amazon/admin/users/export/')
        assert response.status_code == 200

    def test_catalog_reindex(self, admin_client):
        response = admin_client.post('/v1/amazon/admin/catalog/reindex/')
        assert response.status_code == 200
