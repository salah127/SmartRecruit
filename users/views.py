from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserListSerializer, UserUpdateSerializer
from .permissions import IsAdminUser, IsOwnerOrAdmin, IsAdminOrRecruiter

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users with role-based access control
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_serializer_class(self):
        """
        Return different serializers based on action
        """
        if self.action == 'list':
            return UserListSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        if self.action == 'create':
            # Only admins can create users
            permission_classes = [IsAdminUser]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Admins can edit any user, users can edit their own profile
            permission_classes = [IsOwnerOrAdmin]
        elif self.action == 'list':
            # All authenticated users can list (filtered by role in get_queryset)
            permission_classes = [IsAuthenticated]
        else:
            # Default: authenticated users only
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Filter queryset based on user role
        """
        user = self.request.user
        
        if user.is_admin:
            # Admins can see all users
            return User.objects.all()
        elif user.is_recruiter:
            # Recruiters can see candidates and other recruiters
            return User.objects.filter(role__in=['candidat', 'recruteur'])
        else:
            # Candidates can only see their own profile
            return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Return current user's profile
        """
        serializer = UserListSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """
        Update current user's profile
        """
        serializer = UserUpdateSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def change_role(self, request, pk=None):
        """
        Change user role (admin only)
        """
        # Explicit permission check
        if not request.user.is_admin:
            return Response(
                {'detail': 'Permission denied. Admin access required.'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        user = self.get_object()
        new_role = request.data.get('role')
        
        if new_role not in ['admin', 'recruteur', 'candidat']:
            return Response(
                {'error': 'Rôle invalide'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.role = new_role
        user.save()
        
        serializer = UserListSerializer(user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """
        Activate/deactivate user (admin only)
        """
        # Explicit permission check
        if not request.user.is_admin:
            return Response(
                {'detail': 'Permission denied. Admin access required.'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        
        serializer = UserListSerializer(user)
        return Response(serializer.data)
