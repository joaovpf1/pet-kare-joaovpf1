from django.shortcuts import render
from rest_framework.views import status, Response, Request, APIView
from pets.serializers import PetSerializer
from .models import Pet
from groups.models import Group
from traits.models import Trait
from rest_framework.pagination import PageNumberPagination
from pets.pagination import CustomPagination


# Create your views here.


class PetView(APIView, CustomPagination):
    def post(self, request: Request) -> Response:
        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group_data = serializer.validated_data.pop("group")
        trait_data = serializer.validated_data.pop("traits")

        try:
            group = Group.objects.get(scientific_name=group_data["scientific_name"])
        except Group.DoesNotExist:
            group = Group.objects.create(**group_data)

        pet: Pet = Pet.objects.create(**serializer.validated_data, group=group)

        for request_trait in trait_data:
            try:
                trait = Trait.objects.get(name__iexact=request_trait["name"])
            except Trait.DoesNotExist:
                trait = Trait.objects.create(**request_trait)
            pet.traits.add(trait)

        serializer = PetSerializer(pet)
        return Response(serializer.data, status.HTTP_201_CREATED)

    def get(self, request: Request) -> Response:
        by_trait = request.query_params.get("trait", None)
        if by_trait:
            pets = Pet.objects.filter(traits__name__icontains=by_trait)
        else:
            pets = Pet.objects.all()
        result_page = self.paginate_queryset(pets, request, view=self)
        serializer = PetSerializer(result_page, many=True)

        return self.get_paginated_response(serializer.data)


class PetViewDetail(APIView):
    def get(self, request: Request, pet_id: int) -> Response:
        try:
            found_pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, status.HTTP_404_NOT_FOUND)

        serializer = PetSerializer(found_pet)
        return Response(serializer.data, status.HTTP_200_OK)

    def delete(self, request: Request, pet_id: int) -> Response:
        try:
            found_pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, status.HTTP_404_NOT_FOUND)
        found_pet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request: Request, pet_id: int) -> Response:
        try:
            found_pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, status.HTTP_404_NOT_FOUND)

        serializer = PetSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        group_data = serializer.validated_data.pop("group", "")
        trait_data = serializer.validated_data.pop("traits", "")

        if group_data:
            try:
                group = Group.objects.get(scientific_name=group_data["scientific_name"])
                found_pet.group = group
            except Group.DoesNotExist:
                group = Group.objects.create(**group_data)
                found_pet.group = group

        new_traits = []
        if trait_data:
            for request_trait in trait_data:
                try:
                    trait = Trait.objects.get(name__iexact=request_trait["name"])
                    new_traits.append(trait)
                except Trait.DoesNotExist:
                    trait = Trait.objects.create(**request_trait)
                    new_traits.append(trait)
            found_pet.traits.set(new_traits)

        for key, value in serializer.validated_data.items():
            setattr(found_pet, key, value)

        found_pet.save()
        serializer = PetSerializer(found_pet)
        return Response(serializer.data, status.HTTP_200_OK)
