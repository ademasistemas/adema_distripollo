from django.shortcuts import render
from .models import TutorialCategory
from agenda.models import Configuracion

def academia_list(request):
    categories = TutorialCategory.objects.prefetch_related('tutorials').all()
    config = Configuracion.objects.first()  # Obtén la configuración global
    return render(request, 'tutorial_list.html', {'categories': categories, 'config': config})
