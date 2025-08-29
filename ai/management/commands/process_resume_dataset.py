import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ResumeDatasetLoader:
    """Classe pour charger et traiter le dataset Resume"""
    def __init__(self):
        self.dataset_path = os.path.join(settings.DATA_DIR, 'kaggle_resume_dataset')
        self.csv_path = os.path.join(self.dataset_path, 'Resume.csv')
        self.pdfs_path = os.path.join(self.dataset_path, 'data')
    
    def load_csv_data(self):
        """Charge le fichier CSV principal"""
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Fichier CSV non trouvé: {self.csv_path}")
        
        # Charger en spécifiant le type de la colonne ID comme string
        return pd.read_csv(self.csv_path, dtype={'ID': str})
    
    def create_enhanced_dataset(self):
        """Crée un dataset enrichi - Version simplifiée"""
        # Créer la structure de dossiers
        extracted_dir = os.path.join(settings.DATA_DIR, 'processed', 'extracted_texts')
        os.makedirs(extracted_dir, exist_ok=True)
        
        # Charger CSV original - IL CONTIENT DÉJÀ LES TEXTES DANS Resume_str !
        df_original = self.load_csv_data()
        
        print(f"📊 Dataset original chargé: {len(df_original)} entrées")
        print("📝 Le CSV contient déjà les textes dans la colonne 'Resume_str'")
        
        # Préparer les données enrichies
        enhanced_data = []
        
        for index, row in df_original.iterrows():
            # Nettoyer le texte (supprimer les HTML tags si nécessaire)
            clean_text = str(row['Resume_str']).replace('<br>', '\n').replace('<p>', '\n').replace('</p>', '\n')
            clean_text = ' '.join(clean_text.split())  # Nettoyer les espaces multiples
            
            enhanced_data.append({
                'ID': row['ID'],
                'file_id': row['ID'],  # Même valeur que ID pour éviter les problèmes de merge
                'category': row['Category'],
                'extracted_text': clean_text,
                'text_length': len(clean_text),
                'original_resume_str': row['Resume_str'],
                'resume_html': row.get('Resume_html', '')  # Garder l'HTML original si existe
            })
        
        # Créer le DataFrame enrichi
        df_enhanced = pd.DataFrame(enhanced_data)
        
        # Sauvegarder le dataset enrichi
        output_path = os.path.join(settings.DATA_DIR, 'processed', 'resume_dataset_enhanced.csv')
        df_enhanced.to_csv(output_path, index=False, encoding='utf-8')
        
        # Aussi sauvegarder les textes individuellement
        for item in enhanced_data:
            output_dir = os.path.join(extracted_dir, item['category'])
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"{item['file_id']}.txt")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(item['extracted_text'])
        
        return df_enhanced

class Command(BaseCommand):
    help = 'Process the Kaggle Resume dataset using existing text from CSV'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--sample',
            type=int,
            help='Nombre d\'échantillons à traiter (pour tester)',
            default=0
        )
    
    def handle(self, *args, **options):
        self.stdout.write('🚀 Début du traitement du dataset Resume...')
        self.stdout.write('📝 Utilisation des textes déjà présents dans le CSV...')
        
        loader = ResumeDatasetLoader()
        
        # Vérifier que le dataset est bien placé
        if not os.path.exists(loader.csv_path):
            self.stdout.write(
                self.style.ERROR('❌ Dataset non trouvé!')
            )
            self.stdout.write(
                f'⚠️  Placez le dataset Kaggle dans: {loader.dataset_path}'
            )
            self.stdout.write('Structure attendue:')
            self.stdout.write(f'  {loader.dataset_path}/Resume.csv')
            self.stdout.write(f'  {loader.dataset_path}/data/ACCOUNTANT/1001.pdf')
            return
        
        # Traiter le dataset
        try:
            enhanced_df = loader.create_enhanced_dataset()
            
            # Si option --sample, limiter le dataset
            sample_size = options['sample']
            if sample_size > 0:
                enhanced_df = enhanced_df.head(sample_size)
                self.stdout.write(
                    self.style.WARNING(f'🧪 Mode test: {sample_size} échantillons seulement')
                )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Dataset enrichi créé avec {len(enhanced_df)} entrées'
                )
            )
            self.stdout.write(
                f'📁 Fichier: {os.path.join(settings.DATA_DIR, "processed", "resume_dataset_enhanced.csv")}'
            )
            
            # Afficher un aperçu
            self.stdout.write('\n📊 Aperçu des catégories:')
            category_counts = enhanced_df['category'].value_counts()
            for category, count in category_counts.items():
                self.stdout.write(f'   {category}: {count} CVs')
            
            self.stdout.write(
                self.style.WARNING('💡 Pour extraire les PDFs réels, installez: pip install PyPDF2')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors du traitement: {e}')
            )
            import traceback
            self.stdout.write(traceback.format_exc())