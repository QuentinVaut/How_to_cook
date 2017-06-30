from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from cookiz.models import Recette, Commentaire, Note


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
    password = forms.CharField(label="Password", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'password'}))


class UserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class UserCreationFormCustom(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationFormCustom, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class RecetteForm(forms.ModelForm):
    class Meta:
        model = Recette
        exclude = ['date_creation', 'date_modification', 'note_moyenne', 'slug', 'user']


class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        exclude = ['recette', 'user', 'date_creation']


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        exclude = ['recette', 'user']
