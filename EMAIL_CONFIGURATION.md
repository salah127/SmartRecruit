# Configuration Email pour SmartRecruit

## Pour recevoir de vrais emails au lieu de les voir dans la console

### Option 1: Configuration Gmail (Recommandée)

1. **Activez l'authentification à 2 facteurs** sur votre compte Gmail
2. **Générez un mot de passe d'application** :
   - Allez dans Paramètres Google → Sécurité
   - Authentification à 2 facteurs
   - Mots de passe des applications
   - Sélectionnez "Autre" et tapez "SmartRecruit"
   - Copiez le mot de passe généré (16 caractères)

3. **Configurez le fichier .env** :
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre_email@gmail.com
EMAIL_HOST_PASSWORD=mot_de_passe_application_16_caracteres
DEFAULT_FROM_EMAIL=noreply@smartrecruit.com
```

### Option 2: Configuration Outlook/Hotmail

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre_email@outlook.com
EMAIL_HOST_PASSWORD=votre_mot_de_passe
DEFAULT_FROM_EMAIL=noreply@smartrecruit.com
```

### Option 3: Configuration Yahoo

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre_email@yahoo.com
EMAIL_HOST_PASSWORD=votre_mot_de_passe_application
DEFAULT_FROM_EMAIL=noreply@smartrecruit.com
```

## Test de la configuration

Une fois configuré, testez avec :

```bash
python manage.py test_email --to votre_email@gmail.com
```

## Retour au mode console (développement)

Pour revenir au mode console (emails affichés dans le terminal) :

```
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

## Troubleshooting

### Erreur "Authentication failed"
- Vérifiez que l'authentification à 2 facteurs est activée
- Utilisez un mot de passe d'application, pas votre mot de passe principal

### Erreur "SMTP connection refused"
- Vérifiez votre connexion internet
- Vérifiez les paramètres HOST et PORT

### Emails marqués comme spam
- Configurez un domaine personnalisé pour DEFAULT_FROM_EMAIL
- Utilisez votre propre serveur SMTP professionnel
