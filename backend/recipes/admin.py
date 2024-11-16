from django.contrib import admin

from core.constants import INGREDIENT_MIN_AMOUNT
from recipes.models import Ingredient, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    """Строчное представление ингредиента в рецепте."""

    model = RecipeIngredient
    min_num = INGREDIENT_MIN_AMOUNT


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_display_links = ('name',)
    search_fields = ('name',)
    search_help_text = 'Поиск по названию ингредиента'
