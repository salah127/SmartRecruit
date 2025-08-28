from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse, Http404
from django.contrib.auth import get_user_model
from .models import Candidature
from .serializers import (
    CandidatureSerializer, CandidatureListSerializer, 
    CandidatureDetailSerializer, CandidatureUpdateSerializer,
    CandidatureCandidatSerializer
)
from .permissions import (
    IsCandidatureOwner, CanCreateCandidature, 
    CanManageCandidatures, CanDeleteCandidature
)

User = get_user_model()


class CandidatureViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing candidatures with file upload and role-based access
    """
    queryset = Candidature.objects.all()
    serializer_class = CandidatureSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        """
        Return different serializers based on action and user role
        """
        if self.action == 'list':
            return CandidatureListSerializer
        elif self.action == 'retrieve':
            return CandidatureDetailSerializer
        elif self.action in ['update', 'partial_update'] and self.request.user.is_candidate:
            return CandidatureCandidatSerializer
        elif self.action in ['update', 'partial_update']:
            return CandidatureUpdateSerializer
        return CandidatureSerializer
    
    def get_permissions(self):
        """
        Instantiate and return the list of permissions
        """
        if self.action == 'create':
            permission_classes = [CanCreateCandidature]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteCandidature]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsCandidatureOwner]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Filter queryset based on user role
        """
        user = self.request.user
        
        if user.is_admin:
            # Admins can see all candidatures
            return Candidature.objects.all()
        elif user.is_recruiter:
            # Recruiters can see all candidatures
            return Candidature.objects.all()
        else:
            # Candidates can only see their own candidatures
            return Candidature.objects.filter(candidat=user)
    
    def perform_create(self, serializer):
        """
        Save candidature with current user as candidat
        """
        serializer.save(candidat=self.request.user)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_candidatures(self, request):
        """
        Return current user's candidatures (for candidates)
        """
        if not request.user.is_candidate:
            return Response(
                {'detail': 'Accessible aux candidats uniquement.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        candidatures = Candidature.objects.filter(candidat=request.user)
        serializer = CandidatureListSerializer(candidatures, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign_recruiter(self, request, pk=None):
        """
        Assign a recruiter to a candidature (admin/recruiter only)
        """
        # Explicit permission check
        if not (request.user.is_admin or request.user.is_recruiter):
            return Response(
                {'detail': 'Permission denied. Admin or recruiter access required.'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        candidature = self.get_object()
        recruiter_id = request.data.get('recruiter_id')
        
        if not recruiter_id:
            return Response(
                {'error': 'recruiter_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            recruiter = User.objects.get(id=recruiter_id, role='recruteur')
            candidature.recruteur_assigne = recruiter
            candidature.save()
            
            serializer = CandidatureDetailSerializer(candidature)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {'error': 'Recruteur non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Update candidature status (admin/recruiter only)
        """
        # Explicit permission check
        if not (request.user.is_admin or request.user.is_recruiter):
            return Response(
                {'detail': 'Permission denied. Admin or recruiter access required.'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        candidature = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Candidature.STATUS_CHOICES):
            return Response(
                {'error': 'Statut invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        candidature.status = new_status
        if 'commentaire' in request.data:
            candidature.commentaire_recruteur = request.data['commentaire']
        
        from django.utils import timezone
        candidature.date_reponse = timezone.now()
        candidature.save()
        
        serializer = CandidatureDetailSerializer(candidature)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsCandidatureOwner])
    def download_cv(self, request, pk=None):
        """
        Download CV file
        """
        candidature = self.get_object()
        
        if not candidature.cv:
            raise Http404("CV non trouvé")
        
        response = HttpResponse(
            candidature.cv.read(),
            content_type='application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{candidature.cv_filename}"'
        return response
    
    @action(detail=True, methods=['get'], permission_classes=[IsCandidatureOwner])
    def download_lettre(self, request, pk=None):
        """
        Download cover letter file
        """
        candidature = self.get_object()
        
        if not candidature.lettre_motivation:
            raise Http404("Lettre de motivation non trouvée")
        
        response = HttpResponse(
            candidature.lettre_motivation.read(),
            content_type='application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{candidature.lettre_filename}"'
        return response
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """
        Get candidatures filtered by status (recruiters/admins only)
        """
        # Explicit permission check
        if not (request.user.is_admin or request.user.is_recruiter):
            return Response(
                {'detail': 'Permission denied. Admin or recruiter access required.'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        status_filter = request.query_params.get('status')
        
        if not status_filter:
            return Response(
                {'error': 'Paramètre status requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        candidatures = self.get_queryset().filter(status=status_filter)
        serializer = CandidatureListSerializer(candidatures, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def assigned_to_me(self, request):
        """
        Get candidatures assigned to current recruiter
        """
        if not request.user.is_recruiter:
            return Response(
                {'detail': 'Accessible aux recruteurs uniquement.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        candidatures = Candidature.objects.filter(recruteur_assigne=request.user)
        serializer = CandidatureListSerializer(candidatures, many=True)
        return Response(serializer.data)
