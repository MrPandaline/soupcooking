from django.shortcuts import get_object_or_404, render

# Create your views here.
from .models import Ingredient
from django.views import generic
from django.http import HttpResponse

# Просто отрисовочка шаблона
class IndexView(generic.TemplateView):
    model = Ingredient
    template_name = 'cooking/index.html'

class IngredientsView(generic.ListView):
    template_name = 'cooking/ingredients.html'
    context_object_name = 'ingredient_list'

    @staticmethod
    def get_queryset():
        return Ingredient.objects.all()

class DetailView(generic.DetailView):
    model = Ingredient
    template_name = 'cooking/detail.html'

class MakeSoupView(generic.ListView):
    template_name = 'cooking/makesoup.html'
    context_object_name = 'ingredient_list'

    @staticmethod
    def get_queryset():
        return Ingredient.objects.all()

def soupinfo(request):

    ingredient_1 = Ingredient.objects.get(pk=request.POST['ingredient1'])
    i = ingredient_1.ingredient_effect
    ingredient_2 = Ingredient.objects.get(pk=request.POST['ingredient2'])
    return render(request, 'cooking/soupinfo.html', {'ingredient_name': i})

@csrf_exempt
def hello(request):
    return HttpResponse('pong')
