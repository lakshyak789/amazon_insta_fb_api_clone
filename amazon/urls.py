from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, ProductViewSet, ProductImageViewSet, InventoryViewSet,
    AddressViewSet, CartViewSet, WishlistViewSet, OrderViewSet,
    PaymentViewSet, ReviewViewSet, ProductReviewViewSet,
    AdminMetricsView, AdminTopProductsView, AdminAuditLogView,
    AdminUserExportView, AdminCatalogReindexView
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'product-images', ProductImageViewSet, basename='product-image')
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'me/addresses', AddressViewSet, basename='address')
router.register(r'me/cart', CartViewSet, basename='cart')
router.register(r'me/wishlist', WishlistViewSet, basename='wishlist')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
    path('products/<uuid:product_id>/reviews/', ProductReviewViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-reviews'),
    path('admin/metrics/sales/', AdminMetricsView.as_view(), name='admin-sales'),
    path('admin/metrics/top_products/', AdminTopProductsView.as_view(), name='admin-top-products'),
    path('admin/audit_logs/', AdminAuditLogView.as_view(), name='admin-audit-logs'),
    path('admin/users/export/', AdminUserExportView.as_view(), name='admin-user-export'),
    path('admin/catalog/reindex/', AdminCatalogReindexView.as_view(), name='admin-catalog-reindex'),
]
