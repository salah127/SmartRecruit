from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Permission class for admin users only
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_admin
        )


class IsRecruiterUser(BasePermission):
    """
    Permission class for recruiter users
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_recruiter
        )


class IsCandidateUser(BasePermission):
    """
    Permission class for candidate users
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_candidate
        )


class IsAdminOrRecruiter(BasePermission):
    """
    Permission class for admin or recruiter users
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_admin or request.user.is_recruiter)
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Permission class allowing owners to edit their own profile or admins to edit any profile
    """
    def has_object_permission(self, request, view, obj):
        # Admin users can access any object
        if request.user.is_admin:
            return True
        # Users can only access their own profile
        return obj == request.user
