import datetime

from django.db.models import Q
from django.utils.deprecation import MiddlewareMixin

from main.models import Meeting
from django.utils import timezone


class StatusUpdateMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        
        # check status tp process
        data = Meeting.objects.filter(
            Q(start_time__lte=timezone.now(), end_time__gt=timezone.now())).update(status=2)
        data2 = Meeting.objects.filter(Q(end_time__lte=timezone.now())).update(status=3)
        data3 = Meeting.objects.filter(
            start_time__gte=timezone.now()).update(status=1)
        return response
