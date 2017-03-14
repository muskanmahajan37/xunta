from rest_framework import permissions


class IsAdminOrIsSelf(permissions.BasePermission):
    message = 'Should be admin or self.'

    """
        Object-level permission to only allow modifications to a User object
        if the request.user is an administrator or you are modifying your own
        user object.
    """

    @classmethod
    def has_object_permission(cls, request, view, obj):
        return request.user.is_staff or request.user == obj
