from django.shortcuts import render

# Create your views here.
from .models import Ingredient
from .models import UserInfo
# from django.views import generic
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
        response = HttpResponse()

        if request.COOKIES.get('livetime'):
            time = int(request.COOKIES.get('livetime'))
            response.set_cookie('wasauthorised', secret, time)
        else:
            response.set_cookie('wasauthorised', secret, 1209600)

        if "," in User.user_soup_list:
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
        return render(request, template_name, {'ingredient_list': ingredient_list, 'username': UserName})

    return render(request, template_name, {'ingredient_list': ingredient_list})


def MakeSoupView(request):
    template_name = 'cooking/makesoup.html'

    ingredient_list = Ingredient.objects.all()
    if request.COOKIES.get('wasauthorised'):
        secret = request.COOKIES.get('wasauthorised')
        User = UserInfo.objects.get(user_secret=secret)
        UserName = User.user_name
        return render(request, template_name, {'ingredient_list': ingredient_list, 'username': UserName})

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

    mass = ingrWeight_1 * count_1 + ingrWeight_2 * count_2 + 5

    if mass > 205 or mass < 25:

        error = 'Суп не удовлетворяет требованиям'
        return render(request, 'cooking/soupinfo.html', {'error_message': error})

    else:

        if mass <= 85:
            effectDuration = 20
        elif 85 < mass <= 145:
            effectDuration = 40
        else:
            effectDuration = 60

        Rarely = random.randint(1, 100)
        if Rarely <= 50:
            soupRarely = "Common"
            effectduration = effectDuration
            soupsteep = random.triangular(0.0001, 0.0129)
            soupsteep = round(soupsteep, 4)

        elif 50 < Rarely <= 75:
            soupRarely = "Rare"
            effectduration = effectDuration + int(round(effectDuration / 10))
            soupsteep = random.triangular(0.013, 0.026)
            soupsteep = round(soupsteep, 4)

        elif 75 < Rarely <= 87:
            soupRarely = "Epic"
            effectduration = effectDuration + int(round(effectDuration / 5))
            soupsteep = random.triangular(0.26, 0.1)
            soupsteep = round(soupsteep, 4)

        elif 87 < Rarely <= 94:
            soupRarely = "Legendary"
            effectduration = effectDuration + int(round(effectDuration / 2))
            soupsteep = random.triangular(0.101, 0.159)
            soupsteep = round(soupsteep, 4)

        elif 94 < Rarely < 100:
            soupRarely = "Ancient"
            effectduration = effectDuration + int(round(effectDuration / 4 * 3))
            soupsteep = random.triangular(0.16, 0.199)
            soupsteep = round(soupsteep, 4)

        else:
            soupRarely = "Divine"
            effectduration = effectDuration * 2
            soupsteep = random.triangular(0.2, 0.26)
            soupsteep = round(soupsteep, 4)

        EffectChance = random.randint(1, 6)

        if EffectChance < 6 and ingrCoeff_1 > ingrCoeff_2 and ingrWeight_2 * count_2 > 1.5 * ingrWeight_1 * count_1:
            soupEffect = ingrEffect_1 + ingrEffect_2
        elif EffectChance < 6 and ingrCoeff_1 < ingrCoeff_2 and ingrWeight_1 * count_1 > 1.5 * ingrWeight_2 * count_2:
            soupEffect = ingrEffect_1 + ingrEffect_2
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

        statistic_save = "Сохранить результат"

        soupsteep = str(soupsteep)

        if request.COOKIES.get('wasauthorised'):
            secret = request.COOKIES.get('wasauthorised')
            User = UserInfo.objects.get(user_secret=secret)
            UserName = User.user_name
            return render(request, 'cooking/soupinfo.html', {'SoupColor': SoupColor,
                                                             'SoupDuration': effectduration,
                                                             'SoupRarely': soupRarely,
                                                             'SoupEffect': soupEffect,
                                                             'SoupWeight': mass,
                                                             'statisticSave': statistic_save,
                                                             'SoupSteep': soupsteep,
                                                             'username': UserName})

        return render(request, 'cooking/soupinfo.html', {'SoupColor': SoupColor,
                                                         'SoupDuration': effectduration,
                                                         'SoupRarely': soupRarely,
                                                         'SoupEffect': soupEffect,
                                                         'SoupWeight': mass,
                                                         'statisticSave': statistic,
                                                         'SoupSteep': soupsteep})


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
            try:
                request.POST['complex']
                User.user_soup_list = text
                User.save()
                response = HttpResponseRedirect('/cooking/')
                return response
            except:
                if "," in User.user_soup_list:
                    soup_list = User.user_soup_list
                    soup_list = soup_list.split(",")
                    soup_count = len(soup_list) / 6
                    if soup_count == 2:
                        del soup_list[0:6]
                        text = text.split(",")
                        soup_list = soup_list + text
                        soup_list = ",".join(soup_list)
                        User.user_soup_list = soup_list
                        User.save()

                    elif soup_count == 1:
                        text = text.split(",")
                        soup_list = soup_list + text
                        soup_list = ",".join(soup_list)
                        User.user_soup_list = soup_list
                        User.save()

                else:
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
            return render(request, 'cooking/statistic.html', {'error_message': error_message, 'username': UserName})
        else:

            text1 = text.replace("'", '')
            res = text1.split(",")
            if len(res) == 6:
                soupEffect = res[0]
                effectduration = res[1]
                soupRarely = res[2]
                mass = res[3]
                SoupColor = res[4]
                soupsteep = res[5]

                return render(request, 'cooking/statistic.html', {'soupColor': SoupColor,
                                                                  'effectDuration': effectduration,
                                                                  'rarely': soupRarely,
                                                                  'soupEffect': soupEffect,
                                                                  'soupWeight': mass,
                                                                  'soupSteep': soupsteep,
                                                                  'username': UserName})

            if len(res) == 12:
                soupEffect = res[0]
                effectduration = res[1]
                soupRarely = res[2]
                mass = res[3]
                SoupColor = res[4]
                soupsteep = res[5]

                soupEffect1 = res[6]
                effectduration1 = res[7]
                soupRarely1 = res[8]
                mass1 = res[9]
                SoupColor1 = res[10]
                soupsteep1 = res[11]

                return render(request, 'cooking/statistic.html', {'soupColor': SoupColor,
                                                                  'effectDuration': effectduration,
                                                                  'rarely': soupRarely,
                                                                  'soupEffect': soupEffect,
                                                                  'soupWeight': mass,
                                                                  'soupSteep': soupsteep,
                                                                  'username': UserName,
                                                                  'soupColor1': SoupColor1,
                                                                  'effectDuration1': effectduration1,
                                                                  'rarely1': soupRarely1,
                                                                  'soupEffect1': soupEffect1,
                                                                  'soupWeight1': mass1,
                                                                  'soupSteep1': soupsteep1,
                                                                  })

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
            soupsteep = res[5]
            return render(request, 'cooking/statistic.html', {'soupColor': SoupColor,
                                                              'effectDuration': effectduration,
                                                              'rarely': soupRarely,
                                                              'soupEffect': soupEffect,
                                                              'soupWeight': mass,
                                                              'soupSteep': soupsteep})


