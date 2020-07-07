from django.shortcuts import get_object_or_404, render

# Create your views here.
from .models import Ingredient
from django.views import generic
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError
from django.conf import settings
import random
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.encoding import force_bytes
from ipaddress import ip_address, ip_network
import requests
import hmac
from hashlib import sha1

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
    try:
        ingredient_1 = Ingredient.objects.get(pk=request.POST['ingredient1'])
        ingrEffect_1 = ingredient_1.ingredient_effect
        ingr1_color = ingredient_1.ingredient_color
        ingrWeight_1 = ingredient_1.ingredient_weight
        ingrCoeff_1 = ingredient_1.ingredient_coefficient



        ingredient_2 = Ingredient.objects.get(pk=request.POST['ingredient2'])
        ingrEffect_2 = ingredient_2.ingredient_effect
        ingr2_color = ingredient_2.ingredient_color
        ingrWeight_2 = ingredient_2.ingredient_weight
        ingrCoeff_2 = ingredient_2.ingredient_coefficient
    except MultiValueDictKeyError:
        return HttpResponse("Вы не установили ингредиенты")

    mass = ingrWeight_1 + ingrWeight_2 + 5

    if mass > 50 or mass < 10 :
       return HttpResponse("Суп не удовлетворяет требованиям")

    else:

        if mass <= 20:
            effectDuration = 20
        elif mass > 20 and mass <= 30:
            effectDuration = 40
        else:
            effectDuration = 60

        Rarely = random.randint(1, 100)
        if Rarely <= 50:
            soupRarely = "Common"
            effectduration = effectDuration
        if Rarely > 50 and Rarely <= 75:
            soupRarely = "Rare"
            effectduration = effectDuration + effectDuration / 10
        if Rarely > 75 and Rarely <= 87:
            soupRarely = "Epic"
            effectduration = effectDuration + effectDuration / 5
        if Rarely > 87 and Rarely <= 94:
            soupRarely = "Ledendary"
            effectduration = effectDuration + effectDuration / 2
        if Rarely > 94 and Rarely < 100:
            soupRarely = "Ancient"
            effectduration = effectDuration + effectDuration / 4 * 3
        if Rarely == 100:
            soupRarely = "Divine"
            effectduration = effectDuration * 2

        EffectChance = random.randint(1, 6)

        count_1 = 1
        count_2 = 1

        if EffectChance < 6 and ingrCoeff_1 > ingrCoeff_2 and ingrWeight_2 * count_2 > 1.5 * ingrWeight_1 * count_1:
            soupEffect = ingrEffect_1 + ", " + ingrEffect_2
        elif EffectChance < 6 and ingrCoeff_1 < ingrCoeff_2 and ingrWeight_1 * count_1 > 1.5 * ingrWeight_2 * count_2:
            soupEffect = ingrEffect_1 + ", " + ingrEffect_2
        elif EffectChance < 6 and ingrCoeff_1 > ingrCoeff_2 and ingrWeight_2 * count_2 < 1.5 * ingrWeight_1 * count_1:
            soupEffect = ingrEffect_1
        else:
            soupEffect = ingrEffect_2



        return render(request, 'cooking/soupinfo.html', { 'soupColor1':ingr1_color, 'soupColor2':ingr2_color, 'effectDuration':effectduration, 'rarely':soupRarely, 'soupEffect':soupEffect, 'soupWeight':mass})

@require_POST
@csrf_exempt
def hello(request):
    # Verify if request came from GitHub
    forwarded_for = u'{}'.format(request.META.get('HTTP_X_FORWARDED_FOR'))
    client_ip_address = ip_address(forwarded_for)
    whitelist = requests.get('https://api.github.com/meta').json()['hooks']

    for valid_ip in whitelist:
        if client_ip_address in ip_network(valid_ip):
            break
    else:
        return HttpResponseForbidden('Permission denied.')

    # Verify the request signature
    header_signature = request.META.get('HTTP_X_HUB_SIGNATURE')
    if header_signature is None:
        return HttpResponseForbidden('Permission denied.')

    sha_name, signature = header_signature.split('=')
    if sha_name != 'sha1':
        return HttpResponseServerError('Operation not supported.', status=501)

    mac = hmac.new(force_bytes(settings.GITHUB_WEBHOOK_KEY), msg=force_bytes(request.body), digestmod=sha1)
    if not hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(signature)):
        return HttpResponseForbidden('Permission denied.')

    # If request reached this point we are in a good shape
    # Process the GitHub events
    event = request.META.get('HTTP_X_GITHUB_EVENT', 'ping')

    if event == 'ping':
        return HttpResponse('pong')
    elif event == 'push':
        # Deploy some code for example
        return HttpResponse('success')

    # In case we receive an event that's not ping or push
    return HttpResponse(status=204)