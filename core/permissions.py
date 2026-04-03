from rest_framework.permissions import BasePermission


class IsAdminBasedOnToken(BasePermission):
    message = {'error': {'code': 'FORBIDDEN', 'message': 'Admin access required'}}

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        token = request.auth
        if token is None:
            return False
        
        token_payload = token.payload if hasattr(token, 'payload') else {}
        role = token_payload.get('role')
        
        return role == 'admin'


class IsAdminUser(BasePermission):
    message = {'error': {'code': 'FORBIDDEN', 'message': 'Admin access required'}}

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or getattr(request.user, 'role', None) == 'admin'
        )


class IsVerifiedUser(BasePermission):
    message = {'error': {'code': 'NOT_VERIFIED', 'message': 'Verified account required'}}

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_verified