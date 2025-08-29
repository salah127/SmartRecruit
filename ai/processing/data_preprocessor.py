import re
import spacy
import pandas as pd
from typing import Dict, List, Tuple
import pdfminer.high_level
import docx
import io

class CVPreprocessor:
    def __init__(self):
        self.nlp_fr = spacy.load("fr_core_news_sm")
        self.nlp_en = spacy.load("en_core_web_sm")
        
        # Listes de compétences communes
        self.competences_techniques = [
            'python', 'java', 'javascript', 'html', 'css', 'react', 'angular',
            'vue', 'django', 'flask', 'node.js', 'sql', 'nosql', 'mongodb',
            'postgresql', 'docker', 'kubernetes', 'aws', 'azure', 'git'
        ]
        
        self.soft_skills = [
            'communication', 'leadership', 'travail d\'équipe', 'résolution de problèmes',
            'créativité', 'adaptabilité', 'gestion du temps', 'empathie'
        ]

    def extract_text_from_file(self, file) -> str:
        """Extrait le texte de différents formats de fichiers"""
        filename = file.name.lower()
        
        if filename.endswith('.pdf'):
            return self._extract_text_from_pdf(file)
        elif filename.endswith(('.doc', '.docx')):
            return self._extract_text_from_docx(file)
        elif filename.endswith('.txt'):
            return file.read().decode('utf-8')
        else:
            raise ValueError("Format de fichier non supporté")

    def _extract_text_from_pdf(self, file) -> str:
        """Extrait le texte d'un PDF"""
        try:
            with io.BytesIO(file.read()) as pdf_file:
                text = pdfminer.high_level.extract_text(pdf_file)
            return text
        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction PDF: {str(e)}")

    def _extract_text_from_docx(self, file) -> str:
        """Extrait le texte d'un DOCX"""
        try:
            doc = docx.Document(io.BytesIO(file.read()))
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction DOCX: {str(e)}")

    def clean_text(self, text: str) -> str:
        """Nettoie et normalise le texte"""
        # Supprimer les caractères spéciaux et normaliser l'espacement
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\sàâäéèêëîïôöùûüçÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ]', ' ', text)
        text = text.lower().strip()
        return text

    def detect_language(self, text: str) -> str:
        """Détecte la langue du texte"""
        # Simple détection basée sur les mots communs
        french_words = ['le', 'la', 'les', 'de', 'des', 'du', 'et', 'est']
        english_words = ['the', 'and', 'is', 'are', 'was', 'were']
        
        fr_count = sum(1 for word in french_words if word in text.lower())
        en_count = sum(1 for word in english_words if word in text.lower())
        
        return 'fr' if fr_count > en_count else 'en'

    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extrait les sections typiques d'un CV"""
        sections = {
            'experience': '',
            'education': '',
            'competences': '',
            'langues': '',
            'interets': ''
        }
        
        patterns = {
            'experience': r'(expériences?|experience|work|employment|professional experience)[\s\S]*?(?=(education|formation|compétences|skills|$))',
            'education': r'(education|formation|academic|études)[\s\S]*?(?=(expérience|experience|compétences|skills|$))',
            'competences': r'(compétences|skills|competences|technical skills)[\s\S]*?(?=(langues|languages|intérêts|interests|$))'
        }
        
        for section, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                sections[section] = match.group(0)
        
        return sections

    def extract_competences(self, text: str) -> List[str]:
        """Extrait les compétences techniques du texte"""
        found_competences = []
        text_lower = text.lower()
        
        for competence in self.competences_techniques:
            if competence in text_lower:
                found_competences.append(competence)
                
        return list(set(found_competences))

    def extract_experience(self, text: str) -> Dict:
        """Extrait les informations d'expérience"""
        # Utilisation de spaCy pour l'extraction NER
        doc = self.nlp_fr(text) if self.detect_language(text) == 'fr' else self.nlp_en(text)
        
        experience = {
            'duree_total': 0,
            'postes': [],
            'entreprises': []
        }
        
        # Extraction des entités ORG (organisations) et des dates
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'ENTREPRISE']:
                experience['entreprises'].append(ent.text)
        
        return experience

    def preprocess_cv(self, file) -> Dict:
        """Pipeline complet de prétraitement"""
        try:
            # Extraction du texte
            raw_text = self.extract_text_from_file(file)
            
            # Nettoyage
            cleaned_text = self.clean_text(raw_text)
            
            # Détection de la langue
            language = self.detect_language(cleaned_text)
            
            # Extraction des sections
            sections = self.extract_sections(cleaned_text)
            
            # Extraction des compétences
            competences = self.extract_competences(cleaned_text)
            
            # Extraction de l'expérience
            experience = self.extract_experience(cleaned_text)
            
            return {
                'raw_text': raw_text,
                'cleaned_text': cleaned_text,
                'language': language,
                'sections': sections,
                'competences': competences,
                'experience': experience,
                'word_count': len(cleaned_text.split())
            }
            
        except Exception as e:
            raise Exception(f"Erreur lors du prétraitement: {str(e)}")