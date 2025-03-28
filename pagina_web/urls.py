from django.urls import path
from . import views

pagina_web_patterns = ([
                        path('home', views.landing, name='landing'), 
                        path('productos/', views.productos, name='productos')                       
                     ], 'pagina_web')
