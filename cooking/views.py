from django.shortcuts import render

# Create your views here.
from .models import Ingredient
from .models import UserInfo
from django.views import generic
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError, HttpResponseRedirect
from django.conf import settings
import random
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.encoding import force_bytes
from ipaddress import ip_address, ip_network
import requests
import hmac
from hashlib import sha1
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.utils.crypto import get_random_string
from django.contrib.auth.password_validation import MinimumLengthValidator, CommonPasswordValidator


def IndexView(request):
    if request.COOKIES.get('wasauthorised'):
        secret = request.COOKIES.get('wasauthorised')
        User = UserInfo.objects.get(user_secret=secret)
        UserName = User.user_name
        if not User.user_soup_list == " ":
            cookie = "."
            return render(request, 'cooking/index.html', {"cookie": cookie, 'username': UserName})
        else:
            return render(request, 'cooking/index.html', {'username': UserName})

    if request.COOKIES.get('usersoup'):
        cookie = "."
        return render(request, 'cooking/index.html', {"cookie": cookie})
    else:
        return render(request, 'cooking/index.html')

def IngredientsView(request):
    template_name = 'cooking/ingredients.html'

    ingredient_list = Ingredient.objects.all()
    if request.COOKIES.get('wasauthorised'):
        secret = request.COOKIES.get('wasauthorised')
        User = UserInfo.objects.get(user_secret=secret)
        UserName = User.user_name
        return render(request, template_name, {'ingredient_list': ingredient_list, 'username':UserName})

    return render(request, template_name, {'ingredient_list': ingredient_list})


def MakeSoupView(request):
    template_name = 'cooking/makesoup.html'

    ingredient_list = Ingredient.objects.all()
    if request.COOKIES.get('wasauthorised'):
        secret = request.COOKIES.get('wasauthorised')
        User = UserInfo.objects.get(user_secret=secret)
        UserName = User.user_name
        return render(request, template_name, {'ingredient_list': ingredient_list, 'username':UserName})

    return render(request, template_name, {'ingredient_list': ingredient_list})


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

    if mass > 205 or mass < 25:

        error = 'Суп не удовлетворяет требованиям'
        return render(request, 'cooking/soupinfo.html', {'error_message': error})

    else:

        if mass <= 85:
            effectDuration = 20
        elif mass > 85 and mass <= 145:
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




        R_1 = int(ingr1_color[0:2], 16) * ingredient1_mass
        G_1 = int(ingr1_color[2:4], 16) * ingredient1_mass
        B_1 = int(ingr1_color[4:], 16) * ingredient1_mass

        R_2 = int(ingr2_color[0:2], 16) * ingredient2_mass
        G_2 = int(ingr2_color[2:4], 16) * ingredient2_mass
        B_2 = int(ingr2_color[4:], 16) * ingredient2_mass


        if round((R_1 + R_2) / ingrediens_mass) <= 15:
            Soup_R = '0' + hex(round((R_1 + R_2) / ingrediens_mass))
        else:
            Soup_R = hex(round((R_1 + R_2) / ingrediens_mass))


        if round((G_1 + G_2) / ingrediens_mass) <= 15:
            Soup_G = '0' + hex(round((G_1 + G_2) / ingrediens_mass))
        else:
            Soup_G = hex(round((G_1 + G_2) / ingrediens_mass))


        if round((B_1 + B_2) / ingrediens_mass) <= 15:
            Soup_B = '0' + hex(round((B_1 + B_2) / ingrediens_mass))
        else:
            Soup_B = hex(round((B_1 + B_2) / ingrediens_mass))



        SoupColor = Soup_R + Soup_G + Soup_B
        SoupColor = SoupColor.replace("0x", "")


        statistic = "Сохранить результат"

        if request.COOKIES.get('wasauthorised'):
            secret = request.COOKIES.get('wasauthorised')
            User = UserInfo.objects.get(user_secret=secret)
            UserName = User.user_name
            return render(request, 'cooking/soupinfo.html', {'soupColor': SoupColor,
                                                             'effectDuration': effectduration,
                                                             'rarely': soupRarely,
                                                             'soupEffect': soupEffect,
                                                             'soupWeight': mass,
                                                             'statisticSave': statistic,
                                                             'username': UserName})

        return render(request, 'cooking/soupinfo.html', {'soupColor': SoupColor,
                                                         'effectDuration': effectduration,
                                                         'rarely': soupRarely,
                                                         'soupEffect': soupEffect,
                                                         'soupWeight': mass,
                                                         'statisticSave': statistic})

