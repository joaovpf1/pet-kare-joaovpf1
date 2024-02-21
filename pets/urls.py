from django.urls import path
from pets.views import PetView, PetViewDetail

urlpatterns = [
    path("pets/", PetView.as_view()),
    path("pets/<int:pet_id>/", PetViewDetail.as_view()),
]
