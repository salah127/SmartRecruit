#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartrecruit.settings')
django.setup()

from candidatures.models import Candidature
from users.models import User
from django.conf import settings
from django.core.mail import send_mail

print("=== CONFIGURATION POUR VRAIS EMAILS ===")
print()
print("📧 ÉTAPES POUR ENVOYER AUX VRAIES ADRESSES :")
print()
print("1️⃣ CRÉEZ UN COMPTE OUTLOOK :")
print("   - Allez sur https://outlook.com")
print("   - Créez un nouveau compte gratuit")
print("   - Exemple: smartrecruit2025@outlook.com")
print()
print("2️⃣ METTEZ À JOUR LE FICHIER .env :")
print("   EMAIL_HOST_USER=smartrecruit2025@outlook.com")
print("   EMAIL_HOST_PASSWORD=votre_mot_de_passe")
print()
print("3️⃣ REDÉMARREZ LE SERVEUR DJANGO")
print()
print("4️⃣ TESTEZ AVEC :")

# Afficher les adresses email réelles des utilisateurs
print()
print("👥 ADRESSES EMAIL RÉELLES DES UTILISATEURS :")
users = User.objects.all()
for user in users:
    if user.email:
        print(f"   - {user.username} ({user.role}): {user.email}")

print()
print("🎯 RÉSULTAT ATTENDU :")
print("   - Les candidats recevront les emails sur leur vraie adresse")
print("   - Les recruteurs recevront les emails sur leur vraie adresse")
print("   - Plus de test Mailtrap !")
print()
print("💡 ALTERNATIVE RAPIDE - TESTEZ AVEC GMAIL :")
print("   1. Activez l'auth 2FA sur votre Gmail")
print("   2. Générez un mot de passe d'application")
print("   3. Remplacez dans .env :")
print("      EMAIL_HOST=smtp.gmail.com")
print("      EMAIL_HOST_USER=salah1999jari@gmail.com")
print("      EMAIL_HOST_PASSWORD=nouveau_mot_de_passe_app")

if __name__ == "__main__":
    pass
