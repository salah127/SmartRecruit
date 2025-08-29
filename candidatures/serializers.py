from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Candidature, AnalyseCV

User = get_user_model()


class CandidatureSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating candidatures
    """
    class Meta:
        model = Candidature
        fields = [
            'id', 'candidat', 'poste', 'cv', 'lettre_motivation', 
            'message', 'status', 'date_candidature', 'date_modification',
            'recruteur_assigne', 'commentaire_recruteur', 'date_reponse'
        ]
        read_only_fields = [
            'id', 'candidat', 'date_candidature', 'date_modification'
        ]
    
    def create(self, validated_data):
        # Automatically set the candidat to the current user
        validated_data['candidat'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate(self, attrs):
        # Ensure only candidates can create candidatures
        user = self.context['request'].user
        if not user.is_candidate:
            raise serializers.ValidationError(
                "Seuls les candidats peuvent créer des candidatures."
            )
        return attrs


class CandidatureListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing candidatures
    """
    candidat_username = serializers.CharField(source='candidat.username', read_only=True)
    candidat_email = serializers.CharField(source='candidat.email', read_only=True)
    candidat_nom_complet = serializers.SerializerMethodField()
    recruteur_username = serializers.CharField(source='recruteur_assigne.username', read_only=True)
    cv_filename = serializers.ReadOnlyField()
    lettre_filename = serializers.ReadOnlyField()
    
    class Meta:
        model = Candidature
        fields = [
            'id', 'candidat_username', 'candidat_email', 'candidat_nom_complet',
            'poste', 'status', 'date_candidature', 'recruteur_username',
            'cv_filename', 'lettre_filename'
        ]
    
    def get_candidat_nom_complet(self, obj):
        return f"{obj.candidat.first_name} {obj.candidat.last_name}".strip() or obj.candidat.username


class CandidatureDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for viewing candidature details
    """
    candidat_info = serializers.SerializerMethodField()
    recruteur_info = serializers.SerializerMethodField()
    cv_filename = serializers.ReadOnlyField()
    lettre_filename = serializers.ReadOnlyField()
    
    class Meta:
        model = Candidature
        fields = [
            'id', 'candidat_info', 'poste', 'cv', 'cv_filename',
            'lettre_motivation', 'lettre_filename', 'message', 'status',
            'date_candidature', 'date_modification', 'recruteur_info',
            'commentaire_recruteur', 'date_reponse'
        ]
    
    def get_candidat_info(self, obj):
        return {
            'id': obj.candidat.id,
            'username': obj.candidat.username,
            'email': obj.candidat.email,
            'nom_complet': f"{obj.candidat.first_name} {obj.candidat.last_name}".strip() or obj.candidat.username,
            'phone': obj.candidat.phone
        }
    
    def get_recruteur_info(self, obj):
        if obj.recruteur_assigne:
            return {
                'id': obj.recruteur_assigne.id,
                'username': obj.recruteur_assigne.username,
                'email': obj.recruteur_assigne.email,
                'nom_complet': f"{obj.recruteur_assigne.first_name} {obj.recruteur_assigne.last_name}".strip() or obj.recruteur_assigne.username
            }
        return None


class CandidatureUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating candidature status (recruiters/admins only)
    """
    class Meta:
        model = Candidature
        fields = [
            'status', 'recruteur_assigne', 'commentaire_recruteur', 'date_reponse'
        ]
    
    def update(self, instance, validated_data):
        # If status is being changed, update date_reponse
        if 'status' in validated_data and validated_data['status'] != instance.status:
            from django.utils import timezone
            validated_data['date_reponse'] = timezone.now()
        
        return super().update(instance, validated_data)


class CandidatureCandidatSerializer(serializers.ModelSerializer):
    """
    Serializer for candidates to view/update their own candidatures
    """
    cv_filename = serializers.ReadOnlyField()
    lettre_filename = serializers.ReadOnlyField()
    
    class Meta:
        model = Candidature
        fields = [
            'id', 'poste', 'cv', 'cv_filename', 'lettre_motivation', 
            'lettre_filename', 'message', 'status', 'date_candidature',
            'date_modification', 'commentaire_recruteur', 'date_reponse'
        ]
        read_only_fields = [
            'id', 'status', 'date_candidature', 'date_modification',
            'commentaire_recruteur', 'date_reponse'
        ]


class AnalyseCVSerializer(serializers.ModelSerializer):
    candidat_email = serializers.CharField(source='candidature.candidat.email', read_only=True)
    poste = serializers.CharField(source='candidature.poste', read_only=True)
    
    class Meta:
        model = AnalyseCV
        fields = [
            'id', 'candidat_email', 'poste', 'donnees_extractes',
            'score_competences', 'score_experience', 'score_global',
            'recommendations', 'date_analyse'
        ]
        read_only_fields = ['date_analyse']