from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .serializers import UserSerializer, UserListSerializer, UserUpdateSerializer
from .permissions import IsAdminUser, IsOwnerOrAdmin, IsAdminOrRecruiter
from .forms import CustomUserCreationForm, UserProfileForm, CustomAuthenticationForm

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


# ============ TEMPLATE-BASED VIEWS ============

def home_view(request):
    """
    Home page view
    """
    return render(request, 'home.html')


def login_view(request):
    """
    Login view
    """
    if request.user.is_authenticated:
        return redirect('users:home')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue, {user.first_name or user.username} !')
                next_url = request.GET.get('next', 'users:home')
                return redirect(next_url)
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})


def register_view(request):
    """
    Registration view
    """
    if request.user.is_authenticated:
        return redirect('users:home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Votre compte a été créé avec succès ! Vous pouvez maintenant vous connecter.')
            return redirect('users:login')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})


def logout_view(request):
    """
    Logout view
    """
    logout(request)
    messages.info(request, 'Vous avez été déconnecté avec succès.')
    return redirect('users:home')


@login_required
def profile_view(request):
    """
    User profile view
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès.')
            return redirect('users:profile')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = UserProfileForm(instance=request.user)
    
    # Get candidature statistics for candidates
    candidatures_stats = None
    if request.user.is_candidate:
        from candidatures.models import Candidature
        candidatures = Candidature.objects.filter(candidat=request.user)
        candidatures_stats = {
            'total': candidatures.count(),
            'en_attente': candidatures.filter(status='en_attente').count(),
            'acceptees': candidatures.filter(status='acceptee').count(),
            'refusees': candidatures.filter(status='refusee').count(),
        }
    
    return render(request, 'users/profile.html', {
        'form': form,
        'candidatures_stats': candidatures_stats
    })


@login_required
def users_list_view(request):
    """
    Users list view (admin only)
    """
    if not request.user.is_admin:
        messages.error(request, 'Accès non autorisé.')
        return redirect('users:home')
    
    users_queryset = User.objects.all().order_by('-created_at')
    
    # Search filter
    search = request.GET.get('search')
    if search:
        users_queryset = users_queryset.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(username__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Role filter
    role = request.GET.get('role')
    if role:
        users_queryset = users_queryset.filter(role=role)
    
    # Pagination
    paginator = Paginator(users_queryset, 20)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    
    return render(request, 'users/list.html', {'users': users})


@login_required
def settings_view(request):
    """
    User settings view
    """
    return render(request, 'users/settings.html')


@login_required
def change_password_view(request):
    """
    Change password view
    """
    if request.method == 'POST':
        # This would be implemented with PasswordChangeForm
        pass
    
    return render(request, 'users/change_password.html')
