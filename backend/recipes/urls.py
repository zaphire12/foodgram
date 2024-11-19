from django.urls import path

from recipes.views import redirect_to_original

urlpatterns = [
    path('<slug:slug>/',
         redirect_to_original,
         name='redirect_to_original'),
]
