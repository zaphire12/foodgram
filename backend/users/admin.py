from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from rest_framework.authtoken.models import TokenProxy

from .models import Subscribe

User = get_user_model()


@admin.register(User)
class UsersAdmin(UserAdmin):
    """Админка для пользователя."""

    list_display = ('id', 'full_name', 'username', 'email', 'avatar_tag',
                    'recipe_count', 'subscriber_count', 'is_staff')
    search_fields = ('username', 'email')
    search_help_text = 'Поиск по `username` и `email`'
    list_display_links = ('id', 'username', 'email', 'full_name')

    @admin.display(description='Имя фамилия')
    def full_name(self, user):
        return user.get_full_name()

    @admin.display(description='Аватар')
    def avatar_tag(self, user):
        if user.avatar:
            return mark_safe(f'<img src="{user.avatar.url}"'
                             'style="border-radius: 50%; object-fit: cover; '
                             'width="80" height="60">')
        return 'Нет аватара'

    @admin.display(description='Кол-во рецептов')
    def recipe_count(self, user):
        return user.recipes.count()

    @admin.display(description='Кол-во подписчиков')
    def subscriber_count(self, user):
        return user.subscriptions_to_author.count()


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')


admin.site.unregister([Group, TokenProxy])
