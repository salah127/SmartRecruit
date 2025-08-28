import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import Dict, List
import joblib
from sklearn.metrics.pairwise import cosine_similarity

class ResumeAnalyzer:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.load_models()
        
    def load_models(self):
        """Charge tous les modèles nécessaires"""
        try:
            # Modèle pour l'embedding de textes
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Modèle pour la classification des compétences (exemple)
            self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
            self.classification_model = AutoModelForSequenceClassification.from_pretrained(
                "bert-base-uncased", 
                num_labels=10
            )
            
            # Charger les embeddings des descriptions de postes
            self.post_embeddings = self._load_post_embeddings()
            
        except Exception as e:
            raise Exception(f"Erreur lors du chargement des modèles: {str(e)}")
    
    def _load_post_embeddings(self):
        """Charge ou crée les embeddings pour les descriptions de postes"""
        # Exemple de descriptions de postes types
        post_descriptions = {
            'developpeur_python': "Développeur Python expérimenté avec Django, Flask, et machine learning",
            'data_scientist': "Data scientist avec expérience en ML, statistiques, et big data",
            'devops': "Ingénieur DevOps avec Kubernetes, Docker, AWS et CI/CD",
            'frontend': "Développeur Frontend React, Angular, Vue.js avec expérience UI/UX"
        }
        
        return {
            post: self.embedding_model.encode(desc)
            for post, desc in post_descriptions.items()
        }
    
    def calculate_similarity_score(self, cv_text: str, poste: str) -> float:
        """Calcule le score de similarité entre le CV et le poste"""
        # Embedding du CV
        cv_embedding = self.embedding_model.encode(cv_text)
        
        # Calcul de la similarité cosine
        if poste in self.post_embeddings:
            similarity = cosine_similarity(
                [cv_embedding], 
                [self.post_embeddings[poste]]
            )[0][0]
            return float(similarity)
        
        return 0.0
    
    def extract_key_information(self, processed_data: Dict) -> Dict:
        """Extract les informations clés du CV"""
        competences = processed_data['competences']
        experience = processed_data['experience']
        
        return {
            'competences_techniques': competences,
            'nombre_competences': len(competences),
            'duree_experience': experience.get('duree_total', 0),
            'nombre_entreprises': len(experience.get('entreprises', [])),
            'langue': processed_data['language'],
            'taille_cv': processed_data['word_count']
        }
    
    def calculate_comprehensive_score(self, processed_data: Dict, poste: str) -> Dict:
        """Calcule un score complet basé sur multiple facteurs"""
        key_info = self.extract_key_information(processed_data)
        similarity_score = self.calculate_similarity_score(
            processed_data['cleaned_text'], 
            poste
        )
        
        # Pondération des différents facteurs
        weights = {
            'similarity': 0.4,
            'competences': 0.3,
            'experience': 0.2,
            'qualite': 0.1
        }
        
        # Score basé sur les compétences
        competence_score = min(key_info['nombre_competences'] / 10, 1.0)
        
        # Score basé sur l'expérience
        experience_score = min(key_info['duree_experience'] / 10, 1.0)
        
        # Score basé sur la qualité (longueur du CV)
        qualite_score = min(key_info['taille_cv'] / 500, 1.0)
        
        # Score global pondéré
        global_score = (
            weights['similarity'] * similarity_score +
            weights['competences'] * competence_score +
            weights['experience'] * experience_score +
            weights['qualite'] * qualite_score
        )
        
        return {
            'score_global': round(global_score * 100, 2),
            'score_similarite': round(similarity_score * 100, 2),
            'score_competences': round(competence_score * 100, 2),
            'score_experience': round(experience_score * 100, 2),
            'score_qualite': round(qualite_score * 100, 2),
            'key_info': key_info
        }
    
    def generate_recommendations(self, scores: Dict, key_info: Dict) -> List[str]:
        """Génère des recommandations basées sur l'analyse"""
        recommendations = []
        
        if scores['score_similarite'] < 50:
            recommendations.append("Le CV ne correspond pas bien au poste visé")
        
        if scores['score_competences'] < 40:
            recommendations.append("Compétences techniques insuffisantes pour ce poste")
        
        if scores['score_experience'] < 30:
            recommendations.append("Expérience professionnelle limitée")
        
        if scores['score_qualite'] < 50:
            recommendations.append("Le CV pourrait être plus détaillé")
        
        if not recommendations:
            recommendations.append("Profil bien adapté au poste")
        
        return recommendations
    
    def analyze_resume(self, processed_data: Dict, poste: str) -> Dict:
        """Pipeline complet d'analyse"""
        try:
            # Calcul des scores
            scores = self.calculate_comprehensive_score(processed_data, poste)
            
            # Génération des recommandations
            recommendations = self.generate_recommendations(scores, scores['key_info'])
            
            return {
                **scores,
                'recommendations': recommendations,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'score_global': 0,
                'recommendations': ["Erreur lors de l'analyse"]
            }