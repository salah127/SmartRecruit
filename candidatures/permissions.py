from rest_framework.permissions import BasePermission


class IsCandidatureOwner(BasePermission):
    """
    Permission to allow candidates to access only their own candidatures
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions for owner
        if request.user == obj.candidat:
            return True
        # Admin and recruiters can access all candidatures
        return request.user.is_admin or request.user.is_recruiter


class CanCreateCandidature(BasePermission):
    """
    Permission to allow only candidates to create candidatures
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_candidate
        )


class CanManageCandidatures(BasePermission):
    """
    Permission for recruiters and admins to manage candidatures
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_recruiter or request.user.is_admin)
        )


class CanDeleteCandidature(BasePermission):
    """
    Permission to delete candidatures - admins and recruiters only
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_admin or request.user.is_recruiter)
        )
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_admin or request.user.is_recruiter
