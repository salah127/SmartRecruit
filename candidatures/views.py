from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse, Http404
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Candidature
from .forms import CandidatureForm, CandidatureSearchForm
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


# ============ TABLEAU DE BORD ============

@login_required
def dashboard_view(request):
    """
    Vue principale du tableau de bord
    """
    # Vérifier que l'utilisateur est un recruteur
    if request.user.role not in ['recruteur', 'admin']:
        return render(request, 'error.html', {
            'message': 'Accès non autorisé. Seuls les recruteurs peuvent accéder au tableau de bord.'
        })
    
    return render(request, 'candidatures/dashboard.html')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats_api(request):
    """
    API pour récupérer les statistiques du tableau de bord
    """
    try:
        if request.user.role not in ['recruteur', 'admin']:
            return Response({'error': 'Accès non autorisé'}, status=403)
        
        # Statistiques générales
        total_candidatures = Candidature.objects.count()
        candidatures_en_attente = Candidature.objects.filter(status='en_attente').count()
        candidatures_acceptees = Candidature.objects.filter(status='acceptee').count()
        candidatures_refusees = Candidature.objects.filter(status='refusee').count()
        candidatures_en_cours = Candidature.objects.filter(status='en_cours').count()
        
        # Statistiques par mois (6 derniers mois)
        six_months_ago = timezone.now() - timedelta(days=180)
        candidatures_par_mois = list(
            Candidature.objects
            .filter(date_candidature__gte=six_months_ago)
            .annotate(month=TruncMonth('date_candidature'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        
        # Top 5 des postes les plus demandés
        postes_populaires = list(
            Candidature.objects
            .values('poste')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
        
        # Répartition des candidatures par statut
        repartition_statuts = [
            {'status': 'En attente', 'count': candidatures_en_attente, 'color': '#ffc107'},
            {'status': 'Acceptées', 'count': candidatures_acceptees, 'color': '#28a745'},
            {'status': 'Refusées', 'count': candidatures_refusees, 'color': '#dc3545'},
            {'status': 'En cours d\'examen', 'count': candidatures_en_cours, 'color': '#17a2b8'},
        ]
        
        # Candidatures récentes (7 derniers jours)
        sept_jours_ago = timezone.now() - timedelta(days=7)
        nouvelles_candidatures = Candidature.objects.filter(
            date_candidature__gte=sept_jours_ago
        ).count()
        
        # Candidatures par recruteur
        candidatures_par_recruteur = list(
            Candidature.objects
            .filter(recruteur_assigne__isnull=False)
            .values('recruteur_assigne__username', 'recruteur_assigne__first_name', 'recruteur_assigne__last_name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Temps de traitement moyen (candidatures avec date_reponse)
        candidatures_traitees = Candidature.objects.filter(
            date_reponse__isnull=False
        ).exclude(status='en_attente')
        
        temps_traitement_stats = []
        if candidatures_traitees.exists():
            for candidature in candidatures_traitees:
                temps_traitement = (candidature.date_reponse - candidature.date_candidature).days
                temps_traitement_stats.append(temps_traitement)
            
            temps_moyen = sum(temps_traitement_stats) / len(temps_traitement_stats) if temps_traitement_stats else 0
        else:
            temps_moyen = 0
        
        response_data = {
            'statistiques_generales': {
                'total_candidatures': total_candidatures,
                'candidatures_en_attente': candidatures_en_attente,
                'candidatures_acceptees': candidatures_acceptees,
                'candidatures_refusees': candidatures_refusees,
                'candidatures_en_cours': candidatures_en_cours,
                'temps_traitement_moyen': round(temps_moyen, 1),
            },
            'candidatures_par_mois': [
                {
                    'mois': item['month'].strftime('%Y-%m'),
                    'count': item['count']
                } for item in candidatures_par_mois
            ],
            'postes_populaires': postes_populaires,
            'repartition_statuts': repartition_statuts,
            'candidatures_par_recruteur': [
                {
                    'recruteur': f"{item['recruteur_assigne__first_name']} {item['recruteur_assigne__last_name']}" if item['recruteur_assigne__first_name'] else item['recruteur_assigne__username'],
                    'count': item['count']
                } for item in candidatures_par_recruteur
            ],
            'activite_recente': {
                'nouvelles_candidatures': nouvelles_candidatures,
            }
        }
        
        return Response(response_data)
        
    except Exception as e:
        return Response({'error': f'Erreur serveur: {str(e)}'}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_charts_data(request):
    """
    API pour les données des graphiques
    """
    try:
        if request.user.role not in ['recruteur', 'admin']:
            return Response({'error': 'Accès non autorisé'}, status=403)
        
        chart_type = request.GET.get('type', 'evolution')
        
        if chart_type == 'evolution':
            # Évolution des candidatures sur 12 mois
            twelve_months_ago = timezone.now() - timedelta(days=365)
            evolution_data = list(
                Candidature.objects
                .filter(date_candidature__gte=twelve_months_ago)
                .annotate(month=TruncMonth('date_candidature'))
                .values('month')
                .annotate(count=Count('id'))
                .order_by('month')
            )
            
            response_data = {
                'labels': [item['month'].strftime('%B %Y') for item in evolution_data],
                'data': [item['count'] for item in evolution_data]
            }
            return Response(response_data)
        
        elif chart_type == 'postes':
            # Graphique en barres des postes
            postes_data = list(
                Candidature.objects
                .values('poste')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
            )
            
            response_data = {
                'labels': [item['poste'] for item in postes_data],
                'data': [item['count'] for item in postes_data]
            }
            return Response(response_data)
        
        elif chart_type == 'statuts':
            # Graphique en secteurs des statuts
            statuts_data = list(
                Candidature.objects
                .values('status')
                .annotate(count=Count('id'))
            )
            
            status_labels = {
                'en_attente': 'En attente',
                'acceptee': 'Acceptées',
                'refusee': 'Refusées',
                'en_cours': 'En cours d\'examen'
            }
            
            response_data = {
                'labels': [status_labels.get(item['status'], item['status']) for item in statuts_data],
                'data': [item['count'] for item in statuts_data],
                'colors': ['#ffc107', '#28a745', '#dc3545', '#17a2b8']
            }
            return Response(response_data)
        
        return Response({'error': 'Type de graphique non valide'}, status=400)
        
    except Exception as e:
        return Response({'error': f'Erreur serveur: {str(e)}'}, status=500)


# ============ TEMPLATE-BASED VIEWS ============

@login_required
def create_candidature_view(request):
    """
    Create new candidature view (candidates only)
    """
    if not request.user.is_candidate:
        messages.error(request, 'Seuls les candidats peuvent créer des candidatures.')
        return redirect('users:home')
    
    if request.method == 'POST':
        form = CandidatureForm(request.POST, request.FILES)
        if form.is_valid():
            candidature = form.save(commit=False)
            candidature.candidat = request.user
            candidature.save()
            messages.success(request, 'Votre candidature a été envoyée avec succès !')
            return redirect('candidatures:my_candidatures')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = CandidatureForm()
    
    return render(request, 'candidatures/create.html', {'form': form})


@login_required
def my_candidatures_view(request):
    """
    User's candidatures view (candidates only)
    """
    if not request.user.is_candidate:
        messages.error(request, 'Accès non autorisé.')
        return redirect('users:home')
    
    candidatures_queryset = Candidature.objects.filter(candidat=request.user).order_by('-date_candidature')
    
    # Search and filter
    form = CandidatureSearchForm(request.GET)
    if form.is_valid():
        search = form.cleaned_data.get('search')
        status_filter = form.cleaned_data.get('status')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        
        if search:
            candidatures_queryset = candidatures_queryset.filter(
                Q(poste__icontains=search) | Q(entreprise__icontains=search)
            )
        if status_filter:
            candidatures_queryset = candidatures_queryset.filter(status=status_filter)
        if date_from:
            candidatures_queryset = candidatures_queryset.filter(date_candidature__gte=date_from)
        if date_to:
            candidatures_queryset = candidatures_queryset.filter(date_candidature__lte=date_to)
    
    # Pagination
    paginator = Paginator(candidatures_queryset, 10)
    page_number = request.GET.get('page')
    candidatures = paginator.get_page(page_number)
    
    # Statistics
    all_candidatures = Candidature.objects.filter(candidat=request.user)
    stats = {
        'total': all_candidatures.count(),
        'en_attente': all_candidatures.filter(status='en_attente').count(),
        'acceptees': all_candidatures.filter(status='acceptee').count(),
        'refusees': all_candidatures.filter(status='refusee').count(),
    }
    
    return render(request, 'candidatures/my_candidatures.html', {
        'candidatures': candidatures,
        'stats': stats,
        'form': form
    })


@login_required
def candidatures_list_view(request):
    """
    All candidatures view (recruiters and admins only)
    """
    if not (request.user.is_recruiter or request.user.is_admin):
        messages.error(request, 'Accès non autorisé.')
        return redirect('users:home')
    
    candidatures_queryset = Candidature.objects.all().order_by('-date_candidature')
    
    # Search and filter
    form = CandidatureSearchForm(request.GET)
    if form.is_valid():
        search = form.cleaned_data.get('search')
        status_filter = form.cleaned_data.get('status')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        
        if search:
            candidatures_queryset = candidatures_queryset.filter(
                Q(poste__icontains=search) | 
                Q(entreprise__icontains=search) |
                Q(candidat__first_name__icontains=search) |
                Q(candidat__last_name__icontains=search) |
                Q(candidat__email__icontains=search)
            )
        if status_filter:
            candidatures_queryset = candidatures_queryset.filter(status=status_filter)
        if date_from:
            candidatures_queryset = candidatures_queryset.filter(date_candidature__gte=date_from)
        if date_to:
            candidatures_queryset = candidatures_queryset.filter(date_candidature__lte=date_to)
    
    # Additional filters
    recruiter_filter = request.GET.get('recruiter')
    if recruiter_filter == 'unassigned':
        candidatures_queryset = candidatures_queryset.filter(recruteur_assigne__isnull=True)
    elif recruiter_filter:
        candidatures_queryset = candidatures_queryset.filter(recruteur_assigne_id=recruiter_filter)
    
    # Pagination
    paginator = Paginator(candidatures_queryset, 20)
    page_number = request.GET.get('page')
    candidatures = paginator.get_page(page_number)
    
    # Statistics
    all_candidatures = Candidature.objects.all()
    stats = {
        'total': all_candidatures.count(),
        'en_attente': all_candidatures.filter(status='en_attente').count(),
        'en_cours': all_candidatures.filter(status='en_cours').count(),
        'acceptees': all_candidatures.filter(status='acceptee').count(),
        'refusees': all_candidatures.filter(status='refusee').count(),
        'non_assignees': all_candidatures.filter(recruteur_assigne__isnull=True).count(),
    }
    
    # Get all recruiters for filter
    recruiters = User.objects.filter(role='recruteur', is_active=True)
    
    return render(request, 'candidatures/list.html', {
        'candidatures': candidatures,
        'stats': stats,
        'form': form,
        'recruiters': recruiters
    })


@login_required
def candidature_detail_view(request, pk):
    """
    Candidature detail view
    """
    candidature = get_object_or_404(Candidature, pk=pk)
    
    # Check permissions
    if request.user.is_candidate and candidature.candidat != request.user:
        messages.error(request, 'Vous ne pouvez voir que vos propres candidatures.')
        return redirect('candidatures:my_candidatures')
    elif not (request.user.is_candidate or request.user.is_recruiter or request.user.is_admin):
        messages.error(request, 'Accès non autorisé.')
        return redirect('users:home')
    
    return render(request, 'candidatures/detail.html', {'candidature': candidature})


@login_required
def edit_candidature_view(request, pk):
    """
    Edit candidature view (candidates only, and only if status is 'en_attente')
    """
    candidature = get_object_or_404(Candidature, pk=pk)
    
    # Check permissions
    if not request.user.is_candidate or candidature.candidat != request.user:
        messages.error(request, 'Vous ne pouvez modifier que vos propres candidatures.')
        return redirect('candidatures:my_candidatures')
    
    if candidature.status != 'en_attente':
        messages.error(request, 'Vous ne pouvez modifier que les candidatures en attente.')
        return redirect('candidatures:my_candidatures')
    
    if request.method == 'POST':
        form = CandidatureForm(request.POST, request.FILES, instance=candidature)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre candidature a été mise à jour avec succès !')
            return redirect('candidatures:my_candidatures')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = CandidatureForm(instance=candidature)
    
    return render(request, 'candidatures/edit.html', {
        'form': form,
        'candidature': candidature
    })
