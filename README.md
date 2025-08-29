# SmartRecruit - Système de Gestion Intelligente des Ressources Humaines

## 🎯 Description

SmartRecruit est une plateforme complète de gestion des ressources humaines développée avec Django et Django REST Framework. Le système intègre des fonctionnalités d'intelligence artificielle pour l'analyse automatique des CV et offre une gestion complète du processus de recrutement.

## ✨ Fonctionnalités Principales

### 🧑‍💼 I. Gestion des Utilisateurs

✅ **Système de comptes utilisateurs complet**
- Modèle utilisateur personnalisé avec rôles définis
- API REST complète pour la gestion des utilisateurs
- Validation avancée des données et gestion d'erreurs
- Interface d'administration intégrée

✅ **Système de rôles hiérarchique**
- **👨‍💼 Admin** : Accès complet au système
- **🎯 Recruteur** : Gestion des candidatures et évaluation
- **👤 Candidat** : Soumission et suivi des candidatures

✅ **Sécurité et permissions**
- Permissions personnalisées basées sur les rôles
- Contrôle d'accès granulaire
- Filtrage des données selon les permissions

### 📋 II. Gestion des Candidatures

✅ **Soumission de candidatures**
- Upload sécurisé de CV (PDF, DOC, DOCX)
- Upload optionnel de lettre de motivation
- Message d'accompagnement personnalisé
- Contrainte d'unicité : un candidat par poste

✅ **Gestion par les recruteurs**
- Visualisation de toutes les candidatures
- Modification des statuts (En attente, Acceptée, Refusée, En cours)
- Assignation de recruteurs spécifiques
- Téléchargement sécurisé des documents
- Système de commentaires et suivi détaillé

✅ **Sécurité des fichiers**
- Validation stricte des extensions de fichiers
- Limitation de taille (5MB maximum)
- Noms de fichiers sécurisés avec UUID
- Organisation hiérarchique par utilisateur
- Suppression automatique lors de la suppression des candidatures

### 🤖 III. Intelligence Artificielle - Analyse de CV

✅ **Analyse automatique des CV**
- Extraction intelligente du texte (PDF, DOC, DOCX)
- Détection automatique de la langue (FR/EN)
- Analyse des compétences techniques
- Évaluation de l'expérience professionnelle
- Score de compatibilité avec le poste

✅ **Modèles IA utilisés**
- **BERT** pour la classification et l'analyse sémantique
- **Sentence Transformers** pour l'embedding et la similarité
- **spaCy** pour le traitement du langage naturel (NLP)
- **scikit-learn** pour les analyses statistiques

✅ **Système de scoring avancé**
- Score global de pertinence (0-100)
- Score par compétences techniques
- Score d'expérience professionnelle
- Score de formation/éducation
- Recommandations personnalisées

✅ **Traitement asynchrone**
- Analyses IA en arrière-plan avec **Celery**
- Support Redis pour la gestion des tâches
- Notifications automatiques des résultats

### 📧 IV. Système de Notifications Email

✅ **Notifications automatiques**
- **Pour les candidats** : Mise à jour du statut des candidatures
- **Pour les recruteurs** : Nouvelle candidature reçue
- **Pour les recruteurs** : Assignation de candidature

✅ **Gestion des préférences**
- Configuration personnalisée des notifications
- Opt-in/Opt-out pour chaque type de notification
- Interface de gestion des préférences

✅ **Journalisation complète**
- Log de tous les emails envoyés
- Suivi des succès/échecs d'envoi
- Traçabilité complète des communications

### 📊 V. Tableau de Bord et Analytics

✅ **Statistiques en temps réel**
- Nombre total de candidatures
- Répartition par statut
- Candidatures par recruteur
- Évolution mensuelle des candidatures

✅ **Graphiques interactifs**
- Évolution temporelle des candidatures
- Postes les plus demandés
- Répartition des statuts (graphique en secteurs)
- Temps de traitement moyen

✅ **Analyses avancées**
- Top 5 des postes populaires
- Candidatures par recruteur
- Activité récente (7 derniers jours)
- Métriques de performance

## 🏗️ Architecture Technique

### Structure du Projet

