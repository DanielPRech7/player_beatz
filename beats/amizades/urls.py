from django.urls import path
from . import views

app_name = 'amizades'

urlpatterns = [
    path('', views.ListaUsuariosView.as_view(), name='lista'),
    path('adicionar/<int:pk>/', views.AdicionarAmigoView.as_view(), name='adicionar'),
    path('responder/<int:pk>/', views.ResponderAmigoView.as_view(), name='responder'),
]
