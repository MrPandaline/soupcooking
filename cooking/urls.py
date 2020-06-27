from django.urls import path

from . import views


app_name = 'cooking'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('ingredient/', views.IngredientsView.as_view(), name='ingredients'),
    path('ingredient/<int:pk>', views.DetailView.as_view(), name='detail'),
    path('makesoup/', views.MakeSoupView.as_view(), name='makesoup'),
    path('makesoup/soupinfo/', views.soupinfo, name='soupinfo'),
    path('api/', views.hello, name='hello')
]
