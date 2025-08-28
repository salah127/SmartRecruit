from django.contrib import admin
from django.utils.html import format_html
from .models import Candidature


@admin.register(Candidature)
class CandidatureAdmin(admin.ModelAdmin):
    """
    Admin configuration for Candidature model
    """
    list_display = [
        'candidat', 'poste', 'status', 'date_candidature', 
        'recruteur_assigne', 'cv_link', 'lettre_link'
    ]
    list_filter = ['status', 'date_candidature', 'poste']
    search_fields = ['candidat__username', 'candidat__email', 'poste']
    ordering = ['-date_candidature']
    
    fieldsets = (
        ('Informations candidat', {
            'fields': ('candidat', 'poste', 'message')
        }),
        ('Fichiers', {
            'fields': ('cv', 'lettre_motivation')
        }),
        ('Statut et suivi', {
            'fields': ('status', 'recruteur_assigne', 'commentaire_recruteur')
        }),
        ('Dates', {
            'fields': ('date_candidature', 'date_modification', 'date_reponse'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['date_candidature', 'date_modification']
    
    def cv_link(self, obj):
        if obj.cv:
            return format_html(
                '<a href="{}" target="_blank">Télécharger CV</a>',
                obj.cv.url
            )
        return "Aucun CV"
    cv_link.short_description = "CV"
    
    def lettre_link(self, obj):
        if obj.lettre_motivation:
            return format_html(
                '<a href="{}" target="_blank">Télécharger Lettre</a>',
                obj.lettre_motivation.url
            )
        return "Aucune lettre"
    lettre_link.short_description = "Lettre de motivation"
    
    def get_queryset(self, request):
        """
        Filter candidatures based on user role
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif hasattr(request.user, 'is_admin') and request.user.is_admin:
            return qs
        elif hasattr(request.user, 'is_recruiter') and request.user.is_recruiter:
            return qs
        return qs.filter(candidat=request.user)
