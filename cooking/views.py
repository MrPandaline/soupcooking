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
    ingredient_1 = Ingredient.objects.get(pk=request.POST['ingredient1'])
    ingrEffect_1 = ingredient_1.ingredient_effect
    ingr1_color = ingredient_1.ingredient_color
    ingrWeight_1 = ingredient_1.ingredient_weight
    ingrCoeff_1 = ingredient_1.ingredient_coefficient
    count_1 = int(request.POST['count1'])


    ingredient_2 = Ingredient.objects.get(pk=request.POST['ingredient2'])
    ingrEffect_2 = ingredient_2.ingredient_effect
    ingr2_color = ingredient_2.ingredient_color
    ingrWeight_2 = ingredient_2.ingredient_weight
    ingrCoeff_2 = ingredient_2.ingredient_coefficient
    count_2 = int(request.POST['count2'])

    mass = ingrWeight_1*count_1 + ingrWeight_2*count_2 + 5

    if mass > 100 or mass < 25:

        error = 'Суп не удовлетворяет требованиям'
        return render(request, 'cooking/soupinfo.html', {'error_message': error})

    else:

        if mass <= 50:
            effectDuration = 20
        elif mass > 50 and mass <= 75:
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

        if EffectChance < 6 and ingrCoeff_1 > ingrCoeff_2 and ingrWeight_2 * count_2 > 1.5 * ingrWeight_1 * count_1:
            soupEffect = ingrEffect_1 + ", " + ingrEffect_2
        elif EffectChance < 6 and ingrCoeff_1 < ingrCoeff_2 and ingrWeight_1 * count_1 > 1.5 * ingrWeight_2 * count_2:
            soupEffect = ingrEffect_1 + ", " + ingrEffect_2
        elif EffectChance < 6 and ingrCoeff_1 > ingrCoeff_2 and ingrWeight_2 * count_2 < 1.5 * ingrWeight_1 * count_1:
            soupEffect = ingrEffect_1
        else:
            soupEffect = ingrEffect_2

        ingredient1_mass = ingrWeight_1 * count_1
        ingredient2_mass = ingrWeight_2 * count_2
        ingrediens_mass = ingredient1_mass + ingredient2_mass


        color1_coeff = round(ingredient1_mass / ingrediens_mass)
        color2_coeff = round(ingredient2_mass / ingrediens_mass)
        R_1 = int(ingr1_color[0:2], 16) * color1_coeff
        G_1 = int(ingr1_color[2:4], 16) * color1_coeff
        B_1 = int(ingr1_color[4:], 16) * color1_coeff

        R_2 = int(ingr2_color[0:2], 16) * color2_coeff
        G_2 = int(ingr2_color[2:4], 16) * color2_coeff
        B_2 = int(ingr2_color[4:], 16) * color2_coeff


        if len(hex(round((R_1 + R_2) / 2))) == 1:
            Soup_R = '0' + hex(round((R_1 + R_2) / 2))
        else:
            Soup_R = hex(round((R_1 + R_2) / 2))


        if len(hex(round((G_1 + G_2) / 2))) == 1:
            Soup_G = '0' + hex(round((G_1 + G_2) / 2))
        else:
            Soup_G = hex(round((G_1 + G_2) / 2))


        if len(hex(round((B_1 + B_2) / 2))) == 1:
            Soup_B = '0' + hex(round((B_1 + B_2) / 2))
        else:
            Soup_B = hex(round((B_1 + B_2) / 2))



        SoupColor = Soup_R + Soup_G + Soup_B
        SoupColor = SoupColor.replace("0x", "")

        return render(request, 'cooking/soupinfo.html', {'soupColor': SoupColor,
                                                         'effectDuration': effectduration,
                                                         'rarely': soupRarely,
                                                         'soupEffect': soupEffect,
                                                         'soupWeight': mass})
"""
        else:
            return render(request, 'cooking/soupinfo.html', {'soupColor1': ingr1_color,
                                                             'soupColor2': ingr2_color,
                                                             'effectDuration': effectduration,
                                                             'rarely': soupRarely,
                                                             'soupEffect': soupEffect,
                                                             'soupWeight': mass})
"""

@require_POST
@csrf_exempt
def api(request):
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