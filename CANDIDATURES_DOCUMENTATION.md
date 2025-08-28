# Gestion des Candidatures - SmartRecruit

## 📋 **Fonctionnalités Implémentées**

### ✅ **Gestion des Candidatures**
- Ajout de candidatures par les candidats (CV + lettre de motivation)
- Consultation et gestion par les recruteurs et administrateurs
- Suppression sécurisée par les recruteurs et administrateurs

### 🔐 **Upload Sécurisé de Fichiers**

#### **Sécurité des Fichiers**
- ✅ **Validation des extensions** : Seuls PDF, DOC, DOCX acceptés
- ✅ **Limitation de taille** : Maximum 5MB par fichier
- ✅ **Noms de fichiers sécurisés** : UUID pour éviter les conflits
- ✅ **Stockage organisé** : Fichiers classés par candidat
- ✅ **Suppression automatique** : Fichiers supprimés avec la candidature

#### **Configuration Sécurisée**
```python
# Dans models.py
def candidature_file_path(instance, filename):
    """Generate secure file path for uploads"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('candidatures', str(instance.candidat.id), filename)

def validate_file_size(file):
    """Validate file size (max 5MB)"""
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        raise ValidationError('La taille du fichier ne doit pas dépasser 5MB.')
```

## 🚀 **API Endpoints**

### **Gestion des Candidatures**
| Endpoint | Méthode | Permission | Description |
|----------|---------|------------|-------------|
| `/api/candidatures/` | GET | Authentifié | Liste des candidatures (filtrée par rôle) |
| `/api/candidatures/` | POST | Candidat | Créer une candidature |
| `/api/candidatures/{id}/` | GET | Propriétaire/Admin/Recruteur | Détails d'une candidature |
| `/api/candidatures/{id}/` | PUT/PATCH | Propriétaire/Admin/Recruteur | Modifier une candidature |
| `/api/candidatures/{id}/` | DELETE | Admin/Recruteur | Supprimer une candidature |

### **Actions Spéciales**
| Endpoint | Méthode | Permission | Description |
|----------|---------|------------|-------------|
| `/api/candidatures/my_candidatures/` | GET | Candidat | Mes candidatures |
| `/api/candidatures/{id}/assign_recruiter/` | POST | Admin/Recruteur | Assigner un recruteur |
| `/api/candidatures/{id}/update_status/` | POST | Admin/Recruteur | Changer le statut |
| `/api/candidatures/{id}/download_cv/` | GET | Propriétaire/Admin/Recruteur | Télécharger CV |
| `/api/candidatures/{id}/download_lettre/` | GET | Propriétaire/Admin/Recruteur | Télécharger lettre |
| `/api/candidatures/by_status/` | GET | Admin/Recruteur | Filtrer par statut |
| `/api/candidatures/assigned_to_me/` | GET | Recruteur | Candidatures assignées |

## 📝 **Exemples d'Utilisation**

### **Créer une Candidature (Candidat)**
```bash
curl -X POST http://127.0.0.1:8000/api/candidatures/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -F "poste=Développeur Python" \
  -F "cv=@/path/to/cv.pdf" \
  -F "lettre_motivation=@/path/to/lettre.pdf" \
  -F "message=Je suis très motivé pour ce poste"
```

### **Mettre à Jour le Statut (Recruteur/Admin)**
```bash
curl -X POST http://127.0.0.1:8000/api/candidatures/1/update_status/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -d '{
    "status": "acceptee",
    "commentaire": "Excellent profil, nous contactons le candidat"
  }'
```

### **Télécharger un CV**
```bash
curl -X GET http://127.0.0.1:8000/api/candidatures/1/download_cv/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -o cv_candidat.pdf
```

## 🔒 **Contrôle d'Accès par Rôle**

### **Candidat**
- ✅ Créer ses candidatures
- ✅ Voir ses candidatures
- ✅ Modifier ses candidatures (avant traitement)
- ✅ Télécharger ses fichiers
- ❌ Voir les candidatures d'autres candidats
- ❌ Changer le statut des candidatures
- ❌ Supprimer des candidatures

### **Recruteur**
- ✅ Voir toutes les candidatures
- ✅ Télécharger tous les fichiers
- ✅ Changer le statut des candidatures
- ✅ Assigner des recruteurs
- ✅ Supprimer des candidatures
- ❌ Créer des candidatures

### **Administrateur**
- ✅ Accès complet à toutes les fonctionnalités
- ✅ Gestion complète des candidatures
- ✅ Suppression et modification sans restriction

## 🏗️ **Architecture du Modèle**

```python
class Candidature(models.Model):
    candidat = ForeignKey(User, role='candidat')
    poste = CharField(max_length=200)
    cv = FileField(upload_to=secure_path, validators=[...])
    lettre_motivation = FileField(upload_to=secure_path, optional)
    message = TextField(optional)
    status = CharField(choices=STATUS_CHOICES)
    recruteur_assigne = ForeignKey(User, role='recruteur', optional)
    commentaire_recruteur = TextField(optional)
    
    # Contrainte unique : un candidat ne peut postuler qu'une fois par poste
    unique_together = ['candidat', 'poste']
```

## 🧪 **Tests Implémentés**

✅ **Tests de Permissions**
- Candidats peuvent créer des candidatures
- Non-candidats ne peuvent pas créer de candidatures
- Candidats voient uniquement leurs candidatures
- Recruteurs voient toutes les candidatures
- Seuls admin/recruteurs peuvent changer les statuts

✅ **Tests de Fonctionnalités**
- Upload de fichiers sécurisé
- Contrainte d'unicité par poste
- Suppression de candidatures
- Téléchargement de fichiers

## 🔧 **Réponse à la Question**

**"Comment gérer l'upload sécurisé de fichiers (CV en PDF/Word) dans Django ?"**

### **1. Validation des Fichiers**
- `FileExtensionValidator` pour limiter les types de fichiers
- Validation personnalisée pour la taille des fichiers
- Vérification du type MIME en production (recommandé)

### **2. Stockage Sécurisé**
- Génération de noms uniques avec UUID
- Organisation hiérarchique des dossiers par utilisateur
- Séparation des fichiers uploadés du code source

### **3. Contrôle d'Accès**
- Permissions basées sur les rôles pour l'accès aux fichiers
- Actions personnalisées pour le téléchargement sécurisé
- Vérification des droits avant chaque accès

### **4. Configuration Django**
```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
```

### **5. Bonnes Pratiques**
- Suppression automatique des fichiers lors de la suppression du modèle
- Gestion des erreurs d'upload
- Logs des accès aux fichiers (recommandé pour la production)
- Scan antivirus des fichiers uploadés (recommandé pour la production)

L'API est maintenant prête pour la gestion complète des candidatures avec upload sécurisé de fichiers !
