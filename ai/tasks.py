from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .processing.data_preprocessor import CVPreprocessor
from .models.resume_analyzer import ResumeAnalyzer
from candidatures.models import Candidature, AnalyseCV
import logging

logger = logging.getLogger(__name__)

@shared_task
def analyze_cv_async(candidature_id):
    """Tâche asynchrone pour l'analyse de CV"""
    try:
        candidature = Candidature.objects.get(id=candidature_id)
        
        # Initialiser les processeurs
        preprocessor = CVPreprocessor()
        analyzer = ResumeAnalyzer()
        
        # Prétraiter le CV
        processed_data = preprocessor.preprocess_cv(candidature.cv)
        
        # Analyser avec l'IA
        analysis_result = analyzer.analyze_resume(processed_data, candidature.poste)
        
        # Sauvegarder les résultats
        analyse_cv = AnalyseCV.objects.create(
            candidature=candidature,
            donnees_extractes=processed_data,
            score_competences=analysis_result['score_competences'],
            score_experience=analysis_result['score_experience'],
            score_global=analysis_result['score_global'],
            recommendations='\n'.join(analysis_result['recommendations'])
        )
        
        # Mettre à jour la candidature
        candidature.score_ia = analysis_result['score_global']
        candidature.competences_extractes = processed_data['competences']
        candidature.statut = 'en_cours'
        candidature.save()
        
        # Envoyer notification
        send_analysis_notification.delay(candidature.id, analysis_result['score_global'])
        
        return {'status': 'success', 'candidature_id': candidature_id}
        
    except Exception as e:
        logger.error(f"Erreur dans analyze_cv_async: {str(e)}")
        return {'status': 'error', 'error': str(e)}

@shared_task
def send_analysis_notification(candidature_id, score):
    """Envoie une notification après analyse"""
    try:
        candidature = Candidature.objects.get(id=candidature_id)
        
        subject = f"Analyse terminée - {candidature.poste}"
        message = f"""
        Bonjour,
        
        L'analyse IA de la candidature pour le poste "{candidature.poste}" 
        est terminée.
        
        Score: {score}/100
        Statut: {candidature.get_statut_display()}
        
        Connectez-vous à la plateforme pour plus de détails.
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [candidature.candidat.email],
            fail_silently=False,
        )
        
    except Exception as e:
        logger.error(f"Erreur d'envoi de notification: {str(e)}")