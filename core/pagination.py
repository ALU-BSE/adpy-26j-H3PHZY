from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class MetaDataPagination(PageNumberPagination):
    """Pagination returning a `meta`/`data` split payload.

    Includes total_count, current_page, next/prev links, and respects
    `?page`/`?size` query params.
    """

    page_size_query_param = 'size'

    def get_paginated_response(self, data):
        return Response({
            'meta': {
                'total_count': self.page.paginator.count,
                'current_page': self.page.number,
                'next_link': self.get_next_link(),
                'prev_link': self.get_previous_link(),
            },
            'data': data,
        })
