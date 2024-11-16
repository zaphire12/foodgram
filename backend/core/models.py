from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class UserRecipeModel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='%(class)ss'
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_%(class)s'
            ),
        )

    def __str__(self):
        return f'{self._meta.verbose_name} - {self.recipe.name}'