def settings(request):
    if request.COOKIES.get('usersoup'):
        soupsave = "exist"
    else:
        soupsave = ""

    if request.COOKIES.get('wasauthorised'):
        secret = request.COOKIES.get('wasauthorised')
        wasauthorised = "exist"
        user = UserInfo.objects.get(user_secret=secret)
        userName = user.user_name

        return render(request, 'cooking/settings.html', {'soupsave': soupsave,
                                                         'wasauthorised': wasauthorised,
                                                         'username': userName})

    else:
        wasauthorised = ""

    return render(request, 'cooking/settings.html', {'soupsave': soupsave,
                                                     'wasauthorised': wasauthorised})


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

            if password:
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


def deletesoup(request):
    response = HttpResponseRedirect('/cooking/')
    if request.COOKIES.get('wasauthorised'):
        secret = request.COOKIES.get('wasauthorised')
        User = UserInfo.objects.get(user_secret=secret)

        if not User.user_soup_list == " ":
            souplist = User.user_soup_list
            souplist = souplist.split(',')
            del souplist[0:6]
            souplist = ",".join(souplist)
            User.user_soup_list = souplist
            User.save()

        return response

    else:
        return response


def deletesoup1(request):
    response = HttpResponseRedirect('/cooking/')
    if request.COOKIES.get('wasauthorised'):
        secret = request.COOKIES.get('wasauthorised')
        User = UserInfo.objects.get(user_secret=secret)

        if not User.user_soup_list == " ":
            souplist = User.user_soup_list
            souplist = souplist.split(',')
            del souplist[6:12]
            souplist = ",".join(souplist)
            User.user_soup_list = souplist
            User.save()

        return response

    else:
        return response


