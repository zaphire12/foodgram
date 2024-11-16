from django.contrib.auth import get_user_model
from django.db.models import Count, Exists, F, OuterRef, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeCreateSerializer, RecipeSerializer,
                             ShoppingCartSerializer, SubscribeGETSerializer,
                             SubscribePOSTSerializer, TagSerializer)
from core.constants import FILE_NAME
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.serializers import AvatarSerializer, UserSerializer

User = get_user_model()

from users.models import Subscribe


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        return Response(self.get_serializer(request.user).data)

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        queryset = User.objects.filter(
            subscriptions_to_author__user=request.user
        ).annotate(recipes_count=Count('recipes')).order_by('username')
        page = self.paginate_queryset(queryset)
        serializer = SubscribeGETSerializer(page, many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=('post',),
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        serializer = SubscribePOSTSerializer(
            data={'user': request.user.id, 'author': author.id},
            context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        deleted, _ = Subscribe.objects.filter(user=request.user,
                                              author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT if deleted
        else status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=('put',), url_path='me/avatar',
            permission_classes=(IsAuthenticated,))
    def avatar(self, request):
        serializer = AvatarSerializer(request.user,
                                      data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        user = request.user
        user.avatar.delete(save=False)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.select_related('author').prefetch_related(
            'tags', 'ingredients'
        )
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(user=user,
                                            recipe=OuterRef('pk'))
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(user=user,
                                                recipe=OuterRef('pk'))
                )
            )
        return queryset

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=('post',),
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        return self.handle_favorite_or_cart(request, pk, FavoriteSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        deleted, _ = Favorite.objects.filter(user=request.user,
                                             recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT if deleted
        else status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=('post',))
    def shopping_cart(
            self,
            request,
            pk=None,
            permission_classes=(IsAuthenticated,)):
        return self.handle_favorite_or_cart(
            request, pk, ShoppingCartSerializer
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        deleted, _ = ShoppingCart.objects.filter(user=request.user,
                                                 recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT if deleted
        else status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shopping_cart__user=request.user)
            .values(name=F('ingredient__name'),
                    unit=F('ingredient__measurement_unit'))
            .annotate(total_amount=Sum('amount'))
            .order_by('name')
        )
        file_list = [
            f'{ingredient["name"]} ({ingredient["unit"]}) — '
            f'{ingredient["total_amount"]}'
            for ingredient in ingredients
        ]
        file_content = 'Список покупок:\n' + '\n'.join(file_list)
        response = FileResponse(file_content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{FILE_NAME}"'
        return response

    @action(detail=True, methods=('get',),
            url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        short_url_path = reverse('redirect_to_original', kwargs={
            'slug': recipe.short_url}
                                 )
        short_link = request.build_absolute_uri(short_url_path)
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)

    def handle_favorite_or_cart(self, request, pk, serializer_class):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = serializer_class(
            data={'user': request.user.id, 'recipe': recipe.id},
            context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
