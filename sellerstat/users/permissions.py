from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsUser(BasePermission):
    """Проверка на залогиненого юзера"""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsAdminOrReadOnly(BasePermission):
    """Проверка на админа или только чтение"""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_staff

class IsAdmin(BasePermission):
    """Проверка прав на роль Админа."""
    def has_permission(self, request, view):
        return request.user and request.user.is_staff
