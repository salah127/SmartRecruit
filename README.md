# SmartRecruit - Gestion Intelligente des Ressources Humaines (RH)

## Description
Système de gestion des ressources humaines avec API REST développé avec Django et Django REST Framework.

## Fonctionnalités Implémentées

### I. Gestion des Utilisateurs

✅ **Système de création, modification et suppression des comptes utilisateurs**
- Modèle utilisateur personnalisé avec rôles
- API REST complète pour la gestion des utilisateurs
- Validation des données et gestion des erreurs

✅ **Rôles des utilisateurs**
- **admin** : Administrateur avec accès complet
- **recruteur** : Recruteur avec accès aux candidats
- **candidat** : Candidat avec accès limité à son profil

✅ **Gestion des rôles dans Django**
- Permissions personnalisées basées sur les rôles
- Décorateurs d'accès pour les vues
- Contrôle d'accès granulaire

### II. Gestion des Candidatures

✅ **Ajout de candidatures par les candidats**
- Upload sécurisé de CV (PDF, DOC, DOCX)
- Upload optionnel de lettre de motivation
- Message d'accompagnement personnalisé
- Contrainte d'unicité par poste

✅ **Consultation et gestion par recruteurs/administrateurs**
- Visualisation de toutes les candidatures
- Modification du statut des candidatures
- Assignation de recruteurs
- Téléchargement sécurisé des fichiers
- Commentaires et suivi des candidatures

✅ **Upload sécurisé de fichiers**
- Validation des extensions de fichiers
- Limitation de taille (5MB max)
- Noms de fichiers sécurisés (UUID)
- Organisation hiérarchique par candidat
- Suppression automatique des fichiers

## Structure du Projet

```
smartrecruit/
├── smartrecruit/          # Configuration Django
├── users/                 # Application gestion utilisateurs
│   ├── models.py         # Modèle User personnalisé
│   ├── serializers.py    # Sérialiseurs REST
│   ├── views.py          # Vues API
│   ├── permissions.py    # Permissions personnalisées
│   ├── admin.py          # Interface admin
│   └── urls.py           # URLs API
└── manage.py
```

## API Endpoints

### Gestion des Utilisateurs
- `GET /api/users/` - Liste des utilisateurs (admin/recruteur)
- `POST /api/users/` - Créer un utilisateur (admin uniquement)
- `GET /api/users/{id}/` - Détails d'un utilisateur
- `PUT /api/users/{id}/` - Modifier un utilisateur
- `DELETE /api/users/{id}/` - Supprimer un utilisateur (admin)
- `GET /api/users/me/` - Profil de l'utilisateur connecté
- `PUT /api/users/update_profile/` - Mettre à jour son profil
- `POST /api/users/{id}/change_role/` - Changer le rôle (admin)
- `POST /api/users/{id}/toggle_active/` - Activer/désactiver (admin)

### Gestion des Candidatures
- `GET /api/candidatures/` - Liste des candidatures (filtrée par rôle)
- `POST /api/candidatures/` - Créer une candidature (candidat uniquement)
- `GET /api/candidatures/{id}/` - Détails d'une candidature
- `PUT /api/candidatures/{id}/` - Modifier une candidature
- `DELETE /api/candidatures/{id}/` - Supprimer une candidature (admin/recruteur)
- `GET /api/candidatures/my_candidatures/` - Mes candidatures (candidat)
- `POST /api/candidatures/{id}/assign_recruiter/` - Assigner un recruteur
- `POST /api/candidatures/{id}/update_status/` - Changer le statut
- `GET /api/candidatures/{id}/download_cv/` - Télécharger CV
- `GET /api/candidatures/{id}/download_lettre/` - Télécharger lettre
- `GET /api/candidatures/by_status/` - Filtrer par statut
- `GET /api/candidatures/assigned_to_me/` - Candidatures assignées (recruteur)

### Authentification
- `GET /api-auth/login/` - Connexion
- `GET /api-auth/logout/` - Déconnexion

## Permissions et Rôles

### Permissions Implémentées
- `IsAdminUser` : Accès admin uniquement
- `IsRecruiterUser` : Accès recruteur uniquement
- `IsCandidateUser` : Accès candidat uniquement
- `IsAdminOrRecruiter` : Accès admin ou recruteur
- `IsOwnerOrAdmin` : Propriétaire ou admin

### Contrôle d'Accès par Rôle
- **Admin** : Accès complet à tous les utilisateurs
- **Recruteur** : Peut voir candidats et autres recruteurs
- **Candidat** : Accès uniquement à son profil

## Installation et Configuration

1. Installer les dépendances :
```bash
pip install django djangorestframework
```

2. Appliquer les migrations :
```bash
python manage.py migrate
```

3. Créer un superutilisateur :
```bash
python manage.py createsuperuser
```

4. Lancer le serveur :
```bash
python manage.py runserver
```

## Technologies Utilisées
- Django 5.2.5
- Django REST Framework
- SQLite (base de données par défaut)

## Réponse à la Question
**Comment mettre en place la gestion des rôles dans Django ?**

1. **Modèle personnalisé** : Extension d'AbstractUser avec champ `role`
2. **Permissions** : Classes de permissions personnalisées basées sur les rôles
3. **Décorateurs d'accès** : Méthodes de contrôle dans les ViewSets
4. **Groupes** : Utilisation du système de permissions Django intégré aux rôles.