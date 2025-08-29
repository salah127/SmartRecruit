from django import forms
from django.core.validators import FileExtensionValidator
from .models import Candidature


class CandidatureForm(forms.ModelForm):
    """
    Form for creating and editing candidatures
    """
    class Meta:
        model = Candidature
        fields = [
            'poste', 'cv', 'lettre_motivation', 'message'
        ]
        widgets = {
            'poste': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'cv': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
            'lettre_motivation': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['poste'].required = True
        self.fields['cv'].required = True
        self.fields['message'].required = False
        self.fields['lettre_motivation'].required = False
        
        # Add custom labels
        self.fields['poste'].label = "Poste visé"
        self.fields['message'].label = "Message d'accompagnement"
        self.fields['cv'].label = "CV"
        self.fields['lettre_motivation'].label = "Lettre de motivation (fichier)"
        
        # Add validators
        self.fields['cv'].validators = [
            FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])
        ]
        self.fields['lettre_motivation'].validators = [
            FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])
        ]

    def clean_cv(self):
        cv = self.cleaned_data.get('cv')
        if cv:
            if cv.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError('Le fichier CV ne peut pas dépasser 5MB.')
        return cv

    def clean_lettre_motivation(self):
        lettre = self.cleaned_data.get('lettre_motivation')
        if lettre:
            if lettre.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError('Le fichier lettre de motivation ne peut pas dépasser 5MB.')
        return lettre

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if message and len(message) < 20:
            raise forms.ValidationError('Le message doit contenir au moins 20 caractères.')
        return message


class CandidatureSearchForm(forms.Form):
    """
    Form for searching and filtering candidatures
    """
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par poste, entreprise...'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'Tous les statuts')] + Candidature.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
