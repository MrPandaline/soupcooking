from django.urls import path

from . import views


app_name = 'cooking'
urlpatterns = [
    path('', views.IndexView, name='index'),
    path('ingredient/', views.IngredientsView.as_view(), name='ingredient'),
    path('makesoup/', views.MakeSoupView.as_view(), name='makesoup'),
    path('makesoup/soupinfo/', views.soupinfo, name='soupinfo'),
    path('api/', views.api, name='api'),
    path('statistic/', views.statistic, name='statistic'),
    path('addstatistic/', views.addstatistic, name='addstatistic'),
    path('resetcookies/', views.resetcookies, name='resetcookies'),
    path('settings/', views.settings, name='settings')
]