```
smartrecruit/
├── smartrecruit/              # Configuration Django principale
│   ├── settings.py           # Configuration générale
│   ├── urls.py               # URLs principales
│   ├── celery.py             # Configuration Celery
│   └── wsgi.py               # WSGI application
├── users/                     # Application gestion utilisateurs
│   ├── models.py             # Modèle User personnalisé
│   ├── serializers.py        # Sérialiseurs DRF
│   ├── views.py              # Vues API et templates
│   ├── permissions.py        # Permissions personnalisées
│   ├── admin.py              # Interface admin
│   └── urls.py               # URLs de l'app
├── candidatures/              # Application gestion candidatures
│   ├── models.py             # Modèles Candidature et AnalyseCV
│   ├── serializers.py        # Sérialiseurs pour l'API
│   ├── views.py              # Vues principales et dashboard
│   ├── ai_views.py           # Vues spécifiques à l'IA
│   ├── forms.py              # Formulaires Django
│   ├── permissions.py        # Permissions candidatures
│   └── admin.py              # Configuration admin
├── notifications/             # Système de notifications
│   ├── models.py             # Modèles preferences et logs
│   ├── services.py           # Services d'envoi d'email
│   ├── signals.py            # Signaux Django automatiques
│   └── views.py              # API notifications
├── ai/                        # Module Intelligence Artificielle
│   ├── models/               # Modèles IA
│   │   ├── resume_analyzer.py    # Analyseur principal CV
│   │   └── model_loader.py       # Chargeur de modèles
│   ├── processing/           # Traitement des données
│   │   ├── data_preprocessor.py  # Préprocesseur CV
│   │   └── feature_extractor.py  # Extracteur de caractéristiques
│   ├── utils/                # Utilitaires IA
│   │   └── file_processor.py     # Traitement fichiers
│   └── tasks.py              # Tâches Celery asynchrones
├── templates/                 # Templates HTML
│   ├── base.html             # Template de base
│   ├── candidatures/         # Templates candidatures
│   └── users/                # Templates utilisateurs
├── media/                     # Fichiers uploadés
│   └── candidatures/         # Organisation par utilisateur
├── ai_models/                 # Modèles IA sauvegardés
├── data/                      # Données d'entraînement
└── requirements.txt           # Dépendances Python
```

### 🛠️ Technologies Utilisées

#### Backend & Framework
- **Django 5.2.5** - Framework web principal
- **Django REST Framework** - API REST
- **Python 3.12** - Langage de programmation

#### Intelligence Artificielle & NLP
- **transformers** - Modèles Hugging Face (BERT)
- **torch** - PyTorch pour l'IA
- **spacy** - Traitement du langage naturel
- **sentence-transformers** - Embeddings sémantiques
- **scikit-learn** - Apprentissage automatique
- **pandas** & **numpy** - Manipulation de données

#### Traitement de Fichiers
- **pdfminer.six** - Extraction de texte PDF
- **PyPDF2** - Manipulation PDF
- **python-docx** - Traitement documents Word
- **textract** - Extraction multi-formats

#### Tâches Asynchrones & Cache
- **celery** - Traitement asynchrone
- **redis** - Broker de messages et cache

#### Base de Données & Déploiement
- **SQLite** - Base de données (développement)
- **PostgreSQL** - Base de données (production recommandée)

#### Visualisation & Analytics
- **matplotlib** - Graphiques statiques
- **seaborn** - Visualisation statistique
- **plotly** - Graphiques interactifs

## 🔗 API Endpoints

### 👥 Gestion des Utilisateurs
```
GET    /api/users/                    # Liste des utilisateurs (admin/recruteur)
POST   /api/users/                    # Créer un utilisateur (admin uniquement)
GET    /api/users/{id}/               # Détails d'un utilisateur
PUT    /api/users/{id}/               # Modifier un utilisateur
DELETE /api/users/{id}/               # Supprimer un utilisateur (admin)
GET    /api/users/me/                 # Profil de l'utilisateur connecté
PUT    /api/users/update_profile/     # Mettre à jour son profil
POST   /api/users/{id}/change_role/   # Changer le rôle (admin)
POST   /api/users/{id}/toggle_active/ # Activer/désactiver (admin)
```

### 📋 Gestion des Candidatures
```
GET    /api/candidatures/                        # Liste des candidatures (filtrée par rôle)
POST   /api/candidatures/                        # Créer une candidature (candidat uniquement)
GET    /api/candidatures/{id}/                   # Détails d'une candidature
PUT    /api/candidatures/{id}/                   # Modifier une candidature
DELETE /api/candidatures/{id}/                   # Supprimer une candidature (admin/recruteur)
GET    /api/candidatures/my_candidatures/        # Mes candidatures (candidat)
POST   /api/candidatures/{id}/assign_recruiter/  # Assigner un recruteur
POST   /api/candidatures/{id}/update_status/     # Changer le statut
GET    /api/candidatures/{id}/download_cv/       # Télécharger CV
GET    /api/candidatures/{id}/download_lettre/   # Télécharger lettre
GET    /api/candidatures/by_status/              # Filtrer par statut
GET    /api/candidatures/assigned_to_me/         # Candidatures assignées (recruteur)
```

