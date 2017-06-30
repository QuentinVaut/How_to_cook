from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Avg
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views import generic

from cookiz.models import Recette, Note
from cookiz.forms import UserCreationFormCustom, RecetteForm, CommentaireForm, NoteForm
from django.contrib.auth import login
from django.contrib.auth.models import User


def add_userView(request):
    if request.user.is_authenticated():
        return redirect('home')
    else:
        if request.method == "POST":
            form = UserCreationFormCustom(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                util = User.objects.create_user(
                    username=cd.get('username'),
                    password=cd.get('password1'),
                )
                util.save
                login(request, util)
                return redirect('home')
        else:
            form = UserCreationFormCustom()
        return render(request, 'registration/register.html', {'form': form})


@login_required(login_url="error")
def recettes_userView(request):
    recettes = Recette.objects.filter(user=request.user)
    page = request.GET.get('page', 1)
    paginator = Paginator(recettes, 5)
    try:
        list_recettes = paginator.page(page)
    except PageNotAnInteger:
        list_recettes = paginator.page(1)
    except EmptyPage:
        list_recettes = paginator.page(paginator.num_pages)
    return render(request, 'cookiz/user_recettes.html',
                  {'recettes': list_recettes, 'page': page, 'paginator': paginator})


@login_required(login_url="error")
def add_recetteView(request):
    if request.method == 'POST':
        form = RecetteForm(request.POST, request.FILES)
        if form.is_valid():
            recette = form.save(commit=False)
            recette.user = request.user
            recette.date_creation = timezone.now()
            recette.save()
            return redirect('home')
    else:
        form = RecetteForm()
    return render(request, 'cookiz/recette_add.html', {'form': form})


@login_required(login_url="error")
def edit_recetteView(request, recette_slug):
    try:
        recette_object = Recette.objects.get(slug=recette_slug)
        if recette_object.user.pk is not request.user.pk:
            raise Recette.DoesNotExist

        if request.method == "POST":
            form = RecetteForm(request.POST, request.FILES, instance=recette_object)
            if form.is_valid():
                recette = form.save(commit=False)
                recette.date_modification = timezone.now()
                recette.save()
                return redirect('recette_detail', recette_slug=recette_object.slug)
        else:
            form = RecetteForm(instance=recette_object)
        return render(request, 'cookiz/recette_edit.html', {'form': form})
    except Recette.DoesNotExist:
        return redirect('error')


@login_required(login_url="error")
def publish_recetteView(request, recette_slug):
    try:
        recette = Recette.objects.get(slug=recette_slug, user=request.user, publier=False)
        recette.publier = True
        recette.save()
        return redirect('home')

    except Recette.DoesNotExist:
        return redirect('error')


@login_required(login_url="error")
def remove_recetteView(request, recette_slug):
    try:
        recette = Recette.objects.get(slug=recette_slug, user=request.user, publier=True)
        recette.publier = False
        recette.save()
        return redirect('home')

    except Recette.DoesNotExist:
        return redirect('error')


class RecetteView(generic.ListView):
    model = Recette
    template_name = 'cookiz/recette_list.html'
    queryset = Recette.objects.filter(publier=True)
    context_object_name = 'recettes'
    paginate_by = 6


def detail_recetteView(request, recette_slug):
    try:
        recette_object = Recette.objects.get(slug=recette_slug)

        if recette_object.publier is False:
            if recette_object.user.pk is not request.user.pk:
                raise Recette.DoesNotExist

        recette_object.notes.aggregate(moyenne=Avg('note'))

    except Recette.DoesNotExist:
        return redirect('error')

    if request.method == 'POST':
        form_commentaire = CommentaireForm(request.POST)
        form_note = NoteForm(request.POST)

        if form_commentaire.is_valid():
            commentaire = form_commentaire.save(commit=False)
            commentaire.recette = Recette.objects.get(slug=recette_slug)
            commentaire.user = request.user
            commentaire.date_creation = timezone.now()
            commentaire.save()
            return redirect('recette_detail', recette_slug=recette_slug)

        if form_note.is_valid():
            old_note = Note.objects.filter(recette=recette_object.id, user=request.user).first()

            if old_note:
                old_note.note = str(request.POST['note'])
                old_note.save()
            else:
                note = form_note.save(commit=False)
                note.recette = Recette.objects.get(slug=recette_slug)
                note.user = request.user
                note.save()

            notes = Note.objects.filter(recette=recette_object.id)

            if notes is not None:
                nb_notes = 0
                sum_notes = 0

                for item in notes:
                    sum_notes += item.note
                    nb_notes += 1

                recette = Recette.objects.get(slug=recette_slug)
                recette.note_moyenne = sum_notes / nb_notes
                recette.save()

            return redirect('recette_detail', recette_slug=recette_slug)
    else:
        form_commentaire = CommentaireForm()
        form_note = NoteForm()

    page = request.GET.get('page', 1)
    paginator = Paginator(recette_object.commentaires.all(), 5)
    try:
        commentaires = paginator.page(page)
    except PageNotAnInteger:
        commentaires = paginator.page(1)
    except EmptyPage:
        commentaires = paginator.page(paginator.num_pages)

    current_user_recette = False;
    if request.user.is_authenticated():
        deja_vote = Note.objects.filter(recette=recette_object, user=request.user).exists()
        if recette_object.user == request.user:
            current_user_recette = True;
    else:
        deja_vote = False

    return render(request, 'cookiz/recette_detail.html',
                  {'recette': recette_object, 'form_commentaire': form_commentaire, 'form_note': form_note,
                   'liste_commentaire': commentaires, 'deja_vote': deja_vote,
                   'current_user_recette': current_user_recette})


def error(request):
    return render(request, 'cookiz/error.html')