def createcomplex(request):

    secret = request.COOKIES.get('wasauthorised')
    User = UserInfo.objects.get(user_secret=secret)
    souplist = User.user_soup_list
    souplist = souplist.replace("'", '')
    res = souplist.split(",")

    soupEffect = res[0]
    effectduration = int(res[1])
    soupRarely = res[2]
    soupRarely = soupRarely.replace(' ', '')
    mass = int(res[3])
    SoupColor = res[4]
    soupsteep = float(res[5])

    soupEffect1 = res[6]
    effectduration1 = int(res[7])
    soupRarely1 = res[8]
    soupRarely1 = soupRarely1.replace(' ', '')
    mass1 = int(res[9])
    SoupColor1 = res[10]
    soupsteep1 = float(res[11])

    User.user_soup_list = ' '
    User.save()

    # Расчёт цвета

    soup_mass = mass + mass1
    SoupColor = SoupColor.replace(' ', '')
    SoupColor1 = SoupColor1.replace(' ', '')

    R_1 = int(SoupColor[0:2], 16) * mass
    G_1 = int(SoupColor[2:4], 16) * mass
    B_1 = int(SoupColor[4:], 16) * mass

    R_2 = int(SoupColor1[0:2], 16) * mass1
    G_2 = int(SoupColor1[2:4], 16) * mass1
    B_2 = int(SoupColor1[4:], 16) * mass1

    if round((R_1 + R_2) / soup_mass) < 15:
        Soup_R = '0' + hex(round((R_1 + R_2) / soup_mass))
    else:
        Soup_R = hex(round((R_1 + R_2) / soup_mass))

    if round((G_1 + G_2) / soup_mass) < 15:
        Soup_G = '0' + hex(round((G_1 + G_2) / soup_mass))
    else:
        Soup_G = hex(round((G_1 + G_2) / soup_mass))

    if round((B_1 + B_2) / soup_mass) < 15:
        Soup_B = '0' + hex(round((B_1 + B_2) / soup_mass))
    else:
        Soup_B = hex(round((B_1 + B_2) / soup_mass))

    # Окончание (Вывод)

    SoupColor = Soup_R + Soup_G + Soup_B
    SoupColor = SoupColor.replace("0x", "")

    # Расчёт редкости

    rarely_list = ['Common', 'Rare', 'Epic', 'Legendary', 'Ancient', 'Divine']
    for i in range(0, len(rarely_list)-1):
        if soupRarely in rarely_list[i]:
            rarely = i
            break

    for i in range(0, len(rarely_list)-1):
        if soupRarely1 in rarely_list[i]:
            rarely1 = i
            break

    if rarely1 == rarely:
        SoupRarely = rarely_list[rarely]
        SoupRarelyIndex = rarely

    elif rarely != rarely1:
        if rarely < rarely1:
            SoupRarelyIndex = rarely + round(abs(rarely - rarely1) / 2)
        else:
            SoupRarelyIndex = rarely1 + round(abs(rarely - rarely1) / 2)
        chanse = random.randint(0, 1)
        if chanse == 1:
            SoupRarely = rarely_list[SoupRarelyIndex+1]
        else:
            SoupRarely = rarely_list[SoupRarelyIndex]

    # Расчёт эффектов

    ingr = Ingredient.objects.get(ingredient_effect=soupEffect)
    ingr_coeff = ingr.ingredient_coefficient

    ingr1 = Ingredient.objects.get(ingredient_effect=soupEffect1)
    ingr_coeff1 = ingr1.ingredient_coefficient

    if ingr_coeff > ingr_coeff1 and mass > 1.3 * mass1:
        SoupEffect = soupEffect
    else:
        SoupEffect = soupEffect

    # Расчёт длительности

        SoupDuration = round((effectduration + effectduration1) / 2)

    # Paсчёт крутизны

    if SoupRarelyIndex >= 3:
        if round((ingr_coeff1 + ingr_coeff) / 2) > 2:
            chanse = random.randint(0, 6)
            if chanse <= 2:
                if soupsteep > soupsteep1:

                    SoupSteep = round(soupsteep + random.triangular(0.08, 0.16), 4)
                else:
                    SoupSteep = round(soupsteep1 + random.triangular(0.07, 0.16), 4)

            else:
                if soupsteep > soupsteep1:

                    SoupSteep = round(soupsteep + random.triangular(0.08, 0.1), 4)
                else:
                    SoupSteep = round(soupsteep1 + random.triangular(0.07, 0.1), 4)

        else:
            Noise = round(random.triangular(0.06, 0.095), 4)
            if soupsteep > soupsteep1:
                SoupSteep = round(soupsteep + Noise, 4)
            else:
                SoupSteep = round(soupsteep1 + Noise, 4)

    else:
        SoupSteep = round((soupsteep + soupsteep1) / 2, 4)
        Chanse = random.randint(0, 3)

        for i in range(len(rarely_list)):
            if soupRarely in rarely_list[i]:
                rarely = i
                break

        if rarely >= 4:
            a = 0.09
            b = 0.11

        else:
            a = 0.001
            b = 0.06

        Noise = round(random.triangular(a, b), 4)
        if Chanse == 3:
            SoupSteep = abs(round(SoupSteep - Noise, 4))
        else:
            SoupSteep = round(SoupSteep + Noise, 4)

        UserName = User.user_name

    SoupSteep = str(SoupSteep)

    statistic = "Сохранить результат"
    lol = 'lol'

    return render(request, 'cooking/soupinfo.html', {'SoupColor': SoupColor,
                                                        'SoupDuration': SoupDuration,
                                                        'SoupRarely': SoupRarely,
                                                        'SoupEffect': SoupEffect,
                                                        'SoupWeight': mass,
                                                        'SoupSteep': SoupSteep,
                                                        'username': UserName,
                                                        'statisticSave': statistic,
                                                        'lol': lol})