### 🤖 Intelligence Artificielle
```
POST   /api/candidatures/{id}/analyze/           # Lancer analyse IA du CV
GET    /api/candidatures/{id}/analysis/          # Récupérer résultats d'analyse
POST   /api/test/preprocess/                     # Test de prétraitement CV
```

### 📊 Tableau de Bord
```
GET    /api/dashboard/stats/                     # Statistiques générales
GET    /api/dashboard/charts/                    # Données pour graphiques
```

### 📧 Notifications
```
GET    /api/notifications/preferences/           # Préférences de notification
PUT    /api/notifications/preferences/           # Modifier préférences
GET    /api/notifications/logs/                  # Historique des notifications
```

### 🔐 Authentification
```
GET    /api-auth/login/                          # Connexion
GET    /api-auth/logout/                         # Déconnexion
```

## 🛡️ Sécurité et Permissions

### Système de Permissions
- **IsAdminUser** : Accès administrateur uniquement
- **IsRecruiterUser** : Accès recruteur uniquement  
- **IsCandidateUser** : Accès candidat uniquement
- **IsAdminOrRecruiter** : Accès admin ou recruteur
- **IsCandidatureOwner** : Propriétaire de la candidature
- **CanCreateCandidature** : Peut créer des candidatures
- **CanManageCandidatures** : Peut gérer les candidatures
- **CanDeleteCandidature** : Peut supprimer des candidatures

### Contrôle d'Accès par Rôle

#### 👨‍💼 Administrateurs
- Accès complet à tous les utilisateurs et candidatures
- Gestion des rôles et permissions
- Accès au tableau de bord complet
- Suppression de comptes et candidatures

#### 🎯 Recruteurs
- Visualisation de tous les candidats et candidatures
- Gestion des statuts des candidatures
- Assignation de candidatures
- Accès aux analyses IA et statistiques
- Téléchargement des documents

#### 👤 Candidats
- Création et modification de leurs candidatures
- Visualisation de leurs candidatures uniquement
- Téléchargement de leurs propres documents
- Accès aux résultats d'analyse de leurs CV

## 📦 Installation et Configuration

### Prérequis
- Python 3.12+
- Redis (pour Celery)
- Git

### Installation

1. **Cloner le projet**
```bash
git clone https://github.com/salah127/SmartRecruit.git
cd SmartRecruit
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Installer les modèles spaCy**
```bash
python -m spacy download fr_core_news_sm
python -m spacy download en_core_web_sm
```

5. **Configuration de la base de données**
```bash
python manage.py migrate
```

6. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

7. **Créer des données de test (optionnel)**
```bash
python manage.py shell
# Exécuter le script de création d'utilisateurs de test
```

8. **Lancer Redis** (requis pour Celery)
```bash
# Windows (avec Redis installé)
redis-server
# Docker
docker run -d -p 6379:6379 redis:alpine
```

9. **Lancer Celery Worker** (dans un terminal séparé)
```bash
celery -A smartrecruit worker --loglevel=info
```

10. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

### Configuration Email (Optionnelle)

Pour recevoir de vrais emails, créez un fichier `.env` :

```env
# Gmail (Recommandé)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre_email@gmail.com
EMAIL_HOST_PASSWORD=mot_de_passe_application_16_caracteres
DEFAULT_FROM_EMAIL=noreply@smartrecruit.com

# Pour le développement (console)
# EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

## 🚀 Utilisation

### 1. Accès à l'application
- **Interface Web** : http://localhost:8000
- **API Documentation** : http://localhost:8000/api/
- **Admin Django** : http://localhost:8000/admin/

### 2. Comptes de test
Après l'installation, créez des comptes pour tester :
- **Admin** : Accès complet
- **Recruteur** : Gestion des candidatures  
- **Candidat** : Soumission de candidatures

### 3. Workflow typique
1. **Candidat** : Crée un compte et soumet une candidature avec CV
2. **Système IA** : Analyse automatiquement le CV en arrière-plan
3. **Recruteur** : Reçoit une notification, consulte la candidature et l'analyse IA
4. **Recruteur** : Met à jour le statut (accepté/refusé/en cours)
5. **Candidat** : Reçoit une notification de mise à jour

## 📊 Fonctionnalités IA Détaillées

### Analyse des CV
- **Extraction de texte** : Support PDF, DOC, DOCX
- **Détection de langue** : Français et Anglais
- **Extraction d'entités** : Compétences, expérience, formation
- **Calcul de scores** : Algorithmes de similarité et classification
- **Recommandations** : Conseils automatiques basés sur l'analyse

