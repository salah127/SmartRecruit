from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Candidature, AnalyseCV
from .serializers import AnalyseCVSerializer
from ai.tasks import analyze_cv_async
from ai.processing.data_preprocessor import CVPreprocessor
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_cv(request, candidature_id):
    """Déclenche l'analyse IA d'un CV"""
    try:
        candidature = get_object_or_404(Candidature, id=candidature_id)
        
        # Vérifier les permissions
        if not (request.user.is_admin or request.user.is_recruteur):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Lancer l'analyse asynchrone
        task = analyze_cv_async.delay(candidature.id)
        
        return Response({
            'status': 'analysis_started',
            'task_id': task.id,
            'message': 'L\'analyse IA a été démarrée'
        })
        
    except Exception as e:
        logger.error(f"Erreur dans analyze_cv: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_analysis_results(request, candidature_id):
    """Récupère les résultats d'analyse"""
    try:
        candidature = get_object_or_404(Candidature, id=candidature_id)
        analysis = get_object_or_404(AnalyseCV, candidature=candidature)
        
        serializer = AnalyseCVSerializer(analysis)
        return Response(serializer.data)
        
    except AnalyseCV.DoesNotExist:
        return Response({
            'status': 'not_analyzed',
            'message': 'Cette candidature n\'a pas encore été analysée'
        })
        
    except Exception as e:
        logger.error(f"Erreur dans get_analysis_results: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def preprocess_cv_test(request):
    """Endpoint de test pour le prétraitement"""
    try:
        if 'cv' not in request.FILES:
            return Response(
                {'error': 'Aucun fichier fourni'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        preprocessor = CVPreprocessor()
        result = preprocessor.preprocess_cv(request.FILES['cv'])
        
        return Response({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Erreur dans preprocess_cv_test: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )