# Système de Notifications Email - SmartRecruit

## Vue d'ensemble

Le système de notifications email de SmartRecruit permet d'informer automatiquement :
- **Les candidats** du statut de leur candidature
- **Les recruteurs** lorsqu'une nouvelle candidature est reçue
- **Les recruteurs** lorsqu'une candidature leur est assignée

## Fonctionnalités

### 1. Notifications automatiques

#### Pour les candidats :
- **Candidature acceptée** : Email de félicitations avec prochaines étapes
- **Candidature refusée** : Email poli avec encouragement pour d'autres postes
- **Candidature en cours d'examen** : Email d'information sur le statut en cours
- **Mise à jour générale** : Email pour tout changement de statut

#### Pour les recruteurs :
- **Nouvelle candidature** : Notification immédiate avec détails du candidat
- **Assignation** : Notification lorsqu'une candidature leur est assignée

### 2. Gestion des préférences

Chaque utilisateur peut gérer ses préférences de notification :
- Recevoir les mises à jour de statut (candidats)
- Recevoir les notifications de nouvelles candidatures (recruteurs)
- Recevoir les notifications d'assignation (recruteurs)

### 3. Journalisation

Toutes les notifications envoyées sont enregistrées avec :
- Destinataire
- Type de notification
- Sujet
- Candidature concernée
- Statut d'envoi (succès/échec)
- Message d'erreur si applicable

## Configuration

### Configuration Email (settings.py)

```python
# Pour le développement (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Pour la production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'votre_email@gmail.com'
EMAIL_HOST_PASSWORD = 'votre_mot_de_passe'
DEFAULT_FROM_EMAIL = 'noreply@smartrecruit.com'
```

### Apps installées

```python
INSTALLED_APPS = [
    # ...
    'notifications',
    # ...
]
```

## API Endpoints

### Préférences Email

- `GET /notifications/api/preferences/my_preferences/` - Obtenir ses préférences
- `PATCH /notifications/api/preferences/update_preferences/` - Mettre à jour ses préférences

### Logs de notifications

- `GET /notifications/api/logs/` - Voir l'historique des notifications (admins voient tout, utilisateurs voient leurs logs)
- `GET /notifications/api/logs/my_logs/` - Voir ses propres logs

## Commandes de gestion

### Test des notifications

```bash
# Test notification de statut
python manage.py test_notifications --type=status --candidature-id=1

# Test notification nouvelle candidature
python manage.py test_notifications --type=new --candidature-id=1

# Test notification d'assignation
python manage.py test_notifications --type=assignment --candidature-id=1
```

## Templates Email

Les templates se trouvent dans `notifications/templates/emails/` :

- `candidature_status_update.html/txt` - Template générique de mise à jour
- `candidature_accepted.html` - Template pour candidature acceptée
- `candidature_rejected.html` - Template pour candidature refusée
- `candidature_in_progress.html` - Template pour candidature en cours
- `new_candidature_notification.html/txt` - Template pour nouvelle candidature
- `recruiter_assignment.html/txt` - Template pour assignation recruteur

## Déclencheurs automatiques

Les notifications sont envoyées automatiquement grâce aux signaux Django :

1. **Nouvelle candidature** : Signal `post_save` lors de la création
2. **Changement de statut** : Signal `pre_save` + `post_save` pour détecter les changements
3. **Assignation recruteur** : Signal `pre_save` + `post_save` pour détecter les changements

## Administration

L'interface d'administration Django permet de :
- Gérer les préférences email des utilisateurs
- Consulter l'historique des notifications envoyées
- Filtrer par type de notification, statut d'envoi, etc.

## Sécurité et Performance

- Les emails sont envoyés de manière asynchrone pour ne pas bloquer l'interface
- Les erreurs d'envoi sont loggées et n'interrompent pas le processus
- Les préférences utilisateurs sont respectées (opt-out possible)
- Templates HTML et texte disponibles pour tous les clients email

## Personnalisation

Pour personnaliser les templates :
1. Modifier les fichiers dans `notifications/templates/emails/`
2. Ajuster les styles CSS inline pour compatibilité email
3. Tester avec différents clients email

Pour ajouter de nouveaux types de notifications :
1. Ajouter le type dans `EmailNotificationLog.NOTIFICATION_TYPES`
2. Créer les templates correspondants
3. Ajouter la méthode dans `EmailNotificationService`
4. Connecter aux signaux appropriés
