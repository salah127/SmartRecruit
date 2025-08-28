# Système de Gestion des Utilisateurs - SmartRecruit

## Résumé de l'Implémentation

### 🎯 Fonctionnalités Réalisées

✅ **Gestion des Utilisateurs**
- Création, modification et suppression des comptes utilisateurs
- Système de rôles : admin, recruteur, candidat
- API REST complète avec Django REST Framework

### 🔐 Gestion des Rôles et Permissions

#### Rôles Implémentés
- **Admin** : Accès complet à toutes les fonctionnalités
- **Recruteur** : Peut gérer les candidats et voir les autres recruteurs
- **Candidat** : Accès limité à son propre profil

#### Permissions Personnalisées
- `IsAdminUser` : Vérification du rôle admin
- `IsRecruiterUser` : Vérification du rôle recruteur
- `IsCandidateUser` : Vérification du rôle candidat
- `IsAdminOrRecruiter` : Accès pour admin ou recruteur
- `IsOwnerOrAdmin` : Propriétaire ou admin

### 🛠️ Architecture Technique

#### Modèle User Personnalisé
```python
class User(AbstractUser):
    role = models.CharField(choices=ROLE_CHOICES, default='candidat')
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### Contrôle d'Accès
- Permissions basées sur les rôles
- Filtrage des données selon le rôle
- Vérifications explicites dans les actions sensibles

### 📡 API Endpoints

| Endpoint | Méthode | Permission | Description |
|----------|---------|------------|-------------|
| `/api/users/` | GET | Authentifié | Liste des utilisateurs (filtrée par rôle) |
| `/api/users/` | POST | Admin | Créer un utilisateur |
| `/api/users/{id}/` | GET/PUT/DELETE | Propriétaire ou Admin | Gérer un utilisateur |
| `/api/users/me/` | GET | Authentifié | Profil de l'utilisateur connecté |
| `/api/users/update_profile/` | PUT/PATCH | Authentifié | Mettre à jour son profil |
| `/api/users/{id}/change_role/` | POST | Admin | Changer le rôle d'un utilisateur |
| `/api/users/{id}/toggle_active/` | POST | Admin | Activer/désactiver un utilisateur |

### 🧪 Tests Implémentés

✅ **Tests de Permissions**
- Admin peut voir tous les utilisateurs
- Recruteur peut voir candidats et recruteurs
- Candidat ne voit que son profil
- Seul admin peut créer des utilisateurs
- Seul admin peut changer les rôles

✅ **Tests de Fonctionnalités**
- Création d'utilisateurs avec validation
- Récupération du profil personnel
- Modification des rôles par admin

### 🔧 Réponse à la Question

**"Comment mettre en place la gestion des rôles dans Django ?"**

1. **Modèle personnalisé** : Extension d'`AbstractUser` avec un champ `role`
2. **Permissions** : Classes de permissions personnalisées basées sur les rôles
3. **Décorateurs d'accès** : Méthodes de contrôle dans les ViewSets
4. **Filtrage des données** : QuerySets filtrés selon le rôle de l'utilisateur
5. **Vérifications explicites** : Contrôles de permissions dans les actions sensibles

### 🚀 Prêt pour le Frontend

L'API est maintenant prête à être consommée par votre application frontend. Tous les endpoints sont documentés et testés, avec un contrôle d'accès robuste basé sur les rôles des utilisateurs.
