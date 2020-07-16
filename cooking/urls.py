from django.urls import path

from . import views


app_name = 'cooking'
urlpatterns = [
    path('', views.IndexView, name='index'),
    path('ingredient/', views.IngredientsView, name='ingredient'),
    path('makesoup/', views.MakeSoupView, name='makesoup'),
    path('makesoup/soupinfo/', views.soupinfo, name='soupinfo'),
    path('api/', views.api, name='api'),
    path('statistic/', views.statistic, name='statistic'),
    path('addstatistic/', views.addstatistic, name='addstatistic'),
    path('resetcookies/', views.resetcookies, name='resetcookies'),
    path('settings/', views.settings, name='settings'),
    path('register/', views.auth, name='auth'),
    path('login/', views.login, name='login'),
    path('register/redir/', views.auth_redir, name='auth-redirect'),
    path('login/redir/', views.login_redir, name='login-redirect'),
    path('exit/', views.exit, name='exit'),
    path('deletesave/', views.deletesave, name='deletesave'),
]
