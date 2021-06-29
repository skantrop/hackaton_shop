from rest_framework.permissions import BasePermission


class IsAuthororAdminPermission(BasePermission):
    # def has_permission(self, request, view):

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user == obj.author or
            request.user == request.user.is_staff
        )


class DenyAll(BasePermission):
    def has_permission(self, request, view):
        return False

    def has_object_permission(self, request, view, obj):
        return False
