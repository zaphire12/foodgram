from rest_framework.pagination import PageNumberPagination

from core.constants import DEFAULT_PAGE_SIZE


class FoodgramPaginator(PageNumberPagination):
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'limit'
