from django.contrib import admin

from cookiz.models import Recette,Commentaire,Note

# Register your models here.
admin.site.register(Recette)
admin.site.register(Note)
admin.site.register(Commentaire)