def addstatistic(request):
    if request.POST.get('livetime'):
        day = request.POST['livetime']
        time = int(day) * 24 * 60 * 60
        response = HttpResponseRedirect('/cooking/')
        response.set_cookie('livetime', str(time), time)
        return response

    else:
        if request.COOKIES.get('wasauthorised'):
            User = UserInfo.objects.get(user_secret=request.COOKIES.get('wasauthorised'))
            text = request.POST['statistic']
            User.user_soup_list = text
            User.save()
            response = HttpResponseRedirect('/cooking/')
            return response

        else:
            text = request.POST['statistic']
            text = text.replace('"', '')
            text = text.replace('\054', ',')
            response = HttpResponseRedirect('/cooking/')
            if request.COOKIES.get('livetime'):
                response.set_cookie('usersoup', text, int(request.COOKIES.get('livetime')))
            else:
                response.set_cookie('usersoup', text)
            return response

def resetcookies(request):
    if request.COOKIES.get('usersoup'):
        response = HttpResponseRedirect('/cooking/')
        response.delete_cookie('usersoup')
        return response

    else:
        return HttpResponseRedirect('/cooking/')

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

def main(request):
    return HttpResponseRedirect('cooking/')

def statistic(request):
    if request.COOKIES.get('wasauthorised'):
        secret = request.COOKIES.get('wasauthorised')
        User = UserInfo.objects.get(user_secret=secret)
        text = User.user_soup_list
        UserName = User.user_name
        if text == " ":
            error_message = "Нет сохранённого супа"
            return render(request, 'cooking/statistic.html', {'error_message': error_message, 'username':UserName})
        else:
            text = text.replace('\054', ',')
            text = text.replace('"', '')
            res = [element.strip("'()") for element in text.split(", ")]
            soupEffect = res[0]
            effectduration = res[1]
            soupRarely = res[2]
            mass = res[3]
            SoupColor = res[4]




            return render(request, 'cooking/statistic.html', {'soupColor': SoupColor,
                                                              'effectDuration': effectduration,
                                                              'rarely': soupRarely,
                                                              'soupEffect': soupEffect,
                                                              'soupWeight': mass,
                                                              'username': UserName})

    else:
        if not request.COOKIES.get('usersoup'):
            error_message = "Нет сохранённого супа"
            return render(request, 'cooking/statistic.html', {'error_message': error_message})
        else:

            text = request.COOKIES.get('usersoup')
            text = text.replace('\054', ',')
            text = text.replace('"', '')
            res = [element.strip("'()") for element in text.split(", ")]
            soupEffect = res[0]
            effectduration = res[1]
            soupRarely = res[2]
            mass = res[3]
            SoupColor = res[4]
            return render(request, 'cooking/statistic.html', {'soupColor': SoupColor,
                                                              'effectDuration': effectduration,
                                                              'rarely': soupRarely,
                                                              'soupEffect': soupEffect,
                                                              'soupWeight': mass,})


