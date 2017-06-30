from datetime import timedelta
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db import models

from django.conf import settings
from django.db.models import Avg
from django.utils.text import slugify
from django.utils.timezone import localdate


class Recette(models.Model):
    TYPES = (
        ('E', "Entrée"),
        ('P', "Plat principal"),
        ('D', "Dessert"),
    )

    DIFFICULTE = (
        ('1', "Simple"),
        ('2', "Moyen"),
        ('3', "Difficile"),
    )

    COUT = {
        ('1', 'Faible'),
        ('2', 'Moyen'),
        ('3', 'Élevé'),
    }

    titre = models.CharField(max_length=200, verbose_name="Titre")
    type = models.CharField(max_length=1, choices=TYPES, verbose_name='Type de plat')
    difficulte = models.CharField(max_length=1, choices=DIFFICULTE, verbose_name="Difficulté")
    cout = models.CharField(null=True, blank=True, max_length=1, choices=COUT, verbose_name="Coût de réalisation")
    temps_preparation = models.DurationField(verbose_name="Temps de préparation")
    temps_cuisson = models.DurationField(null=True, blank=True, verbose_name="Temps de cuisson")
    temps_repos = models.DurationField(null=True, blank=True, verbose_name="Temps de repos")
    ingredients = models.TextField(verbose_name="Ingrédients")
    etapes_preparations = models.TextField(verbose_name="Étapes de préparation")
    publier = models.BooleanField(default=True, verbose_name="Publier ? ")
    date_creation = models.DateField(blank=True, null=True, verbose_name="Date de publication")
    date_modification = models.DateField(blank=True, null=True, verbose_name="Date de dernière modification")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user')
    photo1 = models.ImageField(upload_to='photos', blank=True, null=True)
    photo2 = models.ImageField(upload_to='photos', blank=True, null=True)
    photo3 = models.ImageField(upload_to='photos', blank=True, null=True)
    note_moyenne = models.PositiveSmallIntegerField(verbose_name="Note", validators=[MaxValueValidator(10)],
                                                    null=True)
    slug = models.SlugField(max_length=100, unique=True)

    def _get_unique_slug(self):
        slug = slugify(self.titre)
        unique_slug = slug
        num = 1
        while Recette.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug

    def save(self):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super(Recette, self).save()

    @property
    def was_edited(self):
        if self.date_modification is not None:
            return localdate() >= self.date_modification >= localdate() - timedelta(days=15)
        else:
            return False

    @property
    def is_new(self):  # Une recette est nouvelle si elle a moins de 7 jours
        if self.date_creation is not None and self.date_modification is None:
            return localdate() >= self.date_creation >= localdate() - timedelta(days=7)
        else:
            return False

    @property
    def get_average_note(self):
        notes = Note.objects.filter(recette=self)
        note_avg = notes.aggregate(moyenne=Avg('note'))['moyenne']
        if note_avg is not None:
            return round(note_avg, 1)
        else:
            return None


class Note(models.Model):
    recette = models.ForeignKey(Recette, on_delete=None, related_name='notes')
    note = models.PositiveSmallIntegerField(verbose_name="Note", validators=[MaxValueValidator(10)])
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Commentaire(models.Model):
    recette = models.ForeignKey(Recette, on_delete=None, related_name='commentaires')
    message = models.CharField(max_length=250, verbose_name="Commentaire")
    date_creation = models.DateField(blank=True, null=True, verbose_name="Date de publication")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
