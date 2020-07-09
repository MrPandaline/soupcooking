from django.urls import path

from . import views


app_name = 'cooking'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('ingredient/', views.IngredientsView.as_view(), name='ingredient'),
    path('ingredient/<int:pk>', views.DetailView.as_view(), name='detail'),
    path('makesoup/', views.MakeSoupView.as_view(), name='makesoup'),
    path('makesoup/soupinfo/', views.soupinfo, name='soupinfo'),
    path('api/', views.api, name='api'),
    path('statistic/', views.statistic, name='statistic'),
    path('addstatistic/', views.addstatistic, name='addstatistic'),
]
