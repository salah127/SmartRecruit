import os
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

User = get_user_model()

def cv_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('cvs', filename)
    

def validate_file_size(file):
    """Validate file size (max 5MB)"""
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        raise ValidationError('La taille du fichier ne doit pas dépasser 5MB.')


def candidature_file_path(instance, filename):
    """Generate secure file path for uploads"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('candidatures', str(instance.candidat.id), filename)


class Candidature(models.Model):
    """
    Model for job applications with secure file upload
    """
    
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
        ('en_cours', 'En cours d\'examen'),
    ]
    
    candidat = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='candidatures',
        limit_choices_to={'role': 'candidat'},
        verbose_name='Candidat'
    )
    
    poste = models.CharField(
        max_length=200,
        verbose_name='Poste visé'
    )
    
    cv = models.FileField(
        upload_to=candidature_file_path,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx']),
            validate_file_size
        ],
        verbose_name='CV',
        help_text='Formats acceptés: PDF, DOC, DOCX (max 5MB)'
    )
    
    lettre_motivation = models.FileField(
        upload_to=candidature_file_path,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx']),
            validate_file_size
        ],
        blank=True,
        null=True,
        verbose_name='Lettre de motivation',
        help_text='Formats acceptés: PDF, DOC, DOCX (max 5MB)'
    )
    
    message = models.TextField(
        blank=True,
        null=True,
        verbose_name='Message d\'accompagnement',
        help_text='Message optionnel du candidat'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='en_attente',
        verbose_name='Statut'
    )
    
    date_candidature = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de candidature'
    )
    
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name='Dernière modification'
    )
    
    # Champs pour le suivi par les recruteurs
    recruteur_assigne = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='candidatures_assignees',
        limit_choices_to={'role': 'recruteur'},
        blank=True,
        null=True,
        verbose_name='Recruteur assigné'
    )
    
    commentaire_recruteur = models.TextField(
        blank=True,
        null=True,
        verbose_name='Commentaire du recruteur'
    )
    
    date_reponse = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Date de réponse'
    )
    
    class Meta:
        verbose_name = 'Candidature'
        verbose_name_plural = 'Candidatures'
        ordering = ['-date_candidature']
        
        # Un candidat ne peut postuler qu'une fois pour le même poste
        unique_together = ['candidat', 'poste']
    
    def __str__(self):
        return f"{self.candidat.username} - {self.poste} ({self.get_status_display()})"
    
    @property
    def cv_filename(self):
        """Return original CV filename"""
        if self.cv:
            return os.path.basename(self.cv.name)
        return None
    
    @property
    def lettre_filename(self):
        """Return original letter filename"""
        if self.lettre_motivation:
            return os.path.basename(self.lettre_motivation.name)
        return None
    
    def delete(self, *args, **kwargs):
        """Override delete to remove files from storage"""
        if self.cv:
            if os.path.isfile(self.cv.path):
                os.remove(self.cv.path)
        
        if self.lettre_motivation:
            if os.path.isfile(self.lettre_motivation.path):
                os.remove(self.lettre_motivation.path)
        
        super().delete(*args, **kwargs)


class AnalyseCV(models.Model):
    """Modèle pour stocker les résultats détaillés de l'analyse IA"""
    
    candidature = models.OneToOneField(
        Candidature, 
        on_delete=models.CASCADE,
        related_name='analyse_ia'
    )
    
    donnees_extractes = models.JSONField(
        default=dict,
        verbose_name='Données extraites',
        help_text='Données brutes extraites par l\'IA'
    )
    
    score_competences = models.FloatField(
        verbose_name='Score compétences',
        help_text='Score des compétences (0-100)'
    )
    
    score_experience = models.FloatField(
        verbose_name='Score expérience',
        help_text='Score de l\'expérience (0-100)'
    )
    
    score_formation = models.FloatField(
        verbose_name='Score formation',
        help_text='Score de la formation (0-100)'
    )
    
    score_global = models.FloatField(
        verbose_name='Score global',
        help_text='Score global de pertinence (0-100)'
    )
    
    recommendations = models.TextField(
        verbose_name='Recommandations',
        help_text='Recommandations et commentaires de l\'IA'
    )
    
    date_analyse = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date d\'analyse'
    )
    
    modele_utilise = models.CharField(
        max_length=100,
        default='BERT',
        verbose_name='Modèle IA utilisé',
        help_text='Nom du modèle IA utilisé pour l\'analyse'
    )
    
    version_modele = models.CharField(
        max_length=50,
        default='1.0',
        verbose_name='Version du modèle'
    )
    
    class Meta:
        verbose_name = 'Analyse IA'
        verbose_name_plural = 'Analyses IA'
        ordering = ['-date_analyse']
    
    def __str__(self):
        return f"Analyse pour {self.candidature.candidat.email} - {self.score_global}/100"