def settings(request):
    if request.COOKIES.get('usersoup'):
        soupsave = "exist"
    else:
        soupsave = ""

    soupsaveacc = ""
    if request.COOKIES.get('wasauthorised'):
        secret = request.COOKIES.get('wasauthorised')
        wasauthorised = "exist"
        user = UserInfo.objects.get(user_secret=secret)
        userName= user.user_name
        if not user.user_soup_list == " ":
            soupsaveacc = "exist"
        else:
            soupsaveacc = ""

        return render(request, 'cooking/settings.html', {'soupsave': soupsave,
                                                         'wasauthorised': wasauthorised,
                                                         'soupsaveacc': soupsaveacc,
                                                         'username': userName})

    else:
        wasauthorised = ""

    return render(request, 'cooking/settings.html', {'soupsave': soupsave,
                                                     'wasauthorised': wasauthorised,
                                                     'soupsaveacc': soupsaveacc})

def auth(request):
    if request.COOKIES.get('wasauthorised'):
        return HttpResponseRedirect('/cooking/')
    return render(request, 'cooking/auth.html')

def login(request):
    if request.COOKIES.get('wasauthorised'):
        return HttpResponseRedirect('/cooking/')
    else:
        return render(request, 'cooking/login.html')


def auth_redir(request):
    try:
        User_name = request.POST['name']
        User_email = request.POST['email']
        User_password = request.POST['password']

        minlengthpass = MinimumLengthValidator()
        commonpass = CommonPasswordValidator()

        try:
            minlengthpass.validate(User_password)
        except:
            minlength_error = "Пароль слишком короткий, он должен содержать минимум 8 символов"
            return render(request, 'cooking/auth.html', {'minlength_error': minlength_error})


        try:
            commonpass.validate(User_password)
        except:
            common_error = "Пароль слишком простой"
            return render(request, 'cooking/auth.html', {'common_error': common_error})



        hasher = PBKDF2PasswordHasher()
        salt = get_random_string(12, "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890")
        User_password = hasher.encode(password=User_password, salt=salt, iterations=180000)
        if UserInfo.objects.filter(user_name=User_name).exists():
            user_error = "Пользователь с таким именем уже существует"
            return render(request, 'cooking/auth.html', {'user_error': user_error})
        else:
            secret = get_random_string(50, 'qwertyuiopasdfghjlkzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890!@#$%^&*()_-')
            Userinfo = UserInfo(user_name=User_name, user_img=" ", user_email=User_email, user_password=User_password,
                                    user_soup_list=" ", user_secret=secret)
            Userinfo.save()
            response = HttpResponseRedirect('/cooking/')
            if request.COOKIES.get('livetime'):
                time = int(request.COOKIES.get('livetime'))
                response.set_cookie('wasauthorised', secret, time)
            else:
                response.set_cookie('wasauthorised', secret, 1209600)
            return response
    except:
        return HttpResponseRedirect('/cooking/register/')

def login_redir(request):
    try:
        username = request.POST['name']
        password = request.POST['password']
        try:
            User = UserInfo.objects.get(user_name=username)
            hasher = PBKDF2PasswordHasher()
            password = hasher.verify(password=password, encoded=User.user_password)

            if password == True:
                response = HttpResponseRedirect('/cooking/')
                response.set_cookie('wasauthorised', User.user_secret)
                if request.COOKIES.get('livetime'):
                    time = int(request.COOKIES.get('livetime'))
                    response.set_cookie('wasauthorised', User.user_secret, time)
                else:
                    response.set_cookie('wasauthorised', User.user_secret, 1209600)
                return response

            else:
                password_error = "Неверный пароль"
                return render(request, 'cooking/login.html', {'password_error': password_error})
        except:
            user_error = "Неверное имя пользователя "
            return render(request, 'cooking/login.html', {'user_error': user_error})
    except:
        return HttpResponseRedirect('/cooking/login/')

def exit(request):
    response = HttpResponseRedirect('/cooking/')
    response.delete_cookie('wasauthorised')

    return response

def deletesave(request):
    response = HttpResponseRedirect('/cooking/')
    secret = request.COOKIES.get('wasauthorised')
    User = UserInfo.objects.get(user_secret=secret)

    if not User.user_soup_list == " ":
        User.user_soup_list = " "
        User.save()

    return response