### Modèles IA Utilisés
- **BERT** : Classification et analyse sémantique
- **Sentence-BERT** : Calcul de similarité entre CV et postes
- **spaCy NLP** : Extraction d'entités nommées
- **Embeddings** : Représentation vectorielle des textes

### Métriques de Performance
- Score global de pertinence (0-100)
- Score de compétences techniques
- Score d'expérience professionnelle  
- Score de formation/éducation
- Recommandations personnalisées

## 🔧 Configuration Avancée

### Variables d'Environnement
```env
# Base de données
DATABASE_URL=postgresql://user:password@localhost/smartrecruit

# IA et Modèles
AI_MODELS_DIR=/path/to/ai_models
ENABLE_AI_ANALYSIS=True

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Sécurité
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Configuration de Production
- Utiliser PostgreSQL comme base de données
- Configurer un serveur web (Nginx + Gunicorn)
- Utiliser un broker Redis en production
- Configurer les logs et monitoring
- Sécuriser les uploads de fichiers

## 🧪 Tests

### Lancer les tests
```bash
python manage.py test
```

### Tests de l'IA
```bash
# Test de prétraitement
python manage.py shell
>>> from ai.processing.data_preprocessor import CVPreprocessor
>>> preprocessor = CVPreprocessor()
>>> # Tester avec un fichier CV
```

## 📚 Documentation Technique

### Architecture des Modèles

#### Modèle User (users/models.py)
```python
class User(AbstractUser):
    role = models.CharField(choices=ROLE_CHOICES, default='candidat')
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### Modèle Candidature (candidatures/models.py)
```python
class Candidature(models.Model):
    candidat = models.ForeignKey(User, on_delete=models.CASCADE)
    poste = models.CharField(max_length=200)
    cv = models.FileField(upload_to=candidature_file_path)
    status = models.CharField(choices=STATUS_CHOICES)
    recruteur_assigne = models.ForeignKey(User, null=True, blank=True)
    # ... autres champs
```

#### Modèle AnalyseCV (candidatures/models.py)
```python
class AnalyseCV(models.Model):
    candidature = models.OneToOneField(Candidature)
    donnees_extractes = models.JSONField(default=dict)
    score_global = models.FloatField()
    score_competences = models.FloatField()
    score_experience = models.FloatField()
    recommendations = models.TextField()
    # ... autres champs
```

## 🤝 Contribution

### Standards de Code
- Suivre PEP 8 pour Python
- Documentation des fonctions et classes
- Tests unitaires pour les nouvelles fonctionnalités
- Messages de commit descriptifs

### Structure des Commits
```
feat: Ajouter analyse IA des CV
fix: Corriger l'upload de fichiers PDF
docs: Mettre à jour la documentation API
test: Ajouter tests pour les permissions
```

## 📝 Changelog

### Version 1.0.0 (Actuelle)
- ✅ Système de gestion des utilisateurs avec rôles
- ✅ Gestion complète des candidatures
- ✅ Intelligence artificielle pour l'analyse des CV
- ✅ Système de notifications email
- ✅ Tableau de bord avec analytics
- ✅ API REST complète
- ✅ Interface d'administration

### Prochaines Fonctionnalités
- 🔄 Système de chat en temps réel
- 🔄 Planification d'entretiens
- 🔄 Génération de rapports PDF
- 🔄 Intégration avec des plateformes externes
- 🔄 Application mobile (React Native)

## ❓ Questions Techniques Résolues

### **Comment mettre en place la gestion des rôles dans Django ?**

1. **Modèle personnalisé** : Extension d'`AbstractUser` avec un champ `role`
2. **Permissions** : Classes de permissions personnalisées basées sur les rôles
3. **Décorateurs d'accès** : Méthodes de contrôle dans les ViewSets  
4. **Filtrage des données** : QuerySets filtrés selon le rôle de l'utilisateur
5. **Vérifications explicites** : Contrôles de permissions dans les actions sensibles

### **Comment intégrer l'IA dans Django ?**

1. **Traitement asynchrone** : Utilisation de Celery pour les analyses longues
2. **Modèles pré-entraînés** : Intégration de BERT et Sentence Transformers
3. **Stockage des résultats** : Modèles Django pour sauvegarder les analyses
4. **API endpoints** : Exposition des fonctionnalités IA via REST API
5. **Gestion des erreurs** : Handling robuste des exceptions IA

## 📞 Support et Contact

### Documentation
- **API** : Consultez les endpoints documentés
- **Code** : Commentaires dans le code source
- **Issues** : Signalez les bugs sur GitHub

### Ressources
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [spaCy Documentation](https://spacy.io/)

---

**SmartRecruit** - Révolutionnez votre processus de recrutement avec l'intelligence artificielle 🚀