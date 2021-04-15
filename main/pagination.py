from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    """
    TODO: 1. page size should be customized to query param number |inside Response, it is called: 'per_page': self.page_size
    """
    page_size_query_param = 'size'
    page_size = 10

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'page_size': self.get_page_size(self.request),
            'current_page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'page_items': len(self.page),
            'total': self.page.paginator.count,
            'results': data
        })




    # def get_paginated_response(self, data):
    #     return Response(OrderedDict([
    #         ('count', self.page.paginator.count),
    #         ('next', self.get_next_link()),
    #         ('previous', self.get_previous_link()),
    #         ('results', data)
    #     ]))
